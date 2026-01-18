import time
import psutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

# Processes we detect to know League/Riot is trying to run
DETECT_TARGETS = {
    "RiotClientServices.exe",
    "LeagueClient.exe",
    "LeagueClientUx.exe",
    "LeagueClientUxRender.exe",
}

# Processes we actually block during delay
BLOCK_TARGETS = {
    "LeagueClient.exe",
    "LeagueClientUx.exe",
}

LOG_FILE = "tiltguard_log.txt"


def log_event(event: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {event}\n")


def get_processes_by_name(names_set: set[str]) -> list[psutil.Process]:
    """Return list of processes whose name matches one of names_set."""
    matches = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = proc.info["name"]
            if name and name in names_set:
                matches.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return matches


def show_interruption_popup() -> str:
    """
    Shows a simple modal pop-up and returns either:
    - "delay"
    - "play"
    """
    result = {"choice": None}

    root = tk.Tk()
    root.title("TiltGuard")
    root.geometry("380x190")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    label = tk.Label(
        root,
        text="League/Riot detected.\nWhat do you want to do?",
        font=("Segoe UI", 12),
        justify="center",
        pady=18,
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

    tk.Button(button_frame, text="Delay 15 minutes", width=16, command=choose_delay).grid(
        row=0, column=0, padx=10
    )
    tk.Button(button_frame, text="Play anyway", width=16, command=choose_play).grid(
        row=0, column=1, padx=10
    )

    def on_close():
        result["choice"] = "play"
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()
    return result["choice"] or "play"


def show_delay_active_popup(minutes_left: int) -> None:
    # Create a hidden root so messagebox works cleanly
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo(
        "TiltGuard",
        f"Delay is active.\nTry again in ~{minutes_left} minute(s)."
    )
    root.destroy()


def kill_process_tree(proc: psutil.Process) -> int:
    """Kill a process and its children. Returns count killed."""
    killed = 0
    try:
        for c in proc.children(recursive=True):
            try:
                c.kill()
                killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        try:
            proc.kill()
            killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    return killed


def terminate_block_targets(debug_print: bool = False) -> int:
    """Kill any running BLOCK_TARGETS. Returns total killed count."""
    killed_total = 0
    procs = get_processes_by_name(BLOCK_TARGETS)

    if debug_print:
        if procs:
            print("Blocking:", [p.name() for p in procs])
        else:
            print("Blocking: (no matching processes found)")

    for p in procs:
        killed_total += kill_process_tree(p)

    if killed_total > 0:
        print(f"Blocked launch (killed {killed_total} process(es))")
        log_event(f"Blocked launch (killed {killed_total})")

    return killed_total


def main():
    print("TiltGuard running (Delay enforced). Press Ctrl + C to stop.\n")
    log_event("TiltGuard started")

    detected_before = False
    delay_until: datetime | None = None
    last_block_popup_time: float = 0.0  # to avoid spamming popups

    try:
        while True:
            detected_now = len(get_processes_by_name(DETECT_TARGETS)) > 0

            # Transition: not detected -> detected
            if detected_now and not detected_before:
                log_event("League/Riot detected (launch)")

                # If delay is active, enforce immediately
                if delay_until is not None and datetime.now() < delay_until:
                    killed = terminate_block_targets(debug_print=True)

                    minutes_left = max(
                        1,
                        int((delay_until - datetime.now()).total_seconds() // 60)
                    )
                    log_event(f"Blocked launch during delay (killed={killed})")

                    # Throttle popup to at most once every 10 seconds
                    now = time.time()
                    if now - last_block_popup_time > 10:
                        show_delay_active_popup(minutes_left)
                        last_block_popup_time = now

                else:
                    # No active delay: ask the user
                    choice = show_interruption_popup()
                    if choice == "delay":
                        delay_until = datetime.now() + timedelta(minutes=15)
                        log_event("User chose DELAY 15 minutes")
                        print("Delay chosen: 15 minutes. League will be closed during this period.")
                    else:
                        log_event("User chose PLAY anyway")
                        print("Play anyway chosen.")

            # Background enforcement while delay is active
            if delay_until is not None:
                if datetime.now() >= delay_until:
                    log_event("Delay finished")
                    print("Delay finished.")
                    delay_until = None
                else:
                    terminate_block_targets(debug_print=False)

            detected_before = detected_now
            time.sleep(0.25)

    except KeyboardInterrupt:
        log_event("TiltGuard stopped")
        print("\n[TiltGuard] Stopped.")


if __name__ == "__main__":
    main()
