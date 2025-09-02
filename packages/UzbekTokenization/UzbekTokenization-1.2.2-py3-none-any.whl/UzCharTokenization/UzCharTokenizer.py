def tokenize(text, white_space=False):
    # Split the text into individual characters
    incorrect_chars = list(text)

    chars = []
    i = 0
    while i < len(incorrect_chars):
        if (i+1 < len(incorrect_chars)) and (incorrect_chars[i] == 'S' or incorrect_chars[i] == 's') and (incorrect_chars[i+1] == 'H' or incorrect_chars[i+1] == 'h'):
            chars.append(incorrect_chars[i] + incorrect_chars[i+1])
            i += 2
            continue
        if (i+1 < len(incorrect_chars)) and (incorrect_chars[i] == 'C' or incorrect_chars[i] == 'c') and (incorrect_chars[i+1] == 'H' or incorrect_chars[i+1] == 'h'):
            chars.append(incorrect_chars[i] + incorrect_chars[i+1])
            i += 2
            continue
        if (i+1 < len(incorrect_chars)) and (incorrect_chars[i] == 'N' or incorrect_chars[i] == 'n') and (incorrect_chars[i+1] == 'G' or incorrect_chars[i+1] == 'g'):
            chars.append(incorrect_chars[i] + incorrect_chars[i+1])
            i += 2
            continue
        if (i+1 < len(incorrect_chars)) and (incorrect_chars[i] == 'O' or incorrect_chars[i] == 'o') and (incorrect_chars[i+1] == f'{chr(39)}' or incorrect_chars[i+1] == f'{chr(96)}' or incorrect_chars[i+1] == f'{chr(699)}' or incorrect_chars[i+1] == f'{chr(700)}' or incorrect_chars[i+1] == f'{chr(8216)}' or incorrect_chars[i+1] == f'{chr(8217)}'):
            chars.append(incorrect_chars[i] + incorrect_chars[i+1])
            i += 2
            continue
        if (i+1 < len(incorrect_chars)) and (incorrect_chars[i] == 'G' or incorrect_chars[i] == 'g') and (incorrect_chars[i+1] == f'{chr(39)}' or incorrect_chars[i+1] == f'{chr(96)}' or incorrect_chars[i+1] == f'{chr(699)}' or incorrect_chars[i+1] == f'{chr(700)}' or incorrect_chars[i+1] == f'{chr(8216)}' or incorrect_chars[i+1] == f'{chr(8217)}'):
            chars.append(incorrect_chars[i] + incorrect_chars[i+1])
            i += 2
            continue
        chars.append(incorrect_chars[i])
        i += 1

    if white_space:
        return chars
    else:
        return list(filter(lambda x: x != ' ', chars))
