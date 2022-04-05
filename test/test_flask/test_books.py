import json
import pytest
import os
from logging import getLogger

logger = getLogger(__name__)

BARCODES = ["9784774172705"]

class Testbooks:

	@pytest.mark.ssnlib
	def test_register_books(self, client):
		auth_res = client.post("/api/v1/auth", data=json.dumps(dict(username="Administrator", password=os.environ.get("LDAP_ADMIN_PASSWD"))), headers={"content-type":"application/json"})
		JWT = auth_res.json.get("access_token")
		logger.debug("access_token is: {}".format(JWT))

		res = client.post("/api/v1/books", headers={"Authorization":"Bearer {}".format(JWT), "content-type":"application/json"}, data=json.dumps({"books":[{"barcode":BARCODES[0]}]}))
		logger.info(res.json)
		assert res.status_code == 200