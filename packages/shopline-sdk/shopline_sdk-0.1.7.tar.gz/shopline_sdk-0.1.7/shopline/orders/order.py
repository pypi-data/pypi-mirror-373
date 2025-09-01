#!/usr/bin/python3
# @Time    : 2025-06-17
# @Author  : Kevin Kong (kfx2007@163.com)

from shopline.comm import Comm
from shopline.comm import API_URL

class Order(Comm):
    
    def get_orders(self, updated_after=None, updated_before=None,created_after=None, created_before=None, order_ids=[], per_page=50, page=1, sort_by="asc", previous_id=None):
        """
        Get the list of orders.
        :param updated_after: Filter orders updated after this date.
        :param updated_before: Filter orders updated before this date.
        :param created_after: Filter orders created after this date.
        :param created_before: Filter orders created before this date.
        :param order_ids: List of specific order IDs to retrieve.
        :param per_page: Number of orders per page.
        :param page: Page number to retrieve.
        :param sort_by: Field to sort the orders by.
        :param previous_id: ID of the last order from the previous page, used for pagination
        
        :return: List of orders.
        """
        
        url = f"{API_URL}/orders"
        params = {
            "updated_after": updated_after,
            "updated_before": updated_before,
            "created_after": created_after,
            "created_before": created_before,
            "order_ids": order_ids,
            "per_page": per_page,
            "page": page,
            "sort_by": sort_by,
            "previous_id": previous_id
        }
        response = self.get(url, params=params)
        return response.json() if response.status_code == 200 else None
    
    def search(
        self,
        previous_id=None,
        per_page=24,
        page=1,
        query=None,
        shipped_before=None,
        shipped_after=None,
        arrived_before=None,
        arrived_after=None,
        collected_before=None,
        collected_after=None,
        returned_before=None,
        returned_after=None,
        cancelled_before=None,
        cancelled_after=None,
        paid_before=None,
        paid_after=None,
        updated_before=None,
        updated_after=None,
        status=None,
        statuses=None,
        payment_id=None,
        payment_status=None,
        delivery_address=None,  # dict
        delivery_option_id=None,
        delivery_option_type=None,
        delivery_status=None,
        delivery_statuses=None,
        affiliate_data=None,  # dict
        created_before=None,
        created_after=None,
        created_by=None,
        order_number=None,
        customer_id=None,
        customer_email=None,
        name=None,
        phone_number=None,
        delivery_data_tracking_number=None,
        promotion_id=None,
        item_id=None,
        delivery_data=None  # dict, e.g. scheduled_delivery_date_before/after
    ):
        """
        Search orders with filters against /orders/search.

        :param previous_id: ID of the last order from the previous page, used for pagination
        :param previous_id: ID of the last order from the previous page, used for pagination.
        :param per_page: Maximum number of records to return per page (capped at 999). Default: 24.
        :param page: Page number for offset pagination when previous_id is not used. Default: 1.
        :param query: Free-text query to search orders (e.g., order number, customer name/email).
        :param shipped_before: Return orders shipped strictly before this timestamp (ISO 8601 string or datetime).
        :param shipped_after: Return orders shipped at or after this timestamp (ISO 8601 string or datetime).
        :param arrived_before: Return orders arrived strictly before this timestamp (ISO 8601 string or datetime).
        :param arrived_after: Return orders arrived at or after this timestamp (ISO 8601 string or datetime).
        :param collected_before: Return orders collected strictly before this timestamp (ISO 8601 string or datetime).
        :param collected_after: Return orders collected at or after this timestamp (ISO 8601 string or datetime).
        :param returned_before: Return orders returned strictly before this timestamp (ISO 8601 string or datetime).
        :param returned_after: Return orders returned at or after this timestamp (ISO 8601 string or datetime).
        :param cancelled_before: Return orders cancelled strictly before this timestamp (ISO 8601 string or datetime).
        :param cancelled_after: Return orders cancelled at or after this timestamp (ISO 8601 string or datetime).
        :param paid_before: Return orders paid strictly before this timestamp (ISO 8601 string or datetime).
        :param paid_after: Return orders paid at or after this timestamp (ISO 8601 string or datetime).
        :param updated_before: Return orders updated strictly before this timestamp (ISO 8601 string or datetime).
        :param updated_after: Return orders updated at or after this timestamp (ISO 8601 string or datetime).
        :param status: Filter by a single order status (string).
        :param statuses: Filter by one or more order statuses (string or iterable of strings). Sent as statuses[] in query.
        :param payment_id: Filter by payment/transaction ID (string).
        :param payment_status: Filter by payment status (e.g., paid, unpaid, refunded).
        :param delivery_address: Nested filters for delivery address as a dict (e.g., {"country": "...", "city": "..."}). Flattened as delivery_address[key]=value.
        :param delivery_option_id: Filter by delivery/shipping option ID.
        :param delivery_option_type: Filter by delivery option type (e.g., standard, express, pickup).
        :param delivery_status: Filter by a single delivery/shipment status (string).
        :param delivery_statuses: Filter by one or more delivery statuses (string or iterable of strings). Sent as delivery_statuses[] in query.
        :param affiliate_data: Nested filters for affiliate metadata as a dict (e.g., {"source": "...", "campaign": "..."}). Flattened as affiliate_data[key]=value.
        :param created_before: Return orders created strictly before this timestamp (ISO 8601 string or datetime).
        :param created_after: Return orders created at or after this timestamp (ISO 8601 string or datetime).
        :param created_by: Filter by creator identifier (e.g., staff ID, system).
        :param order_number: Filter by order number (human-readable).
        :param customer_id: Filter by customer ID.
        :param customer_email: Filter by customer email address.
        :param name: Filter by customer name.
        :param phone_number: Filter by customer phone number.
        :param delivery_data_tracking_number: Filter by shipment tracking number.
        :param promotion_id: Filter orders associated with a specific promotion ID.
        :param item_id: Filter orders containing a specific item/product ID.
        :param delivery_data: Nested filters for delivery-specific data as a dict (e.g., {"scheduled_delivery_date_before": "..."}). Flattened as delivery_data[key]=value.
        :return: Parsed JSON response (dict/list) when the request succeeds (HTTP 200); otherwise None.
        """
        url = f"{API_URL}/orders/search"

        # Cap per_page to API max
        if per_page is not None:
            try:
                per_page = min(int(per_page), 999)
            except Exception:
                pass

        params = {
            "previous_id": previous_id,
            "per_page": per_page,
            "page": page if not previous_id else None,  # follow API note
            "query": query,
            "shipped_before": shipped_before,
            "shipped_after": shipped_after,
            "arrived_before": arrived_before,
            "arrived_after": arrived_after,
            "collected_before": collected_before,
            "collected_after": collected_after,
            "returned_before": returned_before,
            "returned_after": returned_after,
            "cancelled_before": cancelled_before,
            "cancelled_after": cancelled_after,
            "paid_before": paid_before,
            "paid_after": paid_after,
            "updated_before": updated_before,
            "updated_after": updated_after,
            "status": status,
            "payment_id": payment_id,
            "payment_status": payment_status,
            "delivery_option_id": delivery_option_id,
            "delivery_option_type": delivery_option_type,
            "delivery_status": delivery_status,
            "created_before": created_before,
            "created_after": created_after,
            "created_by": created_by,
            "order_number": order_number,
            "customer_id": customer_id,
            "customer_email": customer_email,
            "name": name,
            "phone_number": phone_number,
            "delivery_data_tracking_number": delivery_data_tracking_number,
            "promotion_id": promotion_id,
            "item_id": item_id,
        }

        # List parameters -> use [] form as API examples show
        if statuses:
            params["statuses[]"] = list(statuses) if isinstance(statuses, (list, tuple, set)) else [statuses]
        if delivery_statuses:
            params["delivery_statuses[]"] = list(delivery_statuses) if isinstance(delivery_statuses, (list, tuple, set)) else [delivery_statuses]

        # Flatten nested dicts using bracket notation: key[subkey]=value
        def _flatten(prefix, data):
            if not isinstance(data, dict):
                return
            for k, v in data.items():
                if v is None:
                    continue
                params[f"{prefix}[{k}]"] = v

        if delivery_address:
            _flatten("delivery_address", delivery_address)
        if affiliate_data:
            _flatten("affiliate_data", affiliate_data)
        if delivery_data:
            _flatten("delivery_data", delivery_data)

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self.get(url, params=params)
        return response.json() if response.status_code == 200 else None
    
        
    def update(
        self,
        order_id,
        tracking_number=None,
        tracking_url=None,
        delivery_provider_name=None,  # dict: {"zh-hant": "...", "en": "..."}
        ref_order_id=None,            # pass None to clear; empty string will be converted to None
        delivery_data=None,           # dict: location_code, location_name, store_address, recipient_name, recipient_phone
        delivery_address=None,        # dict: country, country_code, address_1, address_2, city, state, postcode
        custom_data=None,             # list[dict]: [{"value": "...", "field_id": "..."}]
    ):
        """
        PATCH /orders/:id
        更新訂單資訊：第三方訂單ID、追蹤資訊、運送資訊與地址、自定義資料。
        """
        url = f"{API_URL}/orders/{order_id}"

        allowed_delivery_data = {
            "location_code",
            "location_name",
            "store_address",
            "recipient_name",
            "recipient_phone",
        }
        allowed_delivery_address = {
            "country",
            "country_code",
            "address_1",
            "address_2",
            "city",
            "state",
            "postcode",
        }

        def _filter(d, allow):
            if not isinstance(d, dict):
                return None
            return {k: v for k, v in d.items() if k in allow and v is not None}

        payload = {}

        if tracking_number is not None:
            payload["tracking_number"] = tracking_number
        if tracking_url is not None:
            payload["tracking_url"] = tracking_url
        if delivery_provider_name:
            payload["delivery_provider_name"] = delivery_provider_name

        if ref_order_id is not None:
            # API requires null to clear, not empty string
            payload["ref_order_id"] = None if ref_order_id == "" else ref_order_id

        if delivery_data:
            filtered_dd = _filter(delivery_data, allowed_delivery_data)
            if filtered_dd:
                payload["delivery_data"] = filtered_dd

        if delivery_address:
            filtered_da = _filter(delivery_address, allowed_delivery_address)
            if filtered_da:
                payload["delivery_address"] = filtered_da

        if custom_data is not None:
            payload["custom_data"] = custom_data

        resp = self.patch(url, json=payload)
        if resp.status_code in (200, 201):
            return resp.json()
        if resp.status_code == 204:
            return True
        return resp
    
    def update_order_status(self, order_id, status, mail_notify=False):
        """
        PATCH /orders/:id/status
        更新訂單狀態。允許狀態：pending, confirmed, completed, cancelled
        注意：平台規則可能限制特定轉換（如已發貨後不可取消等）。
        """
        if not order_id:
            raise ValueError("order_id is required")
        if not status:
            raise ValueError("status is required")

        allowed_statuses = {"pending", "confirmed", "completed", "cancelled"}
        if status not in allowed_statuses:
            raise ValueError(f"status must be one of {sorted(allowed_statuses)}")

        url = f"{API_URL}/orders/{order_id}/status"
        payload = {
            "status": status,
            "mail_notify": bool(mail_notify) if mail_notify is not None else False,
        }

        resp = self.patch(url, json=payload)
        if resp.status_code in (200, 201):
            return resp.json()
        if resp.status_code == 204:
            return True
        return resp
    
    def update_delivery_status(
        self,
        order_id,
        delivery_status,
        mail_notify=False,
        timestamp=None,
    ):
        """
        PATCH /orders/:id/delivery_status
        更新送貨/物流狀態。允許：pending, shipped, arrived, collected, returned, cancelled
        可選 timestamp：ISO8601 字串，會依狀態自動填入對應欄位（如 shipped_at、arrived_at...）。
        """
        if not order_id:
            raise ValueError("order_id is required")
        if not delivery_status:
            raise ValueError("delivery_status is required")

        allowed_delivery_statuses = {
            "pending",
            "shipped",
            "arrived",
            "collected",
            "returned",
            "cancelled",
        }
        if delivery_status not in allowed_delivery_statuses:
            raise ValueError(f"delivery_status must be one of {sorted(allowed_delivery_statuses)}")

        url = f"{API_URL}/orders/{order_id}/order_delivery_status"
        payload = {
            "status": delivery_status,
            "mail_notify": bool(mail_notify) if mail_notify is not None else False,
        }

        # Optional timestamp field mapped by delivery status
        status_ts_field = {
            "shipped": "shipped_at",
            "arrived": "arrived_at",
            "collected": "collected_at",
            "returned": "returned_at",
            "cancelled": "cancelled_at",
        }
        if timestamp and delivery_status in status_ts_field:
            payload[status_ts_field[delivery_status]] = timestamp
        resp = self.patch(url, json=payload)
        if resp.status_code in (200, 201):
            return resp.json()
        if resp.status_code == 204:
            return True
        return resp

    def update_payment_status(
        self,
        order_id,
        status,
        mail_notify=False,
    ):
        """
        PATCH /orders/:id/order_payment_status
        更新訂單付款狀態。允許：pending, failed, expired, completed, refunding, refunded
        """
        if not order_id:
            raise ValueError("order_id is required")
        if not status:
            raise ValueError("status is required")

        allowed_statuses = {
            "pending",
            "failed",
            "expired",
            "completed",
            "refunding",
            "refunded",
        }
        if status not in allowed_statuses:
            raise ValueError(f"status must be one of {sorted(allowed_statuses)}")

        url = f"{API_URL}/orders/{order_id}/order_payment_status"
        payload = {
            "status": status,
            "mail_notify": bool(mail_notify) if mail_notify is not None else False,
        }

        resp = self.patch(url, json=payload)
        if resp.status_code in (200, 201):
            return resp.json()
        if resp.status_code == 204:
            return True
        return resp