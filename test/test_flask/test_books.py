import json
import pytest
import os
from logging import getLogger

logger = getLogger(__name__)

BARCODES = [
	"9784774172705",
	"4910058270590"
]

class Testbooks:

	@pytest.mark.ssnlib
	def test_register_books(self, client):
		auth_res = client.post("/api/v1/auth", data=json.dumps(dict(username="Administrator", password=os.environ.get("LDAP_ADMIN_PASSWD"))), headers={"content-type":"application/json"})
		JWT = auth_res.json.get("access_token")

		# register regular book
		res = client.post("/api/v1/books", headers={"Authorization":"Bearer {}".format(JWT), "content-type":"application/json"}, data=json.dumps({"books":[{"barcode":BARCODES[0]}]}))
		assert res.status_code == 200
		assert res.json.get("status") == "ok"

		# register regular book again
		res = client.post("/api/v1/books", headers={"Authorization":"Bearer {}".format(JWT), "content-type":"application/json"}, data=json.dumps({"books":[{"barcode":BARCODES[0]}]}))
		assert res.status_code == 200
		assert res.json.get("status") == "partial ng"
		assert res.json.get("ngList")[0].get("msg") == "this book is already registered"

		# register book manually
		book_data = {
			"self":True,
			"books":
				[{
					"title": "Googleを支える技術",
					"barcode": "978477413432",
					"author":"西田 圭介",
					"publishmonth":"2008-03",
					"publisher":"技術評論社"
				}]
		}
		res = client.post("/api/v1/books", 
					headers={"Authorization":"Bearer {}".format(JWT), "content-type":"application/json"}, 
					data=json.dumps(book_data))
		assert res.status_code == 200
		assert res.json.get("status") == "ok"

		# register book manually again
		res = client.post("/api/v1/books", 
					headers={"Authorization":"Bearer {}".format(JWT), "content-type":"application/json"}, 
					data=json.dumps(book_data))
		logger.debug(res.json)
		assert res.status_code == 200
		assert res.json.get("status") == "partial ng"
		assert res.json.get("ngList")[0].get("msg") == "this book is already registered"

		# register magazine
		res = client.post("/api/v1/books", headers={"Authorization":"Bearer {}".format(JWT), "content-type":"application/json"}, data=json.dumps({"books":[{"barcode":BARCODES[1]}]}))
		logger.debug(res.json)
		assert res.status_code == 200
		assert res.json.get("status") == "ok"

		# check book exists
		res = client.get("/api/v1/books")
		logger.debug(res.json)
		assert res.status_code == 200
		assert res.json.get("status") == "ok"
		assert res.json.get("Books")[0].get("title") == "正規表現技術入門 : 最新エンジン実装と理論的背景"
		assert res.json.get("Books")[1].get("title") == "Googleを支える技術"
		assert res.json.get("Books")[2].get("title") == "Software Design 2019年05月号"

		#
		# test invalid format
		#

		# invalid credentials
		res = client.post("/api/v1/auth", headers={"content-type":"application/json"}, data=json.dumps({"username":"hoge", "password":"huga"}))
		assert res.json.get("msg") == "Authentication was failed"

		res = client.post("/api/v1/auth", data=json.dumps({"username":"hoge", "password":"huga"}))
		assert res.json.get("msg") == "Content-Type is invalid. Please set application/json"

		# invalid data format
		res = client.post("/api/v1/books", headers={"Authorization":"Bearer {}".format(JWT), "content-type":"application/json"})
		assert res.json.get("msg") == "can not read book data. Please sent book data in json's list format"

		# invalid header
		res = client.post("/api/v1/books", headers={"Authorization":"Bearer {}".format(JWT)}, data=json.dumps({"books":[{"barcode":BARCODES[1]}]}))
		assert res.json.get("msg") == "Content-Type is invalid. Please set application/json"