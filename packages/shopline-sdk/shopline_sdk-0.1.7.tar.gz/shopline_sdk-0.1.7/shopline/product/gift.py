#!/usr/bin/python3
# @Time    : 2025-08-31
# @Author  : Kevin Kong (kfx2007@163.com)

from shopline.comm import Comm
from shopline.comm import API_URL

class Gift(Comm):
    
    def gets(self):
        """
        Get detailed information of gifts.
        撈取贈品的詳細資訊
        
        Returns:
            dict: Gift information response
        """
        response =  self.get(f"{API_URL}/gifts")
        print(response.content)
        return response.json() if response.status_code == 200 else None
 
    def search(self, id=None, page=1, per_page=24, status=None, sort_by=None, 
              sku=None, quantity=None, updated_at=None, created_at=None):
        """
        Search gifts with specific conditions.
        利用特殊條件搜尋贈品列表。
        
        
        param: id (str, optional): Gift's ID 贈品 ID
        param: page (int, optional): Page Number 頁數（第n頁）. Defaults to 1.
        param: per_page (int, optional): Numbers of gifts per page 每頁顯示 n 筆資料. Defaults to 24.
        param: status (str, optional): Status 贈品狀態 (active/draft)
        param: sort_by (str, optional): Sort by created_at (desc/asc)
        param: sku (str, optional): SKU 貨物編號
        param: quantity (str, optional): Quantity 數量 (supports operators: =, not:, lt:, lte:, gt:, gte:)
        param: updated_at (str, optional): Updated Time 更新時間 (supports operators: =, not:, lt:, lte:, gt:, gte:)
        param: created_at (str, optional): Created Time 創建時間 (supports operators: =, not:, lt:, lte:, gt:, gte:)
        
        Returns:
            dict: Search results response
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if id is not None:
            params['id'] = id
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
        
        return self.get(f"{API_URL}/gifts/search", params=params).json()
    
    def create(self, title_translations, media_ids=None, unlimited_quantity=None, 
               sku=None, cost=None, weight=None, quantity=None, product_id=None):
        """
        Create a new gift.
        創建新贈品
        
        
        param: title_translations (dict): Gift Title 贈品名稱 e.g. {"en": "create by open api"}
        param: media_ids (list, optional): Array of Media ID 一組圖片ID e.g. ["603f06f7f6ba0c00451d0f12"]
        param: unlimited_quantity (bool, optional): Gift unlimited quantity or not 贈品是否無限數量
        param: sku (str, optional): Gift SKU 贈品SKU e.g. "SKU-456344881"
        param: cost (dict, optional): Gift Cost 贈品成本 e.g. {"dollars": 12}
        param: weight (float, optional): Gift Weight 贈品重量 e.g. 12.1
        param: quantity (float, optional): Gift Quantity 贈品數量 e.g. 200
        param: product_id (str, optional): Shared Product ID 共用商品 e.g. "603f06f7f6ba0c00451d0f12"
        
        Returns:
            dict: Create gift response
        """
        data = {
            'title_translations': title_translations
        }
        
        if media_ids is not None:
            data['media_ids'] = media_ids
        if unlimited_quantity is not None:
            data['unlimited_quantity'] = unlimited_quantity
        if sku is not None:
            data['sku'] = sku
        if cost is not None:
            data['cost'] = cost
        if weight is not None:
            data['weight'] = weight
        if quantity is not None:
            data['quantity'] = quantity
        if product_id is not None:
            data['product_id'] = product_id
        
        return self.post(f"{API_URL}/gifts", data=data).json()
    
    def update(self, gift_id, title_translations=None, media_ids=None, unlimited_quantity=None, 
               sku=None, cost=None, weight=None, quantity=None):
        """
        Update a gift.
        更新贈品
        
        param: gift_id (str): Gift ID 贈品ID
        param: title_translations (dict, optional): Gift Title 贈品名稱 e.g. {"en": "create by open api"}
        param: media_ids (list, optional): Array of Media ID 一組圖片ID e.g. ["603f06f7f6ba0c00451d0f12"]
        param: unlimited_quantity (bool, optional): Gift unlimited quantity or not 贈品是否無限數量
        param: sku (str, optional): Gift SKU 贈品SKU e.g. "SKU-456344881"
        param: cost (dict, optional): Gift Cost 贈品成本 e.g. {"dollars": 12}
        param: weight (float, optional): Gift Weight 贈品重量 e.g. 12.1
        param: quantity (float, optional): Gift Quantity 贈品數量 e.g. 200
        
        Returns:
            dict: Update gift response
        """
        data = {}
        
        if title_translations is not None:
            data['title_translations'] = title_translations
        if media_ids is not None:
            data['media_ids'] = media_ids
        if unlimited_quantity is not None:
            data['unlimited_quantity'] = unlimited_quantity
        if sku is not None:
            data['sku'] = sku
        if cost is not None:
            data['cost'] = cost
        if weight is not None:
            data['weight'] = weight
        if quantity is not None:
            data['quantity'] = quantity
        
        return self.put(f"{API_URL}/gifts/{gift_id}", data=data).json()
    
    def update_quantity(self, gift_id, quantity):
        """
        Update gift quantity.
        更新贈品數量
        
        param: gift_id (str): Gift ID 贈品ID
        param: quantity (float): Gift Quantity 贈品數量 e.g. 200
        
        Returns:
            dict: Update gift quantity response
        """
        data = {
            'quantity': quantity
        }
        
        return self.put(f"{API_URL}/gifts/{gift_id}", data=data)
    
    def update_quantity_by_sku(self, sku, quantity, replace=True):
        """
        Update gift quantity by SKU.
        根據 SKU 更新贈品數量
        
        param: sku (str): Gift's SKU 贈品的商品貨號
        param: quantity (int): Quantity (新增/減少)贈品數量
        param: replace (bool, optional): Whether replacing the original quantity 是否取代原本數量
                                       - True: replace the quantity with the number you provided 取代原本數量
                                       - False: increase/decrease the quantity with the number you provided 增加/減少數量
                                       Default: True
        
        Returns:
            dict: Update gift quantity response
        """
        data = {
            'sku': sku,
            'quantity': quantity,
            'replace': replace
        }
        
        return self.put(f"{API_URL}/gifts/update_quantity", data=data).json()