from prompt_toolkit.layout.containers import (
    VSplit, HSplit, Window, ConditionalContainer,
    DynamicContainer, Container, AnyContainer
)
from prompt_toolkit.widgets.base import Border, Condition, Label, Template
from prompt_toolkit.formatted_text import AnyFormattedText
from functools import partial


class CLIfaceFrame:
        
    def __init__(self, body: AnyContainer, title: AnyFormattedText = "", style: str = ""):
        self.title = title
        self.body = body

        fill = partial(Window, style="class:frame.border")
        style = "class:frame " + style


        top_row_with_title = VSplit(
                    [
                        fill(width=1, height=1, char=Border.TOP_LEFT),
                        fill(char=Border.HORIZONTAL),
                        fill(width=1, height=1, char="|"),
                        # Notice: we use `Template` here, because `self.title` can be an
                        # `HTML` object for instance.
                        Label(
                            lambda: Template(" {} ").format(self.title),
                            style="class:frame.label",
                            dont_extend_width=True,
                        ),
                        fill(width=1, height=1, char="|"),
                        fill(char=Border.HORIZONTAL),
                        fill(width=1, height=1, char=Border.TOP_RIGHT),
                    ],
                    height=1,
                )

        top_row_without_title = VSplit(
                    [
                        fill(width=1, height=1, char=Border.TOP_LEFT),
                        fill(char=Border.HORIZONTAL),
                        fill(width=1, height=1, char=Border.TOP_RIGHT),
                    ],
                    height=1,
                )

        @Condition
        def has_title() -> bool:
            return bool(self.title)

        self.container = HSplit(
                    [
                        ConditionalContainer(content=top_row_with_title, filter=has_title),
                        ConditionalContainer(content=top_row_without_title, filter=~has_title),
                        VSplit(
                            [
                                fill(width=1, char=Border.VERTICAL),
                                DynamicContainer(lambda: body),
                                fill(width=1, char=Border.VERTICAL),
                                # Padding is required to make sure that if the content is
                                # too small, the right frame border is still aligned.
                            ],
                            padding=1
                        ),
                        VSplit(
                            [
                                fill(width=1, height=1, char=Border.BOTTOM_LEFT),
                                fill(char=Border.HORIZONTAL),
                                fill(width=1, height=1, char=Border.BOTTOM_RIGHT),
                            ],
                            # specifying height here will increase the rendering speed.
                            height=1,
                        ),
                    ],
                    width=None,
                    height=None,
                    style=style,
                )


    def __pt_container__(self) -> Container:
        return self.container