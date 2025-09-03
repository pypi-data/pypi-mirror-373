from sysstra.orders import add_order_to_redis, fetch_orders_list
from sysstra.sysstra_utils import send_order_alert
from sysstra.config import config
import requests
import datetime
import json
orders_url = config.get("orders_url")


def place_lt_order(tradingsymbol, quantity, transaction_type, order_type, lot_size=15, exchange="NSE",
                   credential_id=None, trigger_price=None, order_price=None):
    """ Function to Place Live Trading Order """
    try:

        if order_type == "MARKET":
            order_data_params = {"symbol": tradingsymbol,
                                 "exchange": exchange,
                                 "transaction_type": transaction_type,
                                 "quantity": quantity * lot_size,
                                 "order_type": order_type,
                                 "product": "MIS",
                                 "validity": "DAY"}

            order_response = place_live_order(credential_id=credential_id, order_details=order_data_params)

            if order_response["status"] == "success":
                return "success", order_response
            else:
                return "error", order_response

        elif order_type == "STOPLOSS":
            order_data_params = {"symbol": tradingsymbol, "exchange": exchange,
                                 "transaction_type": transaction_type,
                                 "quantity": quantity * lot_size, "product": "MIS", "validity": "DAY",
                                 "order_type": "STOPLOSS", "trigger_price": trigger_price, "price": order_price}
            order_response = place_live_order(credential_id=credential_id, order_details=order_data_params)

            if order_response["status"] == "success":
                return "success", order_response["order_id"]
            else:
                return "error", order_response

        elif order_type == "LIMIT":
            order_data_params = {"symbol": tradingsymbol, "exchange": exchange,
                                 "transaction_type": transaction_type, "quantity": quantity * lot_size,
                                 "product": "MIS", "validity": "TTL", "validity_ttl": 1,
                                 "order_type": "LIMIT",  "price": order_price}

            order_response = place_live_order(credential_id=credential_id, order_details=order_data_params)

            if order_response["status"] == "success":
                return "success", order_response["order_id"]
            else:
                return "error", order_response

    except Exception as e:
        print(f"Exception in placing live trade : {e}")
        return "failed", None


def save_lt_order(app_db_cursor, redis_cursor, orders_list, tradingsymbol, quantity, quantity_left=0,
                  position_type="LONG", transaction_type="BUY", trade_action="ENTRY", order_type="MARKET",
                  exit_type=None, params=None, market_type="options", expiry=None, trigger_price=None, lot_size=25,
                  user_id=None, strategy_id=None, request_id=None, exchange="NSE", exchange_timestamp=None,
                  order_id=None, broker_response=None, sl_order_id=None):
    """ Function to save order in Database """
    try:
        order_dict = {"exchange": exchange,
                      "user_id": user_id,
                      "strategy_id": strategy_id,
                      "request_id": request_id,
                      "tradingsymbol": tradingsymbol,
                      "quantity": quantity,
                      "quantity_left": quantity_left,
                      "position_type": position_type,
                      "transaction_type": transaction_type,
                      "trade_action": trade_action,
                      "order_type": order_type,
                      "exit_type": exit_type,
                      "lot_size": lot_size,
                      "exchange_timestamp": exchange_timestamp,
                      "status": "COMPLETE",
                      "trigger_price": trigger_price,
                      "order_id": order_id}

        if sl_order_id:
            order_dict["sl_order_id"] = sl_order_id

        order_dict["order_timestamp"] = exchange_timestamp
        order_dict["date"] = datetime.datetime.strptime(str(datetime.datetime.today().date()), '%Y-%m-%d')
        order_dict["day"] = order_dict["date"].strftime("%A")

        if params:
            order_dict.update(params)

        # Creating New Dict for saving data in to db
        lt_order_dict = {}
        for key in order_dict.keys():
            lt_order_dict[key] = order_dict[key]

        lt_order_dict["order_id"] = order_id
        lt_order_dict["broker_response"] = broker_response
        lt_order_dict["trade_action"] = lt_order_dict["trade_action"]

        # Saving Order Details to Database
        app_db_cursor["lt_orders"].insert_one(lt_order_dict)

        # Converting Dict to String
        redis_dict = {k: str(v) if not isinstance(v, (int, float)) else v for k, v in order_dict.items()}

        # redis_dict["quantity_left"] = str(quantity_left)

        # Adding Order to Redis
        add_order_to_redis(redis_cursor=redis_cursor, request_id=str(request_id), order_dict=redis_dict, mode="lt")

        # Creating Alert Dict
        alert_dict = {"user_id": str(order_dict["user_id"]),
                      "strategy_id": str(order_dict["strategy_id"]),
                      "request_id": str(order_dict["request_id"]),
                      "mode": "lt",
                      "exit_type": exit_type,
                      "symbol": tradingsymbol,
                      "quantity": quantity,
                      "price": trigger_price,
                      "quantity_left": quantity_left,
                      "trade_action": trade_action,
                      "position_type": position_type,
                      "template_id": 0
                      }
        print(f"Alert Dict : {alert_dict}")
        send_order_alert(alert_dict)

        orders_list = fetch_orders_list(redis_cursor=redis_cursor, request_id=str(request_id))
        return "success", orders_list

    except Exception as e:
        print(f"Exception in Saving Order in DB : {e}")
        return "failed", orders_list


def save_lt_trade(app_db_cursor, redis_cursor, trade_dict):
    """Function to save order in Database"""
    try:
        app_db_cursor["lt_trades"].insert_one(trade_dict)
        request_id = trade_dict["request_id"]
        redis_cursor.rpush(str(request_id) + "_trades", json.dumps(trade_dict, default=str))
        redis_cursor.publish(str(request_id) + "_trades", json.dumps(trade_dict, default=str))
        redis_cursor.publish(f"{trade_dict['user_id']}_lt_trades", json.dumps(trade_dict, default=str))
    except Exception as e:
        print(f"Exception in saving LT trade in DB : {e}")
        pass


def place_live_order(credential_id, order_details):
    """Function to place live trade order via REST API"""
    try:
        print("Placing Live Trade Order")
        request_dict = {"credential_id": str(credential_id),
                        "order_params": order_details}
        print(f"request_dict : {request_dict}")

        response = requests.post(url=orders_url+"place_order", json=request_dict)
        print("******** Order Placement Response *********")
        print(response.json())
        return response.json()
    except Exception as e:
        print(f"Exception in placing live trade order : {e}")
        return None


def modify_live_order(credential_id, order_details):
    """Function to Modify Live Order"""
    try:
        print("* Modifying Live Order")
        request_dict = {"credential_id": str(credential_id),
                        "order_params": order_details}
        print(f"request_dict : {request_dict}")

        response = requests.post(url=orders_url + "modify_order", json=request_dict)
        print("******** Order Placement Response *********")
        print(response.json())
        return response.json()
    except Exception as e:
        print(f"Exception in Modify Live Order : {e}")
        pass


def check_order_status(credential_id, order_id, exchange):
    """Function to fetch current order status"""
    try:
        print("Fetching Order Status")
        request_dict = {
            "credential_id": str(credential_id),
            "order_params": {
                'order_id': order_id,
                "exchange": exchange
            }
        }
        # last_order = requests.post(url=orders_url+"get_order_by_id", params={"credential_id": credential_id, 'order_details': json.dumps(get_order_params)}).json()
        last_order = requests.post(url=orders_url+"check_order_status", json=request_dict).json()
        print(f"order_status_response : {last_order}")

        if last_order["status"] == "COMPLETED":
            last_order["timestamp"] = datetime.datetime.strptime(str(last_order["timestamp"]), '%Y-%m-%d %H:%M:%S')
            return "success", last_order

        elif last_order["status"] == "CANCELLED" or last_order["status"] == "REJECTED":
            return "cancelled", None
        else:
            return "error", None
    except Exception as e:
        print(f"Exception in Check Order Status Function : {e}")
        return "failed", None