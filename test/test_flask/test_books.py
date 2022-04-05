import json
import pytest
from logging import getLogger

logger = getLogger(__name__)

BARCODES = ["9784774172705"]

class Testbooks:

	@pytest.mark.ssnlib
	def test_register_books(self, client):
		auth_res = client.post("/api/v1/auth", data=json.dumps(dict(username="testuser", password="Ohghee2eeyoo0ael")), headers={"content-type":"application/json"})
		JWT = auth_res.json.get("access_token")

		res = client.post("/api/v1/books", headers={"Authorization":"Bearer {}".format(JWT), "content-type":"application/json"}, data=json.dumps({"books":[{"barcode":BARCODES[0]}]}))
		logger.info(res.json)
		assert res.status_code == 200