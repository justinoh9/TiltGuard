import time
import psutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

TARGETS = {
    "LeagueClient.exe",
    "RiotClientServices.exe",
}

LOG_FILE = "tiltguard_log.txt"


def log_event(event: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {event}\n")


def get_running_process_names():
    names = set()
    for proc in psutil.process_iter(["name"]):
        try:
            name = proc.info["name"]
            if name:
                names.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return names


def show_interruption_popup() -> str:
    """
    Shows a simple modal pop-up and returns either:
    - "delay"
    - "play"
    """
    result = {"choice": None}

    root = tk.Tk()
    root.title("TiltGuard")
    root.geometry("360x180")
    root.resizable(False, False)

    # Make it appear on top
    root.attributes("-topmost", True)

    label = tk.Label(
        root,
        text="League/Riot detected.\nWhat do you want to do?",
        font=("Segoe UI", 12),
        justify="center",
        pady=15,
    )
    label.pack()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    def choose_delay():
        result["choice"] = "delay"
        root.destroy()

    def choose_play():
        result["choice"] = "play"
        root.destroy()

    delay_btn = tk.Button(button_frame, text="Delay 15 minutes", width=16, command=choose_delay)
    delay_btn.grid(row=0, column=0, padx=10)

    play_btn = tk.Button(button_frame, text="Play anyway", width=16, command=choose_play)
    play_btn.grid(row=0, column=1, padx=10)

    # If they close the window, treat it as "play anyway"
    def on_close():
        result["choice"] = "play"
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()
    return result["choice"] or "play"


def main():
    print("TiltGuard running (with popup). Press Ctrl + C to stop.\n")
    log_event("TiltGuard started")

    detected_before = False
    delay_until = None  # datetime when delay period ends

    while True:
        running = get_running_process_names()
        detected_now = any(name in running for name in TARGETS)

        # If League just started:
        if detected_now and not detected_before:
            log_event("League/Riot detected (launch)")
            choice = show_interruption_popup()

            if choice == "delay":
                delay_until = datetime.now() + timedelta(minutes=15)
                log_event("User chose DELAY 15 minutes")
                print("Delay chosen: 15 minutes (not blocking yet).")
                messagebox.showinfo("TiltGuard", "Delay started (15 minutes).\nBlocking comes next step.")
            else:
                log_event("User chose PLAY anyway")
                print("Play anyway chosen.")

        # If delay is active, show remaining time in terminal (no blocking yet)
        if delay_until is not None:
            if datetime.now() >= delay_until:
                log_event("Delay finished")
                print("Delay finished.")
                delay_until = None

        detected_before = detected_now
        time.sleep(1)


if __name__ == "__main__":
    main()
