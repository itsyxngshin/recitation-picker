import json
import os
import random
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
# We use the standard buttons that work on ALL versions
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, IconLeftWidget, MDList
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
# We use 'toast' instead of Snackbar because it is much more stable
from kivymd.toast import toast

class StudentListItem(OneLineAvatarIconListItem):
    """Custom list item with access to update score text"""
    def __init__(self, name, score, delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.student_name = name 
        self.text = f"{name} (Points: {score})"
        self.delete_callback = delete_callback

        # Left Icon (Account)
        self.add_widget(IconLeftWidget(icon="account"))

        # Right Icon (Delete)
        delete_icon = IconRightWidget(icon="trash-can-outline", theme_text_color="Error")
        delete_icon.bind(on_release=lambda x: self.delete_callback(self))
        self.add_widget(delete_icon)

    def update_score_display(self, new_score):
        self.text = f"{self.student_name} (Points: {new_score})"

class RecitationPicker(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        
        # --- File Path Logic (Android vs PC) ---
        if platform == "android":
            self.data_file = os.path.join(self.user_data_dir, "class_data.json")
        else:
            self.data_file = "class_data.json"

        self.students = {} 
        self.student_widgets = {} 
        self.is_animating = False
        self.grading_dialog = None

        # --- Main Layout ---
        self.screen = MDScreen()
        main_layout = MDBoxLayout(orientation='vertical', spacing=0)

        # 1. Top Bar
        toolbar = MDTopAppBar(
            title="Classroom Picker",
            elevation=2,
            pos_hint={"top": 1},
            md_bg_color=self.theme_cls.primary_color
        )
        toolbar.right_action_items = [["delete-sweep", lambda x: self.confirm_clear_all()]]

        # 2. Input Area
        input_layout = MDBoxLayout(orientation='horizontal', spacing=10, padding=20, size_hint_y=None, height=dp(80))
        self.input_name = MDTextField(
            hint_text="Add Student Name",
            mode="fill",
            size_hint_x=0.7,
            on_text_validate=self.add_student
        )
        add_btn = MDIconButton(
            icon="plus-box",
            icon_size="48sp",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=self.add_student
        )
        input_layout.add_widget(self.input_name)
        input_layout.add_widget(add_btn)

        # 3. List Area
        list_label_layout = MDBoxLayout(size_hint_y=None, height=dp(30), padding=[20,0])
        self.count_label = MDLabel(text="Class List (0)", theme_text_color="Secondary", font_style="Caption")
        list_label_layout.add_widget(self.count_label)

        scroll = MDScrollView()
        self.list_container = MDList()
        scroll.add_widget(self.list_container)

        # 4. Result Area
        result_layout = MDBoxLayout(orientation='vertical', size_hint_y=None, height=dp(180), padding=20, spacing=10)
        self.result_label = MDLabel(text="Ready?", halign="center", font_style="H3", theme_text_color="Primary")
        
        self.pick_btn = MDFillRoundFlatIconButton(
            text="PICK STUDENT",
            icon="dice-multiple",
            font_size="20sp",
            size_hint_x=1,
            size_hint_y=None,
            height=dp(60),
            on_release=self.start_roulette
        )
        
        result_layout.add_widget(self.result_label)
        result_layout.add_widget(self.pick_btn)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(input_layout)
        main_layout.add_widget(list_label_layout)
        main_layout.add_widget(scroll)
        main_layout.add_widget(result_layout)
        
        self.screen.add_widget(main_layout)
        
        self.load_data()
        
        return self.screen

    # --- DATA PERSISTENCE ---

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.students, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for name, score in data.items():
                        self.students[name] = score
                        item = StudentListItem(name=name, score=score, delete_callback=self.remove_student)
                        self.student_widgets[name] = item
                        self.list_container.add_widget(item)
                    self.update_count()
            except Exception as e:
                print(f"Error loading data: {e}")

    # --- APP LOGIC ---

    def add_student(self, instance=None):
        name = self.input_name.text.strip()
        if name:
            if name not in self.students:
                self.students[name] = 0
                item = StudentListItem(name=name, score=0, delete_callback=self.remove_student)
                self.student_widgets[name] = item
                self.list_container.add_widget(item)
                self.input_name.text = ""
                self.update_count()
                self.save_data()
            else:
                toast(f"{name} is already in the list!")
        else:
            toast("Please enter a name")

    def remove_student(self, list_item):
        name = list_item.student_name
        if name in self.students:
            del self.students[name]
            del self.student_widgets[name]
            self.list_container.remove_widget(list_item)
            self.update_count()
            self.save_data()
            toast(f"Removed {name}")

    def update_count(self):
        self.count_label.text = f"Class List ({len(self.students)})"

    # --- ROULETTE & GRADING ---

    def start_roulette(self, instance):
        if not self.students:
            toast("Add students first!")
            return
        if self.is_animating: return

        self.is_animating = True
        self.pick_btn.disabled = True
        self.cycle_count = 0
        Clock.schedule_interval(self.cycle_names, 0.1)

    def cycle_names(self, dt):
        self.result_label.text = random.choice(list(self.students.keys()))
        self.cycle_count += 1
        if self.cycle_count > 20: return False
        if self.cycle_count == 20: Clock.schedule_once(self.finalize_pick, 0.1)

    def finalize_pick(self, dt):
        names = list(self.students.keys())
        points = list(self.students.values())
        weights = [1 / (1 + p) for p in points]
        
        selected_name = random.choices(names, weights=weights, k=1)[0]
        
        self.result_label.text = selected_name
        self.result_label.theme_text_color = "Custom"
        self.result_label.text_color = self.theme_cls.primary_color
        
        self.show_grading_dialog(selected_name)
        
        self.is_animating = False
        self.pick_btn.disabled = False

    def show_grading_dialog(self, name):
        # We use a standard MDDialog that works on most versions
        self.grading_dialog = MDDialog(
            title=f"Evaluate {name}",
            text="Did the student answer correctly?",
            buttons=[
                MDRaisedButton(
                    text="INCORRECT / PASS",
                    md_bg_color=(0.8, 0.4, 0.4, 1),
                    on_release=lambda x: self.grade_student(name, correct=False)
                ),
                MDRaisedButton(
                    text="CORRECT (+1)",
                    md_bg_color=(0.2, 0.6, 0.2, 1),
                    on_release=lambda x: self.grade_student(name, correct=True)
                ),
            ]
        )
        self.grading_dialog.open()

    def grade_student(self, name, correct):
        if correct:
            self.students[name] += 1
            if name in self.student_widgets:
                self.student_widgets[name].update_score_display(self.students[name])
            toast(f"Point added to {name}!")
        else:
            toast(f"No points added for {name}.")
        
        self.save_data()
        
        # Schedule the dismiss to prevent button crash
        Clock.schedule_once(self.dismiss_dialog)

    def dismiss_dialog(self, dt):
        if self.grading_dialog:
            self.grading_dialog.dismiss()
            self.grading_dialog = None

    def confirm_clear_all(self):
        if not self.students: return
        MDDialog(
            title="Reset Class?",
            text="Clear all names and scores permanently?",
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: x.parent.parent.parent.parent.dismiss()),
                MDRaisedButton(text="CLEAR", md_bg_color=(1,0,0,1), on_release=lambda x: self.clear_data(x.parent.parent.parent.parent))
            ]
        ).open()

    def clear_data(self, dialog):
        self.students.clear()
        self.student_widgets.clear()
        self.list_container.clear_widgets()
        self.update_count()
        self.result_label.text = "Ready?"
        self.save_data()
        dialog.dismiss()

if __name__ == '__main__':
    RecitationPicker().run() 