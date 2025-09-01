import requests
import pandas as pd
import json
from pandas import json_normalize
from datetime import datetime, timedelta

# Chỉ số các ngành
def macro_eco(indicator,time,start,end):
    try:  
        headers={
            'authority': 'data.maybanktrade.com.vn',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://data.maybanktrade.com.vn',
            'referer': 'https://data.maybanktrade.com.vn/du-lieu-vi-mo',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        indicator_list={
            43:'GDP',
            52:'CPI',
            46:'Sản xuất công nghiệp',
            47:'Bán lẻ',
            48:'Xuất nhập khẩu',
            50:'FDI',
            51:'Tín dụng',
            53:'Lãi suất',
            55:'Dân số và lao động'
        }
        # Alias map (cho phép gõ thường, viết tắt hoặc tiếng Việt)
        alias_map = {}
        for k, v in indicator_list.items():
            alias_map[v.lower()] = k
            if v.isupper():  # GDP, CPI, FDI
                alias_map.update({v.lower(): k, v.upper(): k})

        def inputindicator():
            if isinstance(indicator, (int, float)):
                return int(indicator)
            name = str(indicator).strip().lower()
            if name.isdigit():
                return int(name)
            if name in alias_map:
                return alias_map[name]
            raise ValueError(f"Không nhận diện được chỉ số: {indicator}")

        period={
            1:'days', #(type=1)
            2:'months', #(type=2)
            3:'quarters', #(tpye=3)
            4:'years'#(type=4)
        }

        def inputtime():
            if isinstance(time,(int,float)):
                return time
            elif isinstance(time,str) and time.isdigit():
                return int(time)
            elif isinstance(time,str) and time.isalpha():
                id_time=[k for k,v in period.items() if v==time]
                return int(id_time[0])


        if inputtime()==1:
            batdau=start
            ketthuc=end
            start='2025'
            end='2025'

        elif inputtime()==2:
            batdau=start.split('-')[1]
            ketthuc=end.split('-')[1]
            start=start.split('-')[0]
            end=end.split('-')[0]

        elif inputtime()==3:
            batdau=1
            ketthuc=4

        else:
            start=start.split('-')[0]
            end=end.split('-')[0]
            batdau=0
            ketthuc=0

        payload={
            "type": inputtime(),
            "fromYear": start,
            "toYear": end,
            "from": batdau, #(tháng hoặc quý) (ngày thì nhập đầy đủ)
            "to": ketthuc,   #(tháng hoặc quý) (ngày thì nhập đầy đủ)
            "normTypeID": inputindicator()
        }

        url='https://data.maybanktrade.com.vn/data/reportdatatopbynormtype'
        response=requests.post(url,headers=headers,data=json.dumps(payload))
        data=pd.json_normalize(response.json())

        #GDP #Sản xuất công nghiệp #bán lẻ năm #tín dụng năm #dân số lao động
        if (inputindicator() in [43,46,48,55]) or (inputindicator()in[47,51,53] and inputtime()==4):

            if inputindicator()==43:
                data=data[~data['ReportTime'].str.contains('tháng',na=False)]

            if inputindicator()==48:
                xuatkhaum=[358,359,360,361,362,364,365,366,367,462]
                nhapkhaum=[368,369,370,371,372,373,374,375,376,463]
                xuatkhauy=[85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,414]
                nhapkhauy=[113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,415]
                data['GroupName']=data['NormID'].apply(lambda x:'Xuất khẩu' if x in (xuatkhauy+xuatkhaum) else 'Nhập khẩu')

            if inputindicator()==51:
                data=data.loc[data['GroupName']!='So với GDP']
                data['GroupName']=data['GroupName'].apply(lambda x:'Giá trị' if x=="" else x)
                data=data.loc[(data['NormName']=='Cung tiền M2')|(data['NormName']=='Tín dụng')]


            if inputindicator()==55:
                danso=[248,247,246,245]
                laodong=[256,260,259,258,257,254,495,494,493,249] 
                data['GroupName']=data['NormID'].apply(lambda x:'Lao động' if x in laodong else 'Dân số')

            data=data.drop(columns=['ReportDataID','TermID','TermYear','TernDay','NormID','CssStyle','NormTypeID','FromSource','NormGroupID'])
            data=data.rename(columns={'GroupName':'Nhóm chỉ tiêu',
                                    'NormName':'Chỉ tiêu',
                                    'UnitCode':'Đơn vị tính',
                                    'NormValue':'Giá trị',
                                    'ReportTime':'Thời gian báo cáo'}).fillna(0)
            data

        #CPI #FDI # bán lẻ tháng #Tín dụng tháng #tỉ giá lãi suất ngày
        if (inputindicator() in [52,50]) or (inputindicator() in [47,51] and inputtime()==2) or (inputindicator() in [53] and inputtime()==1) :
            if inputindicator()==50:
                data=data.loc[(data['NormName']=='Giải ngân') | (data['NormName']=='Đăng ký')]

            if inputindicator()==53:
                 data=data.loc[data['NormValue'].notna()]

            data=data.drop(columns=['ReportDataID','TermID','TermYear','TernDay','NormID','CssStyle','NormTypeID','FromSource','NormGroupID','GroupName'])
            data=data.rename(columns={'NormName':'Chỉ tiêu',
                                    'UnitCode':'Đơn vị tính',
                                    'NormValue':'Giá trị',
                                    'ReportTime':'Thời gian báo cáo'}).fillna(0)

        if 'Nhóm chỉ tiêu' in data.columns:
            pivot_data=data.pivot(
                index=['Nhóm chỉ tiêu','Chỉ tiêu','Đơn vị tính'],
                columns='Thời gian báo cáo',
                values='Giá trị'
            ).reset_index()
        else:
            pivot_data=data.pivot(
            index=['Chỉ tiêu','Đơn vị tính'],
            columns='Thời gian báo cáo',
            values='Giá trị'
            ).reset_index()
        pivot_data.columns.name = None
        pd.set_option('display.max_columns', None)
        return pivot_data
    except Exception as e:
        print(f"[{indicator}] ⚠️ Lỗi: {str(e)}")
        return pd.DataFrame()