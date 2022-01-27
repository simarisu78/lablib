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

    window = sg.Window('Library System', layout, size=(x, y), element_justification="c").Finalize()
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
    threading.Thread(target=worker, args=(event_queue, window), daemon=True).start()
    
    # Event Loop
    while True: 
        event, values = window.read()

        if event == "-EXIT-":
            break

        print(event)
        
    window.close()
    
if __name__ == "__main__":
    main()
