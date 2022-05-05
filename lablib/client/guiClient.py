import PySimpleGUI as sg
from logging import getLogger
from queue import Queue
import threading
import hashlib
import requests
import os

from barcode import BarcodeReader
from felica import FelicaReader
from client_conf import CLIENT_CONF

REGISTER_URL = CLIENT_CONF.REGISTER_URL
TOKEN = CLIENT_CONF.TOKEN

logger = getLogger(__name__)
sg.theme('Light Brown')
x, y = sg.Window.get_screen_size()

# worker function for receive messages from barcode and felica reader
def worker(queue, window):
    while True:
        event = queue.get()
        logger.debug("event received %s".format(event))
        if event[0] == "barcode":
            window.write_event_value("-BARCODE-", event)
        elif event[0] == "nfc-connect":
            window.write_event_value("-FELICA_CON-", event)
        elif event[0] == "nfc-release":
            window.write_event_value("-FELICA_REL-", event)


def rent(studentID):
    pass


def return_book(barcode):
    pass


def login():
    # THIS IS A PASSWORD FOR TESTING #
    password_hash = "66206db9bd44faccedf3a0af4c2afd34fbedf13795b0f3fea089892a599efb57"
    salt = "akljfsadkljiuhkjlhr"

    message = "書籍の登録にはパスワードが必要です"
    layout = [
        [sg.Text(message)],
        [sg.Text("", key="-notice-", text_color="Red")],
        [sg.Text("Password"), sg.Input(
            "", password_char='*', key="-password-")],
        [sg.Button("Login", key="-login_button-"),
         sg.Button("Cancel", key="-cancel_button-")],
    ]
    login_window = sg.Window("Login Window",
                             layout,
                             return_keyboard_events=True,
                             element_justification='center',
                             keep_on_top=True,
                             size=(x, y)).Finalize()
    login_window.Maximize()

    while True:
        event, values = login_window.read()

        if event in [sg.WIN_CLOSED, '-exit-', 'Escape:27', "-cancel_button-"]:
            break

        elif event in ["-login_button-", '\r']:
            input = values["-password-"]
            if hashlib.sha256((salt + input).encode()).hexdigest() == password_hash:
                login_window["-notice-"].update("Welcome")
                register()
                break
            else:
                login_window["-notice-"].update("Login Failed")

    login_window.close()


def register():
    message = "登録したい書籍のバーコードを読み込んでください"
    message2 = "エラーが発生した場合は直接入力してください"
    layout = [
        [sg.Text(message)],
        [sg.Text(message2)],
        [sg.Text("", key="-notice1-", text_color="Green")],
        [sg.Text("", key="-notice2-", text_color="Red")],
        [sg.Text("Barcode"), sg.Input("", key="-barcode-")],
        [sg.Text("Title"), sg.Input("", key="-title-")],
        [sg.Text("Author"), sg.Input("", key="-author-")],
        [sg.Button("Apply", key="-apply_button-"),
         sg.Button("Cancel", key="-cancel_button-")],
    ]
    register_window = sg.Window("Register Window",
                             layout,
                             return_keyboard_events=True,
                             element_justification='center',
                             keep_on_top=True,
                             size=(x, y)).Finalize()
    register_window.Maximize()

    header = {"Authorization" : " ".join(["Bearer",TOKEN])}
    while True:
        window, event, values = sg.read_all_windows()

        if event in [sg.WIN_CLOSED, '-exit-', 'Escape:27', "-cancel_button-"]:
            break

        if event in ["-BARCODE-"]:
            barcode = values[1]
            try:
                res = requests.post(REGISTER_URL, json={"books":[{"barcode":barcode}]}, headers=header)
            except:
                register_window["-notice1-"].update("")
                register_window["-notice2-"].update("Connection refused. Please check server")
                register_window["-barcode-"].update(barcode)
                continue

            if res.status_code == 200 and res.json().get("status") == "ok":
                register_window["-notice1-"].update("Success! : Barcode {}".format(barcode))
                register_window["-notice2-"].update("")
            else:
                register_window["-notice1-"].update("")
                register_window["-notice2-"].update("Register Failure : Barcode {}".format(barcode))
                register_window["-barcode-"].update(barcode)

        if event in ["-apply_button-"]:
            barcode = values["-barcode-"]
            title = values["-title-"]
            author = values["-author-"]

            try:
                res = requests.post(REGISTER_URL, json={"self":True ,"books":[{"barcode":barcode, "title":title, "author":author}]}, headers=header)
            except:
                register_window["-notice1-"].update("")
                register_window["-notice2-"].update("Connection refused. Please check server")
                register_window["-barcode-"].update(barcode)
                continue

            if res.status_code == 200 and res.json().get("status") == "ok":
                register_window["-notice1-"].update("Success! : Barcode {}".format(barcode))
                register_window["-notice2-"].update("")
                register_window["-barcode-"].update("")
            else:
                register_window["-notice1-"].update("")
                register_window["-notice2-"].update("Register Failure! Please check inputs".format(barcode))
                register_window["-barcode-"].update(barcode)

    register_window.close()


def main():
    greet = "書籍管理システムへようこそ！"
    greet_2 = "貸出の場合は学生証をかざすかボタンをクリック"
    greet_3 = "返却の場合は書籍のバーコード(ISBN)を読み取るかボタンをクリック"

    layout = [
        [sg.Text(greet, font=("メイリオ", 22), text_color="Black")],
        [sg.Text(greet_2, font=("メイリオ", 22))],
        [sg.Text(greet_3, font=("メイリオ", 22))],
        [],
        [sg.Button("", key="-RENT-", image_filename="./static/rent.png"),
         sg.Button("", key="-RETURN-", image_filename="./static/return.png")],
        [sg.Button("", key="-REGISTER-", image_filename="./static/register.png")],
        [sg.Button("DEBUG", key="-EXIT-")],
    ]

    window = sg.Window('Library System', layout, size=(
        x, y), element_justification="c").Finalize()
    window.Maximize()

    # init barcode reader and felica reader
    event_queue = Queue()
    br = BarcodeReader(event_queue)
    br.daemon = True
    br.start()
    fr = FelicaReader(event_queue)
    fr.daemon = True
    fr.start()

    # thread for polling event queue
    #threading.Thread(target=worker, args=(event_queue, window), daemon=True).start()

    # Event Loop
    while True:
        event, values = window.read()

        if event == "-EXIT-":
            break
        elif event == "-REGISTER-":
            login()

        print(event)

    window.close()


if __name__ == "__main__":
    main()
