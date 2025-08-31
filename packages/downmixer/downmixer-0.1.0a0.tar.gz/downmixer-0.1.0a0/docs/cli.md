# CLI

Downmixer's purpose is not to be an end-user command line tool like spotDL, youtubeDL and others. It's a Python library
to automate syncing of music from any music library, audio, and lyrics platform.

That being said, Downmixer *does* provide a simple command line interface for convenience, testing and simple usage.

It uses the default [`BasicProcessor`](reference/processing/index.md#downmixer.processing.BasicProcessor) class to
search, download and convert a song, playlist or album. It uses the bundled `SpotifyInfoProvider`, meaning the `id`
value must be a valid Spotify track, album or playlist ID.

## Spotify API Authentication
The default `SpotifyInfoProvider` will use OAuth to authenticate its API requests. For that, you'll need to set up a Spotify developer account and provide the information as environment variables. The information needed is:

| Env. Variable Name    | Value                        |
|-----------------------|------------------------------|
| SPOTIPY_CLIENT_ID     | <your client ID\>            |
| SPOTIPY_CLIENT_SECRET | <your client secret\>        |
| SPOTIPY_REDIRECT_URI  | <one of your redirect URIs\> |

On the first usage or when the token expires, the Spotipy library will open a webpage where you'll need to login, authorize the app and paste the URL you were redirected to.

## Usage

````shell
downmixer [OPTIONS] {COMMAND}

````

### Positional arguments

- `command`
    - Command to execute. Currently, the only option is `download`.
- `id`
    - A valid identifier for the info provider. By default, a valid **Spotify** ID, URI or URL for a track, album or playlist.

### Options

* `-h, --help`
  * Show the help message
* `-t THREADS, --threads THREADS`
  * Number of threads to use for parallel downloads.
* `-o OUTPUT, --output-folder OUTPUT`
  * Path to the folder in which the final processed files will be placed.
* `-ip PROVIDER, --info-provider PROVIDER`
  * Info provider extending BaseInfoProvider to use. Defaults to 'SpotifyInfoProvider'.
* `-ip-settings SETTINGS, --info-provider-settings SETTINGS`
  * Settings for the info provider as a JSON string. See documentation for available options for each provider.
* `-ap PROVIDER, --audio-provider PROVIDER`
  * Audio provider extending BaseAudioProvider to use. Defaults to 'YouTubeMusicAudioProvider'.
* `-ap-settings SETTINGS, --audio-provider-settings SETTINGS`
  * Settings for the audio provider as a JSON string. See documentation for available options for each provider.
* `-lp PROVIDER, --lyrics-provider PROVIDER`
  * Lyrics provider extending BaseLyricsProvider to use. Defaults to 'AZLyricsProvider'.
* `-lp-settings SETTINGS, --lyrics-provider-settings SETTINGS`
  * Settings for the lyrics provider as a JSON string. See documentation for available options for each provider.

