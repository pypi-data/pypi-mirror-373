import requests
import pandas as pd
import json
from pandas import json_normalize
from datetime import datetime, timedelta

# Thông tin cổ đông
def shareholders_info(symbol):
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

    url1=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/shareholder'
    response=requests.get(url1,headers=headers)
    data1=response.json()['data']
    data1=pd.json_normalize(data1)
    data1=data1.drop(columns=['ownerNameEn','ownerCode','positionNameEn'])
    data1['percentage']=round(data1['percentage']*100,4)
    data1['updateDate']=pd.to_datetime(data1['updateDate'],format='mixed').dt.strftime('%Y-%m-%d')
    data1['ownerType']=data1['ownerType'].replace({'INDIVIDUAL':'Cá nhân','CORPORATE':'Doanh nghiệp'})
    data1['Mã CK']=symbol.upper()
    col = data1.pop('Mã CK')
    data1.insert(0, 'Mã CK', col)
    data1['positionName'] = data1['positionName'].fillna('-')
    data1=data1.rename(columns={
        'ownerName': 'Tên chủ sở hữu',
        'positionName' : 'Chức vụ',
        'quantity': 'Số lượng sở hữu',
        'percentage':'Phần trăm sở hữu (%)',
        'ownerType':'Loại sở hữu',
        'updateDate': 'Ngày cập nhật'
    })
    pd.set_option('display.max_rows', None)
    return data1
  except Exception as e:
    print(f"❌ Không có dữ liệu '{symbol}': {e}")
    return pd.DataFrame()

#Cấu trúc cổ đông
def shareholders_structure(symbol):
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

    url2=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/shareholder-structure'
    response=requests.get(url2,headers=headers)
    data2=response.json()['data']
    data2=pd.json_normalize(data2)
    percent_cols=['statePercentage','foreignPercentage','otherPercentage','bodPercentage','institutionPercentage']
    data2[percent_cols]=round(data2[percent_cols]*100,4)
    data2['totalShares']=data2['totalShares'].astype(int)
    data2['Mã CK']=symbol.upper()
    col = data2.pop('Mã CK')
    data2.insert(0, 'Mã CK', col)
    data2=data2[['Mã CK','totalShares',
                'stateVolume', 'statePercentage',
                'foreignerVolume', 'foreignPercentage',      
                'otherVolume', 'otherPercentage',            
                'bodPercentage',                             
                'institutionPercentage'                     
                ]]  
    data2.rename(columns={
        'totalShares': 'Số cổ phiếu đang lưu hành',
        'statePercentage': 'Tỷ lệ Nhà nước sở hữu (%)',
        'foreignPercentage': 'Tỷ lệ nước ngoài sở hữu (%)',
        'otherPercentage': 'Tỷ lệ nhóm cổ đông khác (%)',
        'foreignerVolume': 'Số lượng cổ phiếu nước ngoài nắm giữ',
        'otherVolume': 'Số lượng cổ phiếu nhóm cổ đông khác nắm giữ',
        'stateVolume': 'Số lượng cổ phiếu Nhà nước nắm giữ',
        'bodPercentage': 'Tỷ lệ Hội đồng Quản trị nắm giữ (%)',
        'institutionPercentage': 'Tỷ lệ các tổ chức đầu tư nắm giữ (%)'
    },inplace=True)
    pd.set_option('display.max_rows', None)
    return data2
  except Exception as e:
    print(f"❌ Không có dữ liệu '{symbol}': {e}")
    return pd.DataFrame()

#Công ty liên quan
def shareholders_relationship(symbol):
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

    url3=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/relationship'
    response=requests.get(url3,headers=headers)
    data3_1=response.json()['data']['affiliates']
    data3_1=pd.json_normalize(data3_1)
    data3_1['Loại cty']='Cty liên kết'
    data3_2=response.json()['data']['subsidiaries']
    data3_2=pd.json_normalize(data3_2)
    data3_2['Loại cty']='Cty con'
    data3=pd.concat([data3_1,data3_2],ignore_index=True)
    data3=data3.drop(columns=['rightOrganCode','rightTicker','rightOrganNameEn'])
    data3['ownedPercentage']=round(data3['ownedPercentage']*100,4)
    data3['ownedQuantity']=data3['ownedQuantity'].astype(int)
    data3['Mã CK']=symbol.upper()
    col = data3.pop('Mã CK')
    data3.insert(0, 'Mã CK', col)
    data3.rename(columns={
        'rightOrganNameVi': 'Tên Cty',
        'ownedQuantity': 'Số lượng cổ phiếu nắm giữ',
        'ownedPercentage': 'Tỷ lệ nắm giữ (%)'
    },inplace=True)
    pd.set_option('display.max_rows', None)  
    return data3[['Mã CK','Tên Cty','Loại cty', 'Số lượng cổ phiếu nắm giữ', 'Tỷ lệ nắm giữ (%)']]
  except Exception as e:
    print(f"❌ Không có dữ liệu '{symbol}': {e}")
    return pd.DataFrame()

# Giao dịch nội bộ
def insider_trans(symbol):
  try:
    headers={
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
    url=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/insider-transaction?page=0&size=1000'
    response=requests.get(url,headers=headers)
    data=pd.json_normalize(response.json()['data']['content'])
    data['Mã CK']=symbol.upper()
    col = data.pop('Mã CK')
    data.insert(0, 'Mã CK', col)
    data['traderNameVi']=data['traderNameVi'].fillna(data['traderOrganNameVi'])
    nacol=['traderPositionVi','relativeNameVi',	'roleNameVi']
    data[nacol]=data[nacol].fillna('-')
    for col in ['shareRegister', 'shareBeforeTrade', 'shareAcquire', 'shareAfterTrade']:
          data[col] = pd.to_numeric(data[col], errors='raise').astype('Int64')

    data=data.drop(columns=[
      'id', 
      'organCode', 
      'eventNameEn', 
      'ticker', 
      'eventCode',
      'sourceUrlVi',
      'sourceUrlEn',
      'tradeStatusEn',
      'traderPersonId',
      'traderNameEn',
      'traderPositionEn',
      'actionTypeCode',
      'actionTypeEn',
      'relativeNameEn',
      'icbCodeLv1',
      'traderOrganNameEn',
      'displayDate1',
      'displayDate2',
      'roleNameEn',
      'traderOrganNameVi'
      ])
    data['eventNameVi']=data['eventNameVi'].replace(r'^Giao dịch nội bộ: ','',regex=True)
    ngay=['startDate','endDate','publicDate']
    for col in ngay:
        data[col]=pd.to_datetime(data[col],format='mixed').dt.strftime('%Y-%m-%d')
    data['ownershipAfterTrade']=data['ownershipAfterTrade']*100
    chucvu=shareholders_info(symbol)[['Tên chủ sở hữu','Chức vụ']]
    data=pd.merge(data,chucvu,left_on='relativeNameVi',right_on='Tên chủ sở hữu',how='left')
    data=data.drop(columns=['Tên chủ sở hữu'])
    mask = data['eventNameVi'] != 'Giao dịch người liên quan'
    data.loc[mask, ['relativeNameVi', 'Chức vụ', 'roleNameVi']] = '-'
    filted_cols=[
      'Mã CK',
      'eventNameVi',
      'traderNameVi',
      'traderPositionVi',
      'actionTypeVi',
      'tradeStatusVi',
      'shareRegister',
      'shareBeforeTrade',
      'shareAcquire',
      'shareAfterTrade',
      'ownershipAfterTrade',
      'startDate',
      'endDate',
      'publicDate',
      'relativeNameVi',
      'Chức vụ',
      'roleNameVi'
      ]
    df=data[filted_cols]
    df=df.rename(columns={ 
      'eventNameVi': 'Loại giao dịch',
      'traderNameVi': 'Người/Tổ chức giao dịch',
      'traderPositionVi': 'Chức vụ',
      'actionTypeVi': 'Phân loại mua/bán',
      'tradeStatusVi': 'Trạng thái',
      'shareRegister': 'Số lượng cp đăng ký',
      'shareBeforeTrade': 'Số lượng cp trước GD',
      'shareAcquire': 'Số lượng mua',
      'shareAfterTrade': 'Số lượng cp sau GD',
      'ownershipAfterTrade': 'Tỷ lệ sở hữu sau GD (%)',
      'startDate': 'Ngày bắt đầu',
      'endDate': 'Ngày kết thúc',
      'publicDate': 'Ngày công bố',
      'relativeNameVi': 'Người liên quan',
      'roleNameVi': 'Quan hệ',
      'Chức vụ': 'Chức vụ người liên quan'
    })

    pd.set_option('display.max_rows', None)
    return df
  except Exception as e:
    print(f"❌ Không có dữ liệu '{symbol}': {e}")
    return pd.DataFrame()
