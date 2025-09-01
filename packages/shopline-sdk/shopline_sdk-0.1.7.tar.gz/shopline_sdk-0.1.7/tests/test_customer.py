#!/usr/bin/python3
# @Time    : 2025-06-16
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from shopline.api import ShoplineAPI


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.shopline = ShoplineAPI(
            "d5c95e06004cbe28a76f306e36ba307d26e2b414ddfae067f137b152193e211b",
            "1b63264ea446d59f08a26db543ea4686b5056ef194c25076deb2ef2652b3db0d",
            handle="Shopline",
            merchant_id="684291be1dc1b00060d52b9e",
        )
        self.redirect_uri = "https://192.168.195.6"
        self.shopline.set_access_token(
            "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI4YjY0NzVmMzc3YzFiZjllN2YzYzgwZGM3ZmVkZWM5NyIsImRhdGEiOnsibWVyY2hhbnRfaWQiOiI2ODQyOTFiZTFkYzFiMDAwNjBkNTJiOWUiLCJhcHBsaWNhdGlvbl9pZCI6IjY4NDI5MzAzMmJkYTMwMDAwYWFhMWZhZCJ9LCJpc3MiOiJodHRwczovL2RldmVsb3BlcnMuc2hvcGxpbmVhcHAuY29tIiwiYXVkIjpbXSwic3ViIjoiNjg0MjkxYmUxZGMxYjAwMDYwZDUyYjllIn0.FKHziGmeOG3N4j73qsRBojvoTnZUq8B_tJIjb4WCRIQ"
        )

    def test_get_customers(self):
        customers = self.shopline.customer.get_customers()
        self.assertIsInstance(customers.get("items"), list, "success")


if __name__ == "__main__":
    unittest.main()
