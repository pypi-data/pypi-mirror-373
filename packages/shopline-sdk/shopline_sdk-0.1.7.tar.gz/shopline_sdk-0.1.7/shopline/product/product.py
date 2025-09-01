#!/usr/bin/python3
# @Time    : 2025-06-17
# @Author  : Kevin Kong (kfx2007@163.com)

from shopline.comm import Comm
from shopline.comm import API_URL

class Product(Comm):
    
    def get_products(
        self,
        sort_by: str = "desc",
        per_page: int = 24,
        page: int = 1,
        excludes: list = None,
        with_product_set: bool = False,
        includes: list = None,
        fields: list = None,
        id: str = None,
        previous_id: str = None,
        include_fields: list = None,
        updated_after: str = None,
        updated_before: str = None,
    ):
        """
        Fetch products based on the provided parameters.

        :param sort_by: Sort the list by creation time, "asc" or "desc", default "desc".
        :param per_page: Number of items to fetch, default is 24.
        :param page: Page number to start fetching, default is 1.
        :param excludes: List of fields to exclude.
        :param with_product_set: Include product set details if True.
        :param includes: List of fields to include.
        :param fields: List of specific fields to return.
        :param id: Specific product IDs to fetch.
        :param previous_id: Previous ID of the last fetched item.
        :param include_fields: Additional attributes to include in the response.
        :param updated_after: Fetch products updated after this UTC time.
        :param updated_before: Fetch products updated before this UTC time.
        :return: Response from the API.
        """
        params = {
            "sort_by": sort_by,
            "per_page": per_page,
            "page": page,
            "excludes": excludes,
            "with_product_set": with_product_set,
            "includes": includes,
            "fields": fields,
            "id": id,
            "previous_id": previous_id,
            "include_fields": include_fields,
            "updated_after": updated_after,
            "updated_before": updated_before,
        }
        
        # Remove None values from params
        params = {key: value for key, value in params.items() if value is not None}
        
        # Make the API request
        response = self.get(f"{API_URL}/products", params=params)
        print(response.content)
        return response.json() if response.status_code == 200 else None