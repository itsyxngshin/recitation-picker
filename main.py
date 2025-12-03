from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
import random

class RecitationPicker(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.students = [] # List to store student names

        # Main Layout (Vertical)
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = MDLabel(
            text="Classroom Picker", 
            halign="center", 
            font_style="H4",
            size_hint_y=None, 
            height=100
        )
        
        # Input Field
        self.input_name = MDTextField(
            hint_text="Enter student name",
            mode="rectangle",
            size_hint_y=None, 
            height=50
        )

        # Button to Add Student
        add_btn = MDRaisedButton(
            text="Add Student",
            pos_hint={"center_x": 0.5},
            on_release=self.add_student
        )

        # Label to show the result
        self.result_label = MDLabel(
            text="Ready to pick...",
            halign="center",
            font_style="H3",
            theme_text_color="Custom",
            text_color=(0, 0.5, 0, 1) # Green color
        )

        # Button to Pick Random
        pick_btn = MDRaisedButton(
            text="PICK RANDOM STUDENT",
            md_bg_color=(1, 0, 0, 1), # Red button
            pos_hint={"center_x": 0.5},
            size_hint=(1, None),
            height=50,
            on_release=self.pick_student
        )

        # Add widgets to layout
        layout.add_widget(title)
        layout.add_widget(self.input_name)
        layout.add_widget(add_btn)
        layout.add_widget(self.result_label)
        layout.add_widget(pick_btn)

        screen = MDScreen()
        screen.add_widget(layout)
        return screen

    def add_student(self, instance):
        name = self.input_name.text.strip()
        if name:
            self.students.append(name)
            self.input_name.text = "" # Clear input
            self.result_label.text = f"Added: {name}"
            self.result_label.theme_text_color = "Primary"
        else:
            self.result_label.text = "Please enter a name!"

    def pick_student(self, instance):
        if not self.students:
            self.result_label.text = "List is empty!"
            self.result_label.theme_text_color = "Error"
        else:
            selected = random.choice(self.students)
            self.result_label.text = selected
            self.result_label.theme_text_color = "Custom"
            self.result_label.text_color = (0, 0.5, 0, 1)

if __name__ == '__main__':
    RecitationPicker().run()