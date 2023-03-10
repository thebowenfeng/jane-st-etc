#!/usr/bin/env python3
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py --test prod-like; sleep 1; done

import argparse
from collections import deque
from enum import Enum
import time
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# Replace "REPLACEME" with your team name!
team_name = "TENTHOUSANDPERCENTLOSS"


# ~~~~~============== MAIN LOOP ==============~~~~~

# You should put your code here! We provide some starter code as an example,
# but feel free to change/remove/edit/update any of it as you'd like. If you
# have any questions about the starter code, or what to do next, please ask us!
#
# To help you get started, the sample code below tries to buy GS for a low
# price, and it prints the current prices for VALE every second. The sample
# code is intended to be a working example, but it needs some improvement
# before it will start making good trades!


def main():
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)

    # Data will be structured as [bid, ask, spread, fee]
    data = {"GS": [], "VALBZ": [], "VALE": [], "GS": [], "MS": [], "WFC": [], "XLF": []}
    buy_data = {"GS": [], "VALBZ": [], "VALE": [], "GS": [], "MS": [], "WFC": [], "XLF": []}

    # access fair_value if exist by fair_values_appro["stock_name"]
    fair_values_appro = {"BOND": None, "GS": None, "MS": None, "WFC": None, "XFL": None}

    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)

    # Send an order for GS at a good price, but it is low enough that it is
    # unlikely it will be traded against. Maybe there is a better price to
    # pick? Also, you will need to send more orders over time.

    # exchange.send_add_message(order_id=1, symbol="BOND", dir=Dir.BUY, price=990, size=1)

    # Set up some variables to track the bid and ask price of a symbol. Right
    # now this doesn't track much information, but it's enough to get a sense
    # of the VALE market.

    vale_bid_price, vale_ask_price = None, None
    bond_bid, bond_ask = None, None
    first_gs = True

    vale_last_print_time = time.time()

    # Here is the main loop of the program. It will continue to read and
    # process messages in a loop until a "close" message is received. You
    # should write to code handle more types of messages (and not just print
    # the message). Feel free to modify any of the starter code below.
    #
    # Note: a common mistake people make is to call write_message() at least
    # once for every read_message() response.
    #
    # Every message sent to the exchange generates at least one response
    # message. Sending a message in response to every exchange message will
    # cause a feedback loop where your bot's messages will quickly be
    # rate-limited and ignored. Please, don't do that!
    order_id = 0
    last_valbz_ask, last_valbz_buy = None, None
    last_valbz_ask_quantity, last_valbz_buy_quantity = 0, 0
    last_vale_buy, last_vale_ask = None, None
    last_vale_buy_quantity, last_vale_ask_quantity = 0, 0
    valbz_limit = 0
    vale_limit = 0
    vale_orders = []

    xfl_limit = 0
    last_xfl_ask, last_xfl_buy = None, None
    last_purchased_xlf_value = 0


    # def fair_value(stock_name):
    #     if (message["type"] == "book" and message["symbol"] == stock_name):
    #         return (message["sell"][0][0] + message["buy"][0][0]) / 2

    # Get the fair value for each individual component and etf
    # BOND_fair_val = fair_value("BOND")
    # GS_fair_val = fair_value("GS")
    # MS_fair_val = fair_value("MS")
    # WFC_fair_val = fair_value("WFC")
    #
    # ETF_fair_val = 0.3 * BOND_fair_val + 0.2 * GS_fair_val + 0.3 * MS_fair_val + 0.2 * WFC_fair_val
    # print(ETF_fair_val)

    # if all values are valid, calculate etf
    # fair_values_appro = {"BOND": [], "GS": [], "MS": [], "WFC": [], "ETF": []}
    # if(fair_values_appro["BOND"] and fair_values_appro["GS"] and fair_values_appro["MS"] and fair_values_appro["WFC"]):
    #     fair_values_appro["ETF"] = 0.3 * fair_values_appro["BOND"] + 0.2 * fair_values_appro["GS"] + 0.3 * fair_values_appro["MS"] + 0.2 * fair_values_appro["WFC"]

    while True:
        message = exchange.read_message()

        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        if message["type"] == "close":
            print("The round has ended")
            break
        elif message["type"] == "error":
            print(message)
        elif message["type"] == "reject":
            print(message)
        elif message["type"] == "fill":
            print(message)
        elif message["type"] == "trade":
            # fair price approximation
            if(not fair_values_appro[message["symbol"]]):
                fair_values_appro[message["symbol"]] = message["price"]

        elif message["type"] == "book":
            # fair price approximation
            if(len(message["sell"]) > 0 and len(message["buy"]) > 0):
                fair_values_appro[message["symbol"]] = (message["sell"][0][0] + message["buy"][0][0]) / 2


            def best_price(side):
                if message[side]:
                    return message[side][0][0]

            '''
            def add_data():
                bid_price = best_price("buy")
                ask_price = best_price("sell")
                spread = bid_price - ask_price

                if message["symbol"] == "VALE":
                    fee = 10
                if message["symbol"] == "XLF":
                    fee = 100
                else:
                    fee = 0
                data[message["symbol"]].append([bid_price, ask_price, spread, fee])

            add_data()
            ### TESTING TO REMOVE
            print(data["GS"])

            if message["symbol"] == "VALE":
                fee = 10
            if message["symbol"] == "XLF":
                fee = 100
            else:
                fee = 0

            add_data()
            ### TESTING TO REMOVE
            print(data["GS"])

            if message["symbol"] == "GS":
                GS_ask = best_price("sell")
                GS_buy = best_price('buy')

                now = time.time()

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    if first_gs:
                        if GS_ask is not None and GS_ask < buy_data["GS"][0]:
                            GS_ask = best_price("sell")
                            GS_buy = best_price('buy')
                            order_id += 1
                            print(f"GS stock at {GS_buy}. Quantity: {message['buy'][0][1]}")
                            exchange.send_add_message(order_id=order_id, symbol="GS", dir=Dir.BUY, price= GS_ask, size=message['sell'][0][1])
                            print(f"Bought GS at {GS_ask}. Quantity: {message['sell'][0][1]}")
                            buy_data["GS"] = [GS_ask, message['sell'][0][1]]
                            first_gs = False
                    if GS_ask is not None and GS_ask < buy_data["GS"][0]:
                        order_id += 1
                        print(f"GS stock at {GS_ask}. Quantity: {message['sell'][0][1]}")
                        if message['sell'][0][1] + buy_data["GS"][1] > 100:
                            exchange.send_add_message(order_id=order_id, symbol="GS", dir=Dir.BUY, price=GS_ask, size=message['sell'][0][1])
                        else:
                            exchange.send_add_message(order_id=order_id, symbol="GS", dir=Dir.BUY, price=GS_ask, size=message['sell'][0][1])
                        print(f"Bought GS at {GS_ask}. Quantity: {message['sell'][0][1]}")
                        buy_data["GS"][1] = buy_data["GS"] + message['sell'][0][1]

                    if GS_buy is not None and GS_buy >= buy_data["GS"][0]:
                        order_id += 1
                        print(f"Selling GS stock at {GS_buy}. Quantity: {message['buy'][0][1]}")
                        exchange.send_add_message(order_id=order_id, symbol="GS", dir=Dir.SELL, price=GS_buy,
                                                size=message['buy'][0][1])
                        print(f"Sold GS at {GS_buy}. Quantity: {message['buy'][0][1]}")
                        buy_data["GS"][1] = buy_data["GS"] - message['sell'][0][1]

            if message["symbol"] == "VALE":
                vale_bid_price = best_price("buy")
                GS_ask_price = best_price("sell")
            '''
            # if message["symbol"] == "GS":
            #     last_gsc_buy = best_price('buy')
            #     last_gsc_buy_quantity = message['buy'][0][1] if message['buy'][0][1] else 0
            #     last_gsc_ask = best_price('sell')
            #     last_gsc_ask_quantity = message["sell"][0][1] if message["sell"][0][1] else 0
            # elif message["symbol"] == "MS":
            #     last_ms_buy = best_price("buy")
            #     last_ms_quantity = message['buy'][0][1] if message['buy'][0][1] else 0
            #     last_ms_ask = best_price('sell')
            #     last_ms_ask_quantity = message["sell"][0][1] if message["sell"][0][1] else 0
            # elif message["symbol"] == "WFC":   
            #     last_wfc_buy = best_price("buy")
            #     last_wfc_quantity = message['buy'][0][1] if message['buy'][0][1] else 0
            #     last_wfc_ask = best_price('sell')
            #     last_wfc_ask_quantity =message["sell"][0][1] if message["sell"][0][1] else 0
            if message["symbol"] == "XLF":
                last_xlf_buy = best_price("buy")
                if len(message["buy"]) > 1:
                    last_xlf_ask_quantity = message["buy"][0][1]
                else:
                    last_xlf_ask_quantity = 0

                last_xlf_ask = best_price("sell")
                if len(message["sell"]) > 1:
                    last_xlf_ask_quantity = message["sell"][0][1]
                else:
                    last_xlf_ask_quantity = 0
            
            if message["symbol"] == "BOND":
                best_bond_ask = best_price("sell")
                best_bond_buy = best_price('buy')

                now = time.time()

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now

                    if best_bond_ask is not None and best_bond_ask < 1000:
                        order_id += 1
                        print(f"BOND stock at {best_bond_ask}. Quantity: {message['sell'][0][1]}")
                        exchange.send_add_message(order_id=order_id, symbol="BOND", dir=Dir.BUY, price=best_bond_ask,
                                                  size=message['sell'][0][1])
                        print(f"Bought BOND at {best_bond_ask}. Quantity: {message['sell'][0][1]}")

                    if best_bond_buy is not None and best_bond_buy >= 1000:
                        order_id += 1
                        print(f"Selling BOND stock at {best_bond_buy}. Quantity: {message['buy'][0][1]}")
                        exchange.send_add_message(order_id=order_id, symbol="BOND", dir=Dir.SELL, price=best_bond_buy,
                                                  size=message['buy'][0][1])
                        print(f"Sold BOND at {best_bond_buy}. Quantity: {message['buy'][0][1]}")
            elif message["symbol"] == "VALBZ":
                last_valbz_ask = best_price('sell')
                last_valbz_ask_quantity = message['sell'][0][1] if message['sell'] else 0
            elif message["symbol"] == "VALE":
                last_vale_buy = best_price('buy')
                last_vale_buy_quantity = message['buy'][0][1] if message['buy'] else 0

            if last_valbz_ask is not None and last_vale_buy is not None and last_valbz_ask < last_vale_buy:
                price_diff = last_vale_buy - last_valbz_ask
                buy_amount = last_valbz_ask * last_valbz_ask_quantity
                sell_amount = last_vale_buy * last_vale_buy_quantity
                profit = sell_amount - buy_amount
                convert_profit = price_diff * last_valbz_ask_quantity - 10
                if buy_amount < 20000:
                    print(f"VALBZ at {last_valbz_ask}, VALE at {last_vale_buy}.")
                    if profit > convert_profit:
                        order_id += 1
                        if valbz_limit + last_valbz_ask_quantity > 10:
                            convert_vale_quantity = valbz_limit + last_valbz_ask_quantity - 10
                            curr_valbz_ask_quantity = 10 - valbz_limit
                            order_id += 1
                            exchange.send_convert_message(order_id=order_id, symbol="VALE", dir=Dir.BUY,
                                                          size=convert_vale_quantity)
                            order_id += 1
                            exchange.send_add_message(order_id=order_id, symbol="VALE", dir=Dir.SELL,
                                                      price=last_vale_buy, size=convert_vale_quantity)
                            print(f"Converted {convert_vale_quantity} VALBZ to {convert_vale_quantity} VALE and sold")
                        else:
                            curr_valbz_ask_quantity = last_valbz_ask_quantity

                        if vale_limit + last_vale_buy_quantity > 10:
                            print(vale_orders)
                            for order_id in vale_orders:
                                exchange.send_cancel_message(order_id=order_id)
                                print(f"Cancel order {order_id}")

                            vale_orders = []
                            # order_id += 1
                            # exchange.send_add_message(order_id=order_id, symbol="VALE", dir=Dir.SELL, price=last_vale_buy, size=10)
                            # vale_orders.append(order_id)
                            # vale_limit = 10
                            print(f"Resold VALE orders")
                        else:
                            exchange.send_add_message(order_id=order_id, symbol="VALBZ", dir=Dir.BUY,
                                                      price=last_valbz_ask, size=curr_valbz_ask_quantity)
                            valbz_limit += curr_valbz_ask_quantity
                            print(f"Bought VALBZ at {last_valbz_ask} : {last_valbz_ask_quantity}. ")

                            curr_vale_buy_quantity = last_vale_buy_quantity
                            order_id += 1
                            exchange.send_add_message(order_id=order_id, symbol="VALE", dir=Dir.SELL,
                                                      price=last_vale_buy, size=curr_vale_buy_quantity)
                            vale_limit += last_vale_buy_quantity
                            vale_orders.append(order_id)
                            print(f"Sold VALE at {last_vale_buy} : {last_vale_buy_quantity}")
                    else:
                        if vale_limit + last_vale_buy_quantity <= 10:
                            order_id += 1
                            exchange.send_add_message(order_id=order_id, symbol="VALBZ", dir=Dir.BUY,
                                                      size=last_valbz_ask_quantity, price=last_valbz_ask)
                            order_id += 1
                            exchange.send_convert_message(order_id=order_id, symbol="VALE", dir=Dir.BUY,
                                                          size=last_valbz_ask_quantity)
                            order_id += 1
                            exchange.send_add_message(order_id=order_id, symbol="VALE", dir=Dir.SELL,
                                                      price=last_vale_buy, size=last_valbz_ask_quantity)
                            vale_limit += last_valbz_ask_quantity
                            vale_orders.append(order_id)
                            print(
                                f"Converted {last_valbz_ask_quantity} VALBZ to {last_valbz_ask_quantity} VALE and sold")
            
            if fair_values_appro["XFL"] is not None and last_xlf_ask is not None and fair_values_appro["XFL"] < last_xlf_ask and xfl_limit < 100:
                order_id += 1
                print(f"XFL stock at {last_xlf_ask}. Quantity: {message['sell'][0][1]}")
                exchange.send_add_message(order_id = order_id, symbol = "XFL",  dir=Dir.BUY, price = last_xlf_ask,
                                          size = message['sell'][0][1])
                xfl_limit += message["sell"][0][1]
                print(f"Bought XFL at {last_xlf_ask}. Quantity: {message['sell'][0][1]}")
            if fair_values_appro["XFL"] is not None and last_xlf_buy is not None and last_xlf_buy >= fair_values_appro["XFL"] and xfl_limit < -100:
                order_id += 1
                print(f"Selling XFL stock at {last_xlf_buy}. Quantity: {message['buy'][0][1]}")
                exchange.send_add_message(order_id = order_id, symbol = "XFL", dir= Dir.SELL, price = last_xlf_buy,
                                          size = message['buy'][0][1])
                xfl_limit -= message["buy"][0][1]
                print(f"Sold XFL at {last_xlf_buy}")

# ~~~~~============== PROVIDED CODE ==============~~~~~

# You probably don't need to edit anything below this line, but feel free to
# ask if you have any questions about what it is doing or how it works. If you
# do need to change anything below this line, please feel free to


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExchangeConnection:
    def __init__(self, args):
        self.message_timestamps = deque(maxlen=500)
        self.exchange_hostname = args.exchange_hostname
        self.port = args.port
        exchange_socket = self._connect(add_socket_timeout=args.add_socket_timeout)
        self.reader = exchange_socket.makefile("r", 1)
        self.writer = exchange_socket

        self._write_message({"type": "hello", "team": team_name.upper()})

    def read_message(self):
        """Read a single message from the exchange"""
        message = json.loads(self.reader.readline())
        if "dir" in message:
            message["dir"] = Dir(message["dir"])
        return message

    def send_add_message(
            self, order_id: int, symbol: str, dir: Dir, price: int, size: int
    ):
        """Add a new order"""
        self._write_message(
            {
                "type": "add",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "price": price,
                "size": size,
            }
        )

    def send_convert_message(self, order_id: int, symbol: str, dir: Dir, size: int):
        """Convert between related symbols"""
        self._write_message(
            {
                "type": "convert",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "size": size,
            }
        )

    def send_cancel_message(self, order_id: int):
        """Cancel an existing order"""
        self._write_message({"type": "cancel", "order_id": order_id})

    def _connect(self, add_socket_timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if add_socket_timeout:
            # Automatically raise an exception if no data has been recieved for
            # multiple seconds. This should not be enabled on an "empty" test
            # exchange.
            s.settimeout(5)
        s.connect((self.exchange_hostname, self.port))
        return s

    def _write_message(self, message):
        what_to_write = json.dumps(message)
        if not what_to_write.endswith("\n"):
            what_to_write = what_to_write + "\n"

        length_to_send = len(what_to_write)
        total_sent = 0
        while total_sent < length_to_send:
            sent_this_time = self.writer.send(
                what_to_write[total_sent:].encode("utf-8")
            )
            if sent_this_time == 0:
                raise Exception("Unable to send data to exchange")
            total_sent += sent_this_time

        now = time.time()
        self.message_timestamps.append(now)
        if len(
                self.message_timestamps
        ) == self.message_timestamps.maxlen and self.message_timestamps[0] > (now - 1):
            print(
                "WARNING: You are sending messages too frequently. The exchange will start ignoring your messages. Make sure you are not sending a message in response to every exchange message."
            )


def parse_arguments():
    test_exchange_port_offsets = {"prod-like": 0, "slower": 1, "empty": 2}

    parser = argparse.ArgumentParser(description="Trade on an ETC exchange!")
    exchange_address_group = parser.add_mutually_exclusive_group(required=True)
    exchange_address_group.add_argument(
        "--production", action="store_true", help="Connect to the production exchange."
    )
    exchange_address_group.add_argument(
        "--test",
        type=str,
        choices=test_exchange_port_offsets.keys(),
        help="Connect to a test exchange.",
    )

    # Connect to a specific host. This is only intended to be used for debugging.
    exchange_address_group.add_argument(
        "--specific-address", type=str, metavar="HOST:PORT", help=argparse.SUPPRESS
    )

    args = parser.parse_args()
    args.add_socket_timeout = True

    if args.production:
        args.exchange_hostname = "production"
        args.port = 25000
    elif args.test:
        args.exchange_hostname = "test-exch-" + team_name
        args.port = 25000 + test_exchange_port_offsets[args.test]
        if args.test == "empty":
            args.add_socket_timeout = False
    elif args.specific_address:
        args.exchange_hostname, port = args.specific_address.split(":")
        args.port = int(port)

    return args


if __name__ == "__main__":
    # Check that [team_name] has been updated.
    assert (
            team_name != "REPLACEME"
    ), "Please put your team name in the variable [team_name]."

    main()
