
def _snip(text: str, n: int = 200) -> str:
    if text is None:
        return ""
    s = str(text).replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"
