from .utils.theme_loader import load_theme

class CLIface:
    def __init__(self):
        self.terminal_name = "CLIface"
        self.bg_color = ""
        self.fg_color= ""
        self.text_color = ""
        self.input_color = ""
        self.logo = ""
        self.logo_color = ""
        self.cursor = ">"
        self.cursor_fg = ""
        self.cursor_bg = ""
        self.title_color = ""
        self.option_color = ""


    def config(self, *, terminal_name=None,
                bg_color=None, fg_color=None,
                text_color=None, input_color=None,
                cursor=None, cursor_fg=None, cursor_bg=None,
                logo=None, logo_color=None,
                title_color=None, option_color=None,
                theme=None
            ):
        if theme:
            loaded_theme = load_theme(theme)
            (
                bg_color, fg_color,
                text_color, input_color,
                cursor_fg, cursor_bg, 
                logo_color, title_color,
                option_color
            ) = (
                loaded_theme["bg_color"], loaded_theme["fg_color"],
                loaded_theme["text_color"], loaded_theme["input_color"],
                loaded_theme["cursor_fg"], loaded_theme["cursor_bg"],
                loaded_theme["logo_color"], loaded_theme["title_color"],
                loaded_theme["option_color"]
            )

        
        if terminal_name : self.terminal_name = terminal_name

        if bg_color : self.bg_color = bg_color
        if fg_color : self.fg_color = fg_color

        if text_color : self.text_color = text_color
        if input_color : self.input_color = input_color

        if cursor : self.cursor = cursor
        if cursor_fg : self.cursor_fg = cursor_fg
        if cursor_bg : self.cursor_bg = cursor_bg

        if logo : self.logo = logo
        if logo_color : self.logo_color = logo_color

        if title_color : self.title_color = title_color
        if option_color : self.option_color = option_color