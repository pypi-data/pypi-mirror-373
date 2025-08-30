

def break_text_by_width(text, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        if len(current_line) + len(word) + 1 > max_width:
            lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += ' ' + word
            else:
                current_line = word
    if current_line:
        lines.append(current_line)

    return '\n'.join(lines)