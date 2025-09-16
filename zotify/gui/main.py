"""
ZSpotifyGUI
It's like youtube-dl, but for Spotify.

(GUI made by PacketSurf - github.com/PacketSurf)
(ZSpotify made by Deathmonger/Footsiefat - @doomslayer117:matrix.org | github.com/Footsiefat)
"""

import sys
import logging
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTreeWidgetItem, QLineEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog
from pathlib import Path
from .main_window import Ui_MainWindow
from .login_dialog import Ui_LoginDialog
from .worker import Worker
import qdarktheme
from .view import set_button_icon, set_label_image
import webbrowser
from librespot.core import Session
from zotify.config import Zotify
from zotify import api
from zotify.track import download_track
from zotify.album import download_album
from zotify.playlist import download_playlist
from zotify.gui.settings_dialog import SettingsDialog

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ZSpotify")
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    win = Window()
    win.show()
    sys.exit(app.exec())


class Window(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)
        self.init_info_labels()
        set_label_image(self.coverArtLabel, "Resources/cover_default.jpg")
        self.logged_in = False
        self.selected_item = None
        self.results = {}
        self.reconnecting = False
        self.load_config()
        self.loginBtn.clicked.connect(self.on_click_login)
        self.searchBtn.clicked.connect(self.on_search_clicked)
        self.searchInput.returnPressed.connect(self.on_search_clicked)
        self.downloadBtn.clicked.connect(self.on_download_clicked)
        self.settingsBtn.clicked.connect(self.on_settings_clicked)
        self.libraryTabs.currentChanged.connect(self.on_library_tab_changed)

    def on_library_tab_changed(self, index):
        if index == 0: # Downloaded Songs Tab
            self.load_downloaded_songs()
        elif index == 1: # Liked Songs Tab
            self.load_liked_songs()

    def load_downloaded_songs(self):
        self.downloadedTree.clear()
        root_path = Zotify.CONFIG.get_root_path()
        worker = Worker(api.get_local_songs, root_path)
        worker.signals.result.connect(self.display_downloaded_songs)
        worker.signals.error.connect(self.search_error) # Can reuse search_error for now
        QThreadPool.globalInstance().start(worker)

    def display_downloaded_songs(self, results):
        for song in results:
            artists = ", ".join(song['artists'])
            item = QTreeWidgetItem([song['name'], artists, song['album']])
            item.setData(0, QtCore.Qt.UserRole, song)
            self.downloadedTree.addTopLevelItem(item)

    def load_liked_songs(self):
        self.likedTree.clear()
        worker = Worker(api.get_liked_songs)
        worker.signals.result.connect(self.display_liked_songs)
        worker.signals.error.connect(self.search_error) # Can reuse search_error for now
        QThreadPool.globalInstance().start(worker)

    def display_liked_songs(self, results):
        for track_item in results:
            track = track_item['track']
            artists = ", ".join([artist['name'] for artist in track['artists']])
            item = QTreeWidgetItem([track['name'], artists, track['album']['name']])
            item.setData(0, QtCore.Qt.UserRole, track)
            self.likedTree.addTopLevelItem(item)

    def on_settings_clicked(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

    def load_config(self):
        """ Loads the config file and sets up the Zotify config object """
        from argparse import Namespace
        args = Namespace(
            config_location=None,
            debug=False,
            update_config=False,
            no_splash=True,
            username=None,
            token=None
        )
        for key in Zotify.CONFIG.Values:
            setattr(args, key.lower(), None)
        Zotify.CONFIG.load(args)

    def show(self):
        """ Show the main window and trigger login flow if necessary """
        super().show()
        creds = Zotify.CONFIG.get_credentials_location()
        if creds and Path(creds).exists():
            try:
                Zotify.SESSION = Session.Builder().stored_file(creds).create()
                self.on_login_finished(True)
                return
            except Exception as e:
                print(f"Failed to load credentials: {e}")

        self.open_login_dialog()

    def open_login_dialog(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            self.on_login_finished(True)
        else:
            # Handle user closing the dialog without logging in
            print("Login cancelled by user.")
            # QCoreApplication.quit() # Or handle it more gracefully

    def on_login_finished(self, success):
        if success:
            self.logged_in = True
            self.loginBtn.setText("Logout")
            self.load_downloaded_songs()
            # In a future step, I will add a call to get user info and display it
        else:
            self.logged_in = False
            self.loginBtn.setText("Login")

    def on_click_login(self):
        if self.logged_in:
            # Logout
            creds = Zotify.CONFIG.get_credentials_location()
            if creds and Path(creds).exists():
                Path(creds).unlink()
            Zotify.SESSION = None
            self.on_login_finished(False)
        else:
            # Login
            self.open_login_dialog()


    def on_search_clicked(self):
        query = self.searchInput.text()
        if not query:
            return

        limit = int(self.resultAmountCombo.currentText())

        # For now, search all types. Later, this can be refined.
        search_type = 'track,album,artist,playlist'

        worker = Worker(api.search, query, search_type, limit)
        worker.signals.result.connect(self.display_search_results)
        worker.signals.error.connect(self.search_error)
        QThreadPool.globalInstance().start(worker)

    def display_search_results(self, results):
        self.songsTree.clear()
        self.albumsTree.clear()
        self.artistsTree.clear()
        self.playlistsTree.clear()

        if 'tracks' in results and results['tracks']['items']:
            for i, track in enumerate(results['tracks']['items']):
                artists = ", ".join([artist['name'] for artist in track['artists']])
                duration_ms = int(track['duration_ms'])
                duration_sec = duration_ms // 1000
                duration_min = duration_sec // 60
                duration_sec %= 60
                duration = f"{duration_min}:{duration_sec:02}"
                item = QTreeWidgetItem([str(i+1), track['name'], artists, track['album']['name'], duration, track['album']['release_date']])
                item.setData(0, QtCore.Qt.UserRole, track) # Store track data in the item
                self.songsTree.addTopLevelItem(item)

        if 'albums' in results and results['albums']['items']:
            for i, album in enumerate(results['albums']['items']):
                artists = ", ".join([artist['name'] for artist in album['artists']])
                item = QTreeWidgetItem([str(i+1), album['name'], artists, str(album['total_tracks']), album['release_date']])
                item.setData(0, QtCore.Qt.UserRole, album) # Store album data in the item
                self.albumsTree.addTopLevelItem(item)

        if 'artists' in results and results['artists']['items']:
            for i, artist in enumerate(results['artists']['items']):
                item = QTreeWidgetItem([str(i+1), artist['name']])
                item.setData(0, QtCore.Qt.UserRole, artist) # Store artist data in the item
                self.artistsTree.addTopLevelItem(item)

        if 'playlists' in results and results['playlists']['items']:
            for i, playlist in enumerate(results['playlists']['items']):
                item = QTreeWidgetItem([str(i+1), playlist['name'], playlist['owner']['display_name'], str(playlist['tracks']['total'])])
                item.setData(0, QtCore.Qt.UserRole, playlist) # Store playlist data in the item
                self.playlistsTree.addTopLevelItem(item)

    def search_error(self, error):
        print("Search failed:", error)

    def on_download_clicked(self):
        active_tab_widget = self.musicTabs.currentWidget()
        if active_tab_widget.objectName() == 'resultLayout':
            tree_widget = self.searchTabs.currentWidget().findChild(QtWidgets.QTreeWidget)
        elif active_tab_widget.objectName() == 'libraryLayout':
            tree_widget = self.libraryTabs.currentWidget().findChild(QtWidgets.QTreeWidget)
        else: # queue or others
            return

        if not tree_widget:
            return

        selected_items = tree_widget.selectedItems()
        if not selected_items:
            return

        item_data = selected_items[0].data(0, QtCore.Qt.UserRole)
        if not item_data:
            return

        self.progressBar.setValue(0)

        # Determine type of download
        if 'type' in item_data:
            item_type = item_data['type']
            if item_type == 'track':
                worker = Worker(download_track, 'single', item_data['id'], None, [], update=self.update_progress_bar)
                QThreadPool.globalInstance().start(worker)
            elif item_type == 'album':
                worker = Worker(download_album, item_data['id'], [], update=self.update_progress_bar)
                QThreadPool.globalInstance().start(worker)
            elif item_type == 'playlist':
                worker = Worker(download_playlist, item_data, [], update=self.update_progress_bar)
                QThreadPool.globalInstance().start(worker)
            # Add artist download later

    def update_progress_bar(self, downloaded, total, percent):
        self.progressBar.setValue(percent)

    def init_info_labels(self):
        self.info_labels = [self.infoLabel1, self.infoLabel2, self.infoLabel3, self.infoLabel4, self.infoLabel5,
                            self.infoLabel6]
        self.info_headers = [self.infoHeader1, self.infoHeader2, self.infoHeader3, self.infoHeader4, self.infoHeader5,
                             self.infoHeader6]


class LoginDialog(QDialog, Ui_LoginDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)
        self.loginBtn.clicked.connect(self.send_login)
        self.cancelBtn.clicked.connect(self.reject)
        self.attempting_login = False

    def send_login(self):
        if self.attempting_login:
            return

        self.loginInfoLabel.setText("Check your browser to continue login...")
        self.attempting_login = True

        session_builder = Session.Builder()
        creds = Zotify.CONFIG.get_credentials_location()
        if creds:
            session_builder.conf.stored_credentials_file = str(creds)
        else:
            session_builder.conf.store_credentials = False
            session_builder.conf.stored_credentials_file = ""

        worker = Worker(Zotify.oauth_login, session_builder, webbrowser.open)
        worker.signals.result.connect(self.login_result)
        worker.signals.error.connect(self.login_error)
        QThreadPool.globalInstance().start(worker)

    def login_result(self, success):
        self.attempting_login = False
        self.accept()

    def login_error(self, error):
        self.attempting_login = False
        self.loginInfoLabel.setText("Login failed. Please try again.")
        print(error)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"CRITICAL ERROR: Main crashed. \nTraceback: \n{e}")
        logging.exception(f"CRITICAL ERROR: Main crashed. Error: {e}")
