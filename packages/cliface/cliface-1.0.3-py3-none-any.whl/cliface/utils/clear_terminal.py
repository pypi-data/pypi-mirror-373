import subprocess
import platform


def clear_terminal():
    """
    Clears the terminal screen based on the OS.
    """

    __os = platform.system().lower()

    if "linux" in __os:
        subprocess.run("clear", shell=True)
    elif "windows" in __os:
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)

if __name__ == "__main__":
    clear_terminal()