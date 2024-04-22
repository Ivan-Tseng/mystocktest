
import json
import re
import time
import smtplib
import datetime
import csv
import yfinance as yf
import requests
import pandas as pd
from twstock import Stock
import pandas_ta as ta
import os

os.environ['TZ'] = "Asia/Taipei"


today = datetime.date.today().strftime('%Y-%m-%d')
stock_tr_big5=[]
print(today)
stock=[]
cannot_read=[]
maybe_exit=[]
really_cannt_read=[]
allturnoverstock_buy=[]
tmaybe_combine=[]
fmaybe_combine=[]
cleaned_data=[]
stock_cannt_read=[]
forein_data=[]
small60=[]
tcontinutemaybeexit=[]
small20tcontinutemayexit=[]
t20maybe_combine=[]
tcontinue_data=[]
small20=[]
exsmall60=[]
threebstock_get_number=[]

headers = {
"content-type": "text/html; charset=UTF-8",
"user-agent": "Chrome/76.0.3809.132"
}

current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d")

# 股票策略分析
def macdanddevire(stock_number,SEN,LEN,SL,day,first,second):
    try:
        df= yf.download(f'{stock_number}.TW', start='2020-06-15', end=formatted_time)
        #df= yf.download(f'{stock_number}.TW', start='1983-06-15', end="2023-12-25")

    # 計算短期EMA13
        short_EMA = df['Close'].ewm(span=SEN, adjust=False).mean()
    # 計算長期EMA34
        long_EMA = df['Close'].ewm(span=LEN, adjust=False).mean()
    # 計算MACD線
        MACD_line = short_EMA - long_EMA
    #計算快線曼縣ma9跟11
        fast_ma=ta.ma("ema",df['Close'],length=9)
        slow_ma=ta.ma("ema",df['Close'],length=11)
    #計算macd4C縣
        MACD4C_line = fast_ma - slow_ma
    # 計算信號線
        signal_line = MACD_line.ewm(span=SL, adjust=False).mean()
        df['MACD'] = MACD_line
        df['Signal Line'] = signal_line

        macd4c_signal_line=MACD4C_line.ewm(span=SL, adjust=False).mean()
        df["MACD_4c"]=MACD4C_line
        df['macd4c_Signal Line']=macd4c_signal_line

    # 計算MACD柱狀圖
        df['MACD Histogram'] = df['MACD'] - df['Signal Line']
    # 計算macd4C柱狀
        df['MACD4C Histogram'] = df["MACD_4c"] - df['macd4c_Signal Line']
    # 檢測MACD背離
        df['Price Increase'] = df['Close'].diff() > 0
        df['MACD Increase'] = df['MACD Histogram'].diff() > 0
        df['MACD Divergence'] = df['Price Increase'] != df['MACD Increase']
    # 檢測背離macd4c
        df['Price Increase'] = df['Close'].diff() > 0
        df['MACD4C Increase'] = df['MACD4C Histogram'].diff() > 0
        df['MACD4C Divergence'] = df['Price Increase'] != df['MACD4C Increase']

    # 如果發現MACD底背離，則輸出"底背離"
        if df['MACD Divergence'].any():
            print("底背離")
        counts = df['MACD Divergence'].tail(day).value_counts()

    # 如果發現MACD4C底背離，則輸出"底背離"
        if df['MACD4C Divergence'].any():

            print("macd4C底背離")
        counts2 = df['MACD4C Divergence'].tail(day).value_counts()

    # 計算60日和100日的移動平均線
        df['10_MA'] = df['Close'].rolling(window=first).mean()
        df['60_MA'] = df['Close'].rolling(window=second).mean()

    # #計算可能連續背離true表示背離幾個day區間
        counts = df['MACD Divergence'].tail(day).value_counts()
        counts2 = df['MACD4C Divergence'].tail(day).value_counts()

    # # 檢查當天20日均線是否大於60日均線且可能連續背離
        is_10_greater = df['10_MA'].iloc[-1] > df['60_MA'].iloc[-1]
        if  df['10_MA'].iloc[-1] > df['60_MA'].iloc[-1]:
            print('10大於60均線')
        else:

            print('無突破60')

        #檢查量大於800
        #volume_data=df['Volume'].iloc[-1]>=1000000

        volume_data=df['Volume'].tail(2).mean()>800000
        #價格小於80
        price_low=df["Close"].iloc[-1]<80


        # # 檢查前天股價是否小於20日均線
        ex_price_lowwer_than20mean = df["Close"].iloc[-2] < df["Close"].tail(20).mean()

       # 檢查當天股價是否大於20日均線
        Today_price_bigger_than_20mean = df["Close"].iloc[-1]>= df["Close"].tail(20).mean()

        # 檢查大於60均
        Today_price_bigger_than_60mean = df["Close"].iloc[-1]>= df["Close"].tail(60).mean()

        # 檢查大於60均
        ex_Today_price_bigger_than_60mean = df["Close"].iloc[-2] < df["Close"].tail(60).mean()

        # 檢查當天股價是否大於60日均線且量大於1000
        if counts2[1]>=5 and counts[1]>=5 and Today_price_bigger_than_20mean and price_low and volume_data and ex_price_lowwer_than20mean:
            small20.append(stock_number)
            print("前日股價小於20 今日股價大於20,可能有連續背離")

        if counts2[1]>=5 and counts[1]>=5 and Today_price_bigger_than_60mean and price_low and volume_data and ex_Today_price_bigger_than_60mean:
            exsmall60.append(stock_number)
            print("前日股價小於60 今日股價大於60,可能有連續背離")

        if counts2[1]>=5 and counts[1]>=5 and Today_price_bigger_than_60mean and price_low and volume_data:
            small60.append(stock_number)
            print("股價大於60,可能有連續背離")


        if counts2[1]>=5  and counts[1]>=5 and is_10_greater and price_low and volume_data:
            maybe_exit.append(stock_number)
            print("10日軍大於60日,可能有連續背離")





    except Exception as e:
            cannot_read.append(stock_number)
            print(f"Failed to download data for {stock_number}.TW: {e}")

# 當yfinance無法讀取使用分析
def canntreadstock(SEN,LEN,SL,day,first,second):
    try:
        stock = Stock(stock_cannt_read)
        data2 = stock.fetch_from(2002,1)
        df2 = pd.DataFrame(data2)

        # 計算短期EMA
        short_EMA = df2['close'].ewm(span=SEN, adjust=False).mean()
    # 計算長期EMA
        long_EMA = df2['close'].ewm(span=LEN, adjust=False).mean()
    # 計算MACD線
        MACD_line = short_EMA - long_EMA
    #計算快線曼縣ma9跟11
        fast_ma=ta.ma("ema",df2['close'],length=9)
        slow_ma=ta.ma("ema",df2['close'],length=11)
    #計算macd4C縣
        MACD4C_line = fast_ma - slow_ma
    # 計算信號線
        signal_line = MACD_line.ewm(span=SL, adjust=False).mean()
        df2['MACD'] = MACD_line
        df2['Signal Line'] = signal_line

        macd4c_signal_line=MACD4C_line.ewm(span=9, adjust=False).mean()
        df2["MACD_4c"]=MACD4C_line
        df2['macd4c_Signal Line']=macd4c_signal_line

    # 計算MACD柱狀圖
        df2['MACD Histogram'] = df2['MACD'] - df2['Signal Line']
    # 計算macd4C柱狀
        df2['MACD4C Histogram'] = df2["MACD_4c"] - df2['macd4c_Signal Line']
    # 檢測MACD背離
        df2['Price Increase'] = df2['close'].diff() > 0
        df2['MACD Increase'] = df2['MACD Histogram'].diff() > 0
        df2['MACD Divergence'] = df2['Price Increase'] != df2['MACD Increase']
    # 檢測背離macd4c
        df2['Price Increase'] = df2['close'].diff() > 0
        df2['MACD4C Increase'] = df2['MACD4C Histogram'].diff() > 0
        df2['MACD4C Divergence'] = df2['Price Increase'] != df2['MACD4C Increase']

    # 如果發現MACD底背離，則輸出"底背離"
        if df2['MACD Divergence'].any():
            print("底背離")
        counts = df2['MACD Divergence'].tail(day).value_counts()

    # 如果發現MACD4C底背離，則輸出"底背離"
        if df2['MACD4C Divergence'].any():

            print("macd4C底背離")
        counts2 = df2['MACD4C Divergence'].tail(day).value_counts()

    # 計算60日和100日的移動平均線
        df2['10_MA'] = df2['close'].rolling(window=first).mean()
        df2['60_MA'] = df2['close'].rolling(window=second).mean()

    # #計算可能連續背離true表示背離幾個
        counts = df2['MACD Divergence'].tail(day).value_counts()
        counts2 = df2['MACD4C Divergence'].tail(day).value_counts()

    # # 檢查當天20日均線是否大於60日均線且可能連續背離
        is_10_greater = df2['10_MA'].iloc[-1] > df2['60_MA'].iloc[-1]
        if  df2['10_MA'].iloc[-1] > df2['60_MA'].iloc[-1]:
            print('10大於60均線')
        else:
            print('無突破60')

      # 交易量
      # voluem_data=df2['transaction'].iloc[-1]>=1000

        voluem_data=df2['transaction'].tail(2).mean()>800
      # 價格小於80
        price_low=df2["close"].iloc[-1]<80

      # # 檢查前天股價是否小於20日均線
        ex_price_lowwer_than20mean = df2["close"].iloc[-2] < df2["close"].tail(20).mean()

       # 檢查當天股價是否大於20日均線
        Today_price_bigger_than_20mean = df2["close"].iloc[-1]>= df2["close"].tail(20).mean()

      # 檢查當天股價是否大於60日均線
        Today_price_bigger_than_60mean = df2["close"].iloc[-1]>= df2["close"].tail(60).mean()

      # 檢查大於60均
        ex_Today_price_bigger_than_60mean = df2["close"].iloc[-2] < df2["close"].tail(60).mean()

        if counts2[1]>=5 and counts[1]>=5 and Today_price_bigger_than_20mean == True and price_low==True and voluem_data==True and ex_price_lowwer_than20mean==True:
            small20.append(stock_cannt_read)
            print("前日股價小於20,今日股價大於20均,可能有連續背離")

        if counts2[1]>=5 and counts[1]>=5 and Today_price_bigger_than_60mean == True and price_low==True and voluem_data==True:
            small60.append(stock_cannt_read)
            print("股價大於60均,可能有連續背離")

        if counts2[1]>=5 and counts[1]>=5 and Today_price_bigger_than_60mean and price_low and voluem_data and ex_Today_price_bigger_than_60mean:
            exsmall60.append(stock_cannt_read)
            print("前日股價小於60 今日股價大於60,可能有連續背離")

        # if counts[1]>=5 and is_10_greater == True:
        #     maybe_exit.append(a)
        #     print("可能有連續背離")



        if counts2[1]>=5  and counts[1] >=5 and is_10_greater == True and price_low==True and voluem_data==True:
            maybe_exit.append(stock_cannt_read)
            print("10日軍大於60日,可能有連續背離")

    except Exception as e:
            really_cannt_read.append(stock_cannt_read)
            print(f"Failed to download data for {stock_cannt_read}.TW: {e}")

# 寄信功能--------------------------------------------------------------------------------------
def send_email():
    message="自動版只有投信且是今日購買"+f"{maybe_exit}"+"\n"+"未列入"+"\n"+f"{really_cannt_read}"+"\n"+"大於60均"+"\n"+f"{small60}"+"\n"+ "股票前日小於20,今日大於20" +"\n"+f"{small20}"+"\n"+ "股票前日小於60,今日大於60" +"\n"+f"{exsmall60}"+"\n"+ "大於60投信有買" +"\n"+f"{tcontinue_data}"+"\n"
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.ehlo()
            connection.starttls()

            result = connection.login('你的信箱', '登入密碼')
            connection.sendmail(
                from_addr='從哪寄',
                to_addrs='寄給誰',
            # to_addrs='66666@gmail.com',
                msg=f"Subject:要開盤囉!以下是周轉率結果\n\n{message}\n".encode("utf-8")
        )



def send_emailtohan():
    message=f"{maybe_exit}"+"\n"+"未列入"+"\n"+f"{really_cannt_read}"+"\n"+"大於60均"+"\n"+f"{small60}"+"\n"+ "股票前日小於20,今日大於20" +"\n"+f"{small20}"+"\n"+ "股票前日小於60,今日大於60" +"\n"+f"{exsmall60}"+"\n"+ "大於60投信有買" +"\n"+f"{tcontinue_data}"+"\n"
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.ehlo()
            connection.starttls()

            result = connection.login('你的信箱', '登入密碼')
            connection.sendmail(
                from_addr='從哪寄',
                # to_addrs='zxcvb4618@gmail.com',
                to_addrs='寄給誰',
                msg=f"Subject:要開盤囉!以下是周轉率結果\n\n{message}\n".encode("utf-8")
        )


# 取得三大法人買賣超代號獲取------------------------------------------------------------------------------------

import requests
headers = {
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}
res = requests.get('https://goodinfo.tw/tw2/StockList.asp?RPT_TIME=&MARKET_CAT=%E7%86%B1%E9%96%80%E6%8E%92%E8%A1%8C&INDUSTRY_CAT=%E6%8A%95%E4%BF%A1%E7%B4%AF%E8%A8%88%E8%B2%B7%E8%B6%85%E5%BC%B5%E6%95%B8+%E2%80%93+%E7%95%B6%E6%97%A5%40%40%E6%8A%95%E4%BF%A1%E7%B4%AF%E8%A8%88%E8%B2%B7%E8%B6%85%40%40%E6%8A%95%E4%BF%A1%E8%B2%B7%E8%B6%85%E5%BC%B5%E6%95%B8+%E2%80%93+%E7%95%B6%E6%97%A5', headers = headers)
res.encoding = 'utf-8'
res.text

from bs4 import BeautifulSoup
bs = BeautifulSoup(res.text, 'html.parser')
data = bs.select_one('#tblStockList')

import pandas
dfs = pandas.read_html(data.prettify())
node = dfs[0]
node.head()
threebstock_get=dfs[0]['代號']






# 取股票代號-----------------------------------------------------------------------------------------
import requests
import pandas as pd
result2 = requests.get("https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y")
dfa = pd.read_html(result2.text)[0][2][1:]
alldatas=dfa

stock_tr_big5=[]
stock_get_number=[]

#stock_get=dfs[0]['代號']
stock_get=alldatas

# stock_get=["2330"]
for i in threebstock_get:
    if len(i)>2 and len(i)<5:
        threebstock_get_number.append(i)

for i in stock_get:
    if len(i)>2 and len(i)<5:
        stock_get_number.append(i)

for stock_no in stock_get_number:
    macdanddevire(stock_no,參數1,參數2,參數3,參數4,參數5,參數6)

for stock_cannt_read in cannot_read:
    canntreadstock(參數1,參數2,參數3,參數4,參數5,參數6)

for i in small60:
  if i in threebstock_get_number:
    tcontinue_data.append(i)


# 寄信------------------------------------------------------------------------------------------------------
send_email()
send_emailtohan()



# 把股票存入mysqldb------------------------------------------------------------------------------------------

import pymysql
import datetime

stock_symbols =exsmall60


conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="ivan6403", db="stock60", charset="utf8")

try:
    # 建立游標
    with conn.cursor() as cursor:
        # 使用當前日期作為資料表名稱
        table_name = datetime.date.today().strftime("stock_data_%Y%m%d")
        # 創建新的資料表
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(255)
        )
        """
        cursor.execute(create_table_sql)
        
       
        insert_sql = f"INSERT INTO {table_name} (symbol) VALUES (%s)"
        
        
        for symbol in stock_symbols:
            
            values = (symbol,)
           
            cursor.execute(insert_sql, values)
        
    
    conn.commit()
    print("資料插入成功！")
except Exception as e:
    
    conn.rollback()
    print("資料插入失敗:", e)
finally:
    # 關閉連線
    conn.close()
    
    

