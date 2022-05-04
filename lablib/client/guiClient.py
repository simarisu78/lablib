import PySimpleGUI as sg
from logging import getLogger
from queue import Queue
import threading

from barcode import BarcodeReader
from felicaReader import FelicaReader

logger = getLogger(__name__)
sg.theme('Light Brown')
x, y = sg.Window.get_screen_size()

# worker function for receive messages from barcode and felica reader


def worker(queue, window):
    while True:
        event = queue.get()
        logger.debug("event received %s".format(event))
        window.write_event_value("-THREAD-", event)


def rent(studentID):
    pass


def return_book(barcode):
    pass


def login():
    import hashlib

    # THIS IS A PASSWORD FOR TESTING #
    password_hash = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"

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
            if hashlib.sha256(input.encode()).hexdigest() == password_hash:
                login_window["-notice-"].update("Welcome")
                break
            else:
                login_window["-notice-"].update("Login Failed")

    login_window.close()


def register():
    pass


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

    # thread for polling event queuee
    threading.Thread(target=worker, args=(
        event_queue, window), daemon=True).start()

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
