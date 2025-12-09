import json
import os
import random
from datetime import datetime
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, IconLeftWidget, MDList
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu
# --- NEW IMPORT: FILE MANAGER ---
from kivymd.uix.filemanager import MDFileManager

# --- PATH CONFIGURATION ---
def get_storage_path():
    if platform == 'android':
        from android.storage import app_storage_path
        return app_storage_path()
    return os.path.dirname(os.path.abspath(__file__))

STORAGE_PATH = get_storage_path()
DATA_FILE = os.path.join(STORAGE_PATH, "class_data.json")
LOG_FILE = os.path.join(STORAGE_PATH, "audit_log.txt")
# We no longer need IMPORT_FILE constant since we pick it dynamically

class StudentListItem(OneLineAvatarIconListItem):
    """Custom list item with access to update score text"""
    def __init__(self, name, score, delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.student_name = name 
        self.text = f"{name} (Points: {score})"
        self.delete_callback = delete_callback

        self.add_widget(IconLeftWidget(icon="account"))
        delete_icon = IconRightWidget(icon="trash-can-outline", theme_text_color="Error")
        delete_icon.bind(on_release=lambda x: self.delete_callback(self))
        self.add_widget(delete_icon)

    def update_score_display(self, new_score):
        self.text = f"{self.student_name} (Points: {new_score})"

class RecitationPicker(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        
        self.students = {} 
        self.student_widgets = {} 
        self.is_animating = False
        self.grading_dialog = None
        self.menu = None

        # --- SETUP FILE MANAGER ---
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,
            ext=['.txt'] # Only allow text files
        )

        # --- Main Layout ---
        self.screen = MDScreen()
        main_layout = MDBoxLayout(orientation='vertical', spacing=0)

        # 1. OPTIMIZED TOP BAR
        toolbar = MDTopAppBar(
            title="Classroom Picker",
            elevation=2,
            pos_hint={"top": 1},
            md_bg_color=self.theme_cls.primary_color
        )
        toolbar.right_action_items = [
            ["dots-vertical", lambda x: self.open_menu(x)]
        ]

        # 2. OPTIMIZED INPUT AREA
        input_layout = MDBoxLayout(orientation='horizontal', spacing=10, padding=12, size_hint_y=None, height=dp(70))
        self.input_name = MDTextField(
            hint_text="Add Student Name",
            mode="fill",
            size_hint_x=0.7,
            on_text_validate=self.add_student_ui
        )
        add_btn = MDIconButton(
            icon="plus-box",
            icon_size="40sp",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=self.add_student_ui
        )
        input_layout.add_widget(self.input_name)
        input_layout.add_widget(add_btn)

        # 3. List Area
        list_label_layout = MDBoxLayout(size_hint_y=None, height=dp(30), padding=[12,0])
        self.count_label = MDLabel(text="Class List (0)", theme_text_color="Secondary", font_style="Caption")
        list_label_layout.add_widget(self.count_label)

        scroll = MDScrollView()
        self.list_container = MDList()
        scroll.add_widget(self.list_container)

        # 4. Result Area
        result_layout = MDBoxLayout(orientation='vertical', size_hint_y=None, height=dp(160), padding=12, spacing=10)
        self.result_label = MDLabel(text="Ready?", halign="center", font_style="H4", theme_text_color="Primary")
        
        self.pick_btn = MDFillRoundFlatIconButton(
            text="PICK STUDENT",
            icon="dice-multiple",
            font_size="18sp",
            size_hint_x=1,
            size_hint_y=None,
            height=dp(55),
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
        self.log_action("App Started")
        
        return self.screen

    # --- FILE MANAGER LOGIC (NEW) ---

    def open_file_manager(self):
        """Opens the file manager starting at the storage path"""
        # On Android, we might want to start at /storage/emulated/0 to see user files
        path = os.path.expanduser("~") if platform != "android" else "/storage/emulated/0"
        self.file_manager.show(path)

    def select_path(self, path):
        """Called when user selects a file"""
        self.exit_manager() # Close the manager
        toast(f"Selected: {os.path.basename(path)}")
        self.import_from_file(path) # Pass the path to import logic

    def exit_manager(self, *args):
        """Closes the file manager"""
        self.file_manager.close()

    # --- MENU LOGIC ---

    def open_menu(self, button):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Import Class",
                "on_release": lambda x="import": self.menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Export Scores",
                "on_release": lambda x="export": self.menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Reset Data",
                "on_release": lambda x="reset": self.menu_callback(x),
            }
        ]
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def menu_callback(self, action):
        if self.menu:
            self.menu.dismiss()
        
        if action == "import":
            self.open_file_manager() # Trigger the file picker instead of direct import
        elif action == "export":
            self.export_score_sheet()
        elif action == "reset":
            self.confirm_clear_all()

    # --- LOGGING & FILE IO ---

    def log_action(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}\n"
        try:
            with open(LOG_FILE, "a", encoding='utf-8') as f:
                f.write(entry)
        except Exception as e:
            print(f"Logging failed: {e}")

    def export_score_sheet(self):
        if not self.students:
            toast("Nothing to export!")
            return

        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"ScoreSheet_{date_str}.txt"
        filepath = os.path.join(STORAGE_PATH, filename)

        try:
            with open(filepath, "w", encoding='utf-8') as f:
                f.write(f"--- CLASS SCORE SHEET ({date_str}) ---\n\n")
                for name, score in self.students.items():
                    f.write(f"{name}: {score}\n")
            
            toast(f"Saved: {filename}")
            self.log_action(f"Exported scores to {filename}")
        except Exception as e:
            toast("Export failed!")
            self.log_action(f"Export failed: {e}")

    def import_from_file(self, filepath):
        """Now accepts a filepath argument"""
        if not os.path.exists(filepath):
            toast("File not found!")
            return

        try:
            count = 0
            with open(filepath, "r", encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    name = line.strip()
                    if name and name not in self.students:
                        self.add_student_data(name, 0)
                        count += 1
            
            if count > 0:
                toast(f"Imported {count} students!")
                self.log_action(f"Imported {count} names from {os.path.basename(filepath)}")
                self.save_data()
            else:
                toast("No new names found.")
                
        except Exception as e:
            toast("Import Error")
            self.log_action(f"Import Error: {e}")

    # --- DATA MANAGEMENT ---

    def save_data(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.students, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, score in data.items():
                        self.add_student_data(name, score, save=False)
                    self.update_count()
            except Exception as e:
                print(f"Error loading data: {e}")

    # --- CORE LOGIC ---

    def add_student_ui(self, instance=None):
        name = self.input_name.text.strip()
        if name:
            if name not in self.students:
                self.add_student_data(name, 0)
                self.input_name.text = ""
                self.log_action(f"Added student: {name}")
                self.save_data()
            else:
                toast(f"{name} is already in the list!")
        else:
            toast("Please enter a name")

    def add_student_data(self, name, score, save=True):
        self.students[name] = score
        item = StudentListItem(name=name, score=score, delete_callback=self.remove_student)
        self.student_widgets[name] = item
        self.list_container.add_widget(item)
        self.update_count()
        if save: self.save_data()

    def remove_student(self, list_item):
        name = list_item.student_name
        if name in self.students:
            del self.students[name]
            del self.student_widgets[name]
            self.list_container.remove_widget(list_item)
            self.update_count()
            self.save_data()
            self.log_action(f"Removed student: {name}")
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
        self.log_action("Started Roulette")
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
        
        self.log_action(f"Picked: {selected_name}")
        self.show_grading_dialog(selected_name)
        
        self.is_animating = False
        self.pick_btn.disabled = False

    def show_grading_dialog(self, name):
        self.grading_dialog = MDDialog(
            title=f"Evaluate {name}",
            text="Correct Answer?",
            buttons=[
                MDRaisedButton(
                    text="PASS",
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
            self.log_action(f"Graded {name}: Correct (+1)")
        else:
            toast(f"No points added for {name}.")
            self.log_action(f"Graded {name}: Incorrect")
        
        self.save_data()
        Clock.schedule_once(self.dismiss_dialog)

    def dismiss_dialog(self, dt):
        if self.grading_dialog:
            self.grading_dialog.dismiss()
            self.grading_dialog = None

    def confirm_clear_all(self):
        if not self.students: return
        MDDialog(
            title="Reset Class?",
            text="Clear all names and scores?",
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
        self.log_action("Cleared all class data")
        dialog.dismiss()

if __name__ == '__main__':
    RecitationPicker().run()