import re

# Fields stuff.
CYRILLIC_CONVERSION_TABLE = str.maketrans(
    {
        "А": "A",
        "В": "B",
        "Е": "E",
        "К": "K",
        "М": "M",
        "Н": "H",
        "О": "O",
        "Р": "P",
        "С": "C",
        "Т": "T",
        "У": "Y",
        "Х": "X",
        # lowercase
        "а": "A",
        "в": "B",
        "е": "E",
        "к": "K",
        "м": "M",
        "н": "H",
        "о": "O",
        "р": "P",
        "с": "C",
        "т": "T",
        "у": "Y",
        "х": "X",
    }
)
NON_WORD_RE = re.compile(r"[^a-zA-Z0-9]+")
NON_DIGIT_RE = re.compile(r"[^0-9]+")
SPACES_RE = re.compile(r"\s+")
REGISTRATION_NUMBER_RE = {
    "HU": re.compile(r"^(?=(CD)?.{6,7}$)[A-Z][A-Z]*[0-9]+$"),
    "RO": re.compile(
        r"""^(
            (MAI|A|CD|TC)\d{1,6}
            |
            (AB|AG|AR|BC|BH|BN|BR|BT|BV|BZ|CJ|CL|CS|CT|CV|DB|DJ|GJ|GL|GR|
             HD|HR|IF|IL|IS|MH|MM|MS|NT|OT|PH|SB|SJ|SM|SV|TL|TM|TR|VL|VN|VS)
            (
                (?!00)\d{2}[A-Z]{3}
                |
                (?!0)\d{4,10}
            )
            |
            B(
                (?!00)[0-9]{2}[A-Z]{3}
                |
                (?!0)(
                    [0-9]{3}[A-Z]{3}
                    |
                    \d{4,10}
                )
            )
        )$""",
        re.VERBOSE,
    ),
}
REGISTRATION_NUMBER_STRICT_RE = {
    "no_q_letter": re.compile(r"^[A-Z]+\d+.*?Q"),
    "no_i_start_letter": re.compile(r"^[A-Z]+\d+I"),
    "no_o_start_letter": re.compile(r"^[A-Z]+\d+O"),
}
REGISTRATION_NUMBER_ROMANIAN_LEASE_RE = re.compile(
    r"""
        ^
        (AB|AG|AR|BC|BH|BN|BR|BT|BV|BZ|CJ|CL|CS|CT|CV|DB|DJ|GJ|GL|GR|
         HD|HR|IF|IL|IS|MH|MM|MS|NT|OT|PH|SB|SJ|SM|SV|TL|TM|TR|VL|VN|VS|B)
        (?!0)\d{0,6}(?P<year>\d{2})(?P<month>\d{2})
        $
    """,
    re.VERBOSE,
)

# Logging stuff.
LINE_LENGTH = 140
THICK_LINE = "=" * LINE_LENGTH
CONTEXT_LINE = " context ".center(LINE_LENGTH, "-")
REQUEST_CONTENT_LINE = " request content ".center(LINE_LENGTH, "-")
REQUEST_DATA_LINE = " request data ".center(LINE_LENGTH, "-")
REQUEST_OVERSIZE_LINE = " request oversize (first 10kb) ".center(LINE_LENGTH, "-")
RESPONSE_CONTENT_LINE = " response content ".center(LINE_LENGTH, "-")
RESPONSE_DATA_LINE = " response data ".center(LINE_LENGTH, "-")
RESPONSE_EXCEPTION_LINE = " response exception ".center(LINE_LENGTH, "-")
RESPONSE_LINE = " response ".center(LINE_LENGTH, "-")
RESPONSE_UNKNOWN_LINE = " response (unknown) ".center(LINE_LENGTH, "-")
TRACEBACK_LINE = " traceback ".center(LINE_LENGTH, "-")
