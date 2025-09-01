
FALSEY_PRECISE_STRINGS = [
    "0",
    "FALSE",
    "False",
    "NO",
    "No",
    "OFF",
    "Off",
    "false",
    "no",
    "off",
]

TRUEY_PRECISE_STRINGS = [
    "1",
    "ON",
    "On",
    "TRUE",
    "True",
    "YES",
    "Yes",
    "on",
    "true",
    "yes",
]

FALSEY_LOWERCASE_STRINGS = [
    "false",
    "no",
    "off",
    "0",
]

TRUEY_LOWERCASE_STRINGS = [
    "true",
    "yes",
    "on",
    "1",
]


def _str2bool(
    s
):
    if s is None:

        return None

    if s in FALSEY_PRECISE_STRINGS:

        return False

    if s in TRUEY_PRECISE_STRINGS:

        return True

    s = s.strip().lower()

    if s in TRUEY_LOWERCASE_STRINGS:

        return True

    if s in FALSEY_LOWERCASE_STRINGS:

        return False

    return None

