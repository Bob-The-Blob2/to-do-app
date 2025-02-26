import flet as ft
import sqlite3

class LoginPage(ft.Column):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success

        self.username = ft.TextField(hint_text="Username", width=300, on_submit=self.submit_clicked)
        self.password = ft.TextField(hint_text="Password", password=True, width=300, on_submit=self.submit_clicked)

        self.login_button = ft.FloatingActionButton(
            icon=ft.Icons.LOGIN,
            on_click=self.submit_clicked,
            bgcolor='#ffa028',
        )

        self.register_button = ft.TextButton(
            text="Create an account",
            on_click=self.switch_to_register,
            style=ft.ButtonStyle(
                color=ft.Colors.BLUE
            )
        )
        self.error_message = ft.Text("", color=ft.colors.RED)

        self.controls = [
            ft.Row([ft.Text("Login", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=40),
            ft.Row([self.username], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.password], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.login_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.register_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.error_message], alignment=ft.MainAxisAlignment.CENTER)
        ]

        self.alignment = ft.MainAxisAlignment.CENTER

        self.is_registering = False

    def submit_clicked(self, e):
        if self.is_registering:
            self.register_user()
        else:
            self.login_user()

    def switch_to_register(self, e):
        self.is_registering = True
        self.controls[0] = ft.Row([ft.Text("Register", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)], alignment=ft.MainAxisAlignment.CENTER)
        self.register_button.visible = False
        self.update()

    def login_user(self):
        username = self.username.value
        password = self.password.value

        if self.check_user_credentials(username, password):
            self.on_login_success()
        else:
            self.error_message.value = "Invalid username or password!"
            self.update()

    def register_user(self):
        username = self.username.value
        password = self.password.value
        
        if username and password:
            if self.check_user_exists(username):
                self.error_message.value = "Username already exists! Please choose a different one."
            else:
                self.add_user_to_db(username, password)
                self.error_message.value = "Account Created! You can now login."
                self.is_registering = False
                self.controls[0] = ft.Row([ft.Text("Login", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)], alignment=ft.MainAxisAlignment.CENTER)
                self.register_button.visible = True
            self.update()
        else:
            self.error_message.value = "Username and Password are required!"
            self.update()

    def check_user_exists(self, username):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(1) FROM users WHERE username = ?", (username,))
        exists = cursor.fetchone()[0] > 0
        conn.close()
        return exists

    def check_user_credentials(self, username, password):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        stored_password = cursor.fetchone()
        conn.close()
        
        return stored_password and stored_password[0] == password

    def add_user_to_db(self, username, password):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
