#!/usr/bin/env python3
# Copyright (c) 2018 Lyndros <lyndros@hotmail.com>
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
###############################################################################
# Trade monitor by Lyndros <lyndros@hotmail.com>                   #
###############################################################################
# Repository: https://github.com/Lyndros/crypto_tools                         #
#                                                                             #
# If you want to support and motivate me I accept donations even 1 TOK is     #
# always welcome :-)!                                                         #
# > ethereum address: 0x44F102616C8e19fF3FED10c0b05B3d23595211ce              #
# > tokugawa address: TqtycVQsthmEtMLGA8RtqHupZNPDH1Fnt9                      #
#                                                                             #
###############################################################################
import yaml
import os
import argparse
from binance.client import Client

def get_current_price_btc(coin_acronym):
    #Get all current prices
    prices = client.get_all_tickers()
    #Iterate over all coins
    for myprice in prices:
        if myprice["symbol"] == coin_acronym+'BTC':
            return myprice["price"]

def stop_loss_btc(coin_acronym):
    print("SELL: Houston, we have a problem")

def sell_coin_btc(coin_acronym):
    print("SELL: Take the money and run")

def hodl_coin_btc(coin_acronym):
    print("HODL: Keep calm and keep holding")

###############################################################################
#                                    MAIN                                     #
###############################################################################
#Program input parameters
parser = argparse.ArgumentParser()
parser.add_argument("configuration", help="The trade monitor configuration file.")
args = parser.parse_args()

#Build abs names to avoid problems
configuration_abspath = os.path.abspath(args.configuration)

#Check input files
if not os.path.exists(configuration_abspath):
    print("Error! Could not open configuration file.")
    sys.exit(-1)

#Parse the configuration file
with open(configuration_abspath, 'r') as ymlfile:
    CONFIG = yaml.load(ymlfile)

#Load the API key
client = Client(CONFIG['API_KEY'], CONFIG['API_SECRET'])

"""
status = client.get_system_status()
print(status)

info = client.get_exchange_info()
print(info)

info = client.get_symbol_info('GRSBTC')
print(info)

deph = client.get_order_book(symbol='GRSBTC')
print(deph)

trades = client.get_my_trades(symbol='GRSBTC')
print(trades)
"""

for mycoin in CONFIG['COINS']:
    #Display coin information
    print("######################################")
    print("Name:          %s (%s)" %(mycoin['NAME'], mycoin['ACRONYM']))
    mycoin_current_balance = client.get_asset_balance(asset=mycoin['ACRONYM'])
    print("Balance:       %s %s"   %(mycoin_current_balance['free'], mycoin['ACRONYM']))
    print("Buy price:     %s BTC"  %mycoin['BUY_PRICE_BTC'])
    mycoin_current_price = get_current_price_btc(mycoin['ACRONYM'])
    print("Current price: %s BTC"  %mycoin_current_price)
    mycoin_delta= (float(mycoin_current_price)*100/float(mycoin['BUY_PRICE_BTC']))-100
    print("Delta:         {:.2f}%".format(mycoin_delta))

    print("Stop Loss:     {0}%".format(mycoin['STOP_LOSS_PERCENTAGE']))
    print("Take Profit:   {0}%".format(mycoin['TAKE_PROFIT_PERCENTAGE']))

    #SET STOP LOSS
    if   mycoin_delta < float(mycoin['STOP_LOSS_PERCENTAGE']):
        stop_loss_btc(mycoin['ACRONYM'])
    #TAKE PROFIT
    elif float(mycoin_delta) >= float(mycoin['TAKE_PROFIT_PERCENTAGE']):
        sell_coin_btc(mycoin['ACRONYM'])
    #HOLD COIN
    else:
        hodl_coin_btc(mycoin['ACRONYM'])
    print("######################################")
