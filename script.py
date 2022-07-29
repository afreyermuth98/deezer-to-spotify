




import requests
import argparse
import sys

def get_titles_and_artists(playlist_id):
    titles_and_artists = []
    r = requests.get("https://api.deezer.com/playlist/" + playlist_id + "/tracks")
    if (r.status_code != 200):
        exit(r.response)

    tracks = r.json()['data']
    for track in tracks:
        titles_and_artists.append({
            'title': track['title'],
            'artist': track['artist']['name']
        })
    while "next" in r.json():
        r = requests.get(r.json()["next"])
        if (r.status_code != 200):
            exit(r.response)
        tracks = r.json()['data']
        for track in tracks:
            titles_and_artists.append({
                'title': track['title'],
                'artist': track['artist']['name']
            })

    return titles_and_artists

def get_score_of_artist(deezer_artist, spotify_artists):
    max_score = 0

    for spotify_artist in spotify_artists:
        # Handle differences between deezer & spotify
        if "œ" in spotify_artist:
            spotify_artist = spotify_artist.replace("œ", "oe")
        if "& the" in spotify_artist and "and the" in deezer_artist:
            spotify_artist = spotify_artist.replace("&", "and")
        if deezer_artist == "m":
            deezer_artist = "-m-"
        if deezer_artist == "charlelie couture":
            deezer_artist = "charl elie couture"
        
        min_len = min(len(deezer_artist), len(spotify_artist))
        matching_letters = 0
        for index, letter in enumerate(deezer_artist):
            if index < len(spotify_artist) and letter == spotify_artist[index]:
                matching_letters += 1
        average = matching_letters/min_len
        if average > max_score:
            max_score = average
    return max_score

def get_spotify_uri_from_title_and_artist(title_name, artist, headers):
    
    request_url = "https://api.spotify.com/v1/search?q=" + title_name + " " + artist.split(" ")[0] + "&type=track"
    r = requests.get(request_url, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)
        exit()
    lower_artist = artist.lower()
    items = r.json()['tracks']['items']
    for item in items:
        artists = [artist['name'].lower() for artist in item['artists']]
        artist_score = get_score_of_artist(lower_artist, artists)
        if lower_artist in artists or artist_score > 0.5:
            return item['uri']
        
    return None

def upload_to_spotify_playlist(playlist_id, titles_and_artists, headers):

    unfound_tracks = []
    for title_and_artist in titles_and_artists:
        title = title_and_artist['title']
        artist = title_and_artist['artist']
        track_uri = get_spotify_uri_from_title_and_artist(title, artist, headers)
        

        if track_uri == None:
            unfound_tracks.append(title + " from " + artist)
            continue

        request_url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks?uris=" + track_uri

        r = requests.post(request_url, headers=headers)
        if r.status_code != 201:
            print(r.status_code)
            print(r.text)
        else:
            print("Successfully uploaded ", title, " from ", artist)

    if len(unfound_tracks) > 0:
        print("Some tracks could not have been upload : ")
        for uf in unfound_tracks:
            print(uf)


def parse_args(args: list):
    """
    Create and Parse CLI

    :param args: args from command line
    :return: the files extracted from cli and the method
    """
    SCRIPT_DESC = "Python script to move deezer playlist to spotify"

    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=SCRIPT_DESC,
    )

    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument(
        "-d",
        "--deezer_playlist",
        dest="deezer_playlist",
        action="store",
        type=str,
        required=True,
        help="The ID of the deezer playlist to migrate",
    )
    requiredNamed.add_argument(
        "-s",
        "--spotify_playlist",
        dest="spotify_playlist",
        action="store",
        type=str,
        required=True,
        help="The ID of the spotify playlist to upload tracks",
    )
    requiredNamed.add_argument(
        "-t",
        "--token",
        dest="token",
        action="store",
        type=str,
        required=True,
        help="Spotify Token",
    )

    parsed_args = parser.parse_args(args)
    return parsed_args.deezer_playlist, parsed_args.spotify_playlist, parsed_args.token



if __name__ == "__main__":
    deezer_playlist_id, spotify_playlist_id, bearer_token = parse_args(sys.argv[1:])

    headers = {}
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + bearer_token

    # Get titles and artists
    titles_and_artists = get_titles_and_artists(deezer_playlist_id)

    # Uploading to spotify
    upload_to_spotify_playlist(spotify_playlist_id, titles_and_artists, headers)
    