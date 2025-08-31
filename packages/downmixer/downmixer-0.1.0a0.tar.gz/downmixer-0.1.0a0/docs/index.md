# Getting started

## Commands

Downmixer is a library first. The `download` command specified below is purely for testing and convenience.

* `downmixer download [spotify-id]` - Download a Spotify song to the current directory.

## Overview

Downmixer is divided into a few modules that cover the basic process of gathering song/playlist information, downloading
individual songs, converting them and tagging them appropriately. These modules are:

- `file_tools` - converting and tagging
- `matching` - matching results from an audio provider to song info from an info provider
- `providers` - info, audio and lyrics providers (explained in the [providers page](providers/index.md))
- `processing` - sample/convenience class to download one or more files - used by the [command line tool](cli.md)

Except for `processing`, these packages have no connection with each other except for the use of common data classes -
they are made to be implemented by your application in whichever way is fits it best. The `processing` module gives an
example of a spotDL-like downloader.

### File Tools

This package uses [FFmpeg](https://ffmpeg.org/) and [Mutagen](https://github.com/quodlibet/mutagen) to convert and tag
downloaded files respectively.
