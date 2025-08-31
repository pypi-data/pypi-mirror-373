# libary for Vietcap trading platform
import requests
import pandas as pd
import json
# from .stocklist import *
from pandas import json_normalize
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# lịch sử giao dịch
def history(symbol, start, end, time="days"):
    headers = {
        'host': 'trading.vietcap.com.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://trading.vietcap.com.vn',
        'referer': 'https://trading.vietcap.com.vn/?filter-group=HOSE&filter-value=HOSE&view-type=FLAT&type=stock',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }

    end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
    end_timestamp = end_dt.timestamp()

    time_dict= {
        'days': 'ONE_DAY',
        'months': 'ONE_MONTH',
        'minutes': 'ONE_MINUTE',
        'hours': 'ONE_HOUR'
        }

    payload = {
        "timeFrame": time_dict[time],
        "symbols": [symbol],
        "countBack": 30_000,
        "to": end_timestamp
    }

    url = "https://trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart"
    
    session = requests.Session()  
    response = session.post(url, headers=headers, data=json.dumps(payload))
    json_data = response.json()

    def is_stock(symbol):
        if len(symbol) <=3:
            return True
        else:
            return False
         

    if not json_data or not isinstance(json_data, list) or len(json_data) ==0:
        print(f"Không có dữ liệu cho mã {symbol}.")
        return pd.DataFrame()

    data = json_data[0]
    
    df = pd.DataFrame(data)
    df = df[["symbol", "t", "o","c", "h", "l", "v"]]
    df["t"] = pd.to_numeric(df['t'], errors='coerce')
    df["t"] = df['t'].apply(lambda x: datetime.fromtimestamp(x))
    if time in ['minutes','hours']:
        df["t"] = pd.to_datetime(df["t"], errors='coerce').dt.tz_localize(None).dt.floor("s")
    if time in ['days','months']:
        df["t"] = pd.to_datetime(df["t"], errors='coerce').dt.tz_localize(None).dt.floor("d")
    df=df.sort_values(by='t',ascending=False).reset_index(drop=True)

    if is_stock(symbol):
        df[["o", "h", "l", "c"]] = df[["o", "h", "l", "c"]].apply(lambda x: round(x / 1000,2))
   
    df.rename(columns={"symbol": "symbol",
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "t": "time",
            "v": "volume"
        }, inplace=True)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    return df[df["time"] >= start]

# sổ lệnh thường
def utc_time_to_hochiminh_time(utc_time: str):
    utc_time = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    vn_time = pytz.utc.localize(utc_time).astimezone(pytz.timezone("Asia/Ho_Chi_Minh"))
    return pd.to_datetime(vn_time.replace(tzinfo=None).replace(microsecond=0))

def intraday(symbol):
        headers = {
            'host': 'trading.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/?filter-group=HOSE&filter-value=HOSE&view-type=FLAT',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }
    
        payload = {
            "symbol": symbol.upper(),
            "limit": 50_000,
            "truncTime": None,
        }
        url = "https://trading.vietcap.com.vn/api/market-watch/LEData/getAll"

        try: 
            session = requests.Session()
            response = session.post(url, headers=headers, data=json.dumps(payload))
            data = response.json()
            data = json_normalize(data)
            data = data[[#"id",
                         "symbol",
                         "matchType",
                         "matchVol",
                         "matchPrice",
                         "createdAt"]]
            data.rename(columns={
            "symbol": "Mã",
            "matchType": "Mua/Bán",
            "matchVol": "Khối lượng",
            "matchPrice": "Giá",
            "createdAt": "Thời gian"
            },inplace=True)
            data[["Giá","Khối lượng"]] = data[["Giá","Khối lượng"]].apply(pd.to_numeric, errors='coerce').astype("Int64")
            data["Giá"]= data["Giá"].apply(lambda x: x / 1000)
            data["Mua/Bán"] = data["Mua/Bán"].replace({"b": "Mua", "s": "Bán", "unknown": "ATO/ATC"})
            data["Thời gian"] = data["Thời gian"].apply(utc_time_to_hochiminh_time)

            return data
        except Exception as e :
            print(f"Lỗi sổ lệnh: {e}")
            return pd.DataFrame()

# Sổ lệnh chi tiết
def intraday_order(symbol):
    headers = {
        'host': 'trading.vietcap.com.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://trading.vietcap.com.vn',
        'referer': 'https://trading.vietcap.com.vn/?filter-group=HOSE&filter-value=HOSE&view-type=FLAT',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }
    payload = {
        "symbol": symbol.upper(),
        "limit": 30_000,
        "truncTime": None,
        "timeFrame": "ONE_SECOND"
    }
    url = "https://trading.vietcap.com.vn/api/sts-computation/BigOrder/getAll"
    
    try: 
        session = requests.Session()
        response = session.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()
        data = json_normalize(data)
        data = data[[ "symbol", "matchType", "matchVol", "price",  "total", "createdAt",  "type"]]
        data.rename(columns={
            "symbol": "Mã",
            "price": "Giá",
            "matchVol": "Khối lượng",
            "total": "Giá trị giao dịch",
            "matchType": "Mua/Bán",
            "type": "Phân Loại",
            "createdAt": "Thời gian"
        }, inplace=True)
        data["Mua/Bán"] = data["Mua/Bán"].replace({"b": "Mua", "s": "Bán"})
        data["Phân Loại"] = data["Phân Loại"].replace({"sheep": "Cừu non", "wolf": "Sói già", "shark": "Cá mập"})
        data["Giá"] = data["Giá"].astype(float)
        data["Giá"] = data["Giá"].apply(lambda x: round(x / 1000, 2))
        data["Thời gian"] = data["Thời gian"].apply(utc_time_to_hochiminh_time)
        int_cols = ["Khối lượng", "Giá trị giao dịch"]
        data[int_cols] = data[int_cols].apply(pd.to_numeric, errors='coerce').astype("Int64")
        return data
    except Exception as e :
        print(f"Lỗi sổ lệnh: {e}")
        return pd.DataFrame()

def exchange_other():
    try:
        headers = {
            'host': 'trading.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/?filter-group=HOSE&filter-value=HOSE&view-type=FLAT&type=stock',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }   

        US = ["^DJI", "^GSPC", "^IXIC", "^RUT", "^GDOW"]
        EU = ["^FTSE", "^STOXX", "^GDAXI", "^FCHI", "FTSEMIB.MI"]
        ASIA = ["^ADOW", "^N225", "^HSI", "000001.SS", "^STI"]
        goods = ["CL=F", "GC=F","SI=F", "HG=F", "ZR=F"]
        other = ["VND=X", "^TNX", "BTC-USD", "ETH-USD"]

        cols = US + EU + ASIA + goods + other

        payload = {
            "symbols": cols
        }

        url = "https://trading.vietcap.com.vn/api/price/globalPrice/getList"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()
        data = json_normalize(data)
        data = data[["id", "price", "change", "changePercent"]]
        data = data.rename(columns={
            "id": "Sàn",
            "price": "Điểm",
            "change": "Thay đổi",
            "changePercent": "Thay đổi (%)",
        })

        data["Sàn"] = data["Sàn"].replace({
            "^DJI": "DOWjones", "^GSPC": "S&P500", "^IXIC": "NASDAQ", "^RUT": "Russell", "^GDOW": "Dow Jones Global", 
            "^FTSE": "FTSE 100", "^STOXX": "STOXX 600", "^GDAXI": "DAX", "^FCHI": "CAC 40", "FTSEMIB.MI": "FTSE MIB",
            "^ADOW": "Asia ASX", "^N225": "NIKKEI 225", "^HSI": "Hang Seng", "000001.SS": "Shanghai", "^STI": "Singapore",
            'CL=F': "Dầu thô", "GC=F": "Vàng", "SI=F": "Bạc", "HG=F": "Đồng", "ZR=F": "Gạo",
            'VND=X': "VND/USD", "^TNX": "TP Mỹ 10 năm(%)", "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum"})
        return data.sort_values("Thay đổi (%)",ascending=False).reset_index(drop=True)
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# dữ liệu sàn chứng khoán việt nam
def stock_exchange(exchange):
    try:
        headers = {
        'host': 'trading.vietcap.com.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://trading.vietcap.com.vn',
        'referer': 'https://trading.vietcap.com.vn/?filter-group=HOSE&filter-value=HOSE&view-type=FLAT',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        exchange_map = {'HOSE': hose,
                        'HNX': hnx,
                        'UPCOM': upcom,
                        'VN30': vn30,
                        'VNMIDCAP': vnmidcap,
                        'HNX30': hnx30,
                        'HDTL': hdtl
                    }

        exchange = exchange_map.get(exchange.upper(), exchange)
        payload = {
            "symbols": exchange
        }
        url = "https://trading.vietcap.com.vn/api/price/symbols/getList"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()
        data = json_normalize(data)
        data = data[["matchPrice.symbol", "matchPrice.highest", "matchPrice.lowest", "matchPrice.matchPrice", 
                     "matchPrice.accumulatedVolume", "matchPrice.foreignSellVolume", "matchPrice.foreignBuyVolume", 
                     "matchPrice.currentRoom", "listingInfo.board"]]
        data.rename(columns={
            "matchPrice.symbol": "Mã",
            "matchPrice.highest": "Giá trần",
            "matchPrice.lowest": "Giá sàn",
            "matchPrice.matchPrice": " Giá hiện tại",
            "matchPrice.accumulatedVolume": "Khối lượng giao dịch",
            "matchPrice.foreignSellVolume": " KL NN Bán",
            "matchPrice.foreignBuyVolume": "KL NN Mua",
            "matchPrice.currentRoom": "Tổng giá trị giao dịch room ngoại",
            "listingInfo.board": "Sàn"
        }, inplace=True)
        cols= ["Giá trần", "Giá sàn", " Giá hiện tại"]
        data[cols] = data[cols].apply(lambda x: x / 1000)
        return data
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

def overview_market(indicator, start, end):
    try:
        headers = {
            'authority': 'restv2.fireant.vn',
            'path':'/symbols/VNINDEX/historical-quotes?startDate=2025-03-18&endDate=2025-04-18&offset=0&limit=100',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7,en-GB;q=0.6',
            'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkdYdExONzViZlZQakdvNERWdjV4QkRITHpnSSIsImtpZCI6IkdYdExONzViZlZQakdvNERWdjV4QkRITHpnSSJ9.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmZpcmVhbnQudm4iLCJhdWQiOiJodHRwczovL2FjY291bnRzLmZpcmVhbnQudm4vcmVzb3VyY2VzIiwiZXhwIjoyMDQyMTgwMDgzLCJuYmYiOjE3NDIxODAwODMsImNsaWVudF9pZCI6ImZpcmVhbnQudHJhZGVzdGF0aW9uIiwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsInJvbGVzIiwiZW1haWwiLCJhY2NvdW50cy1yZWFkIiwiYWNjb3VudHMtd3JpdGUiLCJvcmRlcnMtcmVhZCIsIm9yZGVycy13cml0ZSIsImNvbXBhbmllcy1yZWFkIiwiaW5kaXZpZHVhbHMtcmVhZCIsImZpbmFuY2UtcmVhZCIsInBvc3RzLXdyaXRlIiwicG9zdHMtcmVhZCIsInN5bWJvbHMtcmVhZCIsInVzZXItZGF0YS1yZWFkIiwidXNlci1kYXRhLXdyaXRlIiwidXNlcnMtcmVhZCIsInNlYXJjaCIsImFjYWRlbXktcmVhZCIsImFjYWRlbXktd3JpdGUiLCJibG9nLXJlYWQiLCJpbnZlc3RvcGVkaWEtcmVhZCJdLCJzdWIiOiI1YWMwOWFmZS00OWQ1LTRlZGQtYTkxOS1mMTc3ZmQ5MmJmZjkiLCJhdXRoX3RpbWUiOjE3NDIxODAwODMsImlkcCI6Ikdvb2dsZSIsIm5hbWUiOiJsdW9uZ2Jhb3F1YW4yNUBnbWFpbC5jb20iLCJzZWN1cml0eV9zdGFtcCI6IjFhNWVkNmRiLTgzNWQtNDcxMC05MzBjLWQ2MWRkMjU2YjgwZCIsImp0aSI6Ijc5ZTE3OTFiYWQ0OWM5YWRlMmUwYWRkMjlmOGVmZDViIiwiYW1yIjpbImV4dGVybmFsIl19.KqciuLmnUfgXD9hb1u3UA31n9imDpENW2ny3XBMF7IUOAoqpEWOVVOHbmdgX8anAS2mLPMP1opJeb66GlCfjWgElTcXXNB8L35TrvA_NnkrqC4xjV4KtJacRY9Y5R0q_Fq58tN0d-lKKgg8A9QZ7TyHkBlzQoHZePsVwlnQEe54hSfIeJeZazvEfJH1GKzcIEbCPOPbUTpJ7iauprgr5WnKQkRV3MseQW5O-KTI0s0BvRNofgNOXZo_j3k96agBgFhKD3YDXCokYTtpTGwQexQuwEogIaDFGIMqZ6zkkdPGYgDrTag9kJBuLInkHiV-siXVHQd_ZHlyaWsE72sV_gQ',
            'Origin': 'https://fireant.vn',
            'referer': 'u=1, i',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }
        url = f"https://restv2.fireant.vn/symbols/{indicator}/historical-quotes"
        params = {
                "startDate": start,
                "endDate": end,
                "offset": 0,
                "limit": 100
            }

        request = requests.get(url, headers=headers, params=params)
        data = request.json()
        data = pd.json_normalize(data)
        data = data[['date','symbol','priceClose','totalVolume','totalValue','buyForeignQuantity','sellForeignQuantity','buyForeignValue','sellForeignValue']]
        cols_ty=['buyForeignValue','sellForeignValue']
        data[cols_ty] = data[cols_ty].round(0) # làm tròn sô thập phân
        cols=[ 'totalVolume', 'totalValue', 'buyForeignQuantity','sellForeignQuantity','buyForeignValue','sellForeignValue']
        data[cols] = data[cols].apply(pd.to_numeric, errors='coerce').astype("Int64")
        data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
        data.rename(columns={
            'date':'Ngày',
            'symbol':'Sàn',
            'priceClose':'Điểm',
            'totalVolume':'KL khớp',
            'dealVolume':'Deal Volume',
            'totalValue':'Tổng giá trị',
            'buyForeignQuantity':'KL Mua NN',
            'sellForeignQuantity':'KL Bán NN',
            'buyForeignValue':'GT Mua NN',
            'sellForeignValue':'GT Bán NN',
        }, inplace=True)
        data["GT Ròng NN"] = data["GT Mua NN"] - data["GT Bán NN"]
        return  data
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# bảng xếp hạng cổ phiếu
def top_stock(exchange,type):
    try:
        headers = {
            'authority': 'scanner.tradingview.com',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://www.tradingview.com',
            'referer': 'https://www.tradingview.com/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        payload = {
            "columns": [
                "name",  # cổ phiếu
                "sector", # ngành
                "exchange", # sàn
                "close",  #giá
                "change", # thay đổi giá
                "volume", # KLGD
                "volume_change", #Thay đổi KLGD #ở đâu ra
                "market_cap_basic", #vốn hóa
                "price_earnings_ttm", #P/E raito
                "earnings_per_share_diluted_ttm", #EPS 
                "relative_volume_10d_calc", #KLTB 10 ngày
                "dividends_yield_current", #Tỷ suất cổ tức
                "total_revenue_ttm", #tổng doanh thu
                "earnings_per_share_diluted_yoy_growth_ttm", # doanh thu tăng trưởng
                "oper_income_ttm", # Lợi nhuận hoạt động(năm)
                "net_income_ttm" #LNST
                ],
            "ignore_unknown_fields": False,
            "markets": ["vietnam"],
            "options": {"lang": "en"},
            "range": [0, 1600],
            "sort": {"sortBy": "market_cap_basic","sortOrder": "desc"}

        }

        url = "https://scanner.tradingview.com/vietnam/scan"
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        data = response.json()
        datax=pd.json_normalize(data['data'])
        datay=datax.drop(columns='s')
        df_data=pd.DataFrame(datay['d'].to_list())
        df_data.columns = ["Cổ phiếu", "Ngành", "Sàn", "Giá", "Thay đổi giá(%)", "Khối lượng", "Thay đổi Khối lượng(%)", "Vốn hóa", "PE Ratio", "EPS", "KLTB 10 ngày", "Tỷ suất cổ tức(%)",
        "Tổng doanh thu", "Tăng trưởng doanh thu(%)", "Lợi nhuận hoạt động (năm)", "LNST"]
        df_data=df_data.fillna(0)
        df_data['Giá'] = df_data['Giá'].apply(lambda x:x / 1000)
        cols_round=['Thay đổi giá(%)',"Thay đổi Khối lượng(%)","PE Ratio", "EPS","KLTB 10 ngày","Tỷ suất cổ tức(%)","Tăng trưởng doanh thu(%)"]
        df_data[cols_round] = df_data[cols_round].apply(lambda x:round(x,2))
        cols=['Khối lượng','Vốn hóa','Tổng doanh thu','Lợi nhuận hoạt động (năm)','LNST']
        df_data[cols]=df_data[cols].astype(int)
        industry_map = {"Finance": "Tài chính",
                        "Transportation": "Vận tải",
                        "Consumer Non-Durables": "Hàng tiêu dùng không bền",
                        "Non-Energy Minerals": "Khoáng sản phi năng lượng",
                        "Technology Services": "Công nghệ",
                        "Utilities": "Tiện ích công cộng",
                        "Process Industries": "Chế biến",
                        "Retail Trade": "Bán lẻ",
                        "Consumer Durables": "Hàng tiêu dùng bền",
                        "Energy Minerals": "Khoáng sản năng lượng",
                        "Producer Manufacturing": "Sản xuất công nghiệp",
                        "Distribution Services": "Phân phối",
                        "Electronic Technology": "Điện tử",
                        "Industrial Services": "Công nghiệp",
                        "Health Technology": "Công nghệ y tế",
                        "Commercial Services": "Thương mại",
                        "Health Services": "Y tế",
                        "Consumer Services": "Tiêu dùng",
                        "Communications": "Viễn thông",
                        "0": "Không xác định",
                        "Miscellaneous": "Khác"
                    }

        df_data["Ngành"] = df_data["Ngành"].replace(industry_map)
        ascending= type != 'up'
        return df_data[df_data['Sàn']==exchange].sort_values("Thay đổi giá(%)",ascending=ascending).iloc[:10]
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# lịch sử giá cổ phiếu
def price_history(symbol,time,start=None,end=None):
    try:
        headers = {
            'host': 'iq.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            }

        time_dict= {
            'days': 'ONE_DAY',
            'months': 'ONE_MONTH',
            'quarters': 'ONE_QUARTER',
            'years': 'ONE_YEAR'
            }

        if time=='months':
            start = start + '-01'
            end = end + '-01'
        elif time=='quarters':
            start = start + '-01-01'
            end = end + '-12-31'
        elif time=='years':
            start = start + '-01-01'
            end = end + '-01-01'

        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(end, '%Y-%m-%d')

        start_date = start.strftime('%Y%m%d')
        end_date = end.strftime('%Y%m%d')

        params = {
            "timeFrame": time_dict[time] ,
            "fromDate": start_date,
            "toDate": end_date,
            "size": 50000
        }
        url=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/price-history'
        response=requests.get(url,headers=headers,params=params)
        data=json_normalize(response.json()['data']['content'])
        cols_price=['closePriceAdjusted',
                    'openPriceAdjusted',
                    'highestPriceAdjusted',
                    'lowestPriceAdjusted']
        col_volume=['totalMatchVolume',
                       'totalMatchValue',
                       'totalDealVolume',
                       'totalDealValue',
                       'totalVolume',
                       'totalValue',
                       'totalBuyUnmatchedVolume',
                       'totalSellUnmatchedVolume',    
                       'marketCap']
        cols_pricehis=['ticker','tradingDate','priceChange','percentPriceChangeAdjusted'] +cols_price + col_volume
        data=data[cols_pricehis]
        data['tradingDate'] = pd.to_datetime(data['tradingDate'])
        quy={'1': 'Q1',
             '4': 'Q2',
             '7': 'Q3',
             '10': 'Q4'}
        if time=='months':
            data['tradingDate'] = data['tradingDate'].dt.strftime('%Y-%m')
        elif time=='quarters':
            data['tradingDate']=(data['tradingDate'].dt.month.map(lambda m:quy.get(str(m),'')))+' '+data['tradingDate'].dt.year.astype(str)
        elif time=='years':
            data['tradingDate'] = data['tradingDate'].dt.strftime('%Y').astype(int)
        data [['priceChange']+ cols_price] = data [['priceChange'] + cols_price].apply(lambda x:round(x/1000,2), axis=1)
        data['percentPriceChangeAdjusted'] = data['percentPriceChangeAdjusted'].apply(lambda x: round(x*100,2))
        data [col_volume] = data [col_volume].fillna(0).round(0).astype(int)
        rename_his={
            'ticker': 'Mã CP',
            'tradingDate': 'Thời điểm GD',
            'priceChange': 'Thay đổi giá',
            'percentPriceChangeAdjusted': 'Thay đổi (%)',
            'closePriceAdjusted': 'Giá đóng cửa',
            'openPriceAdjusted': 'Giá mở cửa',
            'highestPriceAdjusted': 'Giá cao nhất',
            'lowestPriceAdjusted': 'Giá thấp nhất',
            'totalMatchVolume': 'KLGD khớp lệnh',
            'totalMatchValue': 'GTGD khớp lệnh',
            'totalDealVolume': 'KLGD thoả thuận',
            'totalDealValue': 'GTGD thoả thuận',
            'totalVolume': 'Tổng KLGD',
            'totalValue': 'Tổng GTGD',
            'totalBuyUnmatchedVolume': 'KLGD mua chờ khớp',
            'totalSellUnmatchedVolume': 'KLGD bán chờ khớp',
            'marketCap': 'Vốn hoá'
        } 
        data=data.rename(columns=rename_his)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        return data
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# lịch sử giá cổ phiếu tổng hợp
def price_history_summary(symbol):
    try:
        headers = {
                'host': 'iq.vietcap.com.vn',
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://trading.vietcap.com.vn',
                'referer': 'https://trading.vietcap.com.vn/',
                'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
                }

        url_sumary=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/price-history-summary'
        response=requests.get(url_sumary,headers=headers)
        data_sumary=pd.json_normalize(response.json()['data'])
        pd.set_option('display.max_columns', None)
        cols_sumary_his_total=['totalMatchVolume','totalMatchValue','totalDealVolume','totalDealValue','totalVolume','totalValue','totalBuyUnmatchedVolume','totalSellUnmatchedVolume']
        cols_sumary_his_avg=['averageMatchVolume','averageMatchValue','averageDealVolume','averageDealValue','averageVolume','averageValue','totalBuyUnmatchedVolumeAvg','totalSellUnmatchedVolumeAvg']
        #pd.Series(data_sumary.columns.tolist()).to_csv(r'D:\DE\API\vietcap\statistic\data_sumary_columns.csv', index=False)

        rename_summary={'totalMatchVolume': 'KLGD khớp lệnh',
                        'totalMatchValue': 'GTGD khớp lệnh',
                        'totalDealVolume': 'KLGD thoả thuận',
                        'totalDealValue': 'GTGD thoả thuận',
                        'totalVolume': 'Tổng KLGD',
                        'totalValue': 'Tổng GTGD',
                        'totalBuyUnmatchedVolume': 'KLGD mua chờ khớp',
                        'totalSellUnmatchedVolume': 'KLGD bán chờ khớp',
                        'averageMatchVolume': 'KLGD khớp lệnh',
                        'averageMatchValue': 'GTGD khớp lệnh',
                        'averageDealVolume': 'KLGD thoả thuận',
                        'averageDealValue': 'GTGD thoả thuận',
                        'averageVolume': 'Tổng KLGD',
                        'averageValue': 'Tổng GTGD',
                        'totalBuyUnmatchedVolumeAvg': 'KLGD mua chờ khớp',
                        'totalSellUnmatchedVolumeAvg': 'KLGD bán chờ khớp'
                        } 

        data_sumary_his_total=data_sumary[cols_sumary_his_total]
        data_sumary_his_total.insert(0, 'Mã CP', symbol.upper())
        data_sumary_his_total.insert(1, 'Phân loại', 'Tổng')
        data_sumary_his_total= data_sumary_his_total.rename(columns=rename_summary)

        data_sumary_his_avg=data_sumary[cols_sumary_his_avg]
        data_sumary_his_avg.insert(0, 'Mã CP', symbol.upper())
        data_sumary_his_avg.insert(1, 'Phân loại', 'Trung bình')
        data_sumary_his_avg = data_sumary_his_avg.rename(columns=rename_summary)

        data_sumary= pd.concat([data_sumary_his_total, data_sumary_his_avg], axis=0)
        cols=data_sumary.columns[2:]
        data_sumary[cols]= data_sumary[cols].apply(lambda x : x.round(0).astype(int))
        return data_sumary
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# lịch sử giao dịch nước ngoài
def foreign_history(symbol,time,start=None,end=None):
    try:
        headers = {
        'host': 'iq.vietcap.com.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://trading.vietcap.com.vn',
        'referer': 'https://trading.vietcap.com.vn/',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        time_dict= {
            'days': 'ONE_DAY',
            'months': 'ONE_MONTH',
            'quarters': 'ONE_QUARTER',
            'years': 'ONE_YEAR'
            }
        if time=='months':
            start = start + '-01'
            end = end + '-01'
        elif time=='quarters':
            start = start + '-01-01'
            end = end + '-12-31'
        elif time=='years':
            start = start + '-01-01'
            end = end + '-01-01'
        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(end, '%Y-%m-%d')
        start_date = start.strftime('%Y%m%d')
        end_date = end.strftime('%Y%m%d')
        params = {
            "timeFrame": time_dict[time] ,
            "fromDate": start_date,
            "toDate": end_date,
            "size": 50000
        }
        url=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/price-history'
        response=requests.get(url,headers=headers,params=params)
        data=json_normalize(response.json()['data']['content'])
        cols_amount=['foreignNetVolumeMatched',
                       'foreignNetValueMatched',
                       'foreignBuyVolumeMatched',
                       'foreignBuyValueMatched',
                       'foreignSellVolumeMatched',
                       'foreignSellValueMatched',
                       'foreignNetVolumeDeal',
                       'foreignNetValueDeal',
                       'foreignBuyVolumeDeal',
                       'foreignBuyValueDeal',
                       'foreignSellVolumeDeal',
                       'foreignSellValueDeal',
                       'foreignNetVolumeTotal',
                       'foreignNetValueTotal',
                       'foreignBuyVolumeTotal',
                       'foreignBuyValueTotal',
                       'foreignSellVolumeTotal',
                       'foreignSellValueTotal']
        cols_percent=['foreignRoomPercentage',   #(%)
                       'foreignOwnedPercentage',  #(%)
                       'foreignAvailablePercentage'] #(%)
        cols_data=['ticker','tradingDate']+cols_amount+cols_percent+['foreignCurrentRoom']
        data=data[cols_data]
        data['tradingDate'] = pd.to_datetime(data['tradingDate'])
        quy={'1': 'Q1',
             '4': 'Q2',
             '7': 'Q3',
             '10': 'Q4'}
        if time=='months':
            data['tradingDate'] = data['tradingDate'].dt.strftime('%Y-%m')
        elif time=='quarters':
            data['tradingDate']=(data['tradingDate'].dt.month.map(lambda m:quy.get(str(m),'')))+' '+data['tradingDate'].dt.year.astype(str)
        elif time=='years':
            data['tradingDate'] = data['tradingDate'].dt.strftime('%Y').astype(int)
        data [cols_amount+['foreignCurrentRoom']] = data [cols_amount+['foreignCurrentRoom']].astype(int)
        data[cols_percent] = data[cols_percent].apply(lambda x: round(x*100,2))
        rename_foreign = {
            'ticker': 'Mã CP',
            'tradingDate': 'Thời điểm GD',
            'foreignNetVolumeMatched': 'KLGD khớp lệnh ròng ',
            'foreignNetValueMatched': 'GTGD khớp lệnh ròng ',
            'foreignBuyVolumeMatched': 'KLGD khớp lệnh mua ',
            'foreignBuyValueMatched': 'GTGD khớp lệnh mua ',
            'foreignSellVolumeMatched': 'KLGD khớp lệnh bán ',
            'foreignSellValueMatched': 'GTGD khớp lệnh bán ',
            'foreignNetVolumeDeal': 'KLGD thoả thuận ròng ',
            'foreignNetValueDeal': 'GTGD thoả thuận ròng ',
            'foreignBuyVolumeDeal': 'KLGD thoả thuận mua ',
            'foreignBuyValueDeal': 'GTGD thoả thuận mua ',
            'foreignSellVolumeDeal': 'KLGD thoả thuận bán ',
            'foreignSellValueDeal': 'GTGD thoả thuận bán ',
            'foreignNetVolumeTotal': 'Tổng KLGD ròng',
            'foreignNetValueTotal': 'Tổng GTGD ròng',
            'foreignBuyVolumeTotal': 'Tổng KLGD mua',
            'foreignBuyValueTotal': 'Tổng GTGD mua',
            'foreignSellVolumeTotal': 'Tổng KLGD bán',
            'foreignSellValueTotal': 'Tổng GTGD bán',
            'foreignRoomPercentage': '% Khối ngoại tối đa',
            'foreignOwnedPercentage': '% Khối ngoại sở hữu',
            'foreignAvailablePercentage': '% Khối ngoại còn lại',
            'foreignCurrentRoom': 'CP còn lại'
        }
        data=data.rename(columns=rename_foreign)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        return data
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# lịch sử giao dịch nước ngoài tổng hợp
def foreign_history_summary(symbol):
    try:
        headers = {
                'host': 'iq.vietcap.com.vn',
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://trading.vietcap.com.vn',
                'referer': 'https://trading.vietcap.com.vn/',
                'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
                }
        url_sumary=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/price-history-summary'
        response=requests.get(url_sumary,headers=headers)
        data_sumary=pd.json_normalize(response.json()['data'])
        pd.set_option('display.max_columns', None)
        cols_sumary_foreign_total=['foreignNetVolumeMatched',
                                   'foreignNetValueMatched',
                                   'foreignBuyVolumeMatched',
                                   'foreignBuyValueMatched',
                                   'foreignSellVolumeMatched',
                                   'foreignSellValueMatched',
                                   'foreignNetVolumeDeal',
                                   'foreignNetValueDeal',
                                   'foreignBuyVolumeDeal',
                                   'foreignBuyValueDeal',
                                   'foreignSellVolumeDeal',
                                   'foreignSellValueDeal',
                                   'foreignNetVolumeTotal',
                                   'foreignNetValueTotal',
                                   'foreignBuyVolumeTotal',
                                   'foreignBuyValueTotal',
                                   'foreignSellVolumeTotal',
                                   'foreignSellValueTotal'
                                   ]
        cols_sumary_foreign_avg=['foreignNetVolumeMatchedAvg',
                                 'foreignNetValueMatchedAvg',
                                 'foreignBuyVolumeMatchedAvg',
                                 'foreignBuyValueMatchedAvg',
                                 'foreignSellVolumeMatchedAvg',
                                 'foreignSellValueMatchedAvg',
                                 'foreignNetVolumeDealAvg',
                                 'foreignNetValueDealAvg',
                                 'foreignBuyVolumeDealAvg',
                                 'foreignBuyValueDealAvg',
                                 'foreignSellVolumeDealAvg',
                                 'foreignSellValueDealAvg',
                                 'foreignNetVolumeTotalAvg',
                                 'foreignNetValueTotalAvg',
                                 'foreignBuyVolumeTotalAvg',
                                 'foreignBuyValueTotalAvg',
                                 'foreignSellVolumeTotalAvg',
                                 'foreignSellValueTotalAvg'
                                 ]

        rename_summary={
            'foreignNetVolumeMatched': 'KLGD khớp lệnh ròng',
            'foreignNetValueMatched': 'GTGD khớp lệnh ròng',
            'foreignBuyVolumeMatched': 'KLGD khớp lệnh mua',
            'foreignBuyValueMatched': 'GTGD khớp lệnh mua',
            'foreignSellVolumeMatched': 'KLGD khớp lệnh bán',
            'foreignSellValueMatched': 'GTGD khớp lệnh bán',

            'foreignNetVolumeDeal': 'KLGD thoả thuận ròng',
            'foreignNetValueDeal': 'GTGD thoả thuận ròng',
            'foreignBuyVolumeDeal': 'KLGD thoả thuận mua',
            'foreignBuyValueDeal': 'GTGD thoả thuận mua',
            'foreignSellVolumeDeal': 'KLGD thoả thuận bán',
            'foreignSellValueDeal': 'GTGD thoả thuận bán',

            'foreignNetVolumeTotal': 'Tổng KLGD ròng',
            'foreignNetValueTotal': 'Tổng GTGD ròng',
            'foreignBuyVolumeTotal': 'Tổng KLGD mua',
            'foreignBuyValueTotal': 'Tổng GTGD mua',
            'foreignSellVolumeTotal': 'Tổng KLGD bán',
            'foreignSellValueTotal': 'Tổng GTGD bán',

            'foreignNetVolumeMatchedAvg': 'KLGD khớp lệnh ròng',
            'foreignNetValueMatchedAvg': 'GTGD khớp lệnh ròng',
            'foreignBuyVolumeMatchedAvg': 'KLGD khớp lệnh mua',
            'foreignBuyValueMatchedAvg': 'GTGD khớp lệnh mua',
            'foreignSellVolumeMatchedAvg': 'KLGD khớp lệnh bán',
            'foreignSellValueMatchedAvg': 'GTGD khớp lệnh bán',

            'foreignNetVolumeDealAvg': 'KLGD thoả thuận ròng',
            'foreignNetValueDealAvg': 'GTGD thoả thuận ròng',
            'foreignBuyVolumeDealAvg': 'KLGD thoả thuận mua',
            'foreignBuyValueDealAvg': 'GTGD thoả thuận mua',
            'foreignSellVolumeDealAvg': 'KLGD thoả thuận bán',
            'foreignSellValueDealAvg': 'GTGD thoả thuận bán',

            'foreignNetVolumeTotalAvg': 'Tổng KLGD ròng',
            'foreignNetValueTotalAvg': 'Tổng GTGD ròng',
            'foreignBuyVolumeTotalAvg': 'Tổng KLGD mua',
            'foreignBuyValueTotalAvg': 'Tổng GTGD mua',
            'foreignSellVolumeTotalAvg': 'Tổng KLGD bán',
            'foreignSellValueTotalAvg': 'Tổng GTGD bán',
        }
        data_sumary_his_total=data_sumary[cols_sumary_foreign_total]
        data_sumary_his_total.insert(0, 'Mã CP', symbol.upper())
        data_sumary_his_total.insert(1, 'Phân loại', 'Tổng')
        data_sumary_his_total= data_sumary_his_total.rename(columns=rename_summary)
        data_sumary_his_avg=data_sumary[cols_sumary_foreign_avg]
        data_sumary_his_avg.insert(0, 'Mã CP', symbol.upper())
        data_sumary_his_avg.insert(1, 'Phân loại', 'Trung bình')
        data_sumary_his_avg = data_sumary_his_avg.rename(columns=rename_summary)
        data_sumary= pd.concat([data_sumary_his_total, data_sumary_his_avg], axis=0)
        cols=data_sumary.columns[2:]
        data_sumary[cols]= data_sumary[cols].apply(lambda x : x.round(0).astype(int))
        return data_sumary
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# lịch sử giao dịch tự doanh
def proprietary_history(symbol,time,start=None,end=None):
    try:
        headers = {
            'host': 'iq.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            }

        time_dict= {
            'days': 'ONE_DAY',
            'months': 'ONE_MONTH',
            'quarters': 'ONE_QUARTER',
            'years': 'ONE_YEAR'
            }
        if time=='months':
            start = start + '-01'
            end = end + '-01'
        elif time=='quarters':
            start = start + '-01-01'
            end = end + '-12-31'
        elif time=='years':
            start = start + '-01-01'
            end = end + '-01-01'
        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(end, '%Y-%m-%d')
        start_date = start.strftime('%Y%m%d')
        end_date = end.strftime('%Y%m%d')
        params = {
            "timeFrame": time_dict[time] ,
            "fromDate": start_date,
            "toDate": end_date,
            "size": 50000
        }
        url=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/proprietary-history'
        response=requests.get(url,headers=headers,params=params)
        data=json_normalize(response.json()['data']['content'])
        cols_volval=['totalMatchTradeNetVolume',
                         'totalMatchTradeNetValue',
                         'totalMatchBuyTradeVolume',
                         'totalMatchBuyTradeValue',
                         'totalMatchSellTradeVolume',
                         'totalMatchSellTradeValue',
                         'totalDealTradeNetVolume',
                         'totalDealTradeNetValue',
                         'totalDealBuyTradeVolume',
                         'totalDealBuyTradeValue',
                         'totalDealSellTradeVolume',
                         'totalDealSellTradeValue',
                         'totalTradeNetVolume',
                         'totalTradeNetValue',
                         'totalBuyTradeVolume',
                         'percentBuyTradeVolume',
                         'totalBuyTradeValue',
                         'percentBuyTradeValue',
                         'totalSellTradeVolume',
                         'percentSellTradeVolume',
                         'totalSellTradeValue',
                         'percentSellTradeValue'
                         ]
        cols_percent=['percentBuyTradeVolume',
                      'percentBuyTradeValue',
                      'percentSellTradeVolume',
                      'percentSellTradeValue'
                    ]
        int_cols=list(set(cols_volval)-set(cols_percent))
        cols_prop=['ticker','tradingDate'] + cols_volval
        data=data[cols_prop]
        data['tradingDate'] = pd.to_datetime(data['tradingDate'])
        quy={'1': 'Q1',
             '4': 'Q2',
             '7': 'Q3',
             '10': 'Q4'}
        if time=='months':
            data['tradingDate'] = data['tradingDate'].dt.strftime('%Y-%m')
        elif time=='quarters':
            data['tradingDate']=(data['tradingDate'].dt.month.map(lambda m:quy.get(str(m),'')))+' '+data['tradingDate'].dt.year.astype(str)
        elif time=='years':
            data['tradingDate'] = data['tradingDate'].dt.strftime('%Y').astype(int)
        data [cols_percent] = data [cols_percent].apply(lambda x:round(x*100,2))
        data [int_cols] = data [int_cols].fillna(0).round(0).astype(int)
        rename_prop={
            'ticker':'Mã CP',
            'tradingDate':'Thời điểm GD',
            'totalMatchTradeNetVolume': 'KLGD khớp lệnh ròng',
            'totalMatchTradeNetValue': 'GTGD khớp lệnh ròng',
            'totalMatchBuyTradeVolume': 'KLGD khớp lệnh mua',
            'totalMatchBuyTradeValue': 'GTGD khớp lệnh mua',
            'totalMatchSellTradeVolume': 'KLGD khớp lệnh bán',
            'totalMatchSellTradeValue': 'GTGD khớp lệnh bán',

            'totalDealTradeNetVolume': 'KLGD thoả thuận ròng',
            'totalDealTradeNetValue': 'GTGD thoả thuận ròng',
            'totalDealBuyTradeVolume': 'KLGD thoả thuận mua',
            'totalDealBuyTradeValue': 'GTGD thoả thuận mua',
            'totalDealSellTradeVolume': 'KLGD thoả thuận bán',
            'totalDealSellTradeValue': 'GTGD thoả thuận bán',

            'totalTradeNetVolume': 'Tổng KLGD ròng',
            'totalTradeNetValue': 'Tổng GTGD ròng',
            'totalBuyTradeVolume': 'Tổng KLGD mua',
            'percentBuyTradeVolume': 'Tỷ lệ KLGD mua (%)',
            'totalBuyTradeValue': 'Tổng GTGD mua',
            'percentBuyTradeValue': 'Tỷ lệ GTGD mua (%)',
            'totalSellTradeVolume': 'Tổng KLGD bán',
            'percentSellTradeVolume': 'Tỷ lệ KLGD bán (%)',
            'totalSellTradeValue': 'Tổng GTGD bán',
            'percentSellTradeValue': 'Tỷ lệ GTGD bán (%)'
        }
        data=data.rename(columns=rename_prop)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        return data
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# lịch sử giao dịch tự doanh tổng hợp
def proprietary_history_summary(symbol,time):
    try:
        headers = {
            'host': 'iq.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            }

        time_dict= {
                'days': 'ONE_DAY',
                'months': 'ONE_MONTH',
                'quarters': 'ONE_QUARTER',
                'years': 'ONE_YEAR'
                }
        params = {
                "timeFrame": time_dict[time] ,
                "size": 50000
            }
        url_sumary=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/proprietary-history-summary'
        response=requests.get(url_sumary,headers=headers,params=params)
        data_sumary=pd.json_normalize(response.json()['data'])
        cols_sumary_prop_total=["totalMatchTradeNetVolume",
                                "totalMatchTradeNetValue",
                                "totalMatchBuyTradeVolume",
                                "totalMatchBuyTradeValue",
                                "totalMatchSellTradeVolume",
                                "totalMatchSellTradeValue",
                                "totalDealTradeNetVolume",
                                "totalDealTradeNetValue",
                                "totalDealBuyTradeVolume",
                                "totalDealBuyTradeValue",
                                "totalDealSellTradeVolume",
                                "totalDealSellTradeValue",
                                "totalTradeNetVolume",
                                "totalTradeNetValue",
                                "totalBuyTradeVolume",
                                "percentBuyTradeVolume",
                                "totalBuyTradeValue",
                                "percentBuyTradeValue",
                                "totalSellTradeVolume",
                                "percentSellTradeVolume",
                                "totalSellTradeValue",
                                "percentSellTradeValue"
                                ]

        cols_sumary_prop_avg=["averageTotalMatchNetVolume",
                              "averageTotalMatchNetValue",
                              "averageTotalMatchBuyTradeVolume",
                              "averageTotalMatchBuyTradeValue",
                              "averageTotalMatchSellTradeVolume",
                              "averageTotalMatchSellTradeValue",
                              "averageTotalDealNetVolume",
                              "averageTotalDealNetValue",
                              "averageTotalDealBuyTradeVolume",
                              "averageTotalDealBuyTradeValue",
                              "averageTotalDealSellTradeVolume",
                              "averageTotalDealSellTradeValue",
                              "averageTotalTradeNetVolume",
                              "averageTotalTradeNetValue",
                              "averageTotalBuyTradeVolume",
                              "averagePercentBuyTradeVolume",
                              "averageTotalBuyTradeValue",
                              "averagePercentBuyTradeValue",
                              "averageTotalSellTradeVolume",
                              "averagePercentSellTradeVolume",
                              "averageTotalSellTradeValue",
                              "averagePercentSellTradeValue"
                            ]
        rename_summary = {
            # Khớp lệnh
            'totalMatchTradeNetVolume': 'KLGD ròng khớp lệnh',
            'totalMatchTradeNetValue': 'GTGD ròng khớp lệnh',
            'totalMatchBuyTradeVolume': 'KLGD mua khớp lệnh',
            'totalMatchBuyTradeValue': 'GTGD mua khớp lệnh',
            'totalMatchSellTradeVolume': 'KLGD bán khớp lệnh',
            'totalMatchSellTradeValue': 'GTGD bán khớp lệnh',

            'averageTotalMatchNetVolume': 'KLGD ròng khớp lệnh',
            'averageTotalMatchNetValue': 'GTGD ròng khớp lệnh',
            'averageTotalMatchBuyTradeVolume': 'KLGD mua khớp lệnh',
            'averageTotalMatchBuyTradeValue': 'GTGD mua khớp lệnh',
            'averageTotalMatchSellTradeVolume': 'KLGD bán khớp lệnh',
            'averageTotalMatchSellTradeValue': 'GTGD bán khớp lệnh',

            # Thỏa thuận
            'totalDealTradeNetVolume': 'KLGD ròng thoả thuận',
            'totalDealTradeNetValue': 'GTGD ròng thoả thuận',
            'totalDealBuyTradeVolume': 'KLGD mua thoả thuận',
            'totalDealBuyTradeValue': 'GTGD mua thoả thuận',
            'totalDealSellTradeVolume': 'KLGD bán thoả thuận',
            'totalDealSellTradeValue': 'GTGD bán thoả thuận',

            'averageTotalDealNetVolume': 'KLGD ròng thoả thuận',
            'averageTotalDealNetValue': 'GTGD ròng thoả thuận',
            'averageTotalDealBuyTradeVolume': 'KLGD mua thoả thuận',
            'averageTotalDealBuyTradeValue': 'GTGD mua thoả thuận',
            'averageTotalDealSellTradeVolume': 'KLGD bán thoả thuận',
            'averageTotalDealSellTradeValue': 'GTGD bán thoả thuận',

            # Tổng mua bán ròng
            'totalTradeNetVolume': 'Tổng KLGD ròng',
            'totalTradeNetValue': 'Tổng GTGD ròng',
            'totalBuyTradeVolume': 'Tổng KLGD mua',
            'percentBuyTradeVolume': 'Tỷ trọng KLGD mua (%)',
            'totalBuyTradeValue': 'Tổng GTGD mua',
            'percentBuyTradeValue': 'Tỷ trọng GTGD mua (%)',
            'totalSellTradeVolume': 'Tổng KLGD bán',
            'percentSellTradeVolume': 'Tỷ trọng KLGD bán (%)',
            'totalSellTradeValue': 'Tổng GTGD bán',
            'percentSellTradeValue': 'Tỷ trọng GTGD bán (%)',

            'averageTotalTradeNetVolume': 'Tổng KLGD ròng',
            'averageTotalTradeNetValue': 'Tổng GTGD ròng',
            'averageTotalBuyTradeVolume': 'Tổng KLGD mua',
            'averagePercentBuyTradeVolume': 'Tỷ trọng KLGD mua (%)',
            'averageTotalBuyTradeValue': 'Tổng GTGD mua',
            'averagePercentBuyTradeValue': 'Tỷ trọng GTGD mua (%)',
            'averageTotalSellTradeVolume': 'Tổng KLGD bán',
            'averagePercentSellTradeVolume': 'Tỷ trọng KLGD bán (%)',
            'averageTotalSellTradeValue': 'Tổng GTGD bán',
            'averagePercentSellTradeValue': 'Tỷ trọng GTGD bán (%)'
        }
        timevie_dict={
                'days': 'ngày',
                'months': 'tháng',
                'quarters': 'quý',
                'years': 'năm'
                }
        data_sumary_prop_total=data_sumary[cols_sumary_prop_total]
        data_sumary_prop_total.insert(0, 'Mã CP', symbol.upper())
        data_sumary_prop_total.insert(1, 'Phân loại', 'Tổng đến hiện tại')
        data_sumary_prop_total= data_sumary_prop_total.rename(columns=rename_summary)
        data_sumary_prop_avg=data_sumary[cols_sumary_prop_avg]
        data_sumary_prop_avg.insert(0, 'Mã CP', symbol.upper())
        data_sumary_prop_avg.insert(1, 'Phân loại', f'Trung bình {timevie_dict[time]}')
        data_sumary_prop_avg = data_sumary_prop_avg.rename(columns=rename_summary)
        data_sumary= pd.concat([data_sumary_prop_total, data_sumary_prop_avg], axis=0)
        cols_percent=['Tỷ trọng KLGD mua (%)',
                      'Tỷ trọng GTGD mua (%)',              
                      'Tỷ trọng KLGD bán (%)',              
                      'Tỷ trọng GTGD bán (%)'
                    ]
        int_cols=list(set(data_sumary.columns[2:])-set(cols_percent))
        data_sumary[cols_percent]=data_sumary[cols_percent].apply(lambda x : round(x*100,2))
        data_sumary[int_cols]= data_sumary[int_cols].apply(lambda x : x.round(0).astype(int))
        return data_sumary
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# lịch sử giao dịch cung cầu
def demand_history(symbol,time,start,end):
    try:
        headers = {
            'host': 'iq.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            }

        time_dict= {
            'days': 'ONE_DAY',
            'months': 'ONE_MONTH',
            'quarters': 'ONE_QUARTER',
            'years': 'ONE_YEAR'
            }
        if time=='months':
            start = start + '-01'
            end = end + '-01'
        elif time=='quarters':
            start = start + '-01-01'
            end = end + '-12-31'
        elif time=='years':
            start = start + '-01-01'
            end = end + '-01-01'
        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(end, '%Y-%m-%d')
        start_date = start.strftime('%Y%m%d')
        end_date = end.strftime('%Y%m%d')
        params = {
            "timeFrame": time_dict[time] ,
            "fromDate": start_date,
            "toDate": end_date,
            "size": 50000
        }
        url=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/price-history'
        response=requests.get(url,headers=headers,params=params)
        data=json_normalize(response.json()['data']['content'])
        cols_demand=['ticker',
                    'tradingDate',
                    'totalBuyUnmatchedVolume',
                    'totalSellUnmatchedVolume',
                    'totalBuyTrade',
                    'totalSellTrade',
                    'totalBuyTradeVolume',
                    'totalSellTradeVolume',
                    'averageBuyTradeVolume',
                    'averageSellTradeVolume',
                    'totalNetTradeVolume']
        data=data[cols_demand]
        data['tradingDate'] = pd.to_datetime(data['tradingDate'])
        quy={'1': 'Q1',
             '4': 'Q2',
             '7': 'Q3',
             '10': 'Q4'}
        if time=='months':
            data['tradingDate'] = data['tradingDate'].dt.strftime('%Y-%m')
        elif time=='quarters':
            data['tradingDate']=(data['tradingDate'].dt.month.map(lambda m:quy.get(str(m),'')))+' '+data['tradingDate'].dt.year.astype(str)
        elif time=='years':
            data['tradingDate'] = data['tradingDate'].dt.strftime('%Y').astype(int)
        rename_his={
            'ticker': 'Mã CP',
            'tradingDate': 'Thời điểm GD',
            'totalBuyUnmatchedVolume': 'Khối lượng CP Mua chưa khớp',
            'totalSellUnmatchedVolume': 'Khối lượng CP Bán chưa khớp',
            'totalBuyTrade': 'Số lệnh đặt Mua',
            'totalSellTrade': 'Số lệnh đặt Bán',
            'totalBuyTradeVolume': 'Khối lượng CP Mua',
            'totalSellTradeVolume': 'Khối lượng CP Bán',
            'averageBuyTradeVolume': 'KLTB 1 lệnh Mua',
            'averageSellTradeVolume': 'KLTB 1 lệnh Bán',
            'totalNetTradeVolume': 'Chênh lệch KL đặt mua - đặt bán'
        } 
        data=data.rename(columns=rename_his)
        cols=data.columns[2:]
        data[cols] = data[cols].apply(lambda x : x.round(0).astype(int))
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        return data
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# Tin tức tổng hợp
def news(symbol):
    try:
        headers = {
            'host': 'iq.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }
        
        now=datetime.today().strftime('%Y%m%d')
        params = {
            'ticker': symbol.upper(),
            "fromDate": '19000101',
            "toDate": now,
            "size": 50000
        }
    
        # Lấy danh sách tin tức
        url = 'https://iq.vietcap.com.vn/api/iq-insight-service/v1/news'
        response = requests.get(url, headers=headers, params=params)
        data = json_normalize(response.json()['data']['content'])
        datax = data[['id', 'publicDate', 'newsTitle']]
    
    
        # Hàm lấy chi tiết tin
        def fetch_news_detail(news_id):
            try:
                url = f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/news/{news_id}'
                response = requests.get(url, headers=headers)
                detail = json_normalize(response.json()['data'])

                html = detail.loc[0, 'newsFullContent']
                source_link = detail.loc[0, 'newsSourceLink'] if 'newsSourceLink' in detail.columns else '-'

                # Trích link file PDF từ HTML (nếu có)
                if pd.notna(html):
                    soup = BeautifulSoup(html, 'html.parser')
                    link = soup.find('a', href=True)
                    file_url = link.get('href') if link else '-'
                else:
                    file_url = '-'

                return {
                    'id': news_id,
                    'newsFullContent': file_url,
                    'newsSourceLink': source_link
                }

            except Exception as e:
                return {'id': news_id, 'newsFullContent': '-', 'newsSourceLink': '-'}

        # Chạy đa luồng lấy chi tiết tin
        results = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(fetch_news_detail, _id) for _id in data['id']]
            for future in as_completed(futures):
                results.append(future.result())

        # Gộp kết quả
        tong = pd.DataFrame(results)
        datax = pd.merge(datax, tong, on='id', how='left')
        datax[['newsSourceLink', 'newsFullContent']] = datax[['newsSourceLink', 'newsFullContent']].fillna('-')
        cols=['publicDate','newsTitle','newsSourceLink','newsFullContent']
        datax=datax[cols]
        datax.insert(0, 'Mã CP', symbol.upper())
        datax['publicDate'] = pd.to_datetime(datax['publicDate'], format='mixed', errors='coerce')
        datax['publicDate'] = datax['publicDate'].dt.floor('s')
        datax = datax[~((datax['newsSourceLink'] == '-') & (datax['newsFullContent'] == '-'))]
        datax['newsTitle']=datax['newsTitle'].replace(r'^.*?:\s*','',regex=True)
        rename_dict = {
            'publicDate': 'Ngày công bố',
            'newsTitle': 'Tiêu đề tin',
            'newsSourceLink': 'Link nguồn',
            'newsFullContent': 'Tệp đính kèm'
        }
        datax=datax.rename(columns=rename_dict)

        # Hiển thị kết quả
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        return datax
    
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# Tin tức cổ tức, cổ phần
def dividend(symbol):
    try:
        headers = {
            'host': 'iq.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        now=datetime.today().strftime('%Y%m%d')
        params = {
            'ticker': symbol.upper(),
            "fromDate": '19000101',
            "toDate": now,
            "eventCode":["DIV","ISS"],
            "size": 50000
        }
        url = 'https://iq.vietcap.com.vn/api/iq-insight-service/v1/events'
        response = requests.get(url, headers=headers, params=params)
        data = json_normalize(response.json()['data']['content'])
        cols=['ticker','eventNameVi', 'eventTitleVi' ,'publicDate', 'exrightDate']
        date_cols=['publicDate', 'exrightDate']
        data=data[cols]
        for col in date_cols:
            data[col] = pd.to_datetime(data[col], errors='coerce').dt.floor('d')
        data['eventTitleVi']=data['eventTitleVi'].replace(r'^.*?-\s*','',regex=True)
        rename_dict = {
            'ticker': 'Mã CP',
            'eventNameVi': 'Sự kiện',
            'eventTitleVi': 'Chi tiết sự kiện',
            'publicDate': 'Ngày thông báo',
            'exrightDate': 'Ngày GD không hiệu quả'
        }
        data=data.rename(columns=rename_dict)
        # Hiển thị kết quả
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        return data
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# Tin tức họp cổ đông
def general_meeting(symbol):
    try:
        headers = {
            'host': 'iq.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        now=datetime.today().strftime('%Y%m%d')
        params = {
            'ticker': symbol.upper(),
            "fromDate": '19000101',
            "toDate": now,
            "eventCode":['AGME','AGMR','EGME'],
            "size": 50000
        }
        url = 'https://iq.vietcap.com.vn/api/iq-insight-service/v1/events'
        response = requests.get(url, headers=headers, params=params)
        data = json_normalize(response.json()['data']['content'])
        cols=['ticker','eventNameVi', 'eventTitleVi' ,'publicDate', 'exrightDate','issueDate']
        date_cols=['publicDate', 'exrightDate','issueDate']
        data=data[cols]
        for col in date_cols:
        # Loại phần sau 'T' (nếu có), sau đó ép kiểu datetime, rồi lấy .date
            data[col] = data[col].astype(str).str.split('T').str[0]          # chỉ lấy phần ngày
            data[col] = pd.to_datetime(data[col], errors='coerce')

        data['eventTitleVi']=data['eventTitleVi'].replace(r'^.*?-\s*','',regex=True)
        rename_dict = {
            'ticker': 'Mã CP',
            'eventNameVi': 'Sự kiện',
            'eventTitleVi': 'Chi tiết sự kiện',
            'publicDate': 'Ngày thông báo',
            'exrightDate': 'Ngày GD không hiệu quả',
            'issueDate' : 'Ngày thực hiện'
        }
        data=data.rename(columns=rename_dict)
        # Hiển thị kết quả
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        return data
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()

# Tin tức khác
def other_event(symbol):
    try:
        headers = {
            'host': 'iq.vietcap.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://trading.vietcap.com.vn',
            'referer': 'https://trading.vietcap.com.vn/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        now=datetime.today().strftime('%Y%m%d')
        params = {
            'ticker': symbol.upper(),
            "fromDate": '19000101',
            "toDate": now,
            "eventCode":['AIS','MA','MOVE','NLIS','OTHE','RETU','SUSPME'],
            "size": 50000
        }
        url = 'https://iq.vietcap.com.vn/api/iq-insight-service/v1/events'
        response = requests.get(url, headers=headers, params=params)
        data = json_normalize(response.json()['data']['content'])
        cols=['ticker','eventNameVi', 'eventTitleVi' ,'publicDate','issueDate']
        date_cols=['publicDate','issueDate']
        data=data[cols]
        for col in date_cols:
        # Loại phần sau 'T' (nếu có), sau đó ép kiểu datetime, rồi lấy .date
            data[col] = data[col].astype(str).str.split('T').str[0]          # chỉ lấy phần ngày
            data[col] = pd.to_datetime(data[col], errors='coerce')

        data['eventTitleVi']=data['eventTitleVi'].replace(r'^.*?-\s*','',regex=True)
        rename_dict = {
            'ticker': 'Mã CP',
            'eventNameVi': 'Sự kiện',
            'eventTitleVi': 'Chi tiết sự kiện',
            'publicDate': 'Ngày thông báo',
            'issueDate' : 'Ngày thực hiện'
        }
        data=data.rename(columns=rename_dict)
        # Hiển thị kết quả
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        return data
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()


#thông tin mã cp
def stock_info(symbol=None,exchange=None):
    try:
        headers={
            'authority': 'api.fmarket.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://fmarket.vn',
            'referer': 'https://fmarket.vn/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
          }
        payload = {
            "pageSize": 50000
        }
        url=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/screening/paging'
        response=requests.post(url,headers=headers,data=json.dumps(payload))
        data=pd.json_normalize(response.json()['data']['content'])
        cols=['ticker','exchange','viSector','viOrganName','enSector','enOrganName']
        data=data[cols]
        rename_cols = {
            "ticker": "Mã CP",
            "exchange": "Sàn",
            "viSector": "Ngành (VI)",
            "enSector": "Ngành (EN)",
            "viOrganName": "Tên công ty (VI)",
            "enOrganName": "Tên công ty (EN)"
        }
        data=data.rename(columns=rename_cols)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        if symbol is None and exchange is None:
            return data
        elif symbol is None and exchange is not None:
            return data.loc[data['Sàn'] == exchange.upper()]
        elif symbol is not None and exchange is None:
            return data.loc[data['Mã CP'] == symbol.upper()]
        else:
            return data.loc[(data['Mã CP'] == symbol.upper()) & (data['Sàn'] == exchange.upper())]
    except Exception as e :
            print(f"Lỗi: {e}")
            return pd.DataFrame()




























