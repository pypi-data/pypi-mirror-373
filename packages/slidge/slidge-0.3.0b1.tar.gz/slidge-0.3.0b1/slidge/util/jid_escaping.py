from functools import lru_cache

JID_ESCAPE_SEQUENCES = {
    "\\20",
    "\\22",
    "\\26",
    "\\27",
    "\\2f",
    "\\3a",
    "\\3c",
    "\\3e",
    "\\40",
    "\\5c",
}


JID_UNESCAPE_TRANSFORMATIONS = {
    "\\20": " ",
    "\\22": '"',
    "\\26": "&",
    "\\27": "'",
    "\\2f": "/",
    "\\3a": ":",
    "\\3c": "<",
    "\\3e": ">",
    "\\40": "@",
    "\\5c": "\\",
}


@lru_cache(1000)
def unescape_node(node: str) -> str:
    """Unescape a local portion of a JID."""
    unescaped = []
    seq = ""
    for i, char in enumerate(node):
        if char == "\\":
            seq = node[i : i + 3]
            if seq not in JID_ESCAPE_SEQUENCES:
                seq = ""
        if seq:
            if len(seq) == 3:
                unescaped.append(JID_UNESCAPE_TRANSFORMATIONS.get(seq, char))

            # Pop character off the escape sequence, and ignore it
            seq = seq[1:]
        else:
            unescaped.append(char)
    return "".join(unescaped)


ESCAPE_TABLE = "".maketrans({v: k for k, v in JID_UNESCAPE_TRANSFORMATIONS.items()})
