import os
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

        self.autoscale_js = """
        function autoscaleKeyboard() {
            const keyboard = document.querySelector('[class^="keyboard-"]');
            if (!keyboard) {
                return;
            }

            const container = keyboard.closest('.card') || keyboard.parentElement;
            if (!container) {
                return;
            }

            const containerWidth = container.clientWidth;
            const keyboardWidth = keyboard.scrollWidth;
            const scaleRatio = Math.min(1, (containerWidth - 150) / keyboardWidth);

            const newScale = `scale(${scaleRatio})`;
            const currentScale = keyboard.style.transform;

            if (scaleRatio < 1) {
                if (currentScale !== newScale) {
                    keyboard.style.transform = newScale;
                }
            } else {
                if (currentScale !== 'none' && currentScale !== '') {
                    keyboard.style.transform = 'none';
                }
            }
        }

        autoscaleKeyboard();

        let resizeTimer;
        window.removeEventListener('resize', window.olhAutoscaleHandler);
        window.olhAutoscaleHandler = () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(autoscaleKeyboard, 30);
        };
        window.addEventListener('resize', window.olhAutoscaleHandler);

        const observer = new MutationObserver((mutations) => {
            autoscaleKeyboard();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        """

        self.browser.loadFinished.connect(self.inject_js)

    def inject_js(self, ok):
        if ok:
            self.browser.page().runJavaScript(
                "if (typeof window.olhAutoscaleHandler === 'undefined') { " +
                self.autoscale_js +
                " }"
            )

    def closeEvent(self, event):
        event.ignore()
        self.hide()
class OpenLinkHubTray:
    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.tray = QSystemTrayIcon()
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        self.tray.setIcon(QIcon(getenv("OLH_ICON_PATH", icon_path)))

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