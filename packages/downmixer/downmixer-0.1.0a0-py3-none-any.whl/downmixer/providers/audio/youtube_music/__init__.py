from __future__ import annotations

import asyncio
import functools
import json
import logging
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Optional, Any, Callable

import yt_dlp
import ytmusicapi

from downmixer import matching, utils
from downmixer.file_tools import AudioCodecs
from downmixer.library import Artist, Album, Song
from downmixer.providers import BaseAudioProvider, AudioSearchResult, Download

logger = logging.getLogger("downmixer").getChild(__name__)


def artist_from_ytmusic(data: dict[str, Any]) -> Artist:
    """Create an Artist instance from a dict provided by the YouTube Music API search function. Sadly the only
    metadata of use form the search results is the title of the artist. More info on the result's schema [here](
    https://ytmusicapi.readthedocs.io/en/stable/reference.html#search).

    Args:
        data (dict):
            Dictionary provided by the YouTube Music API from the
            [`ytmusicapi`](https://github.com/sigma67/ytmusicapi) package.

    Returns:
        Artist instance populated from the dict.
    """
    return Artist(name=data["name"])


def album_from_ytmusic(data: dict[str, Any]) -> Album:
    """Create an Album instance from a dict provided by the YouTube Music API search function. Sadly the only
    metadata of use form the search results is the title of the album. More info on the result's schema [here](
    https://ytmusicapi.readthedocs.io/en/stable/reference.html#search).

    Args:
        data (dict):
            Dictionary provided by the YouTube Music API from the
            [`ytmusicapi`](https://github.com/sigma67/ytmusicapi) package.

    Returns:
        Album instance populated from the dict.
    """
    return Album(name=data["name"])


def song_from_ytmusic(data: dict[str, Any]) -> Song:
    """Create a Song instance from a dict provided by the YouTube Music API search function, including the Artist and
    Album objects. More info on the result's schema
    [here](https://ytmusicapi.readthedocs.io/en/stable/reference.html#search).

    Args:
        data (dict):
            Dictionary provided by the YouTube Music API from the
            [`ytmusicapi`](https://github.com/sigma67/ytmusicapi) package.

    Returns:
        Song instance populated from the dict.
    """
    return Song(
        name=data["title"],
        artists=[artist_from_ytmusic(x) for x in data["artists"]],
        album=album_from_ytmusic(data["album"]),
        duration=data["duration_seconds"],
        url=f"https://music.youtube.com/watch?v={data['videoId']}",
    )


def search_result_from_ytmusic(
    original_song: Song, result_song: Song
) -> AudioSearchResult:
    """Create an AudioSearchResult instance from a dict provided by the YouTube Music API search function. Sadly the only
    metadata of use form the search results is the title of the artist. More info on the result's schema [here](
    https://ytmusicapi.readthedocs.io/en/stable/reference.html#search).

    Args:
        original_song (Song): Instance of a song from Spotify that will be compared against this search result.
        result_song (Song): Song extracted from the search result info.

    Returns:
        AudioSearchResult from YT Music.
    """
    return AudioSearchResult(
        provider="ytmusic",
        _original_song=original_song,
        _result_song=result_song,
        match=matching.match(original_song, result_song),
        download_url=result_song.url,
    )


def _get_auth_headers(cookiejar: CookieJar) -> str | None:
    """Makes the headers that `ytmusicapi` expects to authorize YT Music requests from cookies extracted from the
    browser_specification. Returns JSON as a string.

    If no YouTube cookies are found, returns None.
    """
    cookie_strings = [
        x.name + "=" + x.value.replace('"', "")
        for x in cookiejar
        if "youtube" in x.domain
    ]
    cookies = ";".join(cookie_strings)

    if len(cookies) == 0:
        return None

    auth_headers = {
        "origin": "https://music.youtube.com",
        "x-origin": "https://music.youtube.com",
        "cookie": cookies,
    }
    return json.dumps(auth_headers)


async def _run_in_loop(func: Callable, kwargs: dict) -> Any:
    """Runs a synchronous function asynchronously using the current event loop.

    Args:
        func: Function to be called.
        kwargs: Dictionary of keyword arguments that will be passed to the function.

    Returns:
        (Any): Whatever the `func` function originally returns.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        functools.partial(func, **kwargs),
    )


class YouTubeMusicAudioProvider(BaseAudioProvider):
    provider_name = "youtube-music"

    def __init__(self, options: dict = None):
        default_options = {"encoding": "UTF-8", "format": "bestaudio"}
        options = utils.merge_dicts_with_priority(default_options, options)
        super().__init__(options)

        self.youtube_dl = yt_dlp.YoutubeDL(self.options)
        logger.debug(f"Initialized YoutubeDL client with options: {self.options}")

        auth_headers = _get_auth_headers(self.youtube_dl.cookiejar)

        # TODO: Some testing relating to this ⬇️
        # For some reason some songs like 70tjloUDVlGYkapPPTWRxU weren't found via ISRC if the language param was not
        # specified 🤷🏻‍♀️. Selecting English bought a completely fucked up result too. I copied "de" (aka German)
        # from spotDL
        self.client = ytmusicapi.YTMusic(auth=auth_headers, language="de")

    async def search(self, song: Song) -> Optional[list[AudioSearchResult]]:
        logger.info(f"Initializing search for song '{song.title}' with URI {song.id}")
        if song.isrc:
            query = song.isrc
        else:
            query = song.title

        # TODO: redo search if ISRC isn't found
        logger.debug(f"Searching query '{query}'")
        results = self.client.search(query, filter="songs", ignore_spelling=True)

        if len(results) == 0:
            logger.warning("Search returned no results")
            return None

        result_objects = []
        for r in results:
            result_song = song_from_ytmusic(r)
            search_result = search_result_from_ytmusic(song, result_song)
            result_objects.append(search_result)
            logger.debug(
                f"Found song '{result_song.title}' with URL {result_song.url}, match value {search_result.match.sum}"
            )

        ordered_results = sorted(
            result_objects, reverse=True, key=lambda x: x.match.sum
        )
        logger.debug(f"Ordered {len(ordered_results)} results")
        return ordered_results

    async def download(
        self, result: AudioSearchResult, path: Path
    ) -> Optional[Download]:
        logger.info(
            f"Starting download for search result '{result.song.title}' with URL {result.download_url}"
        )

        # Set output path of YoutubeDL on the fly
        self.youtube_dl.params["outtmpl"]["default"] = (
            str(path.absolute()) + "/%(id)s.%(ext)s"
        )
        url = result.download_url
        metadata = await _run_in_loop(
            self.youtube_dl.extract_info, {"url": url, "download": True}
        )
        logger.info("Finished downloading")

        downloaded = metadata["requested_downloads"][0]

        logger.debug("Creating download object")
        return Download.from_parent(
            parent=result,
            filename=Path(downloaded["filepath"]),
            bitrate=downloaded["abr"],
            audio_codec=AudioCodecs(downloaded["acodec"]),
        )


def instance():
    return YouTubeMusicAudioProvider
