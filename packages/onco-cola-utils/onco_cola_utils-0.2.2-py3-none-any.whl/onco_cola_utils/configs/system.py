class System:
    __ALL__: str = "__all__"
    NULLED = {"0", 0}
    SKIP = {"0", "_", 0}
    NO = {"", None}
    FROG: str = "___"
    TRIDASH: str = "___"
    ID: str = "ID"
    DASH: str = "_"
    DASHES = {DASH, TRIDASH}
    FULL_SKIP = {*SKIP, *NO}
    WARN: str = "!!!!!"
    FASIS: str = "field_asis"
    FTOBE: str = "field_tobe"
