import flet as ft
import sqlite3
import openai
import os
from login import LoginPage
from dotenv import load_dotenv

conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

class Task(ft.Column):
    def __init__(self, task_name, task_status_change, task_delete, task_id=None, completed=False):
        super().__init__()
        self.task_id = task_id
        self.completed = completed
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.display_task = ft.Checkbox(
            value=self.completed, label=self.task_name, on_change=self.status_changed, active_color=ft.Colors.PURPLE_ACCENT
        )
        self.edit_name = ft.TextField(expand=1, border_color=ft.Colors.GREY)

        self.popup_menu = ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT,
            items=[
                ft.PopupMenuItem(
                    text="Edit",
                    on_click=self.edit_clicked,
                    icon=ft.Icons.CREATE_OUTLINED
                ),
                ft.PopupMenuItem(
                    text="Delete",
                    on_click=self.delete_clicked,
                    icon=ft.Icons.DELETE_OUTLINE
                ),
                ft.PopupMenuItem(
                    text="Create plan",
                    on_click=self.create_plan,
                    icon=ft.Icons.DATE_RANGE
                ),
            ]
        )

        self.expansion_tile = ft.ExpansionTile(
            title=ft.Text("show plan"),
            controls=[ft.Text("No plan available yet.")]
        )

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=10,
                    controls=[self.popup_menu],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )

        self.controls = [self.display_view, self.edit_view, self.expansion_tile]

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

        # Update task name in the database
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET task_name = ? WHERE id = ?", (self.display_task.label, self.task_id))
        conn.commit()
        conn.close()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_status_change(self)

        # Update task status in the database
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (self.completed, self.task_id))
        conn.commit()
        conn.close()

    def delete_clicked(self, e):
        self.task_delete(self)

        # Delete task from the database
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (self.task_id,))
        conn.commit()
        conn.close()

    def create_plan(self, e):
        load_dotenv(override = True)
        
        API_KEY = os.environ.get('OPENAI_API_KEY', "dont-know")
        MODEL = "gpt-3.5-turbo"

        openai.api_key = API_KEY

        try:
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Create a detailed plan to \
                     achieve the given goal, breaking it down into actionable steps with a timeline. Make sure \
                     the plan is practical and achievable, including daily or weekly tasks, milestones, and any \
                     additional tips or resources that might be helpful. Format the output in a proffesional manner \
                     goal as a key and the plan/steps as sub-keys."},
                    {"role": "user", "content": self.task_name}
                ]
            )
            self.response_var = response.choices[0].message.content

            self.expansion_tile.controls = [ft.Text(f"{self.response_var}")]
            self.update()

        except Exception as ex:
            print(f"Error while generating plan: {ex}")
            self.response_var = "Error generating plan"
            self.expansion_tile.controls = [ft.Text(f"{self.response_var}")]
            self.update()

class DailyTasksApp(ft.Column):
    def __init__(self, page, drawer_button, drawer):
        super().__init__()

        self.page = page
        self.new_task = ft.TextField(
            hint_text="What needs to be done today?", on_submit=self.add_clicked, expand=True,
            border_color=ft.Colors.GREY
        )
        self.tasks = ft.Column()

        self.drawer_button = drawer_button
        self.drawer = drawer

        # Load tasks from the database
        self.load_tasks_from_db()

        self.controls = [
            self.drawer_button,  # Add the drawer button for navigation
            ft.Row(
                [ft.Text(value="Daily Tasks", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, color=ft.Colors.PURPLE)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=20),
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        icon=ft.Icons.ADD,
                        on_click=self.add_clicked,
                        bgcolor='#ffa028',
                    ),
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            ft.Column(
                spacing=25,
                controls=[self.tasks],
            ),
        ]
        self.width = 500
        self.padding = ft.Padding(20, 20, 20, 20)
        self.bgcolor = ft.Colors.LIGHT_BLUE_50

    def add_clicked(self, e):
        if self.new_task.value:
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update()

            # Add the new task to the database
            conn = sqlite3.connect("tasks.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (task_name, completed) VALUES (?, ?)", (task.task_name, task.completed))
            conn.commit()
            conn.close()

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def load_tasks_from_db(self):
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, task_name, completed FROM tasks")
        rows = cursor.fetchall()
        for row in rows:
            task = Task(row[1], self.task_status_change, self.task_delete, task_id=row[0], completed=row[2])
            self.tasks.controls.append(task)
        conn.close()

def daily_tasks(page: ft.Page):
    page.title = "Daily Tasks"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    drawer_button = ft.IconButton(icon=ft.Icons.MENU, on_click=lambda e: page.open(drawer))

    drawer = ft.NavigationDrawer(
        selected_index=0,
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="To-Do List",
                icon=ft.Icons.LIST,
                selected_icon=ft.Icon(ft.Icons.LIST_ALT),
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Daily Tasks",
                icon=ft.Icons.DATE_RANGE,
                selected_icon=ft.Icon(ft.Icons.DATE_RANGE),
            ),
            ft.NavigationDrawerDestination(
                label="Switch Modes",
                icon=ft.Icons.DARK_MODE_OUTLINED,
            ),
        ]
    )

    def on_drawer_index_change(e):
        selected_index = drawer.selected_index
        if selected_index == 0:
            page.clean()
            page.add(TodoApp(drawer_button, drawer, page))
        elif selected_index == 1:
            page.clean()
            daily_tasks(page)
        elif selected_index == 2:
            if page.theme_mode == ft.ThemeMode.LIGHT:
                page.theme_mode = ft.ThemeMode.DARK
            else:
                page.theme_mode = ft.ThemeMode.LIGHT
            page.update()

    drawer.on_change = on_drawer_index_change

    page.add(DailyTasksApp(page, drawer_button, drawer))

class TodoApp(ft.Column):
    def __init__(self, drawer_button, drawer, page):
        super().__init__()

        self.page = page
        self.drawer_button = drawer_button
        self.drawer = drawer

        self.new_task = ft.TextField(
            hint_text="What needs to be done?", on_submit=self.add_clicked, expand=True,
            border_color=ft.Colors.GREY
        )
        self.tasks = ft.Column()

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="All"), ft.Tab(text="Active"), ft.Tab(text="Completed")]
        )

        self.items_left = ft.Text("0 items left")

        self.width = 500
        self.controls = [
            self.drawer_button,
            ft.Row(
                [ft.Text(value="To-Do List", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, color=ft.Colors.PURPLE)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=20),
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        icon=ft.Icons.ADD,
                        on_click=self.add_clicked,
                        bgcolor='#ffa028',
                    ),
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            ft.Column(
                spacing=25,
                controls=[self.filter, self.tasks, ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.items_left, ft.OutlinedButton(text="Clear completed", on_click=self.clear_clicked)]
                )],
            ),
        ]
        self.padding = ft.Padding(20, 20, 20, 20)
        self.bgcolor = ft.Colors.LIGHT_BLUE_50

    def add_clicked(self, e):
        if self.new_task.value:
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update()

            # Add the new task to the database
            conn = sqlite3.connect("tasks.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (task_name, completed) VALUES (?, ?)", (task.task_name, task.completed))
            conn.commit()
            conn.close()

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.task_delete(task)

    def before_update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "All"
                or (status == "Active" and task.completed == False)
                or (status == "Completed" and task.completed)
            )
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} active item(s) left"

def main(page: ft.Page):
    page.title = "ToDo App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    drawer_button = ft.IconButton(icon=ft.Icons.MENU, on_click=lambda e: page.open(drawer))

    drawer = ft.NavigationDrawer(
        selected_index=0,
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="To-Do List",
                icon=ft.Icons.LIST,
                selected_icon=ft.Icon(ft.Icons.LIST_ALT),
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Daily Tasks",
                icon=ft.Icons.DATE_RANGE,
                selected_icon=ft.Icon(ft.Icons.DATE_RANGE),
            ),
            ft.NavigationDrawerDestination(
                label="Switch Modes",
                icon=ft.Icons.DARK_MODE_OUTLINED,
            ),
        ]
    )

    def on_drawer_index_change(e):
        selected_index = drawer.selected_index
        if selected_index == 0:
            page.clean()
            page.add(TodoApp(drawer_button, drawer, page))
        elif selected_index == 1:
            page.clean()
            daily_tasks(page)
        elif selected_index == 2:
            if page.theme_mode == ft.ThemeMode.LIGHT:
                page.theme_mode = ft.ThemeMode.DARK
            else:
                page.theme_mode = ft.ThemeMode.LIGHT
            page.update()

    drawer.on_change = on_drawer_index_change

    def on_login_success():
        page.clean()
        page.add(TodoApp(drawer_button, drawer, page))

    page.add(LoginPage(on_login_success=on_login_success))

ft.app(main)