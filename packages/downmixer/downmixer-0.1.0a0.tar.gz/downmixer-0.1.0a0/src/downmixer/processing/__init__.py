"""Takes a playlist or song and processes it using audio and lyric providers."""

from __future__ import annotations

import asyncio
import logging
import shutil
from pathlib import Path
from typing import Type

from downmixer.file_tools import tag, utils
from downmixer.file_tools.convert import Converter
from downmixer.providers import (
    Download,
    BaseInfoProvider,
    BaseAudioProvider,
    BaseLyricsProvider,
)

logger = logging.getLogger("downmixer").getChild(__name__)


async def _convert_download(download: Download) -> Download:
    converter = Converter(download)
    return await converter.convert()


class BasicProcessor:
    def __init__(
        self,
        info_provider: BaseInfoProvider,
        audio_provider_class: Type[BaseAudioProvider],
        audio_provider_settings: str | None,
        lyrics_provider: BaseLyricsProvider,
        output_folder: Path,
        temp_folder: Path,
        threads: int = 3,
        max_retries: int = 10,
    ):
        """Basic processing class to search an ID and download it, using the providers passed on by the user. For
        playlist downloads, it uses an [`asyncio.Semaphore`](
        https://docs.python.org/3/library/asyncio-sync.html#semaphore) with a value of `threads` - so the number of
        concurrent downloads is equal to the `threads` value.

        Args:
            info_provider (BaseInfoProvider): Class instance to use when searching an ID.
            audio_provider_class (Type[BaseAudioProvider]): Class reference to use when downloading songs.
            audio_provider_settings (str, optional): JSON formatted settings for the BaseAudioProvider.
            lyrics_provider (BaseLyricsProvider): Class instance to use when downloading lyrics.
            output_folder (str): Folder path where the final file will be placed.
            temp_folder (str): Folder path where temporary files will be placed and removed from when processing
                is finished.
            threads (int): Amount of threads that will simultaneously process songs.
        """
        self.output_folder: Path = Path(output_folder).absolute()
        self.temp_folder = temp_folder

        self.info_provider = info_provider
        self.audio_provider_class = audio_provider_class
        self.audio_provider_settings = audio_provider_settings
        self.lyrics_provider = lyrics_provider

        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(threads)

    async def _get_lyrics(self, download: Download):
        # TODO: Test if lyrics are actually working
        lyrics_results = await self.lyrics_provider.search(download.song)
        if lyrics_results is not None:
            lyrics = await self.lyrics_provider.get_lyrics(lyrics_results[0])
            download.song.lyrics = lyrics

    async def pool_processing(self, song_id: str):
        async with self.semaphore:
            logger.debug(f"Processing song '{song_id}'")
            retries = 0
            while retries <= self.max_retries:
                try:
                    await self.process_song(song_id)
                    return
                except Exception as e:
                    # TODO: Pick out exceptions instead of catching all exceptions
                    logger.warning(
                        f"Error processing song '{song_id}', retrying ({self.max_retries - retries} left)",
                        exc_info=e,
                    )
                    retries += 1

            logger.error(f"Max retries exceeded for song '{song_id}'")

    async def process_playlist(self, playlist_id: str):
        """Searches and downloads all songs in a playlist using a queue with limited threads.

        Args:
            playlist_id (str): ID for the playlist to be downloaded."""
        songs = self.info_provider.get_all_playlist_songs(playlist_id)

        tasks = [self.pool_processing(s.id) for s in songs]
        await asyncio.gather(*tasks)

    async def process_song(self, song_id: str):
        """Searches and downloads a single song based on data provided by a `BaseInfoProvider`.

        Args:
            song_id (str): Valid ID of a single track.
        """
        song = self.info_provider.get_song(song_id)
        audio_provider = self.audio_provider_class(self.audio_provider_settings)

        result = await audio_provider.search(song)
        if result is None:
            logger.warning("Song not found", extra={"songinfo": song.__dict__})
            return
        downloaded = await audio_provider.download(result[0], self.temp_folder)
        converted = await _convert_download(downloaded)

        await self._get_lyrics(converted)
        tag.tag_download(converted)

        new_name = (
            utils.make_sane_filename(converted.song.title) + converted.filename.suffix
        )

        self.output_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(
            f"Moving file from '{converted.filename}' to '{self.output_folder}'"
        )
        shutil.move(converted.filename, self.output_folder.joinpath(new_name))
