import time
import psutil

# These are the Windows process names we will look for.
TARGETS = {
    "LeagueClient.exe",
    "RiotClientServices.exe",
}

def get_running_process_names():
    """Return a set of running process executable names, like 'chrome.exe'."""
    names = set()
    for proc in psutil.process_iter(["name"]):
        try:
            name = proc.info["name"]
            if name:
                names.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process ended or we don't have permission; ignore it.
            pass
    return names

def main():
    print("TiltGuard detector running.")
    print("Open Riot Client / League, and this will print when detected.")
    print("Press Ctrl + C to stop.\n")

    detected_before = False

    while True:
        running = get_running_process_names()
        detected_now = any(name in running for name in TARGETS)

        # Print only when the state changes (so we don't spam the terminal).
        if detected_now and not detected_before:
            print("Detected League/Riot running!")
        elif not detected_now and detected_before:
            print("League/Riot closed.")

        detected_before = detected_now
        time.sleep(1)

if __name__ == "__main__":
    main()
