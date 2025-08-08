import sys
from os import getenv

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl


class OpenLinkHubWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenLinkHub")
        self.setGeometry(0, 0, 1024, 768)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(getenv("OLH_URL", "http://localhost:27003")))
        self.setCentralWidget(self.browser)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

class OpenLinkHubTray:
    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("icon.png"))

        self.menu = QMenu()

        self.show_action = QAction("Show")
        self.quit_action = QAction("Quit")

        self.menu.addAction(self.show_action)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip("OpenLinkHub")

        self.show_action.triggered.connect(self.window.show)
        self.quit_action.triggered.connect(self.quit_app)

        self.tray.activated.connect(self.icon_clicked)

        self.tray.show()

    def icon_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.window.isVisible():
                self.window.hide()
            else:
                self.window.show()

    def quit_app(self):
        self.tray.hide()
        self.app.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = OpenLinkHubWindow()
    tray_app = OpenLinkHubTray(app, window)
    if int(getenv("OLH_START_MINIMIZED", 0)) == 0:
        window.show()
    sys.exit(app.exec())