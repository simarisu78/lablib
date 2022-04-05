from mmap import ACCESS_COPY
from os import access
import re
from xml.dom import NotFoundErr
from flask import Blueprint, make_response, request, abort, jsonify, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

api = Blueprint('api', __name__, url_prefix='/api/v1')
from lablib.app.auth import ldap_auth
from ..models import Book, BookSchema, Checkout
from ..db import db

from lablib.app import jwt, limiter

# generate token
@api.route('/auth', methods=['POST'])
def auth():
	if request is None:
		return jsonify({"msg": "Authentication was failed"})

	username = request.json.get("username", None)
	password = request.json.get("password", None)
	if ldap_auth(username, password) is False:
		return jsonify({"msg": "Authentication was failed"})

	access_token = create_access_token(identity=username)
	return jsonify(access_token=access_token)

# get book list
@api.route('/books', methods=['GET'])
def book_list():
	books = Book.query.all()
	if books is not None:
		return jsonify({"status": "ok", "Books" : BookSchema(many=True).dump(books)})
	else:
		return jsonify({"status": "ng"})

# register books
@api.route('/books', methods=['POST'])
@jwt_required()
@limiter.limit("1/second")
def register_books():
	if request is None:
		return jsonify({"status": "ng", "msg": "Please post data"})

	if request.headers['Content-Type'] != 'application/json':
		return jsonify({"status": "ng", "msg": "Content-Type is invalid. Please set application/json"})
	
	try:
		data = request.get_json()
		selfRegister = data.get('self')
		books = data.get('books')
	except:
		return jsonify({"status":"ng", "msg":"can not read book data. Please sent book data in json's list format"})

	if selfRegister:
		ngList = []
		try:
			for book_req in books:
				barcode = book_req.get('barcode')
    
				if len(Book.query.filter_by(barcode=barcode).all()) != 0:
					ngList.append({"barcode":barcode, "msg":"this book is already registered"})
					continue
    
				title = book_req.get('title')
				author = book_req.get('author')
				detail = book_req.get('detail')
				publishmonth = book_req.get('publishmonth')
				publisher = book_req.get('publisher')
				amount = stock = 1

				barcode_pat = re.compile("\d+")
				publishmonth_pat = re.compile("\d{4}-\d{2}")
				if not barcode_pat.fullmatch(barcode) or not publishmonth_pat.fullmatch(publishmonth):
					raise ValueError

				book = Book(barcode=barcode, title=title, author=author,
                   detail=detail, publishmonth=publishmonth, publisher=publisher,
                   amount=amount, stock=stock)
				db.session.add(book)

			db.session.commit()
		except ValueError:
			return ngList.append({"status":"ng", "msg":"The format is invalid. Please check barcode and publishmonth."})
		except:
			return ngList.append({"status":"ng", "msg":"Some error occured. Please check your book data. barcode, title, author, publishmonth are required."})

		if len(ngList) == 0:
			return jsonify({"status": "ok"})
		else:
			return jsonify({"status": "partial ng", "ngList":ngList})
	else:
		return search_external_api(books)

# search for external apis
# default api is OpenBD
import requests
import time
RAKUTEN_ICHIBA = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
RAKUTEN_BOOKS = "https://app.rakuten.co.jp/services/api/BooksTotal/Search/20170404"
OPENBD = "https://api.openbd.jp/v1/get"
MAGAZINE_CODELIST = {"05827":"Software Design",
                     "01619":"Interface"}
AUTHOR_LIST = {"05827":"技術評論社",
               "01619":"ＣＱ出版"}
TRANSLATE_LIST = {
  '\u3000': ' ',
}
def search_external_api(books):
	notFoundList = []
	for books_req in books:
		try:
			barcode = books_req.get("barcode")
			if barcode is None:
				notFoundList.append({"msg":"Please pass barcodes"})
				continue
			
			if len(Book.query.filter_by(barcode=barcode).all()) != 0:
				notFoundList.append({"barcode":barcode, "msg":"this book is already registered"})
				continue
   
			newbook = Book(barcode=barcode)
			
			# 雑誌の場合
			# 楽天市場APIを検索
			# 雑誌コードを事前に登録しておき、年月だけ抽出する
			if barcode[:3] == '491':
       
				data = {"applicationId": current_app.config['RAKUTEN_APPLICATION_ID'],
						"format":"json",
						"keyword":str(barcode)}
				res = requests.get(RAKUTEN_ICHIBA, data)
				if res.status_code != 200:
					raise ConnectionRefusedError
		
				if res.json().get('hits') == 0:
					raise NotFoundErr

				year_month = ""
				publish_month = ""
				for item in res.json().get("Items"):
					tmp = item.get("Item").get("itemName")
					reg = re.search("(\d+).*年.*(\d+).*月", tmp)
					if reg is not None:
						year_month = "{}年{:0>2}月号".format(reg.groups()[0], reg.groups()[1])
						publish_month = "-".join([reg.groups()[0], "{:0>2}".format(reg.groups()[1]) ])
						break
				
				magazine_code = barcode[4:9]
				if magazine_code in MAGAZINE_CODELIST:
					newbook.title = " ".join([MAGAZINE_CODELIST.get(magazine_code), year_month])
					newbook.publishmonth = publish_month
					newbook.author = newbook.publisher = AUTHOR_LIST.get(magazine_code)
					newbook.amount = newbook.stock = 1
     
				else:
					notFoundList.append({"barcode":barcode, "msg":"Not registered in the magazine list.Please tell the administrator."})
					continue
			
			# JAN以外の場合（ほぼISBN）
			else:
				data = {"isbn":barcode, "pretty":True}
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
					newbook.publishmonth = "-".join([pubdate[:4], pubdate[4:6]])
					
				newbook.publisher = result.get("summary").get("publisher")
				newbook.amount = newbook.stock = 1
				newbook.large_url = result.get("summary").get("cover")
    
			db.session.add(newbook)
			db.session.commit()
   
		except NotFoundErr:
			notFoundList.append({"barcode":barcode,"msg":"barcode not found."})
   
		except ConnectionRefusedError:
			return jsonify({"status":"ng", "msg":"Connection to API was Refused. Please check token."})

		#except KeyError:
			#notFoundList.append({"barcode":barcode,"msg":"Required information was not available. Please register manually."})
		
		#except Exception as e:
			#print(e)
			#notFoundList.append({"barcode":barcode,"msg":"some error occured."})

		finally:
			db.session.rollback()
			db.session.close()
  
		time.sleep(1)
	
	if len(notFoundList) == 0:
		return jsonify({"status":"ok"})
	else:
		return jsonify({"status":"partial ng", "nglist":notFoundList})

# borrow books
@api.route('/checkout', methods=['POST'])
def borrow_books():
	return "check out books"

# return books
@api.route('/checkout', methods=['DELETE'])
def return_books():
	return "return books"

# error handler
@api.errorhandler(400)
@api.errorhandler(404)
def error_handler(error):
	return "error"

@api.errorhandler(429)
def ratelimit_handler(e):
	return make_response(jsonify(error="ratelimit exceeded: %s" % e.description), 429)