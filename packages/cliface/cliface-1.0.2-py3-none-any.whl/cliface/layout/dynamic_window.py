from cliface.utils.break_text import break_text_by_width
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
import math
import os


def make_dynamic_window(
        screen_logo=None, logo_color=None,
        text=None, text_color=None,
        use_logo=False
    ):
    def get_text():
        terminal_columns = os.get_terminal_size().columns
        terminal_lines = os.get_terminal_size().lines
        logo_lines = screen_logo.splitlines()
        
        screen_text = break_text_by_width(text, terminal_columns - 4)
        split_text = len(screen_text.splitlines())

        terminal_h = (terminal_lines - split_text) - 4
        if use_logo:
            terminal_h -= len(logo_lines)

        padding_top = max(0, math.ceil(terminal_h / 2))
        aligned_text = f"{'\n' * padding_top}{screen_text}"
        
        body = [
            (f"fg:{logo_color}", f"{screen_logo}"),
            (f"fg:{text_color}", f"{aligned_text}")
        ]
        
        return FormattedText(body)
    
    return Window(content=FormattedTextControl(get_text))