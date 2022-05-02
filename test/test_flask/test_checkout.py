import os
from itsdangerous import json
import pytest
from logging import getLogger
logger = getLogger(__name__)

# local import
from .test_books import BARCODES

class TestCheckout:
	TestUser = os.environ.get("TEST_STUDENT_ID")

	@pytest.mark.ssnlib
	def test_checkout(self, client):
		###
		# Prepare testing
		###
		# get JWT token
		auth_res = client.post("/api/v1/auth", data=json.dumps(dict(username="Administrator", password=os.environ.get("LDAP_ADMIN_PASSWD"))), headers={"content-type":"application/json"})
		JWT = auth_res.json.get("access_token")

		# register user
		data = {"ldap_user_name":"Administrator", "student_id":self.TestUser}
		res = client.post("/api/v1/users", headers={"Authorization":"Bearer {}".format(JWT)}, json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ok"

		###
		# Normal behavior
		###

		# checkout a book
		data = {"student_id":self.TestUser, "barcode":BARCODES[0]}
		res = client.post("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ok"

		###
		# error handling
		###

		# specify a book that does'nt exist
		data = {"student_id":self.TestUser, "barcode":"1234567890123"}
		res = client.post("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ng"
		assert res.json.get("msg") == "this book does not exist"

		# specify a book that does'nt exist
		data = {"student_id":"invalid1", "barcode":BARCODES[0]}
		res = client.post("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ng"
		assert res.json.get("msg") == "this user does not exist"

		# student_id is not specified
		data = {"barcode":BARCODES[0]}
		res = client.post("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ng"
		assert res.json.get("msg") == "please post student_id and barcode in json format"

		# barcode is not specified
		data = {"student_id":self.TestUser}
		res = client.post("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ng"
		assert res.json.get("msg") == "please post student_id and barcode in json format"

		# out of stock
		data = {"student_id":self.TestUser, "barcode":BARCODES[0]}
		res = client.post("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ng"
		assert res.json.get("msg") == "this book is already checked out"

		# if neither element is specified
		res = client.post("/api/v1/checkout", json={})
		assert res.status_code == 200
		assert res.json.get("status") == "ng"
		assert res.json.get("msg") == "please post student_id and barcode in json format"

		# invalid content-type
		data = {"student_id":self.TestUser, "barcode":BARCODES[0]}
		res = client.post("/api/v1/checkout", data=json.dumps(data))
		assert res.status_code == 200
		assert res.json.get("msg") == "Content-Type is invalid. Please set application/json"