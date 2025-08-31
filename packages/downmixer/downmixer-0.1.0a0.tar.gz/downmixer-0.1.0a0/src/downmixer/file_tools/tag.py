from __future__ import annotations

import logging
from typing import Any, Optional
from urllib.request import urlopen

import mutagen

# noinspection PyProtectedMember
from mutagen.id3 import APIC, USLT, ID3

from downmixer.providers import Download

logger = logging.getLogger("downmixer").getChild(__name__)


def tag_download(download: Download):
    """Tag the Download with metadata from its `song` attribute, overriding existing metadata.

    Args:
        download (Download): Downloaded file to be tagged with song data.
    """
    logger.info(f"Tagging file {download.filename}")
    _save_easy_tag(download)

    has_cover = (
        download.song.album.cover is not None and len(download.song.album.cover) != 0
    )
    if download.song.lyrics or has_cover:
        _save_advanced_tag(download, has_cover)


def _save_easy_tag(download: Download):
    easy_id3 = mutagen.File(download.filename, easy=True)

    logger.debug("Deleting old tag information")
    easy_id3.delete()

    logger.debug(f"Filling with info from attached song '{download.song.title}'")
    easy_id3["title"] = download.song.name
    easy_id3["titlesort"] = download.song.name
    easy_id3["artist"] = download.song.all_artists
    easy_id3["isrc"] = _return_if_valid(download.song.isrc)
    easy_id3["album"] = _return_if_valid(download.song.album.name)
    easy_id3["date"] = _return_if_valid(download.song.date)
    easy_id3["originaldate"] = _return_if_valid(download.song.date)
    easy_id3["albumartist"] = _return_if_valid(download.song.album.artists)
    easy_id3["tracknumber"] = [
        _return_if_valid(download.song.track_number),
        _return_if_valid(download.song.album.track_count),
    ]
    # TODO: include all tags possible here, grab them from youtube/spotify if needed

    logger.info("Saving EasyID3 data to file")
    easy_id3.save()


def _save_advanced_tag(download: Download, has_cover):
    id3 = ID3(download.filename)
    if download.song.lyrics:
        logger.debug("Adding lyrics")
        id3["USLT::'eng'"] = USLT(
            encoding=3, lang="eng", desc="Unsynced Lyrics", text=download.song.lyrics
        )
    if has_cover:
        url = download.song.album.cover
        logger.debug(f"Downloading cover image from URL {url}")

        with urlopen(url) as raw_image:
            id3["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=raw_image.read(),
            )
    logger.info("Saving ID3 data to file")
    id3.save()


def _return_if_valid(value: Any | None) -> Optional[Any]:
    if value is None:
        return ""
    else:
        return value
