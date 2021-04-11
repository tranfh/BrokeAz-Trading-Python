import sqlite3
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Charts:

    def __init__(self):
        connection = sqlite3.connect('BrokeAz.db')
        cursor = connection.cursor()

        # df = pd.read_csv(
        #     'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

        # def FiveMinuteChart(ticker: str):
    
        query = """SELECT s.company, sp.end, sp.open, sp.high, sp.low, sp.close, sp.volume 
                    FROM stock_price sp 
                    INNER JOIN stock s 
                    ON sp.stock_id = s.id 
                    WHERE s.symbol is '{}'
                    limit 100"""

        # Query for ticket shown as a list 
        cursor.execute(query.format('AAPL'))
        output = cursor.fetchall()
        print(output)

        # Convert to Dataframe
        df = pd.DataFrame(output, columns =['Company', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # include candlestick with rangeselector
        fig.add_trace(go.Candlestick(x=df['Date'],
                        open=df['Open'], 
                        high=df['High'],
                        low=df['Low'], 
                        close=df['Close']),
                    secondary_y=True)

        fig.update_layout(
            title='Apple Inc.',
            yaxis_title='AAPL Stock',
            shapes = [dict(
                x0='2019-12-09', x1='2019-12-09', y0=0, y1=1, xref='x', yref='paper',
                line_width=2)],
            annotations=[dict(
                x='2019-12-09', y=0.05, xref='x', yref='paper',
                showarrow=False, xanchor='left', text='Increase Period Begins')]
)
        # fig.layout.yaxis2.showgrid=False

        # include a go.Bar trace for volumes
        # fig.add_trace(go.Bar(x=df['Date'], y=df['Volume']),
        #             secondary_y=False)
        
        fig.show()

        # # Calculate and define moving average of 30 periods
        # avg_30 = df.Close.rolling(window=30, min_periods=1).mean()

        # # Calculate and define moving average of 50 periods
        # avg_50 = df.Close.rolling(window=50, min_periods=1).mean()

        # trace2 = {
        #     'x': df.index,
        #     'y': avg_30,
        #     'type': 'scatter',
        #     'mode': 'lines',
        #     'line': {
        #         'width': 1,
        #         'color': 'blue'
        #     },
        #     'name': 'Moving Average of 30 periods'
        # }

        # trace3 = {
        #     'x': df.index,
        #     'y': avg_50,
        #     'type': 'scatter',
        #     'mode': 'lines',
        #     'line': {
        #         'width': 1,
        #         'color': 'red'
        #     },
        #     'name': 'Moving Average of 50 periods'
        # }

Charts()