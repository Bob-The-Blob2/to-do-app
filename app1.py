import flet as ft
from login import LoginPage
from openai import OpenAI
import os

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
                ft.PopupMenuItem(
                    text = "Create schedule",
                    on_click = self.create_plan,
                    icon = ft.Icons.DATE_RANGE
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
    
    def create_plan(self, e):
        API_KEY = os.environ.get('OPENAI_API_KEY', "dont-know")
        MODEL = "gpt-3.5-turbo"

        client = OpenAI(api_key=API_KEY)
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Create a detailed plan to achieve the given goal, breaking it down into actionable steps with a timeline. Make sure the plan is practical and achievable, including daily or weekly tasks, milestones, and any additional tips or resources that might be helpful. Give me the output in JSON format with goal as a key and the plan/steps as sub-keys."},
                    {"role": "user", "content": self.task_name}
                ]
            )
            print("Assistant: " + response.choices[0].message.content)

        except Exception as ex:
            print(f"Error while generating plan")




class TodoApp(ft.Column):
    def __init__(self):
        super().__init__()
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
            ft.Container(
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(
                            icon=ft.Icons.ADD,
                            on_click=self.add_clicked,
                            bgcolor='#ffa028',
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                padding=ft.Padding(top=20, left=20, right=20, bottom=20)
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

    def on_login_success():
        page.clean()
        page.add(TodoApp())

    page.add(LoginPage(on_login_success=on_login_success))


ft.app(main)    