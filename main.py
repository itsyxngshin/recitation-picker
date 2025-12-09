from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import Snackbar
from kivy.clock import Clock
from kivy.metrics import dp
import random

class StudentListItem(OneLineAvatarIconListItem):
    """Custom list item with access to update score text"""
    def __init__(self, name, score, delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.student_name = name # Store raw name separately
        self.text = f"{name} (Points: {score})"
        self.delete_callback = delete_callback

        # Left Icon (Account/Person)
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
        
        # CHANGED: Dictionary to store Name:Score pairs
        # Example: {'Carlo': 0, 'Maria': 2}
        self.students = {} 
        self.student_widgets = {} # To keep track of UI items for updating
        self.is_animating = False

        # --- Main Layout ---
        self.screen = MDScreen()
        main_layout = MDBoxLayout(orientation='vertical', spacing=0)

        # 1. Top Bar
        toolbar = MDTopAppBar(
            title="Smart Recitation Picker",
            elevation=2,
            pos_hint={"top": 1},
            md_bg_color=self.theme_cls.primary_color
        )
        toolbar.right_action_items = [["delete-sweep", lambda x: self.confirm_clear_all()]]

        # 2. Input Area
        input_layout = MDBoxLayout(
            orientation='horizontal', 
            spacing=10, 
            padding=20, 
            size_hint_y=None, 
            height=dp(80)
        )
        
        self.input_name = MDTextField(
            hint_text="Student Name",
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

        # 3. Student List Area
        list_label_layout = MDBoxLayout(size_hint_y=None, height=dp(30), padding=[20,0])
        self.count_label = MDLabel(text="Class List (0)", theme_text_color="Secondary", font_style="Caption")
        list_label_layout.add_widget(self.count_label)

        scroll = MDScrollView()
        self.list_container = MDList()
        scroll.add_widget(self.list_container)

        # 4. Result Area
        result_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),
            padding=20,
            spacing=10
        )
        
        self.result_label = MDLabel(
            text="Ready?",
            halign="center",
            font_style="H3",
            theme_text_color="Primary"
        )
        
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
        return self.screen

    # --- Logic ---

    def add_student(self, instance=None):
        name = self.input_name.text.strip()
        if name:
            if name not in self.students:
                # Initialize student with 0 points
                self.students[name] = 0
                
                # Add UI Item
                item = StudentListItem(name=name, score=0, delete_callback=self.remove_student)
                self.student_widgets[name] = item # Store reference
                self.list_container.add_widget(item)
                
                self.input_name.text = ""
                self.update_count()
            else:
                Snackbar(text=f"{name} is already in the list!", bg_color=(0.8, 0, 0, 1)).open()
        else:
            Snackbar(text="Please enter a name", bg_color=(0.5, 0.5, 0.5, 1)).open()

    def remove_student(self, list_item):
        name = list_item.student_name
        if name in self.students:
            del self.students[name]
            del self.student_widgets[name]
            self.list_container.remove_widget(list_item)
            self.update_count()
            Snackbar(text=f"Removed {name}").open()

    def update_count(self):
        self.count_label.text = f"Class List ({len(self.students)})"

    def start_roulette(self, instance):
        if not self.students:
            Snackbar(text="Add students first!", bg_color=(0.8, 0, 0, 1)).open()
            return
        
        if self.is_animating:
            return

        self.is_animating = True
        self.pick_btn.disabled = True
        self.result_label.theme_text_color = "Primary"
        
        self.cycle_count = 0
        Clock.schedule_interval(self.cycle_names, 0.1)

    def cycle_names(self, dt):
        # Visual effect: Just pick purely random names for the "flashing" part
        temp_names = list(self.students.keys())
        self.result_label.text = random.choice(temp_names)
        self.cycle_count += 1

        if self.cycle_count > 20:
            return False 
        
        if self.cycle_count == 20:
            Clock.schedule_once(self.finalize_pick, 0.1)

    def finalize_pick(self, dt):
        # --- THE WEIGHTED LOGIC ---
        names = list(self.students.keys())
        points = list(self.students.values())
        
        # Calculate weights: Higher points = Lower weight
        # Formula: 1 / (1 + points)
        weights = [1 / (1 + p) for p in points]
        
        # random.choices returns a list, so we take [0]
        selected_name = random.choices(names, weights=weights, k=1)[0]
        
        # --- UPDATE SCORES ---
        self.students[selected_name] += 1
        new_score = self.students[selected_name]
        
        # Update the UI List Item to show new score
        if selected_name in self.student_widgets:
            self.student_widgets[selected_name].update_score_display(new_score)

        # Update Result Label
        self.result_label.text = selected_name
        self.result_label.theme_text_color = "Custom"
        self.result_label.text_color = self.theme_cls.primary_color
        
        self.is_animating = False
        self.pick_btn.disabled = False
        
        self.show_winner_dialog(selected_name, new_score)

    def show_winner_dialog(self, name, score):
        dialog = MDDialog(
            title="🎉 Selected!",
            text=f"[b]{name}[/b] has been chosen!\nThey now have {score} points.",
            buttons=[
                MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()

    def confirm_clear_all(self):
        if not self.students:
            return
            
        dialog = MDDialog(
            title="Reset Class?",
            text="Clear all names and scores?",
            buttons=[
                MDRaisedButton(text="CANCEL", md_bg_color=(0.5,0.5,0.5,1), on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="CLEAR", md_bg_color=(1,0,0,1), on_release=lambda x: self.clear_data(dialog))
            ]
        )
        dialog.open()

    def clear_data(self, dialog):
        self.students.clear()
        self.student_widgets.clear()
        self.list_container.clear_widgets()
        self.update_count()
        self.result_label.text = "Ready?"
        dialog.dismiss()

# Required for MDList to work
from kivymd.uix.list import MDList

if __name__ == '__main__':
    RecitationPicker().run()