import os
import sys
import traceback
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def setup_error_logging():
    os.makedirs("logs/errors", exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H%M")
    return open(f"logs/errors/{now}.log", "w", encoding="utf-8")

def prompt_user_recovery(error_msg):
    print("\n[!] The bot encountered an error.")
    print(error_msg)
    print("Options:")
    print("1) Retry")
    print("2) Open log file")
    print("3) Exit")
    choice = input("Enter choice [1/2/3]: ").strip()
    return choice

error_log_file = setup_error_logging()

try:
    import subprocess

    print("=== ETH Scalp Backtest Launcher ===\n")
    print("1) Optimize Strategy Parameters")
    print("2) Run Backtest with Best Strategy")
    print("3) Exit")
    option = input("Enter option [1-3]: ").strip()

    if option == "1":
        subprocess.run(["python", "scripts/optimize.py"], check=True)
    elif option == "2":
        subprocess.run(["python", "launcher/run_best_strategy.py"], check=True)
    else:
        print("Exiting...")

except Exception as e:
    error_details = traceback.format_exc()
    print(f"\n[!] ERROR OCCURRED:\n{error_details}")
    error_log_file.write(f"--- ERROR: {datetime.now()} ---\n")
    error_log_file.write(error_details)
    error_log_file.write("\n--- HINTS ---\n")

    if "No such file or directory" in error_details:
        error_log_file.write("Hint: Make sure paths to scripts/configs/data are correct.\n")
    elif "CalledProcessError" in error_details:
        error_log_file.write("Hint: One of the subprocess commands failed.\n")

    error_log_file.close()

    choice = prompt_user_recovery(error_details)

    if choice == "1":
        os.execv(sys.executable, ['python'] + sys.argv)
    elif choice == "2":
        print(f"Opening log file: {error_log_file.name}")
        os.system(f'start {error_log_file.name}')
    else:
        raise SystemExit("Bot terminated by user.")
