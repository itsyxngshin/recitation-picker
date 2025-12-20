import os
import time
from datetime import datetime
import random 

STUDENT_DATA = "student_data.txt"
APP_LOG = "log.txt"

def load_data():
    # Loads data from file into a dictionary once.
    data = {}
    if os.path.exists(STUDENT_DATA):
        try:
            with open(STUDENT_DATA, 'r', encoding='utf-8') as f:
                for line in f:
                    if "," in line:
                        name, score = line.strip().rsplit(",", 1)
                        data[name] = int(score)
        except Exception as e:
            print(f"Error loading file: {e}")
    return data

def save_data(students):
    # Saves the dictionary back to the text file.
    try:
        with open(STUDENT_DATA, 'w', encoding='utf-8') as f:
            for name, score in students.items():
                f.write(f"{name},{score}\n")
    except Exception as e:
        print(f"Error saving data: {e}")

def log_action(message):
    # Record processes that occured within the system
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(APP_LOG, "a", encoding='utf-8') as f:
        f.write(entry)

# --- FEATURES ---

def view_scores(students):
    os.system('clear') # Use 'cls' if on Windows
    print(f"--- CLASS LIST ({len(students)}) ---")
    print(f"{'NAME':<20} | {'SCORE':<5}")
    print("-" * 30)
    for name, score in sorted(students.items()):
        print(f"{name:<20} | {score:<5}")
    input("\nPress Enter to return...")

def pick_student(students):
    os.system('clear')
    if not students:
        print("Error: Roster is empty.")
        input("Press Enter to return...")
        return

    print("=== PICKING STUDENT ===")
    print("Rolling...")
    
    # Animation effect
    for _ in range(10):
        print(f"\r> {random.choice(list(students.keys()))}   ", end="", flush=True)
        time.sleep(0.1)
    
    # Weighted Random Logic (lower score = higher chance)
    names = list(students.keys())
    scores = list(students.values())
    weights = [1 / (1 + s) for s in scores]
    winner = random.choices(names, weights=weights, k=1)[0]
    
    print(f"\r>> WINNER: {winner.upper()} <<")
    log_action(f"Picked: {winner}")
    
    print("\n[1] Correct (+1 Point)")
    print("[2] Incorrect/Pass (No Change)")
    choice = input("Enter Grade: ")
    
    if choice == '1':
        students[winner] += 1
        save_data(students) # Save immediately!
        print("Score updated!")
        log_action(f"Graded {winner}: Correct")
    else:
        print("No points awarded.")
        log_action(f"Graded {winner}: Pass")
    
    input("\nPress Enter to return...")

def add_student(students):
    os.system('clear')
    print("=== Add Student to the Roster ===")
    student_name = input("Enter student name: ").strip()
    if student_name:
        if student_name in students:
            print(f"Error: {student_name} is already in the roster.")
        else:
            students[student_name] = 0
            save_data(students) # Save immediately!
            log_action(f"Added student: {student_name}")
            print(f"Success: {student_name} has been added.")
    input("\nPress Enter to return...")

def import_list(students):
    os.system('clear')
    print("=== Import Student List ===")
    file_path = input("Enter filename (e.g. import.txt): ").strip()
    
    if not os.path.exists(file_path):
        print("Error: File does not exist.")
        input("\nPress Enter to return...")
        return
    
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "," in line:
                    name, score = line.strip().rsplit(",", 1)
                    if name not in students:
                        students[name] = int(score)
                        count += 1
                elif line.strip(): # Handle simple list of names
                    name = line.strip()
                    if name not in students:
                        students[name] = 0
                        count += 1
        
        if count > 0:
            save_data(students) # Save immediately!
            print(f"\nSuccess! Added {count} new students.")
            log_action(f"Imported {count} students from {file_path}")
        else:
            print("\nNo new students added.")
    except Exception as e:
        print(f"Error reading file: {e}")
    input("\nPress Enter to return...")

def export_score_sheet(students):
    filename = f" ScoreSheet_{datetime.now().strftime('%Y%m%d')}.txt "
    with open(filename, "w") as f:
        f.write("--- CLASS SCORES ---\n")
        for k, v in students.items():
            f.write(f"{k}: {v}\n")
    print(f" Exported to {filename} ")
    log_action(f" Exported data to {filename} ")
    input("Press Enter...")

def clear_students(students): 
    os.system('clear')
    print("=== WARNING ===")
    print("This will permanently delete ALL student names and scores.")
    opt = input("Type 'DELETE' to confirm: ")
    
    if opt == 'DELETE':
        students.clear()
        save_data(students) # Save immediately!
        log_action("User cleared all student data")
        print("\nSuccess: All student data has been cleared.")
    else:
        print("\nOperation cancelled.")
    input("\nPress Enter to return...")

# --- MAIN MENU ---

def main_menu():
    # Load data once at the start
    student_data = load_data()
    
    while True:
        os.system('clear')
        print("======================================")
        print(" Welcome to Recite - Classroom Picker ")
        print("======================================\n")
        print("-- [1] View Class Scores")
        print("-- [2] Pick a Student")
        print("-- [3] Add a Student")
        print("-- [4] Import Student List")
        print("-- [5] Export Score Sheet")
        print("-- [6] Clear Student List")
        print("-- [7] Exit")
        
        opt = input("\nSelect an option: ")

        # Pass 'student_data' to every function call
        if opt == '1':
            view_scores(student_data)
        elif opt == '2':
            pick_student(student_data)
        elif opt == '3':
            add_student(student_data)
        elif opt == '4':
            import_list(student_data)
        elif opt == '5':
            export_score_sheet(student_data)
        elif opt == '6':
            clear_students(student_data)
        elif opt == '7':
            print("Exiting...")
            break
        else:
            print("Invalid option.")
            time.sleep(2)

if __name__ == "__main__":
    main_menu()