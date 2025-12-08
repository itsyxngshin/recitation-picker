from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
import random

class RecitationPicker(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_hue = "500"
        
        self.students = []  # List to store student names
        
        # Main Layout (Vertical)
        main_layout = MDBoxLayout(orientation='vertical', spacing=0)
        
        # Top App Bar
        toolbar = MDTopAppBar(
            title="Classroom Recitation Picker",
            elevation=4,
            md_bg_color=self.theme_cls.primary_color,
            specific_text_color=(1, 1, 1, 1)
        )
        
        # Content Layout
        content_layout = MDBoxLayout(
            orientation='vertical',
            padding=[20, 20, 20, 20],
            spacing=20,
            size_hint_y=None
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Input Section Card
        input_card = MDCard(
            elevation=2,
            radius=10,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=200
        )
        
        input_layout = MDBoxLayout(orientation='vertical', spacing=15)
        
        # Title for input section
        input_title = MDLabel(
            text="Add Student",
            halign="center",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height=30
        )
        
        # Input Field
        self.input_name = MDTextField(
            hint_text="Enter student name here...",
            mode="rectangle",
            icon_right="account-plus",
            size_hint_y=None,
            height=50
        )
        
        # Add Button
        add_btn = MDRaisedButton(
            text="ADD STUDENT",
            md_bg_color=self.theme_cls.primary_color,
            size_hint_y=None,
            height=50,
            on_release=self.add_student
        )
        
        input_layout.add_widget(input_title)
        input_layout.add_widget(self.input_name)
        input_layout.add_widget(add_btn)
        input_card.add_widget(input_layout)
        
        # Current Students Card
        students_card = MDCard(
            elevation=2,
            radius=10,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=120
        )
        
        students_layout = MDBoxLayout(orientation='vertical', spacing=10)
        
        students_title = MDLabel(
            text="Current Students",
            halign="center",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height=30
        )
        
        # Label to show current student count
        self.students_label = MDLabel(
            text="No students added yet",
            halign="center",
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=40
        )
        
        students_layout.add_widget(students_title)
        students_layout.add_widget(self.students_label)
        students_card.add_widget(students_layout)
        
        # Result Display Card
        result_card = MDCard(
            elevation=2,
            radius=10,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=150
        )
        
        result_layout = MDBoxLayout(orientation='vertical', spacing=10)
        
        result_title = MDLabel(
            text="Selected Student",
            halign="center",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height=30
        )
        
        self.result_label = MDLabel(
            text="Ready to pick...",
            halign="center",
            font_style="H4",
            theme_text_color="Secondary",
            bold=True
        )
        
        result_layout.add_widget(result_title)
        result_layout.add_widget(self.result_label)
        result_card.add_widget(result_layout)
        
        # Pick Button
        pick_btn = MDRaisedButton(
            text="🎯 PICK RANDOM STUDENT",
            md_bg_color=(0.8, 0.1, 0.1, 1),  # Red color
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=60,
            font_style="H6",
            on_release=self.pick_student
        )
        
        # Stats Label
        self.stats_label = MDLabel(
            text="Total Students: 0",
            halign="center",
            font_style="Subtitle1",
            theme_text_color="Primary",
            size_hint_y=None,
            height=30
        )
        
        # Clear All Button
        clear_btn = MDRaisedButton(
            text="CLEAR ALL STUDENTS",
            md_bg_color=(0.5, 0.5, 0.5, 1),  # Gray color
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=45,
            on_release=self.clear_all_students
        )
        
        # Add widgets to content layout
        content_layout.add_widget(input_card)
        content_layout.add_widget(students_card)
        content_layout.add_widget(result_card)
        content_layout.add_widget(pick_btn)
        content_layout.add_widget(clear_btn)
        content_layout.add_widget(self.stats_label)
        
        # Add everything to main layout
        main_layout.add_widget(toolbar)
        main_layout.add_widget(content_layout)
        
        screen = MDScreen()
        screen.add_widget(main_layout)
        return screen
    
    def add_student(self, instance):
        name = self.input_name.text.strip()
        if name:
            if name not in self.students:
                self.students.append(name)
                self.input_name.text = ""  # Clear input
                
                # Update display
                self.update_display()
                
                # Show success message
                self.result_label.text = f"✓ Added: {name}"
                self.result_label.theme_text_color = "Primary"
            else:
                self.result_label.text = f"{name} already exists!"
                self.result_label.theme_text_color = "Error"
        else:
            self.result_label.text = "Please enter a name!"
            self.result_label.theme_text_color = "Error"
    
    def update_display(self):
        # Update student count display
        if self.students:
            if len(self.students) <= 5:
                self.students_label.text = ", ".join(self.students)
            else:
                self.students_label.text = f"{len(self.students)} students added"
            self.students_label.theme_text_color = "Primary"
        else:
            self.students_label.text = "No students added yet"
            self.students_label.theme_text_color = "Secondary"
        
        # Update stats
        self.stats_label.text = f"Total Students: {len(self.students)}"
    
    def pick_student(self, instance):
        if not self.students:
            self.result_label.text = "Student list is empty!"
            self.result_label.theme_text_color = "Error"
            return
        
        # Pick random student
        selected = random.choice(self.students)
        
        # Remove the selected student from the list
        self.students.remove(selected)
        
        # Update display
        self.update_display()
        
        # Update result display
        self.result_label.text = f"🎉 {selected} 🎉"
        self.result_label.theme_text_color = "Custom"
        self.result_label.text_color = (0, 0.6, 0, 1)  # Green color
        
        # Show congratulatory dialog
        self.show_congrats_dialog(selected)
    
    def clear_all_students(self, instance):
        if not self.students:
            self.result_label.text = "List is already empty!"
            self.result_label.theme_text_color = "Error"
            return
        
        # Show confirmation dialog
        self.show_clear_confirmation()
    
    def show_congrats_dialog(self, student_name):
        dialog = MDDialog(
            title="🎊 Selected! 🎊",
            text=f"{student_name} has been selected for recitation!",
            size_hint=[0.8, None],
            buttons=[
                MDFillRoundFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    md_bg_color=self.theme_cls.primary_color,
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_clear_confirmation(self):
        dialog = MDDialog(
            title="Clear All Students",
            text=f"Are you sure you want to remove all {len(self.students)} students?",
            size_hint=[0.8, None],
            buttons=[
                MDFillRoundFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    md_bg_color=(0.5, 0.5, 0.5, 1),
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFillRoundFlatButton(
                    text="CLEAR ALL",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    md_bg_color=(0.8, 0.1, 0.1, 1),
                    on_release=lambda x: self.confirm_clear_all(dialog)
                )
            ]
        )
        dialog.open()
    
    def confirm_clear_all(self, dialog):
        # Clear all students
        self.students.clear()
        
        # Update display
        self.update_display()
        
        # Update result label
        self.result_label.text = "All students cleared!"
        self.result_label.theme_text_color = "Error"
        
        dialog.dismiss()

if __name__ == '__main__':
    RecitationPicker().run()