# `library.py` file

Every **info provider** must include a `library.py` file which includes overrides for each of the `BaseLibraryItem`
child classes:

- [`Artist`](../reference/library.md#downmixer.library.Artist)
- [`Album`](../reference/library.md#downmixer.library.Album)
- [`Song`](../reference/library.md#downmixer.library.Song)
- [`Playlist`](../reference/library.md#downmixer.library.Playlist)

The child classes must override
the [`from_provider`](../reference/library.md#downmixer.library.BaseLibraryItem.from_provider) method, since that method
needs to adapt depending on the API of the info provider. Sometimes it might be necessary to override
the [`from_provider_list`](../reference/library.md#downmixer.library.BaseLibraryItem.from_provider_list) method as well.