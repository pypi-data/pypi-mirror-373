import requests
import pandas as pd
import json
from pandas import json_normalize
from datetime import datetime, timedelta

# Tổng quan danh sách các quỹ
def fund_market():
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
        payload={
            "types": [
                    "TRADING_FUND",
                    "NEW_FUND"
                ],
        }
        url='https://api.fmarket.vn/res/products/filter'
        response=requests.post(url,headers=headers,data=json.dumps(payload))
        data=pd.json_normalize(response.json()['data']['rows'])
        #data[['id','code']].to_csv(r'D:\DE\API\Fmarrket\category.csv',encoding='utf-8-sig')
        lower_col=['name','type','owner.name']
        for col in lower_col:
            data[col] = data[col].astype(str).str.title()
        data[['productNavChange.navTo12Months','productNavChange.annualizedReturn36Months']]=data[['productNavChange.navTo12Months','productNavChange.annualizedReturn36Months']].fillna(0)
        col_collect=['id','shortName','dataFundAssetType.name','name','type','nav','lastYearNav','productNavChange.navTo12Months','productNavChange.annualizedReturn36Months','owner.name','owner.shortName']
        data=data[col_collect]
        data=data.rename(columns={
            'id':'ID Quỹ',
            'shortName':'Chứng chỉ Quỹ',
            'name':'Tên Chứng chỉ Quỹ',
            'type':'Phân loại',
            'dataFundAssetType.name':'Loại quỹ',
            'nav':'Giá gần nhất',
            'lastYearNav':'Giá năm trước',
            'productNavChange.navTo12Months':'Lợi nhuận 1 năm gần nhất',
            'productNavChange.annualizedReturn36Months':'LN bình quân hàng năm',
            'owner.name':'Tổ chức phát hành',
            'owner.shortName':'Tên tổ chức'
        })
        data=data.sort_values('Lợi nhuận 1 năm gần nhất',ascending=False)
        return data
    except Exception as e:
        print(f"❌ Không có dữ liệu {e}")
        return pd.DataFrame()

# Tăng trưởng tài sản ròng (NAV) của quỹ
def NAV_grown(fund,start=None,end=None):
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

        category={
            '88':'MBAM',
            '87':'BMFF',
            '86':'KDEF',
            '83':'RVPF24',
            '82':'VCBFAIF',
            '81':'ENF',
            '80':'VDEF',
            '79':'TCGF',
            '78':'UVDIF',
            '77':'MDI',
            '76':'LHCDF',
            '75':'VCAMDF',
            '72':'MAFEQI',
            '71':'MAFBAL',
            '70':'VCAMBF',
            '69':'GFMVIF',
            '40':'VNDCF',
            '68':'VMPF',
            '67':'VFMVFC',
            '66':'PHVSF',
            '65':'ABBF',
            '64':'LHBF',
            '63':'VCAMFI',
            '62':'HDBOND',
            '61':'PBIF',
            '58':'UVEEF',
            '53':'VLBF',
            '52':'TVPF',
            '51':'ASBF',
            '50':'MAFF',
            '49':'VLGF',
            '47':'MBVF',
            '48':'MBBOND',
            '46':'VCBFMGF',
            '45':'PVBF',
            '41':'TBLF',
            '37':'VNDBF',
            '38':'VNDAF',
            '35':'MAGEF',
            '32':'VCBFBCF',
            '33':'VCBFFIF',
            '31':'VCBFTBF',
            '20':'VEOF',
            '21':'VFF',
            '22':'VIBF',
            '23':'VESAF',
            '27':'VFMVFB',
            '25':'VFMVF4',
            '28':'VFMVF1',
            '12':'BVFED',
            '13':'BVBF',
            '14':'BVPF',
            '29':'DCAF',
            '30':'DFIX',
            '8':'SSIBF',
            '11':'SSISCA'
        }

        def input():
            if isinstance(fund,(int,float)):
                return fund
            elif isinstance(fund,str) and fund.isdigit():
                return int(fund)
            elif isinstance(fund,str) and fund.isalpha():
                id_fund=[k for k,v in category.items() if v==fund.upper()]
                return int(id_fund[0])

        if start is not None:
            start1=datetime.strptime(start,'%Y-%m-%d')
            start_day=start1.strftime('%Y%m%d')
            if end is not None:
                end1=datetime.strptime(end,'%Y-%m-%d')
                end_day=end1.strftime('%Y%m%d')
            else:
                end_day=datetime.today().strftime('%Y%m%d')
        if start is None:
                start_day=19700101
                if end is not None:
                    end1=datetime.strptime(end,'%Y-%m-%d')
                    end_day=end1.strftime('%Y%m%d')
                else:
                    end_day=datetime.today().strftime('%Y%m%d') 


        payload={
            "fromDate":start_day,#"20240620",
            "productId": input(),
            "toDate": end_day #"20250621"
        }

        url='https://api.fmarket.vn/res/product/get-nav-history'
        response=requests.post(url,headers=headers,data=json.dumps(payload))
        data=pd.json_normalize(response.json()['data'])
        data=data[['productId','nav','navDate']].sort_values('navDate',ascending=False)
        data['productId']=data['productId'].astype(str).map(category)
        data=data.rename(columns={
            'productId':'Chứng chi Quỹ',
            'nav':'Giá trị tài sản ròng',
            'navDate':'Ngày'    
        })
        return data
    except Exception as e:
        print(f"❌ Không có dữ liệu '{fund}': {e}")
        return pd.DataFrame()

# Phân bổ theo tài sản
def asset_holding(fund):
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

        category={
            '88':'MBAM',
            '87':'BMFF',
            '86':'KDEF',
            '83':'RVPF24',
            '82':'VCBFAIF',
            '81':'ENF',
            '80':'VDEF',
            '79':'TCGF',
            '78':'UVDIF',
            '77':'MDI',
            '76':'LHCDF',
            '75':'VCAMDF',
            '72':'MAFEQI',
            '71':'MAFBAL',
            '70':'VCAMBF',
            '69':'GFMVIF',
            '40':'VNDCF',
            '68':'VMPF',
            '67':'VFMVFC',
            '66':'PHVSF',
            '65':'ABBF',
            '64':'LHBF',
            '63':'VCAMFI',
            '62':'HDBOND',
            '61':'PBIF',
            '58':'UVEEF',
            '53':'VLBF',
            '52':'TVPF',
            '51':'ASBF',
            '50':'MAFF',
            '49':'VLGF',
            '47':'MBVF',
            '48':'MBBOND',
            '46':'VCBFMGF',
            '45':'PVBF',
            '41':'TBLF',
            '37':'VNDBF',
            '38':'VNDAF',
            '35':'MAGEF',
            '32':'VCBFBCF',
            '33':'VCBFFIF',
            '31':'VCBFTBF',
            '20':'VEOF',
            '21':'VFF',
            '22':'VIBF',
            '23':'VESAF',
            '27':'VFMVFB',
            '25':'VFMVF4',
            '28':'VFMVF1',
            '12':'BVFED',
            '13':'BVBF',
            '14':'BVPF',
            '29':'DCAF',
            '30':'DFIX',
            '8':'SSIBF',
            '11':'SSISCA'
        }

        def input():
            if isinstance(fund,(int,float)):
                return fund
            elif isinstance(fund,str) and fund.isdigit():
                return int(fund)
            elif isinstance(fund,str) and fund.isalpha():
                id_fund=[k for k,v in category.items() if v==fund.upper()]
                return int(id_fund[0])

        url=f'https://api.fmarket.vn/res/products/{input()}'
        response=requests.get(url,headers=headers)
        data=pd.json_normalize(response.json()['data']['productAssetHoldingList'])
        data['Chứng chỉ Quỹ']=[v for k,v in category.items() if k==str(input())][0]
        data=data.drop(columns=['id','updateAt','assetType.id','assetType.code','assetType.colorCode','createAt'])
        data=data[['Chứng chỉ Quỹ','assetType.name','assetPercent']]
        data=data.rename(columns={
            'assetType.name':'Loại tài sản nắm giữ',
            'assetPercent':'Tỉ trọng (%)'
        }).sort_values('Tỉ trọng (%)',ascending=False).reset_index(drop=True)
        return data
    except Exception as e:
        print(f"❌ Không có dữ liệu '{fund}': {e}")
        return pd.DataFrame()

# Phân bổ theo ngành
def indusstries_holding(fund):
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

        category={
            '88':'MBAM',
            '87':'BMFF',
            '86':'KDEF',
            '83':'RVPF24',
            '82':'VCBFAIF',
            '81':'ENF',
            '80':'VDEF',
            '79':'TCGF',
            '78':'UVDIF',
            '77':'MDI',
            '76':'LHCDF',
            '75':'VCAMDF',
            '72':'MAFEQI',
            '71':'MAFBAL',
            '70':'VCAMBF',
            '69':'GFMVIF',
            '40':'VNDCF',
            '68':'VMPF',
            '67':'VFMVFC',
            '66':'PHVSF',
            '65':'ABBF',
            '64':'LHBF',
            '63':'VCAMFI',
            '62':'HDBOND',
            '61':'PBIF',
            '58':'UVEEF',
            '53':'VLBF',
            '52':'TVPF',
            '51':'ASBF',
            '50':'MAFF',
            '49':'VLGF',
            '47':'MBVF',
            '48':'MBBOND',
            '46':'VCBFMGF',
            '45':'PVBF',
            '41':'TBLF',
            '37':'VNDBF',
            '38':'VNDAF',
            '35':'MAGEF',
            '32':'VCBFBCF',
            '33':'VCBFFIF',
            '31':'VCBFTBF',
            '20':'VEOF',
            '21':'VFF',
            '22':'VIBF',
            '23':'VESAF',
            '27':'VFMVFB',
            '25':'VFMVF4',
            '28':'VFMVF1',
            '12':'BVFED',
            '13':'BVBF',
            '14':'BVPF',
            '29':'DCAF',
            '30':'DFIX',
            '8':'SSIBF',
            '11':'SSISCA'
        }

        def input():
            if isinstance(fund,(int,float)):
                return fund
            elif isinstance(fund,str) and fund.isdigit():
                return int(fund)
            elif isinstance(fund,str) and fund.isalpha():
                id_fund=[k for k,v in category.items() if v==fund.upper()]
                return int(id_fund[0])

        url=f'https://api.fmarket.vn/res/products/{input()}'
        response=requests.get(url,headers=headers)
        data=pd.json_normalize(response.json()['data']['productIndustriesHoldingList'])
        data['Chứng chỉ Quỹ']=[v for k,v in category.items() if k==str(input())][0]
        data=data.drop(columns=['id'])[['Chứng chỉ Quỹ','industry','assetPercent']]
        data=data.rename(columns={
                        'industry':'Ngành',
                        'assetPercent':'Tỉ trọng(%)'}).sort_values('Tỉ trọng(%)',ascending=False).reset_index(drop=True)
        return data
    except Exception as e:
        print(f"❌ Không có dữ liệu '{fund}': {e}")
        return pd.DataFrame()

# Danh mục đầu tư lớn
def top_holding(fund):
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

        category={
            '88':'MBAM',
            '87':'BMFF',
            '86':'KDEF',
            '83':'RVPF24',
            '82':'VCBFAIF',
            '81':'ENF',
            '80':'VDEF',
            '79':'TCGF',
            '78':'UVDIF',
            '77':'MDI',
            '76':'LHCDF',
            '75':'VCAMDF',
            '72':'MAFEQI',
            '71':'MAFBAL',
            '70':'VCAMBF',
            '69':'GFMVIF',
            '40':'VNDCF',
            '68':'VMPF',
            '67':'VFMVFC',
            '66':'PHVSF',
            '65':'ABBF',
            '64':'LHBF',
            '63':'VCAMFI',
            '62':'HDBOND',
            '61':'PBIF',
            '58':'UVEEF',
            '53':'VLBF',
            '52':'TVPF',
            '51':'ASBF',
            '50':'MAFF',
            '49':'VLGF',
            '47':'MBVF',
            '48':'MBBOND',
            '46':'VCBFMGF',
            '45':'PVBF',
            '41':'TBLF',
            '37':'VNDBF',
            '38':'VNDAF',
            '35':'MAGEF',
            '32':'VCBFBCF',
            '33':'VCBFFIF',
            '31':'VCBFTBF',
            '20':'VEOF',
            '21':'VFF',
            '22':'VIBF',
            '23':'VESAF',
            '27':'VFMVFB',
            '25':'VFMVF4',
            '28':'VFMVF1',
            '12':'BVFED',
            '13':'BVBF',
            '14':'BVPF',
            '29':'DCAF',
            '30':'DFIX',
            '8':'SSIBF',
            '11':'SSISCA'
        }

        def input():
            if isinstance(fund,(int,float)):
                return fund
            elif isinstance(fund,str) and fund.isdigit():
                return int(fund)
            elif isinstance(fund,str) and fund.isalpha():
                id_fund=[k for k,v in category.items() if v==fund.upper()]
                return int(id_fund[0])

        url=f'https://api.fmarket.vn/res/products/{input()}'
        response=requests.get(url,headers=headers)
        data1=pd.json_normalize(response.json()['data']['productTopHoldingList'])
        data2=pd.json_normalize(response.json()['data']['productTopHoldingBondList'])
        data=pd.concat([data1,data2])
        data['Chứng chỉ Quỹ']=[v for k,v in category.items() if k==str(input())][0]
        data=data.drop(columns=['id','updateAt'])
        data=data[['Chứng chỉ Quỹ','type','stockCode','industry','netAssetPercent','price','changeFromPrevious','changeFromPreviousPercent']]
        data['type']=data['type'].replace({'STOCK':'Cổ phiếu'})
        data.loc[data['type'].str.contains('BOND', case=False, na=False), 'type'] = 'Trái phiếu'
        data=data.rename(columns={
            'stockCode':'Mã',
            'industry':'Ngành',
            'netAssetPercent':'Tỷ trọng trên tổng giá trị tài sản gộp (%)',
            'price':'Giá',
            'changeFromPrevious':'Thay đổi giá',
            'changeFromPreviousPercent':'% thay đổi giá',
            'type':'Loại đầu tư'
        })
        data=data.fillna(0).sort_values('Tỷ trọng trên tổng giá trị tài sản gộp (%)', ascending=False).reset_index(drop=True)
        has_stock = data['Loại đầu tư'].str.contains('Cổ phiếu', case=False, na=False).any()
        has_bond = data['Loại đầu tư'].str.contains('Trái phiếu', case=False, na=False).any()

        if has_stock:
            return data
        elif has_bond:
            data=data.drop(columns=['Giá','Thay đổi giá','% thay đổi giá'])
            return data
    except Exception as e:
        print(f"❌ Không có dữ liệu '{fund}': {e}")
        return pd.DataFrame()

