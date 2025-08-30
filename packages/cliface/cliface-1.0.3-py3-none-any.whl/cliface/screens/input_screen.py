from cliface.cliface import CLIface
from cliface.layout import CLIfaceFrame, CLIfaceApp, make_dynamic_window
from prompt_toolkit.shortcuts import set_title
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style


class InputScreen():
    def __init__(self, config: CLIface, title:str="", text:str="", 
                is_password=False, password_char='*', use_logo=False):
        if not config:
            raise Exception("No main config was given")

        self.terminal_name = config.terminal_name
        self.bg_color = config.bg_color
        self.fg_color = config.fg_color
        self.cursor = config.cursor
        self.cursor_fg = config.cursor_fg
        self.cursor_bg = config.cursor_bg
        self.logo = config.logo
        self.logo_color = config.logo_color
        self.text_color = config.text_color
        self.input_color = config.input_color
        self.title_color = config.title_color

        self.title = title
        self.is_password = is_password
        self.password_char = password_char
        self.use_logo = use_logo
        self.text = text


    def show(self):
        set_title(self.terminal_name)

        screen_logo = self.logo if self.use_logo and self.logo else ''

        style = Style.from_dict({
            '': f'fg:{self.input_color} bg:{self.cursor_bg}',
            'input': f'fg:{self.input_color} bg:{self.cursor_bg}'
        })

        window = make_dynamic_window(
            screen_logo=screen_logo, logo_color=self.logo_color,
            text=self.text, text_color=self.text_color,
            use_logo=self.use_logo
        )

        frame = CLIfaceFrame(
                body=window,
                title=HTML(f'<style fg="{self.title_color}">{self.title}</style>'),
                style=f"bg:{self.bg_color} fg:{self.fg_color}"
            )

        app_answer = CLIfaceApp(
            window=window,
            frame=frame,
            style=style,
            cursor=self.cursor,
            cursor_fg=self.cursor_fg,
            is_password=self.is_password,
            password_char=self.password_char
        )

        result = app_answer.result.lower()

        return result