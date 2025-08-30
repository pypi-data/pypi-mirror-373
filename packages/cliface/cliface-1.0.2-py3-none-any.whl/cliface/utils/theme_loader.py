import os
import json
import sys


def load_theme(theme):
    try:
        dirpath = os.path.dirname(__file__)
        path = os.path.join(dirpath, "themes")
        
        file_path = os.path.join(path, f"{theme}.json")

        if not os.path.isfile(file_path):
            raise FileNotFoundError()


        with open(file_path, "r") as data:
            theme_data = json.load(data)

            return theme_data

    except FileNotFoundError:
        print(
            "\033[0;31m" +
            f'[ERROR] CLIKit.config.theme_loader | Theme "{theme}" not found.'+
            "\033[0m"
        )
        sys.exit()

    except Exception as e:
        print(
            "\033[0;31m" +
            f'[ERROR] CLIKit.config.theme_loader | {e}'+
            "\033[0m"
        )
        sys.exit()


if __name__ == "__main__":
    print(load_theme('dark'))