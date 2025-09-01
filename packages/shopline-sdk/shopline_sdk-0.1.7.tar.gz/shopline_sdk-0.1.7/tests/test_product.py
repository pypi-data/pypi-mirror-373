#!/usr/bin/python3
# @Time    : 2025-06-16
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from shopline.api import ShoplineAPI


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.shopline = ShoplineAPI(
            "d5c95e06004cbe28a76f306e36ba307d26e2b414ddfae067f137b152193e211b",
            "1b63264ea446d59f08a26db543ea4686b5056ef194c25076deb2ef2652b3db0d",
            handle="Shopline",
            merchant_id="684291be1dc1b00060d52b9e",
        )
        self.redirect_uri = "https://192.168.195.6"
        self.shopline.set_access_token(
            "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1YjJhYmVlMDZjOTFlZWQ0YTcwMDNhNmViM2VhMjhlMiIsImRhdGEiOnsibWVyY2hhbnRfaWQiOiI2OGFiZjg0NWM1YTEwYjAwODgzMDE4ZTgiLCJhcHBsaWNhdGlvbl9pZCI6IjY4NzY3ZjQ2NWM5YWU3MDAwYTI0ZWRlMCJ9LCJpc3MiOiJodHRwczovL2RldmVsb3BlcnMuc2hvcGxpbmVhcHAuY29tIiwiYXVkIjpbXSwic3ViIjoiNjhhYmY4NDVjNWExMGIwMDg4MzAxOGU4In0.thyXOF1f8GcqzVihsjca-7m9YCOtuLaVxGk8jIwydBA"
        )

    def test_get_products(self):
        products = self.shopline.product.get_products()
        self.assertIsInstance(products.get("items"), list, "success")
        
    def test_get_addons(self):
        res = self.shopline.addon_product.gets()
        print(res)

    def test_get_gifts(self):
        res = self.shopline.gift.gets()
        print(res)


if __name__ == "__main__":
    unittest.main()
