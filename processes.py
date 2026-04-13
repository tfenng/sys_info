import psutil


def main():
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=["pid", "username", "name"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        else:
            print(f"{pinfo['pid']}\t{pinfo['username']}\t{pinfo['name']}")


if __name__ == "__main__":
    main()
