import json
import os
import random
import time
from datetime import datetime
def reset_class(data):
    os.system('clear')
    print("!!! DANGER ZONE !!!")
    print("This will permanently delete ALL student names and scores.")
    confirm = input("Are you sure you want to reset the class? (Type 'YES' to confirm): ")
    
    if confirm == 'YES':
        # 1. Clear the dictionary in memory
        data.clear()
        
        # 2. Clear the file on the disk
        # Opening in 'w' mode without writing anything wipes the file
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            pass 
            
        log_action("User reset/wiped all class data")
        print("\nSuccess: Class data has been wiped.")
    else:
        print("\nOperation cancelled. Data is safe.")
        
    input("\nPress Enter to return...")
    
# --- CONFIGURATION ---
DATA_FILE = "class_data.txt"
LOG_FILE = "audit_log.txt"

def import_from_file(data):
    os.system('clear')
    print("--- IMPORT STUDENTS ---")
    filename = input("Enter filename to import (e.g., import.txt): ").strip()
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        input("Press Enter to return...")
        return

    count = 0
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue # Skip empty lines
                
                # Handle "Name,Score" or just "Name"
                if "," in line:
                    name, score_str = line.rsplit(",", 1)
                    score = int(score_str)
                else:
                    name = line
                    score = 0
                
                # Only add if not already there
                if name not in data:
                    data[name] = score
                    count += 1
                    print(f"Imported: {name}")
                else:
                    print(f"Skipped (Duplicate): {name}")
        
        if count > 0:
            save_data(data)
            log_action(f"Imported {count} students from {filename}")
            print(f"\nSuccess! Added {count} new students.")
        else:
            print("\nNo new students added.")
            
    except Exception as e:
        print(f"Error reading file: {e}")

    input("\nPress Enter to return...")
    
# --- DATA MANAGEMENT ---
def load_data():
    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    # Expecting format: "Name,Score"
                    if "," in line:
                        name, score = line.strip().rsplit(",", 1)
                        data[name] = int(score)
        except Exception as e:
            print(f"Error loading file: {e}")
            return {}
    return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        for name, score in data.items():
            # Saving format: "Name,Score"
            f.write(f"{name},{score}\n")

def log_action(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(entry)

# --- CORE FEATURES ---
def add_student(data):
    os.system('clear') # 'clear' for Linux/Replit
    print("--- ADD STUDENT ---")
    name = input("Enter student name: ").strip()
    if name:
        if name in data:
            print(f"Error: {name} already exists.")
        else:
            data[name] = 0
            save_data(data)
            log_action(f"Added student: {name}")
            print(f"Success: {name} added.")
    input("\nPress Enter to return...")

def view_students(data):
    os.system('clear')
    print(f"--- CLASS LIST ({len(data)}) ---")
    print(f"{'NAME':<20} | {'SCORE':<5}")
    print("-" * 30)
    for name, score in sorted(data.items()):
        print(f"{name:<20} | {score:<5}")
    input("\nPress Enter to return...")

def pick_student(data):
    os.system('clear')
    if not data:
        print("Error: Class list is empty.")
        input("Press Enter to return...")
        return

    print("--- PICKING STUDENT ---")
    print("Rolling...")
    # Simulating animation
    for _ in range(10):
        print(f"\r> {random.choice(list(data.keys()))}   ", end="", flush=True)
        time.sleep(0.1)
    
    # Weighted Random Logic
    names = list(data.keys())
    points = list(data.values())
    weights = [1 / (1 + p) for p in points]
    winner = random.choices(names, weights=weights, k=1)[0]
    
    print(f"\r>> WINNER: {winner.upper()} <<")
    log_action(f"Picked: {winner}")
    
    print("\n[1] Correct (+1 Point)")
    print("[2] Incorrect/Pass (No Change)")
    choice = input("Enter Grade: ")
    
    if choice == '1':
        data[winner] += 1
        save_data(data)
        log_action(f"Graded {winner}: Correct")
        print("Score updated!")
    else:
        print("No points awarded.")
        log_action(f"Graded {winner}: Pass")
    
    input("\nPress Enter to return...")

def export_data(data):
    filename = f"ScoreSheet_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(filename, "w") as f:
        f.write("--- CLASS SCORES ---\n")
        for k, v in data.items():
            f.write(f"{k}: {v}\n")
    print(f"Exported to {filename}")
    log_action(f"Exported data to {filename}")
    input("Press Enter...")

# --- MAIN MENU ---
def main():
    while True:
        data = load_data()
        os.system('clear') 
        print("==============================")
        print(" SYSTEM ADMIN CLASS PICKER V1 ")
        print("==============================")
        print("1. Pick Student (Roulette)")
        print("2. Add Student")
        print("3. View Class List")
        print("4. Export Log")
        print("5. Exit")
        
        choice = input("\nSelect Option [1-5]: ")
        
        if choice == '1': pick_student(data)
        elif choice == '2': add_student(data)
        elif choice == '3': view_students(data)
        elif choice == '4': export_data(data)
        elif choice == '5': 
            print("Exiting...")
            break

if __name__ == "__main__":
    main()