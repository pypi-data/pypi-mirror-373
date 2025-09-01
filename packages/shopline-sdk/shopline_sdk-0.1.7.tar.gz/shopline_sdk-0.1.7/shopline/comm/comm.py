#!/usr/bin/python3
# @Time    : 2025-06-16
# @Author  : Kevin Kong (kfx2007@163.com)

import requests
import json
from .exceptions import ShoplineAuthenticationException

URL = "https://developers.shoplineapp.com"
API_URL = "https://open.shopline.io/v1"


class Comm(object):
    """封装公共请求"""

    def __get__(self, instance, owner):
        self.client_id = instance.client_id
        self.client_secretkey = instance.client_secretkey
        self.merchant_id = instance.merchant_id
        self.handle = instance.handle
        self.access_token = instance.access_token if hasattr(instance, 'access_token') else None
        return self

    def get_oauth_url(self, redirect_uri, scope="addon_products"):
        """
        Get the OAuth URL for Shopline API.

        :param redirect_uri: The redirect URI for OAuth.
        :return: The OAuth URL.
        """

        return f"{URL}/oauth/authorize?client_id={self.client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"

    def get_access_token(self, code, redirect_uri):
        """
        Get the access token for Shopline API.

        :return: The access token.
        """
        headers = {"Content-Type": "application/json"}
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secretkey,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code,
        }
        
        return requests.post(f"{URL}/oauth/token", headers=headers, data=json.dumps(data)).json()

    def refresh_access_token(self, refresh_token, redirect_uri):
        """
        Refresh the access token for Shopline API.

        :param refresh_token: The refresh token.
        :return: The new access token.
        """
        headers = {"Content-Type": "application/json"}
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secretkey,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": redirect_uri,
        }

        return requests.post(f"{URL}/oauth/token", headers=headers, json=data).json()
    
    def get_headers(self, access_token):
        """
        Get the headers for Shopline API requests.

        :param access_token: The access token.
        :return: The headers.
        """
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.handle,
        }
        
    def get(self, url, params=None):
        """
        Make a GET request to the Shopline API.
        :param url: The URL for the request.
        :param params: The query parameters for the request.
        :param access_token: The access token for authentication.
        :return: The response from the API.
        """
        if not self.access_token:
            raise ShoplineAuthenticationException("Invid Access Token")
        headers = self.get_headers(self.access_token)
        response = requests.get(url, headers=headers, params=params)
        return response


    def post(self, url, json=None):
        """
        Make a POST request to the Shopline API.
        :param url: The URL for the request.
        :param json: The JSON payload for the request.
        :param access_token: The access token for authentication.
        :return: The response from the API.
        """
        if not self.access_token:
            raise ShoplineAuthenticationException("Invid Access Token")
        headers = self.get_headers(self.access_token)
        response = requests.post(url, headers=headers, json=json)
        return response

    def patch(self, url, json=None):
        """
        Make a PATCH request to the Shopline API.
        :param url: The URL for the request.
        :param json: The JSON payload for the request.
        :param access_token: The access token for authentication.
        :return: The response from the API.
        """
        if not self.access_token:
            raise ShoplineAuthenticationException("Invid Access Token")
        headers = self.get_headers(self.access_token)
        response = requests.patch(url, headers=headers, json=json)
        return response