import flet as ft
from openai import OpenAI
import os
from login import LoginPage
from daily_tasks import daily_tasks

class Task(ft.Column):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed, active_color=ft.Colors.PURPLE_ACCENT
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
            ]
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

        self.controls = [self.display_view, self.edit_view]

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

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_status_change(self)

    def delete_clicked(self, e):
        self.task_delete(self)


class DailyTasksApp(ft.Column):
    def __init__(self, page):
        super().__init__()

        self.page = page
        self.new_task = ft.TextField(
            hint_text="What needs to be done today?", on_submit=self.add_clicked, expand=True,
            border_color=ft.Colors.GREY
        )
        self.tasks = ft.Column()

        self.controls = [
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
                controls=[
                    self.tasks,
                ],
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

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()


def daily_tasks(page: ft.Page):
    page.title = "Daily Tasks"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    page.add(DailyTasksApp(page))


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
            ft.Row(
                [ft.Text(value="To-Do List", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, color=ft.Colors.PURPLE)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=20),
            ft.Row(
                controls=[
                    self.drawer_button,
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
                controls=[
                    self.filter,
                    self.tasks,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.items_left,
                            ft.OutlinedButton(
                                text="Clear completed", on_click=self.clear_clicked,
                                style=ft.ButtonStyle(
                                    padding=ft.Padding(left=20, right=20, top=10, bottom=10),
                                    bgcolor=ft.Colors.ORANGE_ACCENT,
                                    color=ft.Colors.BLACK
                                )
                            ),
                        ],
                    ),
                ],
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

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def tabs_changed(self, e):
        pass

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
                label="Daily Tasks",  # This is Item 2 now
                icon=ft.Icons.DATE_RANGE,
                selected_icon=ft.Icon(ft.Icons.DATE_RANGE),
            ),
            ft.NavigationDrawerDestination(
                label="Switch Modes",  # Mode Switch
                icon=ft.Icons.DARK_MODE_OUTLINED,
            ),
        ]
    )

    # Function to handle navigation when a drawer item is selected
    def on_drawer_index_change(e):
        selected_index = drawer.selected_index
        if selected_index == 0:  # To-Do List selected
            page.clean()  # Clear current content
            page.add(TodoApp(drawer_button, drawer, page))  # Add To-Do list page
        elif selected_index == 1:  # Daily Tasks selected
            page.clean()  # Clear current content
            daily_tasks(page)  # Add Daily Tasks page
        elif selected_index == 2:  # Switch mode selected
            if page.theme_mode == ft.ThemeMode.LIGHT:
                page.theme_mode = ft.ThemeMode.DARK
            else:
                page.theme_mode = ft.ThemeMode.LIGHT
            page.update()

    drawer.on_change = on_drawer_index_change

    # Add login or initial page if needed
    def on_login_success():
        page.clean()
        page.add(TodoApp(drawer_button, drawer, page))

    page.add(LoginPage(on_login_success=on_login_success))

ft.app(main)
