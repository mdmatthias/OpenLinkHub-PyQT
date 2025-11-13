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
const d=document,w=window;const a=(s,p)=>{const e=d.querySelector(s);if(!e)return;const c=e.closest('.card-body')||e.closest('.card')||e.parentElement;if(!c)return;const r=Math.min(1,Math.max(1,c.clientWidth-p)/e.scrollWidth),ns=`scale(${r})`,cs=e.style.transform;r<1?cs!==ns&&(e.style.transform=ns):cs&&cs!=='none'&&(e.style.transform='none')};const b=(s)=>{const e=d.querySelector(s);e&&e.parentElement&&(e.parentElement.style.overflowX='auto')};const f=()=>{a('[class^="keyboard-"]',150);b('.table.mb-0')};let t;w.removeEventListener('resize',w.olhAutoscaleHandler);w.olhAutoscaleHandler=()=>{clearTimeout(t);t=setTimeout(f,30)};w.addEventListener('resize',w.olhAutoscaleHandler);new MutationObserver(f).observe(d.body,{childList:!0,subtree:!0});f();
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