import pytest
import subprocess
from queue import Queue

from lablib.client.barcode import BarcodeReader

from logging import getLogger

logger = getLogger(__name__)


class TestBarcodeReader:

    _path = "/dev/input/event0"
    _q = None

    @pytest.fixture(autouse=True)
    def background_thread(self):
        self._q = Queue()
        br = BarcodeReader(self._q)
        br.start()
        yield br

    def test_reader(self):
        with open(self._path, "wb") as f:
            cmd = [
                "./test/write_event",
                "11",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "28",
            ]
            result = subprocess.run(cmd, stdout=f).returncode
            assert result == 0

        barcode = self._q.get()
        assert barcode == "0123456789"
