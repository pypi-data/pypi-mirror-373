from cliface.cliface import CLIface
from cliface.layout import CLIfaceFrame, CLIfaceApp
from cliface.layout.menu_options import Options
from prompt_toolkit.shortcuts import set_title
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
import os


class MenuScreen():
    def __init__(self, config: CLIface, title:str="",
                text:str="", options:dict=None,
                inline=True, use_logo=False):
        
        if not config:
            raise Exception("No main config was given")
        if not options:
            raise Exception("No options were given")

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
        self.option_color = config.option_color

        self.title = title
        self.text = text
        self.inline = inline
        self.use_logo = use_logo
        self.options = {name:function for name, function in options.items()}

    def show(self):
        set_title(self.terminal_name)

        screen_logo = self.logo + "\n" if self.use_logo and self.logo else ''

        style = Style.from_dict({
            '': f'fg:{self.input_color} bg:{self.cursor_bg}',
            'input': f'fg:{self.input_color} bg:{self.cursor_bg}'
        })

        option_names, option_functions = {}, []
        count = 0
        
        max_spaces = len(max(self.options, key=lambda k: len(k))) + 2
        inline_options = []
        
        for option, function in self.options.items():
            inline_options.append(f'{option} [{count+1}]')
            option_names[option] = count
            option_functions.append(function)
            count+=1

        inline_options = ' '.join(inline_options)

        def generate_options():
            terminal_columns = os.get_terminal_size().columns
            terminal_lines = os.get_terminal_size().lines

            logo_lines = screen_logo.splitlines()

            if len(inline_options) > terminal_columns:
                self.inline = False
            else:
                self.inline = True

            terminal_h = (terminal_lines - len(logo_lines)) / 2
            if not self.inline:
                terminal_h = (terminal_lines - count - len(logo_lines)) / 2

            return Options(
                option_names=option_names,
                max_spaces=max_spaces,
                text_color=self.text_color,
                option_color=self.option_color,
                inline=self.inline,
                size=[terminal_h, terminal_columns]
            )

        def make_dynamic_window():
            def get_text():
                body = [
                    (f"fg:{self.logo_color}", f"{screen_logo}"),
                    (f"fg:{self.text_color}", f"{self.text}\n")
                ]
                body += generate_options()
                return FormattedText(body)

            return Window(content=FormattedTextControl(get_text))


        window = make_dynamic_window()

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
            cursor_fg=self.cursor_fg
        )

        result = app_answer.result.lower()
        try:
            return option_functions[int(result)-1]()
        except Exception:
            return self.show()