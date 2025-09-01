#!/usr/bin/python3
# @Time    : 2025-06-16
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from shopline.api import ShoplineAPI


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.shopline = ShoplineAPI(
            "28409731dbfdb98da7a114845ef0d1ae4fd93252da23e1c16d5d9020219a8b09",
            "666bfaeb55cebd29c09771800aca8ed83c70f66fe0a870b7268428fd5372ad51",
            handle="Shopline",
            merchant_id="68abf845c5a10b00883018e8",
        )
        self.redirect_uri = "https://192.168.195.6"
        self.shopline.set_access_token(
            "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiNDAyM2Y4MTM1MmFhZTI0YmQ0MWQwMTEyMWE0ODlmMSIsImRhdGEiOnsibWVyY2hhbnRfaWQiOiI2OGFiZjg0NWM1YTEwYjAwODgzMDE4ZTgiLCJhcHBsaWNhdGlvbl9pZCI6IjY4NzY3ZjQ2NWM5YWU3MDAwYTI0ZWRlMCJ9LCJpc3MiOiJodHRwczovL2RldmVsb3BlcnMuc2hvcGxpbmVhcHAuY29tIiwiYXVkIjpbXSwic3ViIjoiNjhhYmY4NDVjNWExMGIwMDg4MzAxOGU4In0.Qfo6KoWnCeg8Jls7IohgkO47mepcup8YNslfh7p3yVM"
        )

    def test_get_orders(self):
        orders = self.shopline.order.get_orders()
        self.assertIsInstance(orders.get("items"), list, "success")
        
    def test_search(self):
        orders = self.shopline.order.search(statuses=['pending','confirmed'])
        print(orders)


if __name__ == "__main__":
    unittest.main()
