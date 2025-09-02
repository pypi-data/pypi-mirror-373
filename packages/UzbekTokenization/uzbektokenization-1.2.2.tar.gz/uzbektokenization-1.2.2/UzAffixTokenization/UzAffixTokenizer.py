def tokenize(word):
    prefixes = ['bad', 'bar', 'ba', 'be', 'bo', 'ham', 'nim', 'no', 'pesh', 'ser']
    noun_suffixes = ['dan', 'da', 'ga', 'ka', 'lar', 'ni', 'ning', 'qa']
    verb_suffixes = ["adi", "ajak", "ay", "aylik", "ayotib", "ayotir", "di", "dir", "gan", "gin", "imiz", "ingiz", "kin", "man", "miz", "moq", "moqchi", "ngiz", "qin", "san", "sin", "siz", "yap", "ylik", "yotib", "yotir"]
    suffixes = ['cha', 'inchi', 'mas', 'mi', 'nchi', 'roq', 'ta']

    # If the text is not a word, it will be returned by itself.
    if not isinstance(word, str) or word.find(' ') > 0:
        return word

    # Save the result list, separating each affix
    prefixed_parts = []
    suffixed_parts = []

    # Separating prefixes
    for prefix in prefixes:
        if word.lower().startswith(prefix):
            prefixed_parts.append(word[:len(prefix)])
            word = word[len(prefix):]

    # Separating suffixes
    suffixes = noun_suffixes + verb_suffixes + suffixes
    while True:
        found = False
        for suffix in suffixes:
            if word.lower().endswith(suffix):
                suffixed_parts.append(word[-len(suffix):])
                word = word[:-len(suffix)]
                found = True
                break
        if not found:
            break

    if prefixed_parts or suffixed_parts:
        affixed_parts = prefixed_parts + [word] + suffixed_parts[::-1]
        return "-".join(affixed_parts)
    else:
        return word
