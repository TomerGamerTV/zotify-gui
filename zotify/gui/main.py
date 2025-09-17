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
        self.downloadBtn.clicked.connect(self.on_download_selected_clicked)
        self.settingsBtn.clicked.connect(self.on_settings_clicked)
        self.libraryTabs.currentChanged.connect(self.on_library_tab_changed)
        self.progressBar.hide()

        # Add loading indicator for liked songs
        self.loadingLikedLabel = QtWidgets.QLabel("Loading, please wait...")
        self.loadingLikedLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.likedTab.layout().addWidget(self.loadingLikedLabel)
        self.loadingLikedLabel.hide()

        # Hide info view by default
        self.infoView.hide()

        # Connect item selection changes to show info view
        self.downloadedTree.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.likedTree.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.songsTree.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.albumsTree.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.artistsTree.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.playlistsTree.itemSelectionChanged.connect(self.on_item_selection_changed)

        # Liked songs cache
        self.liked_songs_cache = None
        self.refresh_liked_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_liked_btn.clicked.connect(self.on_refresh_liked_clicked)
        self.likedTab.layout().addWidget(self.refresh_liked_btn)

    def on_refresh_liked_clicked(self):
        self.liked_songs_cache = None
        self.load_liked_songs()

    def get_current_tree_widget(self):
        # Determine the currently visible tree widget
        current_music_tab = self.musicTabs.currentWidget()
        if current_music_tab.objectName() == 'libraryLayout':
            current_library_tab = self.libraryTabs.currentWidget()
            return current_library_tab.findChild(QtWidgets.QTreeWidget)
        elif current_music_tab.objectName() == 'resultLayout':
            current_search_tab = self.searchTabs.currentWidget()
            return current_search_tab.findChild(QtWidgets.QTreeWidget)
        return None

    def on_item_selection_changed(self):
        tree = self.get_current_tree_widget()
        if tree and tree.selectedItems():
            self.infoView.show()
            self.update_info_panel(tree.selectedItems()[0])
        else:
            self.infoView.hide()

    def update_info_panel(self, item):
        data = item.data(0, QtCore.Qt.UserRole)
        if not data:
            return

        # Clear previous info
        for i in range(len(self.info_labels)):
            self.info_labels[i].setText("")
            self.info_headers[i].setText("")

        item_type = data.get('type')

        if item_type == 'track':
            self.infoHeader1.setText("Title:")
            self.infoLabel1.setText(data.get('name', 'N/A'))
            self.infoHeader2.setText("Artists:")
            self.infoLabel2.setText(", ".join([a['name'] for a in data.get('artists', [])]))
            self.infoHeader3.setText("Album:")
            self.infoLabel3.setText(data.get('album', {}).get('name', 'N/A'))

            if data.get('album') and data['album'].get('images'):
                image_url = data['album']['images'][0].get('url')
                if image_url:
                    worker = Worker(set_label_image, self.coverArtLabel, image_url, from_url=True)
                    QThreadPool.globalInstance().start(worker)

        elif item_type == 'album':
            self.infoHeader1.setText("Album:")
            self.infoLabel1.setText(data.get('name', 'N/A'))
            self.infoHeader2.setText("Artists:")
            self.infoLabel2.setText(", ".join([a['name'] for a in data.get('artists', [])]))
            self.infoHeader3.setText("Release Date:")
            self.infoLabel3.setText(data.get('release_date', 'N/A'))
            self.infoHeader4.setText("Tracks:")
            self.infoLabel4.setText(str(data.get('total_tracks', 'N/A')))

            if data.get('images'):
                image_url = data['images'][0].get('url')
                if image_url:
                    worker = Worker(set_label_image, self.coverArtLabel, image_url, from_url=True)
                    QThreadPool.globalInstance().start(worker)

        elif item_type == 'artist':
            self.infoHeader1.setText("Artist:")
            self.infoLabel1.setText(data.get('name', 'N/A'))
            self.infoHeader2.setText("Followers:")
            self.infoLabel2.setText(str(data.get('followers', {}).get('total', 'N/A')))
            self.infoHeader3.setText("Genres:")
            self.infoLabel3.setText(", ".join(data.get('genres', [])))

            if data.get('images'):
                image_url = data['images'][0].get('url')
                if image_url:
                    worker = Worker(set_label_image, self.coverArtLabel, image_url, from_url=True)
                    QThreadPool.globalInstance().start(worker)

        elif item_type == 'playlist':
            self.infoHeader1.setText("Playlist:")
            self.infoLabel1.setText(data.get('name', 'N/A'))
            self.infoHeader2.setText("Owner:")
            self.infoLabel2.setText(data.get('owner', {}).get('display_name', 'N/A'))
            self.infoHeader3.setText("Tracks:")
            self.infoLabel3.setText(str(data.get('tracks', {}).get('total', 'N/A')))

            if data.get('images'):
                image_url = data['images'][0].get('url')
                if image_url:
                    worker = Worker(set_label_image, self.coverArtLabel, image_url, from_url=True)
                    QThreadPool.globalInstance().start(worker)

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

        if self.liked_songs_cache is not None:
            self.display_liked_songs(self.liked_songs_cache)
            return

        self.likedTree.hide()
        self.loadingLikedLabel.setText("Loading, please wait...")
        self.loadingLikedLabel.show()
        self.refresh_liked_btn.setEnabled(False)

        worker = Worker(api.get_liked_songs)
        worker.signals.result.connect(self.display_liked_songs)
        worker.signals.error.connect(self.display_liked_songs_error)
        QThreadPool.globalInstance().start(worker)

    def display_liked_songs(self, results):
        self.liked_songs_cache = results
        self.loadingLikedLabel.hide()
        self.likedTree.show()
        self.refresh_liked_btn.setEnabled(True)
        self.likedTree.clear()
        for track_item in results:
            track = track_item['track']
            artists = ", ".join([artist['name'] for artist in track['artists']])
            item = QTreeWidgetItem([track['name'], artists, track['album']['name']])
            item.setData(0, QtCore.Qt.UserRole, track)
            self.likedTree.addTopLevelItem(item)

    def display_liked_songs_error(self, error):
        self.loadingLikedLabel.setText("Error loading liked songs. Please try again later.")
        self.refresh_liked_btn.setEnabled(True)
        print("Error loading liked songs:", error)

    def on_settings_clicked(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec() == QDialog.Accepted:
            # Settings were saved, reload relevant parts of the UI
            self.load_downloaded_songs()

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

    def on_download_selected_clicked(self):
        active_tab_widget = self.musicTabs.currentWidget()
        if active_tab_widget.objectName() == 'resultLayout':
            tree_widget = self.searchTabs.currentWidget().findChild(QtWidgets.QTreeWidget)
        elif active_tab_widget.objectName() == 'libraryLayout':
            tree_widget = self.libraryTabs.currentWidget().findChild(QtWidgets.QTreeWidget)
        else:  # queue or others
            return

        if not tree_widget:
            return

        selected_items = tree_widget.selectedItems()
        if not selected_items:
            return

        self.progressBar.show()
        self.progressBar.setValue(0)

        for item in selected_items:
            item_data = item.data(0, QtCore.Qt.UserRole)
            if not item_data:
                continue

            # Determine type of download
            if 'type' in item_data:
                item_type = item_data['type']
                if item_type == 'track':
                    worker = Worker(download_track, self.update_progress_bar, 'single', item_data['id'], None, [])
                    worker.signals.finished.connect(lambda: self.progressBar.hide())
                    QThreadPool.globalInstance().start(worker)
                elif item_type == 'album':
                    worker = Worker(download_album, self.update_progress_bar, item_data['id'], [])
                    worker.signals.finished.connect(lambda: self.progressBar.hide())
                    QThreadPool.globalInstance().start(worker)
                elif item_type == 'playlist':
                    worker = Worker(download_playlist, self.update_progress_bar, item_data, [])
                    worker.signals.finished.connect(lambda: self.progressBar.hide())
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
