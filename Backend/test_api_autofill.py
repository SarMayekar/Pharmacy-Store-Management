import pytest

from app import app


def test_api_medicine_returns_purchase_rate(monkeypatch):
    # fake DB response with purchase_rate included
    fake_meds = [
        {
            'batch_no': 'BATCH1',
            'expiry_date': '2025-12-31',
            'hsn_code': '1234',
            'mrp': '200.00',
            'sgst_percent': 5.0,
            'cgst_percent': 5.0,
            'sale_rate': '220.00',
            'sale_discount_percent': '5.0',
            'purchase_rate': '180.00'
        }
    ]

    class FakeCursor:
        def __init__(self, dictionary=True):
            self.dictionary = dictionary

        def execute(self, *args, **kwargs):
            return None

        def fetchall(self):
            return fake_meds

    class FakeConn:
        def cursor(self, dictionary=True):
            return FakeCursor(dictionary=dictionary)

        def close(self):
            return None

    # Monkeypatch DB connection to use fake
    monkeypatch.setattr(app, 'get_db_connection', lambda: FakeConn())

    client = app.test_client()
    resp = client.get('/api/medicine/TestSomeName')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert 'purchase_rate' in data[0]
    assert str(data[0]['purchase_rate']) == '180.00'
