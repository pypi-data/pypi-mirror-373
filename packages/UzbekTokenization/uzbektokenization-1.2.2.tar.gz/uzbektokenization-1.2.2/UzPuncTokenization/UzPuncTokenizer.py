import re


def tokenize(text, punctuation=True):
    # Regex to capture words and punctuation separately
    tokens = re.findall(r'\w+|[^\w\s]', text)

    # Group consecutive words together
    result = []
    current_phrase = [tokens[0]]
    i = 1
    while i < len(tokens):
        if re.match(r'\w+', tokens[i]):  # It's a word
            current_phrase.append(tokens[i])
        else:  # It's a punctuation mark
            if current_phrase:
                if tokens[i-1][-1] in ['O', 'o', 'G', 'g'] and tokens[i] in ["'", "`", "ʻ", "ʼ", "‘", "’"]:
                    if i+1 < len(tokens):
                        current_phrase[len(current_phrase) - 1] += tokens[i]+tokens[i+1]
                        i += 2
                    else:
                        current_phrase[len(current_phrase) - 1] += tokens[i]
                        i += 1
                    continue

                # if tokens[i] == ''
                result.append(' '.join(current_phrase))  # Add the grouped words as one token
                current_phrase = []
            if punctuation:
                result.append(tokens[i])  # Add the punctuation mark as a separate token
        i += 1

    # Add any remaining phrase if it exists
    if current_phrase:
        result.append(' '.join(current_phrase))

    return result
