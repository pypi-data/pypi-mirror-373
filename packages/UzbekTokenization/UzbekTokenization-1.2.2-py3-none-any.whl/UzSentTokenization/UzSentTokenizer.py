import re


def tokenize(text):
    # Regex pattern to split the text by sentence-ending punctuation marks, ensuring that abbreviations are not split
    sentences = re.split(r'(?<=\.|\!|\?)(?=\s)(?![A-Za-z]\.[A-Za-z]\.)', text)
    # Join any sentences where the first word starts with a capital letter but is actually part of a previous sentence.
    sentences = [sentence.strip() for sentence in sentences if sentence]
    # Merging sentences where we have abbreviations and periods followed by capital letters
    sentences = re.sub(r'(?<=\w\.\w\.)\s+(?=[A-Z])', ' ', '\n'.join(sentences))

    return sentences.splitlines()
