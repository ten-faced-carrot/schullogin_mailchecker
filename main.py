from ui import *
from PyQt5.QtWidgets import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from typing import Any
from pyqt_toast import Toast
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
import sys
import yaml
import os
optn = webdriver.ChromeOptions()
"""
__import__("zipfile").ZipFile(__import__("io").BytesIO(__import__("requests").get(f"https://chromedriver.storage.googleapis.com/108.0.5359.22/chromedriver_{'win32' if os.name == 'nt' else 'linux64'}.zip").content)).extractall()
if sys.platform == "win32":
    dlurl = "https://portableapps.com/downloading/?a=GoogleChromePortable&s=s&p=&d=pa&n=Google%20Chrome%20Portable&f=GoogleChromePortable_107.0.5304.107_online.paf.exe"
    open("chrome.exe", "wb+").write(__import__("requests").get(dlurl).content)
    optn.binary_location = "./chrome.exe"
"""
def showTray(icon=None, menu=None):
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setContextMenu(menu)
    tray.setVisible(True)


def sendMsg(msg):
    if sys.platform == "win32":

        from win10toast import ToastNotifier
        toast = ToastNotifier()
        toast.show_toast(
            "QSchulloginMailChecker",
            msg,
            duration=10,
            threaded=True,
        )
    else:
        import subprocess
        subprocess.call(["notify-send", msg])


auth = {}
running = True
driver = webdriver.Chrome()


class Worker(QThread):
    mailRecv = pyqtSignal(dict, str, str)
    finished = pyqtSignal()

    def run(self):
        last = 0
        win = self.win

        print("Started!")
        while running:
            self._refresh(last, win)
            time.sleep(20)
        self.finished.emit()

    def _refresh(self, last, win):
        data = {"mails": []}
        try:
            new = driver.find_element(
                'xpath',
                '//*[@id="rl-left"]/div[1]/div/div[2]/div[1]/div/div[1]/div[1]/a/span[1]'
            ).text or "0"
        except:
            new = "0"
        print(new)
        if int(new) != last:
            mail = driver.find_element(
                'xpath',
                '/html/body/div[1]/div[3]/div[2]/div[3]/div[2]/div/div/div[2]/div[4]/div[1]/div/div[9]/div'
            )
            mails = mail.find_elements(By.CLASS_NAME, 'unseen')
            for unseen in mails:
                unseen.click()
                time.sleep(1)
                data["mails"].append({
                    'sender':
                    driver.find_element(By.CLASS_NAME, "from").text,
                    'subject':
                    driver.find_element(By.CLASS_NAME,
                                        "subject").get_attribute("innerHTML"),
                    'content':
                    driver.find_element(By.CLASS_NAME, 'bodyText').text
                })
                print(data["mails"][-1])
                self.mailRecv.emit(data["mails"][-1], new, str(last))
            sendMsg(
                f'{int(new) - int(last)} Neue Nachricht(en) von SchulLogin abgerufen!'
            )
            last = int(new)


def stop(ui):
    global running
    running = False
    ui.thread.quit()


sessionconfig = yaml.safe_load(open("config.yml"))
filters = []


class FilterAdd(Ui_AddFilter):
    def setupUi(self, AddFilter, master):
        super(FilterAdd, self).setupUi(AddFilter)
        self.master = master
        self.mw = AddFilter
        print("ww")


class Ruleset(Ui_MailRules):
    def setupUi(self, MailRules):
        super(Ruleset, self).setupUi(MailRules)
        self.pushButton.clicked.connect(lambda: self.apply())
        for filter in sessionconfig["filters"]:
            filters.append(filter)
            self.listWidget.addItem(filter["val"])
        self.pushButton_3.clicked.connect(lambda: self.addFilter())
        self.pushButton_2.clicked.connect(lambda: self.rmFilter())
        self.mw = MailRules

    def rmFilter(self):
        for item in self.listWidget.selectedItems():
            for i, f in enumerate(filters):
                if f["val"] == item.text():
                    filters.pop(i)
                    self.listWidget.clear()
                    for filter in sessionconfig["filters"]:
                        self.listWidget.addItem(filter["val"])

    def addFilter(self):
        subwin = QDialog()
        FilterAdd().setupUi(subwin, self)
        subwin.show()

    def apply(self):
        if self.checkBox.isChecked():
            emails = self.lineEdit.text()
            skipFilter = self.checkBox_2.isChecked()

            sessionconfig["forward"] = {
                "fwd": True,
                "to": emails.split(),
                "skipflt": skipFilter
            }
        else:
            sessionconfig["forward"] = {"fwd": False}
        sessionconfig["filters"] = filters

        yaml.safe_dump(sessionconfig, open("config.yml", "w+"))


class New(Ui_SendMailUI):
    def setupUi(self, SendMailUI):
        super().setupUi(SendMailUI)
        self.pushButton.clicked.connect(lambda: self.sendMail())

    def sendMail(self):
        receiver = self.lineEdit.text()
        ccs = self.lineEdit_2.text()
        subj = self.lineEdit_3.text()
        innerText = self.textEdit.toHtml()
        driver.find_element(
            'xpath', '//*[@id="rl-left"]/div[1]/div/div[1]/a[1]').click()
        driver.find_element(
            'xpath',
            '//*[@id="rl-popups"]/div/div/div/div[2]/div/div[1]/div/div[2]/div[2]/ul/li[1]/input'
        ).send_keys(receiver)
        if ccs:
            driver.find_element(
                'xpath',
                '//*[@id="rl-popups"]/div/div/div/div[2]/div/div[1]/div/div[1]/div[2]/span/span[1]'
            ).send_keys(ccs)
        driver.find_element(
            'xpath',
            '//*[@id="rl-popups"]/div/div/div/div[2]/div/div[1]/div/div[6]/div[2]/input'
        ).send_keys(subj)
        driver.find_element('xpath', '//*[@id="cke_11"]').click()
        driver.find_element(
            'xpath', '//*[@id="cke_1_contents"]/textarea').send_keys(innerText)
        driver.find_element(
            'xpath',
            '//*[@id="rl-popups"]/div/div/div/div[1]/a[1]/span').click()


class Main(Ui_MailMainUI):
    def setupUi(self, MailMainUI: QMainWindow):
        self.mw = MailMainUI
        self.thread = Worker()
        self.thread.win = self.mw
        icon = QIcon.fromTheme("application")
        menu = QMenu()
        refresh = QAction("Scan for Mail")
        refresh.triggered.connect(lambda: self.thread._refresh(0, self.mw))
        menu.addAction(refresh)
        showTray(icon, menu)

        self.thread.finished.connect(self.mw.destroy)
        super().setupUi(MailMainUI)
        self.mw.setMenuBar(self.menubar)
        self.actionRegelns.triggered.connect(lambda: self.rules())

        self.thread.mailRecv.connect(self.addNewMail)
        self.sessionMails = []

        self.listWidget.itemClicked.connect(self.displayInfo)
        self.actionNach_Mail_suchen.triggered.connect(
            lambda: self.thread._refresh(0, self.mw))
        self.mw.destroyed.connect(lambda: stop(self))
        self.thread.start()
        self.pushButton.clicked.connect(lambda: self.popupNew())
        self.actionAbmelden.triggered.connect(app.quit)

    def rules(self):
        subwin = QMainWindow(self.mw)
        Ruleset().setupUi(subwin)
        subwin.show()

    def popupNew(self):
        print("e")
        subwin = QMainWindow(self.mw)
        New().setupUi(subwin)
        subwin.show()

    def addNewMail(self, m, new, last):
        # t = Toast(f'{int(new)-int(last)} Neue Nachricht(en) erhalten!', parent=self.mw)
        # t.show()
        m["id"] = len(self.sessionMails)
        self.sessionMails.append(m)
        self.listWidget.addItem(f'{m["id"]}.: {m["subject"]}')

    def displayInfo(self):
        item = self.listWidget.currentItem()
        id = item.text().split(".")[0]
        self.mw.setWindowTitle(
            f"RainLoop | Posteingang | {len(self.sessionMails)} Nachrichten")
        for i in self.sessionMails:
            if i["id"] == int(id):
                self.textBrowser.setText(f'''
{i["sender"]}: {i["subject"]}
------------------------------
{i["content"]}
                ''')


class Start(Ui_MainWindow):
    def setupUi(self, MainWindow: QMainWindow):
        super().setupUi(MainWindow)
        self.mw = MainWindow
        self.pushButton.clicked.connect(lambda: self.authenticate())

    def authenticate(self):
        auth["username"] = self.lineEdit.text()
        auth["passwd"] = self.passwd.text()
        driver.get(
            "https://schullogin.de/p/sbs.singlesignon/authentication/index")
        user = driver.find_element(By.XPATH, '//*[@id="js-auth-username"]')
        passwd = driver.find_element(By.XPATH, '//*[@id="js-auth-password"]')
        user.send_keys(auth["username"])
        passwd.send_keys(auth["passwd"])
        driver.find_element(By.XPATH, '//*[@id="js-auth-submit"]').click()
        driver.find_element('xpath',
                            '/html/body/div[2]/main/div/div[1]/div/a').click()
        driver.find_element(
            'xpath', '/html/body/div[2]/main/div/div[3]/div[2]/a[2]').click()
        # self.mw.destroy()
        nw = QMainWindow(self.mw)
        Main().setupUi(nw)
        nw.show()


app = QApplication([])

login = QMainWindow()
Start().setupUi(login)
login.show()

app.exec()
driver.quit()
