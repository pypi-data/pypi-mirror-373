import json
import datetime
from bson import ObjectId
from sysstra.sysstra_utils import calculate_brokerage


def add_order_to_redis(rdb_cursor, request_id, order_dict, mode):
    """Function to add order to redis"""
    try:
        rdb_cursor.rpush(str(request_id) + "_orders", json.dumps(order_dict, default=str))
        rdb_cursor.publish(str(request_id) + "_orders", json.dumps(order_dict, default=str))
        rdb_cursor.publish(str(order_dict["user_id"]) + "_{}".format(mode) + "_orders", json.dumps(order_dict, default=str))
    except Exception as e:
        print(f"Exception in adding order in redis : {e}")
        pass


def fetch_orders_list(rdb_cursor, request_id):
    """ Function to fetch an orders list for request_id """
    try:
        orders_list_json = rdb_cursor.lrange(str(request_id)+"_orders", 0, -1)
        orders_list = [json.loads(i) for i in orders_list_json]
        return orders_list
    except Exception as e:
        print(f"Exception in fetching orders list : {e}")
        pass


def fetch_last_order(rdb_cursor, request_id):
    """Function to fetch last order from redis database"""
    try:
        last_order = json.loads(rdb_cursor.lindex(str(request_id) + "_orders", -1))
        return last_order
    except Exception as e:
        print(f"Exception in fetching last order : {e}")
        pass


def check_open_orders(orders_list):
    """ Function to open orders available """
    try:
        if orders_list:
            quantity_dict = {}
            for order in orders_list:
                trade_symbol = order["tradingsymbol"]
                quantity_dict[trade_symbol] = {}
                quantity_dict[trade_symbol]["buy_quantity"] = 0
                quantity_dict[trade_symbol]["sell_quantity"] = 0
                quantity_dict[trade_symbol]["quantity"] = 0
                quantity_dict[trade_symbol]["option_type"] = ""
                quantity_dict[trade_symbol]["strike_price"] = ""
                quantity_dict[trade_symbol]["exit_levels"] = []
                quantity_dict[trade_symbol]["order_timestamp"] = ""
                quantity_dict[trade_symbol]["quantity_left"] = 0
                quantity_dict[trade_symbol]["bnf_price"] = 0
                quantity_dict[trade_symbol]["expiry"] = ""
                quantity_dict[trade_symbol]["sl_order_id"] = ""
                quantity_dict[trade_symbol]["option_order_price"] = 0
                quantity_dict[trade_symbol]["hka_option_order_price"] = 0
                quantity_dict[trade_symbol]["trailing_sl"] = 0

            for order in orders_list:
                trade_symbol = order["tradingsymbol"]
                if order["trade_type"] == "ENTRY":
                    quantity_dict[trade_symbol]["buy_quantity"] = order["quantity"]
                    quantity_dict[trade_symbol]["quantity"] = order["quantity"]
                    quantity_dict[trade_symbol]["option_type"] = order["option_type"]
                    quantity_dict[trade_symbol]["strike_price"] = order["strike_price"]
                    quantity_dict[trade_symbol]["trigger_price"] = order["trigger_price"]
                    quantity_dict[trade_symbol]["order_timestamp"] = datetime.datetime.strptime(str(order["order_timestamp"]), '%Y-%m-%d %H:%M:%S')
                    quantity_dict[trade_symbol]["quantity_left"] = order["quantity_left"]
                    quantity_dict[trade_symbol]["bnf_price"] = order["bnf_price"]
                    quantity_dict[trade_symbol]["hka_option_order_price"] = order["hka_option_order_price"]
                    quantity_dict[trade_symbol]["option_order_price"] = order["option_order_price"]

                if "expiry" in order:
                    quantity_dict[trade_symbol]["expiry"] = order["expiry"]

                if "sl_order_id" in order:
                    quantity_dict[trade_symbol]["sl_order_id"] = order["sl_order_id"]

                if "trailing_sl" in order:
                    quantity_dict[trade_symbol]["trailing_sl"] = order["trailing_sl"]

                elif order["trade_type"] == "EXIT":
                    quantity_dict[trade_symbol]["sell_quantity"] += order["quantity"]
                    quantity_dict[trade_symbol]["quantity_left"] = order["quantity_left"]
                    quantity_dict[trade_symbol]["exit_levels"].append(order["exit_type"])

            final_out = {}
            for entries in quantity_dict:
                # if quantity_dict[entries]["buy_quantity"] - quantity_dict[entries]["sell_quantity"] > 0:
                if quantity_dict[entries]["quantity_left"] > 0:
                    final_out[entries] = quantity_dict[entries]
            return final_out

        else:
            return {}
    except Exception as e:
        print(f"Exception in checking open orders : {e}")
        return {}


def convert_to_trades(orders_list, market_type, order_exit_levels, mode, broker):
    """Function to convert Orders to Trades """
    try:
        trade_dict = {}
        trades_array = []
        for order in orders_list:
            if order["trade_type"] == "ENTRY":
                trade_dict["date"] = order["date"]
                trade_dict["stock"] = order["tradingsymbol"]
                trade_dict["lot_size"] = order["lot_size"]
                trade_dict["trade_type"] = order["trade_type"]
                trade_dict["bnf_price"] = order["bnf_price"]
                trade_dict["bar_color"] = order["bar_color"]
                trade_dict["entry_time"] = order["order_timestamp"]
                trade_dict["entry_price"] = order["trigger_price"]
                trade_dict["quantity"] = order["quantity"]
                trade_dict["pnl"] = 0
                trade_dict["points"] = 0
                trade_dict["exit_time"] = None
                trade_dict["exit_price"] = None
                trade_dict["exit_type"] = ""
                trade_dict["day"] = order["day"]
                trade_dict["expiry"] = order["expiry"]
                trade_dict["brokerage"] = 0
                trade_dict["net_pnl"] = 0

                if mode == "lt" or mode == "vt":
                    trade_dict["date"] = datetime.datetime.strptime(str(datetime.datetime.today().date()), '%Y-%m-%d')
                    trade_dict["user_id"] = ObjectId(order["user_id"])
                    trade_dict["strategy_id"] = ObjectId(order["strategy_id"])
                    trade_dict["request_id"] = ObjectId(order["request_id"])

            else:
                if market_type == "cash":
                    if order["trade_type"] == "SHORT":
                        points = trade_dict["entry_price"] - order["trigger_price"]
                        trade_dict["points"] += round(points)
                        trade_dict["pnl"] += round(order["quantity"] * points)
                    else:
                        points = order["trigger_price"] - trade_dict["entry_price"]
                        trade_dict["points"] += round(points)
                        trade_dict["pnl"] += round(order["quantity"] * points)
                    # trade_dict["pnl"] += round(order["quantity"] * trade_dict["points"])
                else:
                    points = order["trigger_price"] - trade_dict["entry_price"]
                    trade_dict["points"] += round(points)
                    trade_dict["pnl"] += round(order["quantity"] * trade_dict["points"] * trade_dict["lot_size"])

                if trade_dict["exit_type"]:
                    trade_dict["exit_type"] += "|" + order["exit_type"]
                else:
                    trade_dict["exit_type"] = order["exit_type"]

                if order["exit_type"] in order_exit_levels:
                    trade_dict["exit_time"] = order["order_timestamp"]
                    trade_dict["exit_price"] = order["trigger_price"]

                    brokerage, net_pnl = calculate_brokerage(buy_price=trade_dict["entry_price"], sell_price=trade_dict["exit_price"],
                                                             quantity=order["quantity"] * trade_dict["lot_size"], broker=broker)
                    trade_dict["brokerage"] += brokerage
                    trade_dict["net_pnl"] += net_pnl

                    trades_array.append(trade_dict)

                    # Emptying Trade Dict for next trade
                    trade_dict = {}
                else:
                    brokerage, net_pnl = calculate_brokerage(buy_price=trade_dict["entry_price"], sell_price=order["trigger_price"],
                                                             quantity=order["quantity"] * trade_dict["lot_size"], broker=broker)
                    trade_dict["brokerage"] += brokerage
                    trade_dict["net_pnl"] += net_pnl
        return trades_array
    except Exception as e:
        print(f"Exception in converting orders to trades : {e}")
        pass


def check_existing_order(strike_price, option_type, position_type, order_type, orders_list, entry_time=None):
    """Function to check existing order on defined symbol"""
    try:
        for order in orders_list:
            # if order["tradingsymbol"] == symbol and order["position_type"] == position_type and order["exit_type"] == order_type :
            if not entry_time:
                if order["strike_price"] == strike_price and order["option_type"] == option_type and order["position_type"] == position_type and order["exit_type"] == order_type:
                    return True
            else:
                if order["strike_price"] == strike_price and order["option_type"] == option_type and order["position_type"] == position_type and order["exit_type"] == order_type and order["order_timestamp"] > entry_time:
                    return True
        return False
    except Exception as e:
        print("Exception in checking existing order : {}".format(e))
        pass

