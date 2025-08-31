"""Data classes to hold standardized metadata about songs, artists, and albums."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any

from slugify import slugify


class AlbumType(Enum):
    ALBUM = 1
    SINGLE = 2
    COMPILATION = 3


class BaseLibraryItem:
    """Base class for library items containing standard methods to easily create class instances from the Spotify
    API. Child classes of this class must be
    [implemented in all info providers.](../providers/library.py file.md)
    """

    @classmethod
    def from_provider(cls, data: Any, extra_data: dict = None):
        """Create an instance of this class from data coming from a provider's API.

        Args:
            data (Any): Data from the provider's API.
            extra_data (dict, optional): Extra data from provider's API to be used to make instances of this class.

        Returns:
             An instance of this class.
        """
        pass

    @classmethod
    def from_provider_list(cls, data: list[Any], extra_data: dict = None) -> list:
        """Creates a list of instances of this class from a list of objects with data coming from a provider's API.

        Args:
            data (list[Any]): List of objects with data from the provider's API.
            extra_data (dict, optional): Extra data from provider's API to be used to make instances of this class.

        Returns:
            A list with instances of this class.
        """
        return [cls.from_provider(x) for x in data]


@dataclass
class Artist(BaseLibraryItem):
    """Holds info about an artist."""

    name: str
    images: Optional[list[str]] = None
    genres: Optional[list[str]] = None
    id: Optional[str] = None
    url: Optional[str] = None

    def slug(self) -> "Artist":
        """Returns self with sluggified text attributes."""
        return Artist(
            name=slugify(self.name),
            images=self.images,
            genres=[slugify(x) for x in self.genres] if self.genres else None,
            id=self.id,
            url=self.url,
        )


@dataclass
class Album(BaseLibraryItem):
    """Holds info about an album. `cover` should be a string containing a valid URL."""

    name: str
    available_markets: Optional[list[str]] = None
    artists: Optional[list[Artist]] = None
    date: Optional[str] = None
    track_count: Optional[int] = None
    cover: Optional[str] = None
    id: Optional[str] = None
    url: Optional[str] = None

    def slug(self) -> "Album":
        """Returns self with sluggified text attributes."""
        return Album(
            name=slugify(self.name),
            available_markets=self.available_markets,
            artists=[x.slug for x in self.artists] if self.artists else None,
            date=self.date,
            track_count=self.track_count,
            cover=self.cover,
            id=self.id,
            url=self.url,
        )


@dataclass
class Song(BaseLibraryItem):
    """Holds info about a song."""

    name: str
    artists: list[Artist]
    duration: float = 0  # in seconds
    album: Optional[Album] = None
    available_markets: Optional[list[str]] = None
    date: Optional[str] = None
    track_number: Optional[int] = None
    isrc: Optional[str] = None
    lyrics: Optional[str] = None
    id: Optional[str] = None
    url: Optional[str] = None
    cover: Optional[str] = None

    def slug(self) -> "Song":
        """Returns self with sluggified text attributes."""
        return Song(
            name=slugify(self.name),
            artists=[x.slug() for x in self.artists],
            album=self.album.slug() if self.album else None,
            available_markets=self.available_markets,
            date=self.date,
            duration=self.duration,
            track_number=self.track_number,
            isrc=self.isrc,
            id=self.id,
            url=self.url,
            lyrics=slugify(self.lyrics) if self.lyrics else None,
        )

    @property
    def title(self) -> str:
        """str: Title of the song, including artist, in the format '[primary artist] - [song name]'."""
        return self.artists[0].name + " - " + self.name

    @property
    def full_title(self) -> str:
        """str: Full title of the song, including all artists, in the format [artist 1, artist 2, ...] - [song name]."""
        return (", ".join(x.name for x in self.artists)) + " - " + self.name

    @property
    def all_artists(self) -> str:
        """str: All artists' names, separated by a comma."""
        return ", ".join(x.name for x in self.artists)


@dataclass
class Playlist(BaseLibraryItem):
    name: str
    description: Optional[str] = None
    tracks: Optional[list[Song]] = None
    images: Optional[list[dict]] = None
    id: Optional[str] = None
    url: Optional[str] = None
