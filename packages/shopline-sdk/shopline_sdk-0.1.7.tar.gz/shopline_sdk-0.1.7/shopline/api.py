#!/usr/bin/python3
# @Time    : 2025-06-16
# @Author  : Kevin Kong (kfx2007@163.com)

from shopline.comm import Comm
from shopline.customer import Customer
from shopline.orders import Order
from shopline.product import Product, AddonProduct, Gift


class ShoplineAPI:
    """Shopline API SDK"""

    def __init__(self, client_id, client_secretkey, handle=None, merchant_id=None):
        """
        Initialize the Shopline API client.

        :param client_id: The client ID for the Shopline API.
        :param client_secretkey: The client secret key for the Shopline API.
        :param merchant_id: Optional merchant ID for the Shopline API.
        
        :return ShoplineAPI: An instance of the ShoplineAPI class.
        """
        self.client_id = client_id
        self.client_secretkey = client_secretkey
        self.merchant_id = merchant_id
        self.handle = handle
        
    def set_access_token(self, access_token):
        """
        Set the access token for the Shopline API.

        :param access_token: The access token for the Shopline API.
        """
        self.access_token = access_token

    comm = Comm()
    customer = Customer()
    order = Order()
    product = Product()
    addon_product = AddonProduct()
    gift = Gift()



    

    
    
