__author__ = 'Frank Tran'
import sqlite3
import requests, json
import subprocess
import sys
import datetime

# # Create Database Connection
# connection = sqlite3.connect('BrokeAz.db')

# # Initialize Python to Run SQL Queries
# cursor = connection.cursor()

# cursor.execute("INSERT INTO stock (symbol, company) VALUES ('ADBE', 'Adobe Inc.')")
# cursor.execute("INSERT INTO stock (symbol, company) VALUES ('VZ', 'Verizon')")


# # Commit to save the changes
# connection.commit()

# UPDATE questrade_token SET refresh_token='AdMN_wl6r59krSZSEM2aR3o8sr1X-vwY0';

class RefreshToken:
    def __init__(self):
        self.connection = sqlite3.connect('BrokeAz.db')
        self.cursor = self.connection.cursor()
        self.response = ''
        self.token_url = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token='
        
        self.cursor.execute("SELECT refresh_token from questrade_token")
        self.refresh_token = self.cursor.fetchone()[0]
        
        self.url = self.token_url + self.refresh_token
        self.response = requests.get(self.url)
        self.response = self.response.text
        self.response = json.loads(self.response)

        refresh = self.response["refresh_token"]
        access = self.response["access_token"]
        api = self.response["api_server"]
        token_type = self.response["token_type"]

        print("Refresh Token: ", refresh)

        try:
            print("Executing Query...")
            query = "UPDATE questrade_token SET refresh_token='{refresh}', access_token='{access}', api_server='{server}', token_type='{type}' where id = 1".format(refresh=refresh, access=access, server=api, type=token_type)
            self.cursor.execute(query)
            print("Committing Query...")
            self.connection.commit()
            self.cursor.execute("SELECT refresh_token from questrade_token")
            self.refresh_token = self.cursor.fetchone()[0]
            print("New Refresh Token: ", self.refresh_token)

        except Exception as e:
            print(e)

        return

    def insertTokens(self):
        refresh = self.response["refresh_token"]
        access = self.response["access_token"]
        api = self.response["api_server"]
        token_type = self.response["token_type"]
        query = "INSERT INTO questrade_token (refresh_token,access_token,api_server,token_type) VALUES ('{refresh}','{access}','{server}','{type}')".format(refresh=refresh, access=access, server=api, type=token_type)
        print(query)
        self.cursor.execute(query)
        self.connection.commit()

        return

class PopulateDB:
    # S&P 500 
    # https://github.com/datasets/s-and-p-500-companies/blob/master/data/constituents.csv
    def __init__(self):
        connection = sqlite3.connect('BrokeAz.db')
        cursor = connection.cursor()
        query = "INSERT INTO stock (symbol, company) VALUES ('{}','{}')"

        with open("sp500.csv", "r") as f:
            company_list = f.readlines()
        
        for companies in company_list:
            if "Symbol" in companies:
                pass
            else:
                company = companies.split(",")
                for info in company:
                    try:
                        print("Inserting {} into stock table...".format(company[0]))
                        cursor.execute(query.format(company[0],company[1]).replace("\\n", ""))
                        connection.commit()
                    except Exception as e:
                        print(e)

        f.close()
        
        # Russell 1000
        # https://raw.githubusercontent.com/mcprentiss/Russell_1000_download/master/rus1000.csv

        with open("russell1000.csv", "r") as f:
            company_list = f.readlines()
        
        for companies in company_list:
            if "Symbol" in companies:
                pass
            else:
                company = companies.split(",")
                for info in company:
                    try:
                        print("Inserting {} into stock table...".format(company[0]))
                        cursor.execute(query.format(company[0],company[1].replace("\\n", "")))
                        connection.commit()
                    except Exception as e:
                        print(e)

        f.close()

        return

class Questrade_Wrapper:
    def __init__(self):
        RefreshToken()
        self.connection = sqlite3.connect('BrokeAz.db')
        self.cursor = self.connection.cursor()

        return

    def UpdateID(self):
        self.cursor.execute("SELECT id, symbol from stock")
        output = self.cursor.fetchall()

        for stock in output:
            counter = 100000
            print("Searching For... ", stock)
            self.cursor.execute("SELECT token_type, access_token, api_server from questrade_token")
            results = self.cursor.fetchone()
            print("Results: ", results)
            token_type = results[0]
            access_token = results[1]
            server = results[2]
            headers = {'Authorization': token_type + ' ' + access_token}
            url = server + "v1/symbols/search?prefix=" + stock[1]

            try:
                r = requests.get(url, headers=headers)
                response = r.json()
                response = response['symbols'][0]
                symbol = response['symbol']
                quest_id = response['symbolId']
                db_id = ""
                db_symbol = ""
                print(quest_id, symbol)

                self.cursor.execute("SELECT id, symbol from stock where id = {}".format(quest_id))
                results = self.cursor.fetchone()
                try:
                    db_id = results[0]
                    db_symbol = results[1]
                    
                    print(db_id, db_symbol)
                except Exception as e:
                    print(e)

                if db_id == "":
                    self.cursor.execute("UPDATE stock SET id = {} where symbol = '{}'".format(quest_id, symbol))
                # queried has a stock id 1 for company X > replace ID
                elif db_id == quest_id:
                    print("Symbol {} Up-to-Date!".format(symbol))
                else:
                    self.cursor.execute("UPDATE stock SET id = {} where symbol = '{}'".format(counter, db_symbol))
                    counter += 1
                    self.cursor.execute("UPDATE stock SET id = {} where symbol = '{}'".format(quest_id, symbol))
                
                self.connection.commit()
            except Exception as e:
                print(e)
        
        return

    def searchSymbol(self, symbol):
        self.cursor.execute("SELECT token_type, access_token, api_server from questrade_token")
        results = self.cursor.fetchone()
        print("Results: ", results)
        token_type = results[0]
        access_token = results[1]
        server = results[2]
        headers = {'Authorization': token_type + ' ' + access_token}
        url = server + "v1/symbols/search?prefix=" + symbol

        try:
            r = requests.get(url, headers=headers)
            response = r.json()
            response = response['symbols'][0]
            symbol = response['symbol']
            quest_id = response['symbolId']
            name = response['description']
            securityType = response['securityType']
            exchange = response['listingExchange']
            currency = response['currency']
            
            print()
            print("ID: {}".format(quest_id))
            print("Symbol: {}".format(symbol))
            print("Company: {}".format(name))
            print("Stock/Option: {}".format(securityType))
            print("Exchange: {}".format(exchange))
            print("Currency: {}".format(currency))
            print()

        except Exception as e:
            print(e)
            print("Could Not Find Symbol: ".format(symbol))
        
        return
    
    def fiveCandles(self):
        self.cursor.execute("SELECT id, symbol from stock")
        startDate = datetime.datetime.now().strftime('%Y-%m-%d') + 'T00:00:00-05'
        endDate = datetime.datetime.now().strftime('%Y-%m-%d') + 'T23:59:59-05'

        customStart = '2020-01-01T00:00:00-05'
        customEnd = '2021-02-15T23:59:59-05'
        output = self.cursor.fetchall()
        

        for stock in output:
            stock_id = stock[0]
            symbol = stock[1]

            self.cursor.execute("SELECT token_type, access_token, api_server from questrade_token")
            results = self.cursor.fetchone()
            print("Results: ", results)
            token_type = results[0]
            access_token = results[1]
            server = results[2]
            headers = {'Authorization': token_type + ' ' + access_token}

            urlParameters = 'v1/markets/candles/{}?startTime={}:00&endTime={}:00&interval=FiveMinutes'.format(stock_id, customStart, customEnd)
            url = server + urlParameters
                    
            try:
                r = requests.get(url, headers=headers)
                response = r.json()
                response = response['candles']

                for candle in response:
                    print()
                    print("Start Time: ", candle['start'])
                    print("End Time: ", candle['end'])
                    print("Low: ", candle['low'])
                    print("High: ", candle['high'])
                    print("Open: ", candle['open'])
                    print("Close: ", candle['close'])
                    print("Volume: ", candle['volume'])
                    print("VWAP: ", candle['VWAP'])

                    query = "INSERT INTO stock_price (stock_id, start, end, open, high, low, close, volume, vwap) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(stock_id, candle['start'], candle['end'], candle['open'], candle['high'], candle['low'], candle['close'], candle['volume'], candle['VWAP'])
                    self.cursor.execute(query)
                    print("Committing Query...")
                    self.connection.commit()

            except Exception as e:
                print(e)
                print("Could Not Find Symbol ID: {}".format(stock_id))
        
        return

            




# RefreshToken()
# PopulateDB()
q = Questrade_Wrapper()
# q.UpdateID()
# q.searchSymbol("RKT")
q.fiveCandles()

