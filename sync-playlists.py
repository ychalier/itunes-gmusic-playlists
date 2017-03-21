import getpass
import sys
import gmusicapi
import pyItunes


def print_gplaylists(playlists):
    for playlist in playlists:
        print(playlist["name"])


def google_login(client):
    print("Google sign in:")
    sys.stdout.flush()
    username = input("login> ")
    password = getpass.getpass(prompt="password> ")
    logged_in = client.login(username, password, gmusicapi.Mobileclient.FROM_MAC_ADDRESS)
    if logged_in:
        print("Successfully logged in.")
    else:
        print("Could not log in.")
        exit(0)


def get_google_library(client):
    google_login(client)
    print("Retrieving Google library...", end="")
    sys.stdout.flush()
    library = client.get_all_songs()
    playlists = client.get_all_playlists()
    print("\rGoogle library loaded: " + str(len(playlists)) + " playlists found.")
    return library, playlists


def get_itunes_library():
    print("Retrieving iTunes library...", end="")
    sys.stdout.flush()
    library = pyItunes.Library("C:/Users/Yohan/Music/iTunes/iTunes Music Library.xml")
    playlists = library.getPlaylistNames()[6:]
    print("\riTunes library loaded: " + str(len(playlists)) + " playlists found.")
    return library, playlists


gClient = gmusicapi.Mobileclient()
gLibray, gPlaylist = get_google_library(gClient)
iLibrary, iPlaylists = get_itunes_library()

while True:
    cmd = input("> ")
    if cmd == "exit":
        break

gClient.logout()
