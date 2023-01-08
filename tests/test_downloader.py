import sys
import os
import pytest  # type: ignore
import json
from typing import TypedDict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cda_downloader.__main__ import parse_args
from cda_downloader.main import Downloader


class _Video(TypedDict):
    url: str
    videoid: str
    resolutions: list[str]
    adjusted_resolution: str
    invalid_resolutions: list[str]


class _Folder(TypedDict):
    url: str
    adjusted_url: str
    next_page_url: str
    title: str


class Unknown(TypedDict):
    url: str


class _Tests(TypedDict):
    videos: list[_Video]
    folders: list[_Folder]
    unknown: list[Unknown]


def get_test_data() -> _Tests:
    folder_path = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(folder_path, "test_data.json")
    with open(json_file) as f:
        dat: _Tests = json.load(f)
    return dat


TEST_DATA = get_test_data()


"""
Now user can pass multiple urls to the downloader.

If user passes only folder urls, just iterate over them
and download like regular folders.

If user passes only videos urls, just iterate over them and
download like regular videos, apply flags to every url.

If user passed videos urls mixed with folders urls, iterate over them
and download, apply flags to every url.
-r 480p video folder - download video, try to download folder but exit cause error
-r 480p folder video - exit instantly
"""


# def test_lol():
#    video1 = TEST_DATA["videos"][0]["url"]
#    video2 = TEST_DATA["videos"][1]["url"]
#    args = parse_args([video1, video2])
#    Downloader(args)


def test_list_resolutions_and_exit_folder() -> None:
    for folder in TEST_DATA["folders"]:
        args = parse_args(["-R", folder["url"]])
        with pytest.raises(
            SystemExit, match="-R flag is only available for videos."
        ):
            Downloader(args)


def test_list_resolutions_and_exit_video() -> None:
    for video in TEST_DATA["videos"]:
        args = parse_args(["-R", video["url"]])
        with pytest.raises(SystemExit, match=""):
            Downloader(args)


def test_list_resolutions_and_exit_unknown() -> None:
    for unknown in TEST_DATA["unknown"]:
        args = parse_args(["-R", unknown["url"]])
        with pytest.raises(
            SystemExit, match="Could not recognize the url. Aborting..."
        ):
            Downloader(args)


def test_handle_r_flag_folder() -> None:
    for folder in TEST_DATA["folders"]:
        res = "720p"
        args = parse_args(["-r", res, folder["url"]])
        with pytest.raises(
            SystemExit, match="-r flag is only available for videos."
        ):
            Downloader(args)


def test_handle_r_flag_video() -> None:
    # Slice cause too many requests
    for video in TEST_DATA["videos"][:2]:
        for res in video["invalid_resolutions"]:
            args = parse_args(["-r", res, video["url"]])
            with pytest.raises(
                SystemExit,
                match=(
                    f"{res} resolution is not available for"
                    f" {video['url'].strip('/')}"
                ),
            ):
                Downloader(args)


def test_handle_r_flag_unknown() -> None:
    for unknown in TEST_DATA["unknown"]:
        res = "720p"
        args = parse_args(["-r", res, unknown["url"]])
        with pytest.raises(
            SystemExit, match="Could not recognize the url. Aborting..."
        ):
            Downloader(args)


def test_is_video() -> None:
    for video in TEST_DATA["videos"]:
        assert Downloader.is_video(video["url"]) == True

    for folder in TEST_DATA["folders"]:
        assert Downloader.is_video(folder["url"]) == False

    for unknown in TEST_DATA["unknown"]:
        assert Downloader.is_video(unknown["url"]) == False


def test_is_folder() -> None:
    for video in TEST_DATA["videos"]:
        assert Downloader.is_folder(video["url"]) == False

    for folder in TEST_DATA["folders"]:
        assert Downloader.is_folder(folder["url"]) == True

    for unknown in TEST_DATA["unknown"]:
        assert Downloader.is_folder(unknown["url"]) == False
