#!/usr/bin/env python3
# Copyright (c) 2018 Lyndros
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
################################################################################
#                          CONFIGURATION PARAMETERS                            #
################################################################################
#Enable by default to test the bot and do not send the actions
TEST_MODE = 1
#List of coins being monitored by the bot
#Be extremelly carefull when setting the buy price
MONITORED_COINS = (
    #Parameters for Storm
    {"COIN_NAME":              "Storm",
     "COIN_ACRONYM":           "STORM",
     "BUY_PRICE_BTC":          "0.00000279",
     "TAKE_PROFIT_PERCENTAGE": +30,
     "STOP_LOSS_PERCENTAGE":   -15 },
    #Parameters for Groestlcoin
    {"COIN_NAME":              "Groestlcoin",
     "COIN_ACRONYM":           "GRS",
     "BUY_PRICE_BTC":          "0.00008677",
     "TAKE_PROFIT_PERCENTAGE": +30,
     "STOP_LOSS_PERCENTAGE":   -15 },
     #Parameters for Wanchain
     {"COIN_NAME":              "Wanchain",
      "COIN_ACRONYM":           "WAN",
      "BUY_PRICE_BTC":          "0.00034490",
      "TAKE_PROFIT_PERCENTAGE": +30,
      "STOP_LOSS_PERCENTAGE":   -15 })

#BINANCE API KEY TO RUN MY BOT
API_KEY         = ""
API_SECRET      = ""
################################################################################
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

client = Client(API_KEY, API_SECRET)

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

for mycoin in MONITORED_COINS:
    #Display coin information
    print("######################################")
    print("Name:          %s (%s)" %(mycoin['COIN_NAME'], mycoin['COIN_ACRONYM']))
    mycoin_current_balance = client.get_asset_balance(asset=mycoin['COIN_ACRONYM'])
    print("Balance:       %s %s"   %(mycoin_current_balance['free'], mycoin['COIN_ACRONYM']))
    print("Buy price:     %s BTC"  %mycoin['BUY_PRICE_BTC'])
    mycoin_current_price = get_current_price_btc(mycoin['COIN_ACRONYM'])
    print("Current price: %s BTC"  %mycoin_current_price)
    mycoin_delta= (float(mycoin_current_price)*100/float(mycoin['BUY_PRICE_BTC']))-100
    print("Delta:         {:.2f}%".format(mycoin_delta))

    print("Stop Loss:     {0}%".format(mycoin['STOP_LOSS_PERCENTAGE']))
    print("Take Profit:   {0}%".format(mycoin['TAKE_PROFIT_PERCENTAGE']))

    #SET STOP LOSS
    if   mycoin_delta < float(mycoin['STOP_LOSS_PERCENTAGE']):
        stop_loss_btc(mycoin['COIN_ACRONYM'])
    #TAKE PROFIT
    elif float(mycoin_delta) >= float(mycoin['TAKE_PROFIT_PERCENTAGE']):
        sell_coin_btc(mycoin['COIN_ACRONYM'])
    #HOLD COIN
    else:
        hodl_coin_btc(mycoin['COIN_ACRONYM'])
    print("######################################")
