---
search:
  boost: 2
---

# Providers

Since Downmixer is made to be as platform-agnostic as possible, it works with a **provider** system. As they need to
communicate with Downmixer, they are expected to follow a certain structure - however, outside of that, they are not
limited on their capabilities.

Providers MUST be packages which have classes derived from a base provider class in their `__init__.py` files.
Additionally, info providers need a [`library.py` file](library.py%20file.md) with classes overriding ALL library classes
deriving from `BaseLibraryItem` (`Artist`, `Album`, `Song`, and`Playlist`). These base classes provide async search and
download methods that must be overridden.

----

## Info Providers

#### Bundled
- `SpotifyInfoProvider`

Where the songs will be searched for a query and (preferably, but not enforced by Downmixer) where the information for
the final file's ID3 tags will be sourced from.

## Audio Providers

#### Bundled
- `YouTubeMusicAudioProvider`

Where the audio file will be downloaded from.

## Lyrics Providers

#### Bundled
- `AZLyricsProvider`

Where lyrics are searched for each song, and if found added to the song's ID3 tag.
