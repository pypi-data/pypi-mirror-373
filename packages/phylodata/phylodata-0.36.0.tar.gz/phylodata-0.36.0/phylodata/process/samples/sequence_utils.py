def contains_sequence(sequence: str):
    return any([ch for ch in sequence if ch.isalpha()])


def is_amino_acid_sequence(sequence: str):
    characters = {c.lower() for c in sequence}
    return characters.issubset(AA_CHARACTERS)


def is_dna_sequence(sequence: str):
    characters = {c.lower() for c in sequence}
    return characters.issubset(DNA_CHARACTERS)


def is_rna_sequence(sequence: str):
    characters = {c.lower() for c in sequence}
    return characters.issubset(RNA_CHARACTERS)


DNA_CHARACTERS = {
    "a",
    "t",
    "c",
    "g",
    "*",
    "?",
    "-",
    "r",
    "y",
    "s",
    "w",
    "k",
    "m",
    "b",
    "d",
    "h",
    "v",
    "n",
}
RNA_CHARACTERS = (DNA_CHARACTERS - {"t"}) | {"u"}
AA_CHARACTERS = {
    "a",
    "r",
    "n",
    "d",
    "c",
    "e",
    "q",
    "g",
    "h",
    "i",
    "l",
    "k",
    "m",
    "f",
    "p",
    "s",
    "t",
    "w",
    "y",
    "v",
    "u",
    "o",
    "?",
    "*",
    "-",
}
