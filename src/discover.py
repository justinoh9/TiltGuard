import time
import psutil

KEYWORDS = ("riot", "league")

def main():
    print("Process discovery running. Open Riot/League now.")
    print("This will print any process with 'riot' or 'league' in its name.")
    print("Press Ctrl+C to stop.\n")

    seen = set()

    while True:
        for p in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
            try:
                name = (p.info["name"] or "")
                low = name.lower()
                if any(k in low for k in KEYWORDS):
                    key = (p.info["pid"], name)
                    if key not in seen:
                        seen.add(key)
                        exe = p.info.get("exe")
                        cmd = p.info.get("cmdline")
                        print(f"PID={p.info['pid']}  NAME={name}")
                        if exe:
                            print(f"  EXE={exe}")
                        if cmd:
                            print(f"  CMD={' '.join(cmd)}")
                        print()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        time.sleep(0.5)

if __name__ == "__main__":
    main()
