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
    data = {"BOND" : [], "VALBZ": [], "VALE" : [], "GS" : [], "MS": [], "WFC": [], "XLF" : []}
    buy_data = {"BOND": [], "VALBZ": [], "VALE": [], "GS": [], "MS": [], "WFC": [], "XLF": []}

    # Stored previous successful orders, structured as [price, ] --------------------------------------------------------------------
    orders = {"BOND": [], "GS": [], "MS": [], "WFC": []}

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
    bond_limit = 0
    valbz_limit = 0
    vale_limit = 0

    last_valbz_ask = None
    last_valbz_ask_quantity = None
    last_vale_buy = None
    last_vale_buy_quantity = None

    last_valbz_buy = 0
    last_valbz_buy_quantity = 0
    last_vale_ask = 0
    last_vale_ask_quantity = 0

    valbz_spent = 0
    vale_sold = 0

    vale_orders = []

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
        elif message["type"] == "book":
            '''
            def fair_value(stock_name):
                if (message["type"] == "book" and message["symbol"] == stock_name):
                   return float(message["sell"][0][0] + message["buy"][0][0]) / 2.0

            # Get the fair value for each individual component and etf
            BOND_fair_val = fair_value("BOND")
            GS_fair_val = fair_value("GS")
            MS_fair_val = fair_value("MS")
            WFC_fair_val = fair_value("WFC")
            ETF_fair_val = 0.3 * BOND_fair_val + 0.2 * GS_fair_val + 0.3 * MS_fair_val + 0.2 * WFC_fair_val
            '''
            '''
                # ------------------------------------------
                # df previous 50 orders
                # grab all the available records
            def moving_average(side, stock_name):
                time_period = 50
                sum = 0
                counter = 0
                if (message["type"] == "trade" and message["symbol"] == stock_name):
                    sum += message["price"]
                    counter += 1
                    if (counter == time_period):
                        return sum/time_period
            '''
            def best_price(side):
                if message[side]:
                    return message[side][0][0]
                else:
                    return 0
            
            def add_data():
                bid_price = best_price("buy")
                ask_price = best_price("sell")
                if bid_price == None or ask_price == None:
                    spread = -1
                else:
                    spread = bid_price - ask_price

                if message["symbol"] == "VALE":
                    fee = 10
                if message["symbol"] == "XLF":
                    fee = 100
                else:
                    fee = 0
                data[message["symbol"]].append([bid_price, ask_price, spread, fee])

            add_data()

            if message["symbol"] == "VALE":
                fee = 10
            if message["symbol"] == "XLF":
                fee = 100
            else:
                fee = 0

            if message["symbol"] == "BOND":
                best_bond_ask = best_price("sell")
                best_bond_buy = best_price('buy')

                now = time.time()

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now

                    if best_bond_ask is not None and best_bond_ask < 1000 and bond_limit < 100:
                        order_id += 1
                        print(f"BOND stock at {best_bond_ask}. Quantity: {message['sell'][0][1]}")
                        exchange.send_add_message(order_id=order_id, symbol="BOND", dir=Dir.BUY, price=best_bond_ask, size=message['sell'][0][1])
                        bond_limit += message['sell'][0][1]
                        print(f"Bought BOND at {best_bond_ask}. Quantity: {message['sell'][0][1]}")

                    if best_bond_buy is not None and best_bond_buy > 1000 and bond_limit > -100:
                        order_id += 1
                        print(f"Selling BOND stock at {best_bond_buy}. Quantity: {message['buy'][0][1]}")
                        exchange.send_add_message(order_id=order_id, symbol="BOND", dir=Dir.SELL, price=best_bond_buy,
                                                  size=message['buy'][0][1])
                        bond_limit -= message['buy'][0][1]
                        print(f"Sold BOND at {best_bond_buy}. Quantity: {message['buy'][0][1]}")

            elif message["symbol"] == "VALBZ":
                last_valbz_ask = best_price('sell')
                last_valbz_ask_quantity = message['sell'][0][1] if message['sell'] else 0
                last_valbz_buy = best_price('buy')
                last_valbz_buy_quantity = message['buy'][0][1] if message['buy'] else 0
            elif message["symbol"] == "VALE":
                last_vale_buy = best_price('buy')
                last_vale_buy_quantity = message['buy'][0][1] if message['buy'] else 0
                last_vale_ask = best_price('sell')
                last_vale_ask_quantity = message['sell'][0][1] if message['sell'] else 0

            '''
            if last_valbz_ask is not None and last_vale_buy is not None:
                price_diff = last_vale_buy - last_valbz_ask
                transact = True
                if valbz_limit + last_valbz_ask_quantity > 9:
                    transact = False
                    order_id += 1

                    if last_valbz_buy_quantity > 9:
                        curr_valbz_sell = 9
                    else:
                        curr_valbz_sell = last_valbz_buy_quantity

                    if last_valbz_buy * curr_valbz_sell > valbz_spent + 10:
                        exchange.send_add_message(order_id=order_id, symbol="VALBZ", dir=Dir.SELL, price=last_valbz_buy, size=curr_valbz_sell)
                        valbz_limit -= last_valbz_buy_quantity
                        valbz_spent = 0

                if vale_limit - last_vale_buy_quantity < -9:
                    transact = False
                    order_id += 1

                    if last_vale_ask_quantity > 9:
                        curr_vale_buy = 9
                    else:
                        curr_vale_buy = last_vale_ask_quantity

                    if vale_sold > last_vale_ask * curr_vale_buy + 10:
                        exchange.send_add_message(order_id=order_id, symbol="VALE", dir=Dir.BUY, price=last_vale_ask, size=curr_vale_buy)
                        vale_limit += last_vale_ask_quantity
                        vale_sold = 0

                if price_diff > 0 and transact and last_valbz_ask_quantity < 10 and last_vale_buy_quantity < 10:
                    order_id += 1
                    exchange.send_add_message(order_id=order_id, symbol="VALBZ", dir=Dir.BUY, price=last_valbz_ask, size=last_valbz_ask_quantity)
                    valbz_limit += last_valbz_ask_quantity
                    valbz_spent += last_valbz_ask * last_valbz_ask_quantity
                    order_id += 1
                    exchange.send_add_message(order_id=order_id, symbol="VALE", dir=Dir.SELL, price=last_vale_buy, size=last_vale_buy_quantity)
                    vale_limit -= last_vale_buy_quantity
                    vale_sold += last_vale_buy * last_vale_buy_quantity

                    print(f"Bought VALBZ at {last_valbz_ask} for {last_valbz_ask_quantity}. Sold VALE at {last_vale_buy} for {last_vale_buy_quantity}")
            '''

            '''
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
                            exchange.send_convert_message(order_id=order_id, symbol="VALE", dir=Dir.BUY, size=convert_vale_quantity)
                            order_id += 1
                            exchange.send_add_message(order_id=order_id, symbol="VALE", dir=Dir.SELL, price=last_vale_buy, size=convert_vale_quantity)
                            print(f"Converted {convert_vale_quantity} VALBZ to {convert_vale_quantity} VALE and sold")
                        else:
                            curr_valbz_ask_quantity = last_valbz_ask_quantity

                        if vale_limit + last_vale_buy_quantity > 10:
                            print(vale_orders)
                            for order_id in vale_orders:
                                exchange.send_cancel_message(order_id=order_id)
                                print(f"Cancel order {order_id}")

                            vale_orders = []
                            vale_limit = 0
                            print(f"Resold VALE orders")
                        else:
                            exchange.send_add_message(order_id=order_id, symbol="VALBZ", dir=Dir.BUY,
                                                      price=last_valbz_ask, size=curr_valbz_ask_quantity)
                            valbz_limit += curr_valbz_ask_quantity
                            print(f"Bought VALBZ at {last_valbz_ask} : {last_valbz_ask_quantity}. ")
                            
                            curr_vale_buy_quantity = last_vale_buy_quantity
                            order_id += 1
                            exchange.send_add_message(order_id=order_id, symbol="VALE", dir=Dir.SELL, price=last_vale_buy, size=curr_vale_buy_quantity)
                            vale_limit += last_vale_buy_quantity
                            vale_orders.append(order_id)
                            print(f"Sold VALE at {last_vale_buy} : {last_vale_buy_quantity}")
                    else:
                        if vale_limit + last_vale_buy_quantity <= 10:
                            order_id += 1
                            exchange.send_add_message(order_id=order_id, symbol="VALBZ", dir=Dir.BUY, size=last_valbz_ask_quantity, price=last_valbz_ask)
                            order_id += 1
                            exchange.send_convert_message(order_id=order_id, symbol="VALE", dir=Dir.BUY, size=last_valbz_ask_quantity)

                            if vale_limit + last_vale_buy_quantity > 10:
                                print(vale_orders)
                                for order_id in vale_orders:
                                    exchange.send_cancel_message(order_id=order_id)
                                    print(f"Cancel order {order_id}")

                                vale_orders = []
                                vale_limit = 0
                                print(f"Resold VALE orders")
                            else:
                                order_id += 1
                                exchange.send_add_message(order_id=order_id, symbol="VALE", dir=Dir.SELL, price=last_vale_buy, size=last_valbz_ask_quantity)

                            vale_limit += last_valbz_ask_quantity
                            vale_orders.append(order_id)
                            print(f"Converted {last_valbz_ask_quantity} VALBZ to {last_valbz_ask_quantity} VALE and sold")
                '''
        # with open("data.txt", "a") as file:
            # file.write(str(data) + "\n")


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
