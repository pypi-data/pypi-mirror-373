# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import os
import re
import sys
import glob
import webbrowser
import traceback
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QFont, QCursor
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLineEdit, QWidget, QVBoxLayout

from arch_wiki_search.exchange import StopFlag, CoreDescriptorFile
from arch_wiki_search import PACKAGE_NAME, __version__, __icon__, __logger__, Colors

class NotifIcon(QSystemTrayIcon):
    """Portable notification area icon that opens a menu with #TODO: 1 entry per wiki, a
    search function
    PyQT6 so runs on Windows (Intel and ARM), macOS (Intel and Apple Silicon) and Linux (Intel and ARM)
    #TODO: detect and quit when the last Core exits
    #TODO: update icon to current /favicon.ico if it exists
    #TODO: show cache size
    #TODO: add --export, --merge
    """
    debug = True #TODO pull debug value from calling thread
    stopFlag = None #write to False to stop the proxying process
    coreinfofile = None #Core will expose info about what it's serving
    last_search = 'Getting involved'

    def __init__(self):     
        self.stopFlag = StopFlag()
        self.coreinfofile = self._loadDescriptorFile() #TODO: load all files
        self.coreinfofile.read_data()

        # generate icon from utf-8 character
        pixmap = QPixmap(64, 64) #TODO: see how portable that looks
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setFont(QFont('Arial', 50))
        painter.drawText(pixmap.rect(), 0, __icon__)
        painter.end()
        self.icon = QIcon(pixmap)
        
        super().__init__(self.icon)
        self.setToolTip(f'{PACKAGE_NAME} {__version__}')
        self.local_url = f'http://localhost:{self.coreinfofile.data.port}'

        header_text = f'Wiki {self.coreinfofile.data.wikiname} on {self.local_url}'
        self.menu = QMenu()
        self.header_action = QAction('header', text=header_text)
        self.header_action.triggered.connect(self._header_clicked)
        self.menu.addAction(self.header_action)
        self.search_action = QAction('Search')
        self.search_action.triggered.connect(self._show_search_box)
        self.menu.addAction(self.search_action)
        self.exit_action = QAction('Exit')
        self.exit_action.triggered.connect(self.stop)
        self.menu.addAction(self.exit_action)
        self.setContextMenu(self.menu)

    def _loadDescriptorFile(self):
        """Find most recent core descriptor file and use it
        #TODO: one icon per active core / allow spawning more by selecting from yaml entries
        """
        try:
            tmppath = CoreDescriptorFile.get_path_pattern()
            files = glob.glob(tmppath + '*')
            files.sort(key=os.path.getmtime, reverse=True)
            #read port number from file name ('/tmp/arch_wiki_search.core.1234')
            regex = tmppath + r'([\d]+)$'
            for file_path in files:
                match = re.search(regex, file_path)
                port = int(match.group(1))
                __logger__.debug(f'iconqt found core on port {port}')
                #TODO: try to open a socket to the port to confirm the core is still there
                return CoreDescriptorFile(port) #TODO: find all cores not just the most recently active
        except Exception as e:
            msg = f'Failed to find core description files in {tmppath}* - can\'t spawn QT icon'
            __logger__.error(msg)
            return None

    def _openbrowser(self, url: str):
        try:
            webbrowser.open(url)
        except Exception as e:
            __logger__.error(f'Failed to start browser: {e}')
            if self.debug:
                print(traceback.format_exc())
        else:
            __logger__.debug('Calling browser')

    def _header_clicked(self):
        self._openbrowser(self.local_url)

    def _search_enter(self):
        searchterm = self.search_box.text()
        self.last_search = searchterm
        url = f'{self.local_url}/{self.coreinfofile.data.wikisearchstring}{searchterm}'
        self._openbrowser(url)
        self.search_widget.close()

    def _show_search_box(self):
        self.search_widget = QWidget()
        self.search_widget.setWindowTitle(f'Search {self.coreinfofile.data.wikiname}')
        layout = QVBoxLayout()
        self.search_box = QLineEdit(self.last_search)
        self.search_box.selectAll()
        self.search_box.returnPressed.connect(self._search_enter)
        layout.addWidget(self.search_box)
        self.search_widget.setLayout(layout)
        self.search_widget.setGeometry(QCursor.pos().x(), QCursor.pos().y(), #mouse cursor position
                                        200, 30) #TODO: adapt size to font/resolution
        self.search_widget.show()

    def stop(self):
        self.stopFlag.write(True) #tell proxying process to stop
        QApplication.quit()
        
def main():
    qt6app = QApplication(sys.argv)
    notificon = NotifIcon()
    notificon.show()
    #TODO: loop and quit if the stop flag file was deleted, meaning the core quit on us
    qt6app.exec()

if __name__ == '__main__':
    main()

