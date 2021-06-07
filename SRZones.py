from numpy import nan, string_
import yfinance as yf
import pandas as pd
import datetime as dt
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt

class SRZones:
    def __init__(self) -> None:
        # Activate yfinance workaround
        yf.pdr_override()
        # Initialize a start and end date
        start = dt.datetime.now() - dt.timedelta(weeks=52)
        end = dt.datetime.now()
        # Retrieve Symbol via User Input
        stock = input("Enter the stock symbol : ")

        df = pdr.get_data_yahoo(stock, start, end)
        
        df["High"].plot(label="High")

        # Store pivot values
        pivots = []
        # Stores dates of pivots
        dates = []
        # How many days since pivot
        counter = 0
        # Stores latest pivot value
        lastPivot = None

        # Store ten pivots and their values
        Range = [0,0,0,0,0,0,0,0,0,0]
        dateRange = [0,0,0,0,0,0,0,0,0,0]

        for i in df.index:
            currentMax = max(Range, default=0)
            # print("CurrentMax", currentMax)
            value=round(df["High"][i],2)
            # print("Value",value)

            Range=Range[1:9]
            # print("Range",Range)
            Range.append(value)
            dateRange=dateRange[1:9]
            dateRange.append(i)
            
            # If current max hasnt changed add 1 to counter
            if currentMax == max(Range,default=0):
                counter+=1
            else:
                counter=0

            # If after 5 days pass and no new high vs previous add to pivot
            if counter==5:
                lastPivot=currentMax
                dateLoc=Range.index(lastPivot)
                lastDate=dateRange[dateLoc]
                pivots.append(lastPivot)
                dates.append(lastDate)
                # print(pivots, dates)
        
        # Define length of the line
        timeD=dt.timedelta(days=60)

        for i in range(len(pivots)):
            print(pivots[i],dates[i])
            # Add resistance lines to the chart
            plt.plot_date([dates[i],dates[i]+timeD],
            [pivots[i],pivots[i]], linestyle="-", linewidth=2, marker=",")

        plt.show()

if __name__ == '__main__':
    SRZones()