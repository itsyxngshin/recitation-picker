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
    """Custom list item to handle individual student deletion"""
    def __init__(self, name, delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.text = name
        self.delete_callback = delete_callback

        # Left Icon (Person)
        self.add_widget(IconLeftWidget(icon="account"))

        # Right Icon (Delete/Trash)
        delete_icon = IconRightWidget(icon="trash-can-outline", theme_text_color="Error")
        delete_icon.bind(on_release=lambda x: self.delete_callback(self))
        self.add_widget(delete_icon)

class RecitationPicker(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.students = []
        self.is_animating = False

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

        # 2. Input Area (Compact)
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
            on_text_validate=self.add_student # Allow "Enter" key
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

        # 3. Student List Area (Scrollable)
        list_label_layout = MDBoxLayout(size_hint_y=None, height=dp(30), padding=[20,0])
        self.count_label = MDLabel(text="Class List (0)", theme_text_color="Secondary", font_style="Caption")
        list_label_layout.add_widget(self.count_label)

        scroll = MDScrollView()
        self.list_container = MDList()
        scroll.add_widget(self.list_container)

        # 4. Result Area (The "Stage")
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
        
        # Pick Button
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

        # Assemble
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
                self.students.append(name)
                
                # Add visually to list
                item = StudentListItem(name=name, delete_callback=self.remove_student)
                self.list_container.add_widget(item)
                
                self.input_name.text = ""
                self.update_count()
            else:
                Snackbar(text=f"{name} is already in the list!", bg_color=(0.8, 0, 0, 1)).open()
        else:
            Snackbar(text="Please enter a name", bg_color=(0.5, 0.5, 0.5, 1)).open()

    def remove_student(self, list_item):
        """Removes a single student from data and UI"""
        name = list_item.text
        if name in self.students:
            self.students.remove(name)
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
        self.pick_btn.disabled = True # Prevent double clicking
        self.result_label.theme_text_color = "Primary"
        
        # Start the cycling animation
        self.cycle_count = 0
        Clock.schedule_interval(self.cycle_names, 0.1)

    def cycle_names(self, dt):
        """Rapidly flashes names to create a roulette effect"""
        self.result_label.text = random.choice(self.students)
        self.cycle_count += 1

        # Stop after 20 flashes (approx 2 seconds)
        if self.cycle_count > 20:
            return False # Stops the interval
        
        # Trigger the final pick slightly after the loop ends
        if self.cycle_count == 20:
            Clock.schedule_once(self.finalize_pick, 0.1)

    def finalize_pick(self, dt):
        """The actual selection logic"""
        selected = random.choice(self.students)
        
        # Visuals for the winner
        self.result_label.text = selected
        self.result_label.theme_text_color = "Custom"
        self.result_label.text_color = self.theme_cls.primary_color
        
        # Remove from logic (optional: depends if you want them pickable again)
        # self.students.remove(selected) 
        # self.update_list_ui() # You would need to refresh the list if you remove them
        
        self.is_animating = False
        self.pick_btn.disabled = False
        
        # Optional: Show a dialog for the winner
        self.show_winner_dialog(selected)

    def show_winner_dialog(self, name):
        dialog = MDDialog(
            title="🎉 We have a speaker!",
            text=f"Please stand up, [b]{name}[/b]!",
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
            text="This will remove all student names.",
            buttons=[
                MDRaisedButton(text="CANCEL", md_bg_color=(0.5,0.5,0.5,1), on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="CLEAR", md_bg_color=(1,0,0,1), on_release=lambda x: self.clear_data(dialog))
            ]
        )
        dialog.open()

    def clear_data(self, dialog):
        self.students.clear()
        self.list_container.clear_widgets()
        self.update_count()
        self.result_label.text = "Ready?"
        self.result_label.theme_text_color = "Primary"
        dialog.dismiss()

if __name__ == '__main__':
    RecitationPicker().run()