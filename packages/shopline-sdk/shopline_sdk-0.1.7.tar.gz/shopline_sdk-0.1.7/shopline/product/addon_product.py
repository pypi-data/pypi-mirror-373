#!/usr/bin/python3
# @Time    : 2025-08-31
# @Author  : Kevin Kong (kfx2007@163.com)

from shopline.comm import Comm
from shopline.comm import API_URL

class AddonProduct(Comm):
    
    def gets(self):
        """
        Get detailed information of add-on products.
        撈取加購品的詳細資訊
            
        Returns:
            dict: Response containing addon products data and pagination info
        """
        url = f"{API_URL}/addon_products"

        return self.get(url).json()
    
    def search(self, id=None, page=1, per_page=24, status=None, sort_by=None, 
               sku=None, quantity=None, updated_at=None, created_at=None):
        """
        Search add-on products with specific conditions.
        利用特殊條件搜尋加購品列表。
        
        
        param: id (str, optional): Addon Product ID
        param: page (int, optional): Page Number (default: 1)
        param: per_page (int, optional): Numbers of Add-on Products Per Page (default: 24)
        param: status (str, optional): Status ('active' or 'draft')
        param: sort_by (str, optional): Sort order ('desc' or 'asc')
        param: sku (str, optional): SKU
        param: quantity (int/str, optional): Quantity (supports operators like 'not:100', 'lt:100', etc.)
        param: updated_at (str, optional): Update Time (supports operators)
        param: created_at (str, optional): Created Time (supports operators)
            
        Returns:
            dict: Response containing search results and pagination info
        """
        url = f"{API_URL}/addon_products/search"
        
        params = {}
        if id is not None:
            params['id'] = id
        if page != 1:
            params['page'] = page
        if per_page != 24:
            params['per_page'] = per_page
        if status is not None:
            params['status'] = status
        if sort_by is not None:
            params['sort_by'] = sort_by
        if sku is not None:
            params['sku'] = sku
        if quantity is not None:
            params['quantity'] = quantity
        if updated_at is not None:
            params['updated_at'] = updated_at
        if created_at is not None:
            params['created_at'] = created_at
        
        return self.get(url, params=params).json()
    
    
    def create(self, title_translations, media_ids=None, unlimited_quantity=None, 
               start_at=None, end_at=None, main_products=None, location_id=None, 
               sku=None, cost=None, weight=None, product_id=None, tax_type=None, 
               oversea_tax_type=None):
        """
        Create a new add-on product.
        創建新的加購品。
        
        
        param: title_translations (dict): Addon Product Title (required)
        param: media_ids (list, optional): Array of Media ID
        param: unlimited_quantity (bool, optional): Addon Product unlimited quantity or not
        param: start_at (str, optional): Addon Product start at
        param: end_at (str, optional): Addon Product end at
        param: main_products (list, optional): Main Products Information
        param: location_id (str, optional): Custom location id
        param: sku (str, optional): Addon Product SKU
        param: cost (dict, optional): Cost
        param: weight (float, optional): Weight
        param: product_id (str, optional): Shared Product ID
        param: tax_type (str, optional): Tax type ("1": 應稅, "3": 免稅)
        param: oversea_tax_type (str, optional): Oversea tax type ("1": 應稅, "2": 零稅率-非經海關出口, "5": 零稅率-經海關出口)
        
        Returns:
            dict: Response containing created addon product data
        """
        url = f"{API_URL}/addon_products"
        
        data = {
            'title_translations': title_translations
        }
        
        if media_ids is not None:
            data['media_ids'] = media_ids
        if unlimited_quantity is not None:
            data['unlimited_quantity'] = unlimited_quantity
        if start_at is not None:
            data['start_at'] = start_at
        if end_at is not None:
            data['end_at'] = end_at
        if main_products is not None:
            data['main_products'] = main_products
        if location_id is not None:
            data['location_id'] = location_id
        if sku is not None:
            data['sku'] = sku
        if cost is not None:
            data['cost'] = cost
        if weight is not None:
            data['weight'] = weight
        if product_id is not None:
            data['product_id'] = product_id
        if tax_type is not None:
            data['tax_type'] = tax_type
        if oversea_tax_type is not None:
            data['oversea_tax_type'] = oversea_tax_type
        
        return self.post(url, data=data).json()
    
    def update(self, addon_product_id, title_translations=None, media_ids=None, 
               unlimited_quantity=None, start_at=None, end_at=None, main_products=None, 
               location_id=None, sku=None, cost=None, weight=None, product_id=None, 
               tax_type=None, oversea_tax_type=None):
        """
        Update an existing add-on product.
        更新現有的加購品。
        
        
        param: addon_product_id (str): Addon Product ID (required)
        param: title_translations (dict, optional): Addon Product Title
        param: media_ids (list, optional): Array of Media ID
        param: unlimited_quantity (bool, optional): Addon Product unlimited quantity or not
        param: start_at (str, optional): Addon Product start at
        param: end_at (str, optional): Addon Product end at
        param: main_products (list, optional): Main Products Information
        param: location_id (str, optional): Custom location id
        param: sku (str, optional): Addon Product SKU
        param: cost (dict, optional): Cost
        param: weight (float, optional): Weight
        param: product_id (str, optional): Shared Product ID
        param: tax_type (str, optional): Tax type ("1": 應稅, "3": 免稅)
        param: oversea_tax_type (str, optional): Oversea tax type ("1": 應稅, "2": 零稅率-非經海關出口, "5": 零稅率-經海關出口)
        
        Returns:
            dict: Response containing updated addon product data
        """
        url = f"{API_URL}/addon_products/{addon_product_id}"
        
        data = {}
        
        if title_translations is not None:
            data['title_translations'] = title_translations
        if media_ids is not None:
            data['media_ids'] = media_ids
        if unlimited_quantity is not None:
            data['unlimited_quantity'] = unlimited_quantity
        if start_at is not None:
            data['start_at'] = start_at
        if end_at is not None:
            data['end_at'] = end_at
        if main_products is not None:
            data['main_products'] = main_products
        if location_id is not None:
            data['location_id'] = location_id
        if sku is not None:
            data['sku'] = sku
        if cost is not None:
            data['cost'] = cost
        if weight is not None:
            data['weight'] = weight
        if product_id is not None:
            data['product_id'] = product_id
        if tax_type is not None:
            data['tax_type'] = tax_type
        if oversea_tax_type is not None:
            data['oversea_tax_type'] = oversea_tax_type
        
        return self.put(url, data=data).json()
    
    def update_quantity(self, addon_product_id, quantity, replace=True):
        """
        Update the quantity of an add-on product.
        更新加購品的數量。
        
        param: addon_product_id (str): Addon Product ID (required)
        param: quantity (int): Quantity to add/subtract or replace (required)
        param: replace (bool, optional): Whether to replace the original quantity (default: True)
                                       True: replace the quantity
                                       False: increase/decrease the quantity
        
        Returns:
            dict: Response containing updated addon product quantity data
        """
        url = f"{API_URL}/addon_products/{addon_product_id}/update_quantity"
        
        data = {
            'quantity': quantity,
            'replace': replace
        }
        
        return self.put(url, data=data).json()
    
    def update_quantity_by_sku(self, sku, quantity, replace=True):
        """
        Update the quantity of an add-on product by SKU.
        根據 SKU 更新加購品的數量。
        
        param: sku (str): Addon Product SKU (required)
        param: quantity (int): Quantity to add/subtract or replace (required)
        param: replace (bool, optional): Whether to replace the original quantity (default: True)
                                       True: replace the quantity
                                       False: increase/decrease the quantity
        
        Returns:
            dict: Response containing updated addon product quantity data
        """
        url = f"{API_URL}/addon_products/update_quantity"
        
        data = {
            'sku': sku,
            'quantity': quantity,
            'replace': replace
        }
        
        return self.put(url, data=data).json()