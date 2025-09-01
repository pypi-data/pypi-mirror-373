#!/usr/bin/python3
# @Time    : 2025-06-17
# @Author  : Kevin Kong (kfx2007@163.com)

from ..comm.comm import Comm
from ..comm.comm import API_URL


class Customer(Comm):
    
    def get_customers(self, updated_after=None, updated_before=None, per_page=50, page=1, sort_by="asc", previous_id=None):
        """
        Get the list of customers.
        :param updated_after: Filter customers updated after this date.
        :param updated_before: Filter customers updated before this date.
        :param per_page: Number of customers per page.
        :param page: Page number to retrieve.
        :param sort_by: Field to sort the customers by.
        :param previous_id: ID of the last customer from the previous page, used for pagination
        
        :return: List of customers.
        """
        
        url = f"{API_URL}/customers"
        params = {
            "updated_after": updated_after,
            "updated_before": updated_before,
            "per_page": per_page,
            "page": page,
            "sort_by": sort_by,
            "previous_id": previous_id
        }
        response = self.get(url, params=params)
        return response.json() if response.status_code == 200 else None