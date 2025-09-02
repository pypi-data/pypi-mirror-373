def __digraf_to_new_latin(word):  # noqa ŌōḠḡŞşÇçŊŋ
    # Converts Uzbek digraphs (e.g., O‘, G‘, SH, CH, NG) to corresponding new Latin Unicode characters.

    # Replace various representations of 'O‘' with 'Ō'
    word = word.replace("O'", 'Ō')
    word = word.replace("O`", 'Ō')
    word = word.replace("Oʻ", 'Ō')
    word = word.replace("Oʼ", 'Ō')
    word = word.replace("O‘", 'Ō')
    word = word.replace("O’", 'Ō')

    # Replace various representations of 'o‘' with 'ō'
    word = word.replace("o'", 'ō')
    word = word.replace("o`", 'ō')
    word = word.replace("oʻ", 'ō')
    word = word.replace("oʼ", 'ō')
    word = word.replace("o‘", 'ō')
    word = word.replace("o’", 'ō')

    # Replace various representations of 'G‘' with 'Ḡ'
    word = word.replace("G'", 'Ḡ')
    word = word.replace("G`", 'Ḡ')
    word = word.replace("Gʻ", 'Ḡ')
    word = word.replace("Gʼ", 'Ḡ')
    word = word.replace("G‘", 'Ḡ')
    word = word.replace("G’", 'Ḡ')

    # Replace various representations of 'g‘' with 'ḡ'
    word = word.replace("g'", 'ḡ')
    word = word.replace("g`", 'ḡ')
    word = word.replace("gʻ", 'ḡ')
    word = word.replace("gʼ", 'ḡ')
    word = word.replace("g‘", 'ḡ')
    word = word.replace("g’", 'ḡ')

    # Replace digraphs for 'SH', 'CH', and 'NG'
    word = word.replace("SH", 'Ş').replace("Sh", 'Ş').replace("sH", 'Ş').replace("sh", 'ş')
    word = word.replace("CH", 'Ç').replace("Ch", 'Ç').replace("cH", 'Ç').replace("ch", 'ç')
    word = word.replace("NG", 'Ŋ').replace("Ng", 'Ŋ').replace("nG", 'Ŋ').replace("ng", 'ŋ')

    return word


def __new_latin_to_digraf(word):  # noqa ŌōḠḡŞşÇçŊŋ
    # Converts new Latin Unicode characters back to Uzbek digraphs.

    word = word.replace('Ō', "O‘")
    word = word.replace('ō', "o‘")
    word = word.replace('Ḡ', "G‘")
    word = word.replace('ḡ', "g‘")
    word = word.replace('Ş', "SH").replace('ş', "sh")
    word = word.replace('Ç', "CH").replace('ç', "ch")
    word = word.replace('Ŋ', "NG").replace('ŋ', "ng")

    return word


def tokenize(word):
    # If the text is not a word, it will be returned by itself.
    if not isinstance(word, str) or word.find(' ') > 0:
        return word

    # Dictionary of words with predefined syllabifications
    exceptions = {  # 56 units
        "abstrakt": "abs-trakt",
        "agglyutinativ": "ag-glyu-ti-na-tiv",
        "ansambl": "an-sambl",
        "aviaekspress": "a-vi-a-eks-press",
        "aviakonstruktor": "a-vi-a-kons-truk-tor",
        "avstraliya": "avs-tra-li-ya",
        "bae'tibor": "ba-e'-ti-bor",
        "bee'tibor": "be-e'-ti-bor",
        "eksklyuziv": "eks-klyu-ziv",
        "ekstremizm": "eks-tre-mizm",
        "elektrlampa": "e-lektr-lam-pa",
        "inflyatsiya": "in-flyat-si-ya",
        "instruksiya": "ins-truk-si-ya",
        "mototransport": "mo-to-trans-port",
        "zoologiya": "zoo-lo-gi-ya",
        "monografiya": "mo-no-gra-fi-ya",
        "transport": "trans-port",
        "kongres": "kon-gres",
        "vengriya": "ven-gri-ya",
        "yangilik": "yan-gi-lik",
        "ob-havo": "ob-ha-vo",
        "xalqchilikka": "xalq-chi-lik-ka",
        "avangard": "a-van-gard",
        "shtanga": "shtan-ga",
        "translator": "trans-la-tor",
        "mexanizmlarini": "me-xa-nizm-la-ri-ni",
        "maxanizmlashtirish": "ma-xa-nizm-lash-ti-rish",
        "qalani": "qa'la-ni",
        "alochi": "a'-lo-chi",
        "tirbandlik": "tir-band-lik",
        "farzandli": "far-zand-li",
        "tanga": "tan-ga",
        "mashal": "mash'-al",
        "angren": "an-gren",
        "sehrli": "sehr-li",
        "sementchi": "se-ment-chi",
        "hunarmandchilik": "hu-nar-mand-chi-lik",
        "afsungar": "af-sun-gar",
        "chilangar": "chi-lan-gar",
        "goshtli": "go'sht-li",
        "daraxtlik": "daraxt-lik",
        "daraxtzor": "daraxt-zor",
        "mehrli": "mehr-li",
        "mehrsiz": "mehr-siz",
        "dostlik": "do'st-lik",
        "dostona": "do's-to-na",
        "dostmuhammad": "do'st-mu-ham-mad",
        "rostlik": "rost-lik",
        "rostgoy": "rost-go'y",
        "pastlik": "past-lik",
        "pasttekislik": "past-te-kis-lik",
        "qorqinchli": "qo'r-qinch-li",
        "faxrli": "faxr-li",
        "faxrlanmoq": "faxr-lan-moq",
        "farqli": "farq-li",
        "farqlanmoq": "farq-lan-moq"
    }
    stem = ''
    exc = False
    for exception in list(exceptions.keys()):
        if word.lower().startswith(exception):
            stem = exceptions[exception]
            word = word[len(exception):]
            if not word:
                return stem
            exc = True

    # Convert Uzbek digraphs to new Latin Unicode characters
    word = __digraf_to_new_latin(word)

    vowels = "AaEeIiOoUuŌō"
    consonants = "BbDdFfGgHhJjKkLlMmNnPpQqRrSsTtVvXxYyZzḠḡŞşÇçŊŋ"

    # Remove leading and trailing spaces
    word = word.strip()

    # If the word does not contain a vowel, return as is
    if not any(char in vowels for char in word):
        return word

    syllables = []
    current_syllable = ""
    i = 0

    # Process the word character by character
    while i < len(word):
        current_syllable += word[i]

        if word[i] in vowels:
            next_char = word[i + 1] if i + 1 < len(word) else ""
            next_next_char = word[i + 2] if i + 2 < len(word) else ""

            # If next two characters are consonants, end syllable here
            if next_char in consonants and next_next_char in consonants:
                current_syllable += next_char
                syllables.append(current_syllable)
                current_syllable = ""
                i += 1
            else:
                syllables.append(current_syllable)
                current_syllable = ""

        i += 1

    # Add any remaining characters to syllables
    if current_syllable:
        if len(current_syllable) == 1 and syllables:
            syllables[-1] += current_syllable
        else:
            syllables.append(current_syllable)

    # Convert back to Uzbek digraphs
    clean_syllables = [__new_latin_to_digraf(syllable) for syllable in syllables]

    if exc:
        return stem + "-" + "-".join(clean_syllables)
    else:
        return "-".join(clean_syllables)
