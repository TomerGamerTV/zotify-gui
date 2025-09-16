from PyQt5.QtWidgets import QDialog, QFileDialog
from zotify.gui.settings_dialog_ui import Ui_SettingsDialog
from zotify.config import Zotify, CONFIG_VALUES
from zotify.const import ROOT_PATH, DOWNLOAD_FORMAT, DOWNLOAD_QUALITY, DOWNLOAD_REAL_TIME, SKIP_EXISTING

class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)
        self.load_settings()
        self.browseBtn.clicked.connect(self.browse_root_path)
        self.buttonBox.accepted.connect(self.save_settings)

    def save_settings(self):
        # General
        Zotify.CONFIG.Values[ROOT_PATH] = self.rootPathEdit.text()

        # Downloads
        Zotify.CONFIG.Values[DOWNLOAD_FORMAT] = self.downloadFormatCombo.currentText()
        Zotify.CONFIG.Values[DOWNLOAD_QUALITY] = self.downloadQualityCombo.currentText()
        Zotify.CONFIG.Values[DOWNLOAD_REAL_TIME] = self.realTimeCheckBox.isChecked()
        Zotify.CONFIG.Values[SKIP_EXISTING] = self.skipExistingCheckBox.isChecked()

        Zotify.CONFIG.save()

    def load_settings(self):
        # General
        self.rootPathEdit.setText(str(Zotify.CONFIG.get(ROOT_PATH)))

        # Downloads
        self.downloadFormatCombo.addItems(['copy', 'aac', 'fdk_aac', 'mp3', 'ogg', 'opus', 'vorbis'])
        self.downloadFormatCombo.setCurrentText(Zotify.CONFIG.get(DOWNLOAD_FORMAT))

        self.downloadQualityCombo.addItems(['auto', 'normal', 'high', 'very_high'])
        self.downloadQualityCombo.setCurrentText(Zotify.CONFIG.get(DOWNLOAD_QUALITY))

        self.realTimeCheckBox.setChecked(Zotify.CONFIG.get(DOWNLOAD_REAL_TIME))
        self.skipExistingCheckBox.setChecked(Zotify.CONFIG.get(SKIP_EXISTING))

    def browse_root_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Music Library Path")
        if directory:
            self.rootPathEdit.setText(directory)
