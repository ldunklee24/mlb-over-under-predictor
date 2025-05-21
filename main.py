import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu():
    clear()
    print("MLB Over/Under Prediction System")
    print("=" * 40)
    print("1. Build historical dataset (games.csv)")
    print("2. Ingest live stats into SQLite (mlb_predictions.db)")
    print("3. Train prediction model (model.pkl)")
    print("4. Predict today's games (using latest stats + model)")
    print("5. Exit")
    print("=" * 40)
    return input("Choose an option: ")

def run_script(name):
    print(f"\n▶️ Running {name}...\n")
    os.system(f"python {name}")
    input("\n⏎ Press Enter to return to menu.")

if __name__ == "__main__":
    while True:
        choice = menu()
        if choice == "1":
            run_script("build_dataset.py")
        elif choice == "2":
            run_script("ingest_to_sqlite.py")
        elif choice == "3":
            run_script("train_model.py")
        elif choice == "4":
            run_script("predict_today.py")
        elif choice == "5":
            print("Exiting.")
            break
        else:
            print("Invalid option.")
            input("Press Enter to try again.")
