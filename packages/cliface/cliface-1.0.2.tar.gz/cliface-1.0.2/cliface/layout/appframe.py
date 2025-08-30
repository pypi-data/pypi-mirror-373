from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.widgets import Label
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.processors import PasswordProcessor
from cliface.layout.components import CLIfaceFrame
import sys


class CLIfaceApp:
    def __init__(
            self,
            window:Window=None, frame:CLIfaceFrame=None,
             cursor=None, cursor_fg=None,
            yes_no=None, 
            is_password=False, password_char=None,
            style=None
        ):
        self.window = window
        self.frame = frame
        self.style = style
        self.cursor = cursor
        self.cursor_fg = cursor_fg
        self.yes_no = yes_no
        self.is_password = is_password


        kb = KeyBindings()
        @kb.add('enter')
        def _(event):
            text = input_area.text.strip()
            event.app.exit(result=text)

        @kb.add('c-c')
        def _(event):
            sys.exit()

        prefix_label = Label(
            HTML(f'<prompt fg="{self.cursor_fg}">{self.cursor}</prompt>'),
            width=len(self.cursor)
        )
        match self.is_password:
            case False:
                input_area = TextArea(style='class:input', multiline=False)
            case True:
                processor = PasswordProcessor(char=password_char)
                input_area = TextArea(
                    style='class:input', multiline=False,
                    password=self.is_password, input_processors=[processor]
                )


        cursor_input = VSplit([
            prefix_label,
            input_area
        ])

        if self.yes_no:
            _yes = yes_no[0]
            _no = yes_no[1]
            layout = Layout(HSplit([
                frame,
                cursor_input,
                Label(HTML(f'<prefix fg="{self.cursor_fg}">({_yes}/{_no})</prefix>'))
            ]))
            
            @kb.add(_yes)
            def _(event):
                event.app.exit(result=_yes)
            
            @kb.add(_no)
            def _(event):
                event.app.exit(result=_no)
        else:
            layout = Layout(HSplit([
                frame,
                cursor_input
            ]))


        app = Application(
            layout=layout, key_bindings=kb, style=style, full_screen=True
        )

        self.result = app.run()

    def __str__(self) -> str:
        return str(self.result)