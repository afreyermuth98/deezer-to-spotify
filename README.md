# deezer-to-spotify

`deezer-to-spotify` is a python script that will migrate a playlist from deezer to spotify

## Prerequisites
You need to have a spotify API token and a spotify playlist already created

## Usage

### Manual
```text
python3 -d <DEEZER_PLAYLIST_ID> -s <SPOTIFY_PLAYLIST_ID> -t <SPOTIFY_API_TOKEN>
```

### Docker
```text
docker run docker.io/anthonymmk/deezer-to-spotify -d <DEEZER_PLAYLIST_ID> -s <SPOTIFY_PLAYLIST_ID> -t <SPOTIFY_API_TOKEN>
```
