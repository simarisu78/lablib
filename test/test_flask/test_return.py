# general import
import os
import json
import pytest
from logging import getLogger

from test.test_flask.test_books import BARCODES
logger = getLogger(__name__)

# local import

class TestReturn:
	
	@pytest.mark.ssnlib
	def test_return(self, client):
		###
		# Normal behavior
		###
		data = {"barcode":BARCODES[0]}
		res = client.delete("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ok"

		###
		# error handling
		###

		# barcode was not specified
		data = {}
		res = client.delete("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ng"
		assert res.json.get("msg") == "please specify barcode in json format"

		# If the book was not checked out
		data = {"barcode":BARCODES[0]}
		res = client.delete("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ng"
		assert res.json.get("msg") == "this book is not checked out"

		# If the book does not exist
		data = {"barcode":"1234567890123"}
		res = client.delete("/api/v1/checkout", json=data)
		assert res.status_code == 200
		assert res.json.get("status") == "ng"
		assert res.json.get("msg") == "this book does not exist"

		# invalid content-type
		data = {"barcode":BARCODES[0]}
		res = client.delete("/api/v1/checkout", data=json.dumps(data))
		assert res.status_code == 200
		assert res.json.get("msg") == "Content-Type is invalid. Please set application/json"