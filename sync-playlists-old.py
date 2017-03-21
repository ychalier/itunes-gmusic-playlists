# coding: utf8

import tkinter
import tkinter.messagebox as tkMessagebox
import tkinter.scrolledtext as tkScrolledtext

import os

from gmusicapi import Mobileclient
from pyItunes import Library

verbosity = True

class API:

    api = None
    googleLibrary = None
    googlePlaylists = None
    itunesLibrary = None
    itunesPlaylists = None
    window = None

    def __init__(self):
        self.api = Mobileclient()

    def login(self,user,password):
        self.window.writeLog("Logging in...")
        logged_in = self.api.login(user, password, Mobileclient.FROM_MAC_ADDRESS)
        if verbosity:
            if logged_in:
                self.window.writeLog("Successfully logged in!")
            else:
                self.window.writeLog("Error: can't log in.")
        return logged_in

    def logout(self):
        self.api.logout()

    def getGoogleLib(self):
        self.window.writeLog("Fetching Google library...")
        self.googleLibrary = self.api.get_all_songs()
        self.googlePlaylists = self.api.get_all_playlists()
        self.window.writeLog("Google library successfully loaded.")

    def getGooglePlaylists(self):
        temp = [playlist["name"] for playlist in self.googlePlaylists]
        temp.sort()
        return temp

    def getItunesLib(self):
        self.window.writeLog("Fetching iTunes library...")
        self.itunesLibrary = Library("C:/Users/Yohan/Music/iTunes/iTunes Music Library.xml")
        self.itunesPlaylists = self.itunesLibrary.getPlaylistNames()
        self.window.writeLog("iTunes library successfully loaded.")
        self.itunesPlaylists.sort()
        uselessLists = ['Bibliothèque', 'Musique', 'Films', 'Séries TV', 'iTunes\xa0U', 'Livres']
        for l in uselessLists:
            self.itunesPlaylists.remove(l)

    def getItunesPlaylists(self):
        return self.itunesPlaylists[:]

    def isANewPlaylist(self, playlistName):
        for playlist in self.googlePlaylists:
            if playlist["name"] == playlistName:
                return False, playlist["id"]
        return True, None

    def addPlaylist(self,playlistName):
        self.window.writeLog("Adding playlist '" + playlistName + "'...",end="")
        bool, pid = self.isANewPlaylist(playlistName)
        if bool:
            id = self.api.create_playlist(playlistName)
        else:
            self.api.delete_playlist(pid)
            id = self.api.create_playlist(playlistName)

        number = 0
        length = len(self.itunesLibrary.getPlaylist(playlistName).tracks)
        for Isong in self.itunesLibrary.getPlaylist(playlistName).tracks:
            number += 1
            for Gsong in self.googleLibrary:
                if Gsong["title"] == Isong.name and Gsong["artist"] == Isong.artist and Gsong["album"] == Isong.album:
                    self.window.writeLog("Adding playlist '" + playlistName + "'..."+str((number*100)//length)+"%", end="",rewrite=True)
                    self.api.add_songs_to_playlist(id, Gsong["id"])
                    break
        self.window.writeLog("Adding playlist '" + playlistName + "'. Done.",rewrite=True)
        return id

    def deleteGooglePlaylist(self,playlistName):
        self.window.writeLog("Deleting playlist '" + playlistName +"'...",end="")
        bool, pid = self.isANewPlaylist(playlistName)
        if bool:
            self.window.writeLog("Error: playlist '"+playlistName+"' not found.",rewrite=True)
            return False
        else:
            self.api.delete_playlist(pid)
            self.window.writeLog("Deleting playlist '" + playlistName +"'. Done.",rewrite=True)
            return True

class MasterWindow(tkinter.Tk):
    api = None
    loginWindow = None

    def __init__(self,api):
        tkinter.Tk.__init__(self)

        self.api = api
        self.api.window = self

        self.wm_title("Google Music Playlists Manager")

        self.buttonLogin = tkinter.Button(self,text="Login",width=15,command=self.login)
        self.labelLogin = tkinter.Label(self, text="Not logged in.")

        self.buttonGoogleLib = tkinter.Button(self,text="Get Google Lib",width=15,command=self.getGoogleLib)
        self.labelGoogleLib = tkinter.Label(self, text="Not loaded.")

        self.buttonItunesLib = tkinter.Button(self,text="Get iTunes Lib",width=15,command=self.getItunesLib)
        self.labelItunesLib = tkinter.Label(self, text="Not loaded.")

        self.log = tkScrolledtext.ScrolledText(self,width=65)

        self.selectorGooglePlaylists = PlaylistSelector(self,"Google playlists")
        self.selectorItunesPlaylists = PlaylistSelector(self,"iTunes playlists")

        self.buttonDeleteGooglePlaylists = tkinter.Button(self,text="Delete selected playlists",width=40,command=self.deleteGooglePlaylists)
        self.buttonImportItunesPlaylists = tkinter.Button(self,text="Import selected playlists",width=40,command=self.importItunesPlaylists)

        self.buttonLogin.grid(row=1, column=2)
        self.labelLogin.grid(row=1, column=3)
        self.buttonGoogleLib.grid(row=2, column=2)
        self.labelGoogleLib.grid(row=2, column=3)
        self.buttonItunesLib.grid(row=3, column=2)
        self.labelItunesLib.grid(row=3, column=3)
        self.buttonDeleteGooglePlaylists.grid(row=4, column=2, columnspan=2)
        self.buttonImportItunesPlaylists.grid(row=5, column=2, columnspan=2)
        self.log.grid(row=6, column=2,columnspan=2)
        self.selectorGooglePlaylists.grid(row=1,column=1,rowspan=6)
        self.selectorItunesPlaylists.grid(row=1,column=4,rowspan=6)

    def login(self):
        self.loginWindow = LoginWindow(self,self.api)

    def loginSuccessful(self):
        self.labelLogin.config(text="Logged in.")
        self.loginWindow.destroy()

    def loginFailed(self):
        self.loginWindow.destroy()

    def getGoogleLib(self):
        self.api.getGoogleLib()
        self.labelGoogleLib.config(text="Loaded.")

        self.selectorGooglePlaylists.clear()
        for playlist in self.api.getGooglePlaylists():
            self.selectorGooglePlaylists.addPlaylist(playlist)
        self.selectorGooglePlaylists.update()

    def getItunesLib(self):
        self.api.getItunesLib()
        self.labelItunesLib.config(text="Loaded.")

        self.selectorItunesPlaylists.clear()
        for playlist in self.api.getItunesPlaylists():
            self.selectorItunesPlaylists.addPlaylist(playlist)
        self.selectorItunesPlaylists.update()

    def deleteGooglePlaylists(self):
        for playlist in self.selectorGooglePlaylists.getSelectedPlaylists():
            self.api.deleteGooglePlaylist(playlist)
        self.getGoogleLib()

    def importItunesPlaylists(self):
        for playlist in self.selectorItunesPlaylists.getSelectedPlaylists():
            self.api.addPlaylist(playlist)
        self.selectorItunesPlaylists.unselectAll()
        self.getGoogleLib()

    def writeLog(self,text,end="\n",rewrite=False):
        if rewrite:
            index = self.log.index("insert")
            newIndex = ""
            i=0
            while index[i] != ".":
                newIndex += index[i]
                i+=1
            newIndex = newIndex+".0"
            self.log.delete(newIndex,"end")
            self.log.insert(newIndex,"\n"+text+end)
        else:
            self.log.insert("end",text+end)
        self.log.see("end")
        self.update_idletasks()

class PlaylistSelector(tkinter.LabelFrame):

    def __init__(self,master,title="",playlists=[]):
        tkinter.LabelFrame.__init__(self,master,text=title,padx=5,pady=5)

        self.playlists = playlists
        self.selectedPlaylists = []

        self.listPlaylists = tkinter.Listbox(self,height=40,width=30,selectmode=tkinter.EXTENDED)
        self.listSelectedPlaylists = tkinter.Listbox(self,height=40,width=30,selectmode=tkinter.EXTENDED)

        self.buttonSelect = tkinter.Button(self, text=">", command=self.select,width=5)
        self.buttonUnselect = tkinter.Button(self, text="<", command=self.unselect,width=5)

        self.buttonSelectAll = tkinter.Button(self, text=">>>", command=self.selectAll,width=5)
        self.buttonUnselectAll = tkinter.Button(self, text="<<<", command=self.unselectAll,width=5)

        self.listPlaylists.grid(row=1,column=1,rowspan=4)
        self.listSelectedPlaylists.grid(row=1,column=3,rowspan=4)
        self.buttonSelect.grid(row=1,column=2)
        self.buttonUnselect.grid(row=2,column=2)
        self.buttonSelectAll.grid(row=3, column=2)
        self.buttonUnselectAll.grid(row=4, column=2)

    def addPlaylist(self,playlist):
        self.playlists.append(playlist)

    def getSelectedPlaylists(self):
        return self.selectedPlaylists[:]

    def select(self):
        for index in self.listPlaylists.curselection():
            self.selectPlaylist(self.listPlaylists.get(index))
        self.update()

    def selectPlaylist(self,playlist):
        self.selectedPlaylists.append(playlist)
        self.playlists.remove(playlist)

    def unselect(self):
        for index in self.listSelectedPlaylists.curselection():
            self.unselectPlaylist(self.listSelectedPlaylists.get(index))
        self.update()

    def unselectPlaylist(self,playlist):
        self.playlists.append(playlist)
        self.selectedPlaylists.remove(playlist)

    def selectAll(self):
        while len(self.playlists)>0:
            self.selectPlaylist(self.playlists[0])
        self.update()

    def unselectAll(self):
        while len(self.selectedPlaylists)>0:
            self.unselectPlaylist(self.selectedPlaylists[0])
        self.update()

    def clear(self):
        self.playlists=[]
        self.selectedPlaylists=[]
        self.update()

    def clearSelection(self):
        self.selectedPlaylists=[]
        self.update()

    def update(self):
        displayedPlaylists = list(self.listPlaylists.get(0,tkinter.END))
        n=0
        for i,p in enumerate(displayedPlaylists):
            if not p in self.playlists:
                self.listPlaylists.delete(i-n)
                n+=1
        for p in self.playlists:
            if not p in displayedPlaylists:
                self.listPlaylists.insert(tkinter.END,p)

        displayedSelectedPlaylists = list(self.listSelectedPlaylists.get(0,tkinter.END))
        n=0
        for i, p in enumerate(displayedSelectedPlaylists):
            if not p in self.selectedPlaylists:
                self.listSelectedPlaylists.delete(i-n)
                n+=1
        for p in self.selectedPlaylists:
            if not p in displayedSelectedPlaylists:
                self.listSelectedPlaylists.insert(tkinter.END,p)

class LoginWindow(tkinter.Toplevel):

    def __init__(self,master,api):
        tkinter.Toplevel.__init__(self,master)

        self.wm_title("Login")

        try:
            path = os.environ['APPDATA'] + "\Playlist Manager\config.cfg"
            file = open(path.replace("\\", "/"), "r")
            lines = file.readlines()
            defaultUser=lines[0].replace("\n","")
            defaultPass=lines[1]
            file.close()
        except Exception as err:
            defaultUser=""
            defaultPass=""

        self.labelUsername = tkinter.Label(self,text="User:")
        self.labelUsername.grid(row=1,column=1)

        self.entryUsername = tkinter.Entry(self,width=30)
        self.entryUsername.grid(row=1,column=2)
        self.entryUsername.insert("end",defaultUser)

        self.labelPassword = tkinter.Label(self,text="Password:")
        self.labelPassword.grid(row=2,column=1)

        self.entryPassword = tkinter.Entry(self,width=30,text=defaultPass,show="*")
        self.entryPassword.grid(row=2,column=2)
        self.entryPassword.insert("end",defaultPass)

        self.buttonLogin = tkinter.Button(self,text="Login",command=self.login)
        self.buttonLogin.grid(row=3,column=1,columnspan=2)

        self.api = api

        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(root.attributes, '-topmost', False)
    def login(self):
        if self.api.login(self.entryUsername.get(),self.entryPassword.get()):
            #tkMessagebox.showinfo("Login", "Successfully logged in.")
            path=os.environ['APPDATA'] + "\Playlist Manager\config.cfg"
            file = open(path.replace("\\","/"), "w")
            file.write(self.entryUsername.get()+"\n")
            file.write(self.entryPassword.get())
            file.close()
            self.master.loginSuccessful()
        else:
            tkMessagebox.showerror("Login","Failed login.")

api = API()
root = MasterWindow(api)
root.mainloop()


