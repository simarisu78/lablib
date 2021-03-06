import requests
import time
import re
from flask import current_app, jsonify

from lablib.app.util.db import db
from lablib.app.models import Book
from xml.dom import NotFoundErr


def self_register(books):
    ngList = []
    try:
        for book_req in books:
            barcode = book_req.get('barcode')

            if len(Book.query.filter_by(barcode=barcode).all()) != 0:
                ngList.append(
                    {"barcode": barcode, "msg": "this book is already registered"})
                continue

            title = book_req.get('title')
            author = book_req.get('author')
            detail = book_req.get('detail')
            publishmonth = book_req.get('publishmonth')
            publisher = book_req.get('publisher')
            amount = stock = 1

            barcode_pat = re.compile("\d+")
            publishmonth_pat = re.compile("\d{4}-\d{2}")

            if len(title) == 0 or len(author) == 0:
                raise ValueError

            if not barcode_pat.fullmatch(barcode):
                raise ValueError

            if publishmonth is not None and not publishmonth_pat.fullmatch(publishmonth):
                raise ValueError

            book = Book(barcode=barcode, title=title, author=author,
                        detail=detail, publishmonth=publishmonth, publisher=publisher,
                        amount=amount, stock=stock)
            db.session.add(book)

        db.session.commit()
    except ValueError:
        ngList.append({"status": "ng", "msg": "The format is invalid. Please check barcode and publishmonth."})
    except Exception as e:
        ngList.append({"status": "ng", "msg": "Some error occured. Please check your book data. barcode, title, author are required."})

    if len(ngList) == 0:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "partial ng", "ngList": ngList})


# search for external apis
# default api is OpenBD
RAKUTEN_ICHIBA = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
RAKUTEN_BOOKS = "https://app.rakuten.co.jp/services/api/BooksTotal/Search/20170404"
OPENBD = "https://api.openbd.jp/v1/get"
MAGAZINE_CODELIST = {"05827": "Software Design",
                     "01619": "Interface"}
AUTHOR_LIST = {"05827": "???????????????",
               "01619": "????????????"}
TRANSLATE_LIST = {
    '\u3000': ' ',
}


def search_external_api(books):
    notFoundList = []
    for books_req in books:

        barcode = books_req.get("barcode")
        if barcode is None:
            notFoundList.append({"msg": "Please pass barcodes"})
            continue

        try:
            wait_time = current_app.config.get("LAST_API_CALL") + 1 - time.time()
            if wait_time > 0:
                print("wait! {}".format(wait_time))
                time.sleep(wait_time)

            if len(Book.query.filter_by(barcode=barcode).all()) != 0:
                notFoundList.append(
                    {"barcode": barcode, "msg": "this book is already registered"})
                continue

            newbook = Book(barcode=barcode)

            # ???????????????
            # ????????????API?????????
            # ????????????????????????????????????????????????????????????????????????
            if barcode[:3] == '491':

                data = {"applicationId": current_app.config['RAKUTEN_APPLICATION_ID'],
                        "format": "json",
                        "keyword": str(barcode)}
                res = requests.get(RAKUTEN_ICHIBA, data)
                current_app.config["LAST_API_CALL"] = time.time()
                if res.status_code != 200:
                    raise ConnectionRefusedError

                if res.json().get('hits') == 0:
                    raise NotFoundErr

                year_month = ""
                publish_month = ""
                for item in res.json().get("Items"):
                    tmp = item.get("Item").get("itemName")
                    reg = re.search("(\d+).*???.*(\d+).*???", tmp)
                    if reg is not None:
                        year_month = "{}???{:0>2}??????".format(
                            reg.groups()[0], reg.groups()[1])
                        publish_month = "-".join([reg.groups()[0], "{:0>2}".format(reg.groups()[1])])
                        break

                magazine_code = barcode[4:9]
                if magazine_code in MAGAZINE_CODELIST:
                    newbook.title = " ".join(
                        [MAGAZINE_CODELIST.get(magazine_code), year_month])
                    newbook.publishmonth = publish_month
                    newbook.author = newbook.publisher = AUTHOR_LIST.get(
                        magazine_code)
                    newbook.amount = newbook.stock = 1

                else:
                    notFoundList.append(
                        {"barcode": barcode, "msg": "Not registered in the magazine list.Please tell the administrator."})
                    continue

            # JAN????????????????????????ISBN???
            else:
                data = {"isbn": barcode, "pretty": True}
                res = requests.get(OPENBD, data)

                if res.status_code != 200:
                    raise ConnectionRefusedError

                if res.json()[0] is None:
                    raise NotFoundErr
                result = res.json()[0]

                newbook.title = result.get("summary").get("title")
                newbook.author = result.get("summary").get("author")
                newbook.detail = result.get("onix").get("CollateralDetail", {}).get("TextContent", {})[0].get("Text", None)

                pubdate = result.get("summary").get("pubdate")
                if '-' in pubdate:
                    reg = re.search("(\d+)-(\d+)", pubdate).groups()
                    newbook.publishmonth = "{}-{:0>2}".format(reg[0], reg[1])
                else:
                    newbook.publishmonth = "-".join(
                        [pubdate[:4], pubdate[4:6]])

                newbook.publisher = result.get("summary").get("publisher")
                newbook.amount = newbook.stock = 1
                newbook.large_url = result.get("summary").get("cover")

            db.session.add(newbook)
            db.session.commit()

        except NotFoundErr:
            notFoundList.append(
                {"barcode": barcode, "msg": "barcode not found."})

        except ConnectionRefusedError:
            return jsonify({"status": "ng", "msg": "Connection to API was Refused. Please check token."})

        except KeyError:
            notFoundList.append(
                {"barcode": barcode, "msg": "Required information was not available. Please register manually."})

        except Exception as e:
            print(e)
            notFoundList.append(
                {"barcode": barcode, "msg": "some error occured."})

        finally:
            db.session.rollback()
            db.session.close()

    if len(notFoundList) == 0:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "partial ng", "ngList": notFoundList})
