

def Options(option_names=None, max_spaces=None, text_color=None, option_color=None, inline=True, size:list=[]):
    options = []
    terminal_h, terminal_columns = size

    if inline:
        for name, value in option_names.items():
            options.append((f"fg:{text_color}", f' {name} '))
            options.append((f"fg:{option_color}", f'[{value + 1}]'))
        return options

    if terminal_h <= 2:
        def calc_limit_per_line(option_names, max_spaces, terminal_columns):
            current_width = 0
            limit = 0

            for value, name in enumerate(option_names.keys()):
                spaces = max_spaces - len(name)
                display_text = f"{name}{' ' * spaces}[{value + 1}]{' ' if (value+1)<10 else ''}"

                spacing = 2 if value + 1 < 10 else 1

                item_length = len(display_text) + spacing

                if current_width + item_length <= terminal_columns:
                    current_width += item_length
                    limit += 1
                else:
                    break

            return max(1, limit)

        _count = 1

        options.append((f"fg:{text_color}", f"{'\n' if terminal_h > -1 else ''}"))

        limit_per_line = calc_limit_per_line(option_names, max_spaces, terminal_columns)


        for name, value in option_names.items():
            spaces = (max_spaces - len(name)) 
            if _count >= limit_per_line:
                _count = 1
                options.append((f"fg:{text_color}", f'{name}{' '*spaces}'))
                options.append((f"fg:{option_color}", f'[{value + 1}]\n'))
                continue

            options.append((f"fg:{text_color}", f'{name}{' '*spaces}'))
            options.append((f"fg:{option_color}", f'[{value + 1}]{'  ' if (value+1)<10 else ' '}'))
            _count += 1
        return options

    options.append((f"fg:{text_color}", "\n"*int((terminal_h + 1) // 2)))
    for name, value in option_names.items():
        spaces = (max_spaces - len(name))
        options.append((f"fg:{text_color}", f'{name}{' '*spaces}'))
        options.append((f"fg:{option_color}", f'[{value + 1}]\n'))
    
    return options