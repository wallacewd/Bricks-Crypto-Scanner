'''
Brick's Scanner
Version: 0.02
Date: 6/6/2021

www.brick.technology
www.coinlab.pro

Notes:
    1. This is a quick fun project i made last night. Use this as a launch pad to build your own, more effective scanner.
    2. You can add any symbol on binance to the 'coins' list and it will be added to the scanner
    3. The scanner looks for a price increase over the last second.
        -> If the scanner detects a increase, 'recording' is turned on
        -> Currently the code will track price increases over 20s
        -> Console prints occur only if the price has kept rising over the past 5-10s
'''

import json, time
import datetime as dt
from websocket import create_connection
from colorama import init, Fore
from threading import Thread

print('----------------------------------- Bricks\'s Scanner ------------------------------------')
print('**************** Updates will only be displayed when conditions are met *****************\n')
print('--------------------------------------- Scanning ----------------------------------------')

# Subscribe to binance /@miniTicker websocket:
coins = ['dogeusdt','btcusdt','ethusdt','linkusdt','uniusdt','algousdt','maticusdt','compusdt','lunausdt','dodousdt','ankrusdt','milusdt','gtcusdt','ampusdt','aaveusdt','adausdt','cakeusdt','bnbusdt','crvusdt','xlmusdt','sushiusdt','grtusdt']

# Parse websocket data into two values: coin, close_price
# Each response is a 'bar'. I chose to use 'c' the value for bar close
def parse_ws(result):
    msg = json.loads(result)
    return str(msg['s']),float(msg['c'])

# Class assigned to each coin after threading. 
class coinData():
    def __init__(self,pair,now): 
        self._coin = pair
        self._price = 1
        self._now = now
        self._record = False
        self._record_start_time = 0
        self._record_start_price = 0
        self._1s = 1
        self._5s = 1
        self._5s_status = True
        self._10s = 1
        self._10s_status = True
        self._15s = 1
        self._15s_status = True
        self._20s = 1
        self._20s_status = True

# Function for thread processes
def coin_thread(c:str):
    ws = create_connection('wss://stream.binance.com:9443/ws/'+c+'@miniTicker')
    start = time.time()
    coin = coinData(c,start)

    # Create infinite loop
    while True:
        try:
            coin._now = time.time()
            result =  ws.recv()
            coin._coin,coin._price = parse_ws(result)

            # If the coin's class properity '_record' is set to 'False' - Check the percentage change over the last second
            # When the price increases over 1s, switched '_record' to 'True
            if coin._record == False:
                if coin._price > coin._1s:
                    print(Fore.WHITE+''+str(dt.datetime.now().strftime('%H:%M:%S'))+' :: '+coin._coin+' :: 1s Gain '+ str(round(((coin._price - coin._1s)/coin._price)*100,4))+'%')
                    coin._record_start_time = coin._now
                    coin._record = True
                    coin._record_start_price = coin._price
                    coin._1s = coin._price
                else:
                    coin._1s = coin._price

            # When '_record' is set to 'True', calculate the length of time since '_record_start_time' as long as the price is increasing.
            # '_record_start_time' is the time the recording of price changes starts
            # This gets reset to 0 after the price stops moving up (or after 20s because i have only built support for 20s so far)
            else:
                if coin._price > coin._record_start_price:
                    if coin._price > coin._record_start_price and coin._now-coin._record_start_time >= 5  and coin._5s_status == True:
                        print(Fore.LIGHTCYAN_EX+''+str(dt.datetime.now().strftime('%H:%M:%S'))+' :: '+coin._coin+' :: 5s Gain '+ str(round(((coin._price - coin._record_start_price)/coin._price)*100,4))+'%')
                        coin._5s = coin._price
                        coin._5s_status = False
                    elif coin._price > coin._5s and coin._now-coin._record_start_time >= 10 and coin._10s_status == True:                 
                        print(Fore.GREEN+''+str(dt.datetime.now().strftime('%H:%M:%S'))+' :: '+coin._coin+' :: 10s Gain: '+str(round(((coin._price - coin._record_start_price)/coin._price)*100,4))+'%')
                        coin._10s = coin._price
                        coin._10s_status = False
                    elif coin._price > coin._10s and coin._now-coin._record_start_time >= 15 and coin._15s_status == True:                 
                        print(Fore.LIGHTMAGENTA_EX+''+str(dt.datetime.now().strftime('%H:%M:%S'))+' :: '+coin._coin+' :: 15s Gain: '+str(round(((coin._price - coin._record_start_price)/coin._price)*100,4))+'%')
                        coin._15s = coin._price
                        coin._15s_status = False
                    elif coin._price > coin._15s and coin._now-coin._record_start_time >= 20 and coin._20s_status == True:                 
                        print(Fore.RED+''+str(dt.datetime.now().strftime('%H:%M:%S'))+' :: '+coin._coin+' :: 20s Gain: '+str(round(((coin._price - coin._record_start_price)/coin._price)*100,4))+'%')
                        coin._20s = coin._price 
                        coin._20s_status = False
                    elif coin._price > coin._20s and coin._now-coin._record_start_time >= 20 and coin._20s_status == False: 
                        pass
                    else:
                        pass
                else:
                    coin._record = False
                    coin._1s = coin._price
                    coin._5s, coin._10s, coin._15s, coin._20s = 0,0,0,0
                    coin._1s_status, coin._5s_status, coin._10s_status, coin._15s_status, coin._20s_status  = True, True, True, True, True
                    coin._record_start_time = 0

        # Handles exceptions from the main while loop
        except Exception as e:
            print(e)
            break

# Crank it up
if __name__ == "__main__":
    price_list = []
    first_run_flag = 0
    init()
    [Thread(target=coin_thread, args=(str(x),),).start() for x in coins]
