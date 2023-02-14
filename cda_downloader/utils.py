import re
import os
import urllib.parse


def get_video_match(url: str) -> re.Match[str] | None:
    video_regex = re.compile(
        r"""https?://(?:(?:www|ebd)\.)?cda\.pl/
        (?:video|[0-9]+x[0-9]+)/([0-9a-z]+)""",
        re.VERBOSE | re.IGNORECASE,
    )
    return video_regex.match(url)


def is_video(url: str) -> bool:
    """Check if url is a cda video."""
    match = get_video_match(url)
    return match is not None


def get_folder_match(url: str) -> re.Match[str] | None:
    folder_regex1 = re.compile(
        r"""(https?://(?:www\.)?cda\.pl/(?!video)[a-z0-9_-]+/
        (?!folder/)[a-z0-9_-]+)/?(\d*)""",
        re.VERBOSE | re.IGNORECASE,
    )
    folder_regex2 = re.compile(
        r"""(https?://(?:www\.)?cda\.pl/(?!video)[a-z0-9_-]+/
        folder/\d+)/?(\d*)""",
        re.VERBOSE | re.IGNORECASE,
    )
    return folder_regex1.match(url) or folder_regex2.match(url)


def is_folder(url: str) -> bool:
    """Check if url is a cda folder."""
    match = get_folder_match(url)
    return match is not None


def get_safe_title(title: str) -> str:
    """Remove characters that are not allowed in the filename
    and convert spaces to underscores."""
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"[\s-]+", "_", title).strip("_")
    return title


def clear() -> None:
    """Clears the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


# source: // https://www.cda.pl/js/player.js?t=1676342296
def decrypt_url(url: str) -> str:
    for p in ("_XDDD", "_CDA", "_ADC", "_CXD", "_QWE", "_Q5", "_IKSDE"):
        url = url.replace(p, "")
    url = urllib.parse.unquote(url)
    b = []
    for c in url:
        f = c if isinstance(c, int) else ord(c)
        b.append(chr(33 + (f + 14) % 94) if 33 <= f <= 126 else chr(f))
    a = "".join(b)
    a = a.replace(".cda.mp4", "")
    a = a.replace(".2cda.pl", ".cda.pl")
    a = a.replace(".3cda.pl", ".cda.pl")
    if "/upstream" in a:
        a = a.replace("/upstream", ".mp4/upstream")
        return "https://" + a
    else:
        return "https://" + a + ".mp4"
