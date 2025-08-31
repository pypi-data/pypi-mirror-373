# Identifying media type from URL

We need to validate the URLs given to Downmixer's processor to not only check they are correct with the info provider chosen, but also determine what resource type it is.

For Downmixer, valid links should contain the type of resource and a Spotify ID. Therefore, it expects either a URI or URL.

Downmixer divides resources into 3 types:

 - Song
 - Artist
 - Playlist

Different platforms have different names (Songs are called Tracks by Spotify, Artists are called Channels on YT Music), but they usually have the same data and concept.

!!! note
    For our purposes, albums are considered playlists since they're a collection of songs as well.

## Spotify

|          | URI                                       | URL                                                | Downmixer Type |
|----------|-------------------------------------------|----------------------------------------------------|----------------|
| Track    | `spotify:track:3WkEKyrkEtbqN6mxZQi1dn`    | `open.spotify.com/track/3WkEKyrkEtbqN6mxZQi1dn`    | Song           |
| Album    | `spotify:album:1ERrUvG31thFCxdwWUoJrY`    | `open.spotify.com/album/1ERrUvG31thFCxdwWUoJrY`    | Playlist       |
| Artist   | `spotify:artist:1oPRcJUkloHaRLYx0olBLJ`   | `open.spotify.com/artist/1oPRcJUkloHaRLYx0olBLJ`   | Artist         |
| Playlist | `spotify:playlist:37i9dQZF1EpqK9TaAhVHZk` | `open.spotify.com/playlist/37i9dQZF1EpqK9TaAhVHZk` | Playlist       |


## YouTube Music

|          | URL                                                                           | Downmixer Type |
|----------|-------------------------------------------------------------------------------|----------------|
| Song     | `music.youtube.com/watch?v=xn4Wp0i-df0`                                       | Song           |
| Album    | `music.youtube.com/playlist?list=OLAK5uy_mfadi1aaUHZ8Vgw9g5iDSZvV3GrhJ7sBA`   | Playlist       |
| Artist   | `music.youtube.com/channel/UCuW8oZH4asLgvJ9FstClVzQ`                          | Artist         |
| Playlist | `music.youtube.com/playlist?list=RDCLAK5uy_lBNUteBRencHzKelu5iDHwLF6mYqjL-JU` | Playlist       |
