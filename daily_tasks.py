import flet as ft

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
        # Fixed width layout, like in the original example
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

