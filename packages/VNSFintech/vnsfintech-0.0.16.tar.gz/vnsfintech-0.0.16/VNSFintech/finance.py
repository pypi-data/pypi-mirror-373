import requests
import pandas as pd
import json
from pandas import json_normalize
from datetime import datetime, timedelta

#test sửa
# chỉ số tài chính
def finance_ratio(symbol,time):
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

    url=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/statistics-financial'
    response=requests.get(url,headers=headers)
    data=response.json()['data']
    data=pd.json_normalize(data)
    cols=['dividendYield',
          'cashRatio',
          'quickRatio',
          'currentRatio',
          'roe',
          'roa',
          'grossMargin',
          'ebitMargin',
          'preTaxProfitMargin',
          'afterTaxProfitMargin',
          'netInterestMargin',
          'averageYieldOnEarningAssets',
          'averageCostOfFinancing',
          'nonAndInterestIncome',
          'costToIncome',
          'loansGrowth',
          'depositGrowth',
          'ldrLoanDepositRatio',
          'npl',
          'loansLossReservesToNPLs',
          'loansLossReserveToLoans',
          'provisionToOutstandingLoans',
          'roic',
          'car',
          'casaRatio',
    ]
    data[cols]= round(data[cols]*100,2)

    if time=='quarters':
      data=data.loc[data['quarter']!=5]
      data['Quý']='Q'+ data['quarter'].astype(str) +" "+ data['year'].astype(str)
      quater=data.pop('Quý')
      data.insert(1,'Quý',quater)
      data=data.loc[:,data.sum()!=0]
      drop_cols=['year','quarter','ratioTTMId','ratioType','organCode','yearReport','cir']
      exsit_cols=[col for col in drop_cols if col in data.columns]
      data=data.drop(columns=exsit_cols)
    else:
      data=data.loc[data['quarter']==5]
      data=data.loc[:,data.sum()!=0]
      drop_cols=['quarter','ratioTTMId','ratioType','organCode','yearReport','cir','ratioYearId']
      exsit_cols=[col for col in drop_cols if col in data.columns]
      data=data.drop(columns=exsit_cols)


    data=data.rename(columns={
      'year':'Năm',
      'Quý':'Quý',
      'numberOfSharesMktCap':'Số cp lưu hành (triệu cp)',
      'marketCap':'Vốn hóa',
      'dividendYield':'Tỷ suất cổ tức(%)',
      'pe':'Chỉ số Giá trên Lợi nhuận',
      'pb':'Chỉ số Giá trên Giá trị sổ sách',
      'ps':'Chỉ số Giá trên Doanh thu',
      'priceToCashFlow':'Tỷ giá trên dòng tiền',
      'evToEbitda':'Chỉ số Giá trị doanh nghiệp trên lợi nhuận trước lãi vay, thuế và khấu hao',
      'cashRatio':'Thanh khoản tiền mặt (%)',
      'quickRatio':'Thanh khoản linh động (%)',
      'currentRatio':'Thanh khoản hiện tại (%)',
      'ownersEquity':'Vốn chủ sở hữu',
      'debtPerEquity':'Vay ngắn và dài hạn trên vốn chủ sở hữu',
      'debtToEquity':'Nợ trên vốn chủ sở hữu',
      'roe':'Chỉ số lợi nhuận trên vốn chủ sở hữu (%)',
      'roa':'Chỉ số lợi nhuận trên tổng tài sản (%)',
      'daySaleOutstanding':'Số ngày thu tiền bình quân',
      'daysInventoryOutstanding':'Số ngày tồn kho bình quân',
      'daysPayableOutstanding':'Số ngày thanh toán bình quân',
      'grossMargin':'Biên lợi nhuận gộp (%)',
      'ebitMargin':'Biên lợi nhuận (%)',
      'preTaxProfitMargin':'Biên lợi nhuận trước thuế (%)',
      'afterTaxProfitMargin':'Biên lợi nhuận ròng (%)',
      'assetTurnover':'Vòng quay tài sản',
      'netInterestMargin':'Tỷ suất lợi nhuận ròng(%)',
      'averageYieldOnEarningAssets':'Tỷ suất sinh lời từ tài sản có sinh lãi (%)',
      'averageCostOfFinancing':'Chi phí tài chính trung bình (%)',
      'nonAndInterestIncome':'Thu nhập ngoài lãi và từ lãi (%)',
      'costToIncome':'Chi phí trên thu nhập(%)',
      'loansGrowth':'Tăng trưởng tín dụng (%)',
      'depositGrowth':'Tăng trưởng tiền gửi(%)',
      'equityToLiabilities':'Vốn chủ trên tổng nợ',
      'equityToLoans':'Vốn chủ trên tổng vay',
      'totalEquityTotalAsset':'Vốn chủ trên tài sản',
      'ldrLoanDepositRatio':'Tỷ lệ dư nợ cho vay so với tiền gửi(%)',
      'npl':'Tỷ lệ nợ xấu(%)',
      'loansLossReservesToNPLs':'Dự phòng rủi ro tín dụng trên nợ xấu (%)',
      'loansLossReserveToLoans':'Dự phòng rủi ro tín dụng trên cho vay(%)',
      'provisionToOutstandingLoans':'Trích lập dự phòng trên cho vay (%)',
      'ebit':'Lợi nhuận trước lãi vay và thuế',
      'ebitda':'Lợi nhuận trước lãi vay, thuế và khấu hao tài sản',
      'roic':'Tỷ suất sinh lợi trên vốn đầu tư (%)',
      'cashCycle':'Chu kỳ tiền',
      'fixedAssetTurnover':'Vòng quay tài sản cố định',
      'financialLeverage':'Đòng bẩy tài chính',
      'car':'CAR(%)',
      #'equity':'kệ',
      'casaRatio':'Tiền gửi không kỳ hạn(%)',
      'nob66':'Tiền gửi không kỳ hạn',
      'nob69':'Tiền gửi ký quỹ',
      'nob70':'Tiền gửi mục đích riêng',
      'bsb113':'Tiền gửi của khách hàng'
      }
    )

    datat=data.T
    datat.reset_index(inplace=True)
    datat.columns=datat.loc[0]
    datat=datat[1:]
    for col in datat.columns[1:]:
      datat[col] = pd.to_numeric(datat[col], errors='raise').astype('float64')
    pd.set_option('display.float_format', '{:.2f}'.format)

    return datat
  except Exception as e:
    print(f"❌ Không có dữ liệu '{symbol}': {e}")
    return pd.DataFrame()

# Bảng cân đối kế toán
def balance_sheet(symbol,time):
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
    url = f"https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/financial-statement?section=BALANCE_SHEET"
    response = requests.get(url, headers=headers)

    data = response.json()['data'][time]
    data= json_normalize(data)
    data=data.loc[:,data.sum()!=0]
    if time == "quarters":
        data['Quý']='Q'+ data['lengthReport'].astype(str) +" "+ data['yearReport'].astype(str)
        quater=data.pop('Quý')
        data.insert(1,'Quý',quater)
        data.drop(["organCode","ticker","updateDate","publicDate",'lengthReport','yearReport'],axis=1,inplace=True)
    else:
        data.drop(["organCode","ticker","updateDate","lengthReport","publicDate"],axis=1,inplace=True)
        data['yearReport']=data['yearReport'].astype(str)

    # ==== Từ điển rename chính (cơ bản) ====
    rename_common = {
        'yearReport':'Năm',
        'Quý':'Quý',
        'bsa1':'TÀI SẢN NGẮN HẠN',
        'bsa10':'Trả trước người bán',
        'bsa11':'Phải thu nội bộ',
        'bsa120':'Cổ phiếu ưu đãi',
        'bsa13':'Phải thu khác',
        'bsa160':'Giao dịch mua bán lại trái phiếu Chính phủ',
        'bsa163':'Tài sản dở dang dài hạn',
        'bsa164':'Chi phí sản xuất, kinh doanh dở dang dài hạn',
        'bsa165':'Đầu tư dài hạn nắm giữ đến ngày đáo hạn',
        'bsa166':'Thiết bị, vật tư, phụ tùng thay thế dài hạn',
        'bsa167':'Doanh thu chưa thực hiện ngắn hạn',
        'bsa169':'Giao dịch mua bán lại trái phiếu chính phủ',
        'bsa170':'Người mua trả tiền trước dài hạn',
        'bsa171':'Chi phí phải trả dài hạn',
        'bsa177':'LNST chưa phân phối lũy kế đến cuối kỳ trước',
        'bsa178':'LNST chưa phân phối kỳ này',
        'bsa18':'Tài sản lưu động khác (tổng)',
        'bsa188':'Xây dựng cơ bản đang dở dang',
        'bsa19':'Chi phí trả trước ngắn hạn',
        'bsa2':'Tiền và tương đương tiền',
        'bsa20':'Thuế GTGT được khấu trừ',
        'bsa209':'Lợi thế thương mại',
        'bsa21':'Phải thu thuế khác',
        'bsa211':'Nguồn kinh phí đã hình thành TSCĐ',
        'bsa23':'TÀI SẢN DÀI HẠN',
        'bsa24':'Phải thu dài hạn',
        'bsa25':'Phải thu khách hàng dài hạn',
        'bsa276':'Vốn Góp liên doanh',
        'bsa277':'Đầu tư vào công ty liên kết',
        'bsa29':'Tài sản cố định',
        'bsa3':'Tiền',
        'bsa31':'Nguyên giá TSCĐ hữu hình',
        'bsa32':'Khấu hao lũy kế TSCĐ hữu hình',
        'bsa33':'GTCL tài sản thuê tài chính',
        'bsa34':'Nguyên giá tài sản thuê tài chính',
        'bsa35':'Khấu hao lũy kế tài sản thuê tài chính',
        'bsa36':'GTCL tài sản cố định vô hình',
        'bsa37':'Nguyên giá TSCĐ vô hình',
        'bsa38':'Khấu hao lũy kế TSCĐ vô hình',
        'bsa39':'Xây dựng cơ bản đang dang dở (trước 2015)',
        'bsa4':'Các khoản tương đương tiền',
        'bsa43':'Đầu tư dài hạn',
        'bsa44':'Đầu tư vào các công ty con',
        'bsa45':'Đầu tư vào các công ty liên kết',
        'bsa46':'Đầu tư dài hạn khác',
        'bsa47':'Dự phòng giảm giá đầu tư dài hạn',
        'bsa48':'Lợi thế thương mại (trước 2015)',
        'bsa49':'Tài sản dài hạn khác',
        'bsa5':'Đầu tư ngắn hạn (tổng)',
        'bsa50':'Trả trước dài hạn',
        'bsa51':'Thuế thu nhập hoãn lại (tài sản)',
        'bsa52':'Các tài sản dài hạn khác',
        'bsa53':'TỔNG TÀI SẢN',
        'bsa54':'NỢ PHẢI TRẢ',
        'bsa55':'Nợ ngắn hạn',
        'bsa57':'Phải trả người bán',
        'bsa58':'Người mua trả tiền trước',
        'bsa59':'Thuế và các khoản phải trả Nhà nước',
        'bsa60':'Phải trả người lao động',
        'bsa61':'Chi phí phải trả',
        'bsa62':'Phải trả nội bộ',
        'bsa64':'Phải trả khác',
        'bsa65':'Dự phòng các khoản phải trả ngắn hạn',
        'bsa66':'Quỹ khen thưởng, phúc lợi',
        'bsa67':'Nợ dài hạn',
        'bsa68':'Phải trả nhà cung cấp dài hạn',
        'bsa69':'Phải trả nội bộ dài hạn',
        'bsa7':'Dự phòng giảm giá',
        'bsa70':'Phải trả dài hạn khác',

        'bsa72':'Thuế thu nhập hoãn lại (nợ dài hạn)',
        'bsa76':'Doanh thu chưa thực hiện',
        'bsa77':'Quỹ phát triển khoa học công nghệ',
        'bsa78':'Vốn chủ sở hữu',
        'bsa79':'Vốn và các quỹ',
        'bsa8':'Các khoản phải thu',
        'bsa81':'Thặng dư vốn cổ phần',
        'bsa82':'Vốn khác',
        'bsa83':'Cổ phiếu quỹ',
        'bsa84':'Chênh lệch đánh giá lại tài sản',
        'bsa85':'Chênh lệch tỷ giá',
        'bsa87':'Quỹ dự phòng tài chính',
        'bsa89':'Quỹ khác',
        'bsa90':'Lợi nhuận chưa phân phối',
        'bsa91':'Quỹ hỗ trợ sắp xếp doanh nghiệp',
        'bsa93':'Quỹ khen thưởng, phúc lợi (trước 2010)',
        'bsa94':'Vốn ngân sách nhà nước và quỹ khác',
        'bsa96':'Tổng cộng nguồn vốn',
        'bsb100':'Chứng khoán kinh doanh',
        'bsb101':'Dự phòng giảm giá chứng khoán kinh doanh',
        'bsb102':'Các công cụ tài chính phái sinh và các tài sản tài chính khác',
        'bsb103':'Cho vay khách hàng (tổng)',
        'bsb104':'Cho vay khách hàng',
        'bsb105':'Dự phòng rủi ro cho vay khách hàng',
        'bsb106':'Chứng khoán đầu tư',
        'bsb107':'Chứng khoán đầu tư sẵn sàng để bán',
        'bsb108':'Đầu tư ngắn hạn nắm giữ đến ngày đáo hạn',
        'bsb109':'Dự phòng giảm giá chứng khoán đầu tư',
        'bsb110':'Tài sản Có khác (tổng)',
        'bsb111':'Các khoản nợ chính phủ và NHNN Việt Nam',
        'bsb112':'Tiền gửi và vay các Tổ chức tín dụng khác',
        'bsb113':'Tiền gửi của khách hàng',
        'bsb114':'Các công cụ tài chính phái sinh và các khoản nợ tài chính khác',
        'bsb115':'Vốn tài trợ, uỷ thác đầu tư của Chính phủ và các tổ chức tín dụng khác',
        'bsb116':'Phát hành giấy tờ có giá',
        'bsb117':'Các khoản nợ khác',
        'bsb118':'Vốn của tổ chức tín dụng',
        'bsb119':'Vốn đầu tư XDCB',
        'bsb120':'Cổ phiếu ưu đãi',
        'bsb121':'Quỹ của tổ chức tín dụng',
        'bsb131':'Bảo lãnh khác',
        'bsb158':'Bảo lãnh vay vốn',
        'bsb179':'Cam kết giao dịch hối đoái',
        'bsb180':'Cam kết mua ngoại tệ',
        'bsb181':'Cam kết bán ngoại tệ',
        'bsb182':'Cam kết giao dịch hoán đổi',
        'bsb183':'Cam kết giao dịch tương lai',
        'bsb184':'Cam kết cho vay không hủy ngang',
        'bsb185':'Cam kết trong nghiệp vụ L/C',
        'bsb186':'Cam kết khác',
        'bsb258':'Tiền gửi tại các TCTD khác',
        'bsb259':'Cho vay các TCTD khác',
        'bsb260':'Dự phòng rủi ro',
        'bsb261':'Hoạt động mua nợ',
        'bsb262':'Mua nợ',
        'bsb263':'Dự phòng rủi ro hoạt động mua nợ',
        'bsb264':'Các khoản phải thu',
        'bsb265':'Các khoản lãi và phí phải thu',
        'bsb266':'Tài sản thuế TNDN hoãn lại',
        'bsb267':'Tài sản Có khác',
        'bsb268':'Trong đó: Lợi thế thương mại',
        'bsb269':'Các khoản dự phòng rủi ro cho các tài sản Có nội bảng khác',
        'bsb270':'Tiền gửi của các tổ chức tín dụng khác',
        'bsb271':'Vay các tổ chức tín dụng khác',
        'bsb272':'Các khoản lãi, phí phải trả',
        'bsb273':'Thuế TNDN hoãn lại phải trả',
        'bsb274':'Các khoản phải trả và công nợ khác',
        'bsb275':'Dự phòng rủi ro khác',
        'bsb97':'Tiền gửi tại Ngân hàng nhà nước Việt Nam',
        'bsb98':'Tiền gửi tại các TCTD khác và cho vay các TCTD khác',
        'bsb99':'Chứng khoán kinh doanh (tổng)',
        'bss133':'Phải thu về hoạt động giao dịch chứng khoán (Trước năm 2016)',
        'bss135':'Phải trả hoạt động giao dịch chứng khoán',
        'bss136':'Phải trả cổ tức, gốc và lãi trái phiếu (Trước năm 2016)',
        'bss137':'Phải trả tổ chức phát hành chứng khoán (Trước năm 2016)',
        'bss138':'Quỹ bảo vệ Nhà đầu tư',
        'bss212':'Tiền chi nộp Quỹ Hỗ trợ thanh toán',
        'bss214':'Tài sản tài chính ngắn hạn',
        'bss215':'Các khoản cho vay',
        'bss216':'Các khoản tài chính sẵn sàng để bán (AFS)',
        'bss217':'Các khoản phải thu (từ 2016)',
        'bss218':'Phải thu bán các tài sản tài chính',
        'bss219':'Phải thu và dự thu cổ tức, tiền lãi các tài sản tài chính',
        'bss220':'Phải thu cổ tức, tiền lãi đến ngày nhận',
        'bss221':'Trong đó : phải thu khó đòi về cổ tức , tiền lãi đến ngày nhận nhưng chưa nhận được',
        'bss222':'Dự thu cổ tức , tiền lãi chưa đến ngày nhận',
        'bss223':'Thuế giá trị gia tăng được khấu trừ (Trước năm 2016)',
        'bss224':'Phải thu các dịch vụ CTCK cung cấp',
        'bss225':'Phải thu về lỗi giao dịch CK',
        'bss226':'Dự phòng suy giảm giá trị các khoản phải thu',
        'bss227':'Tạm ứng',
        'bss228':'Vật tư văn phòng, công cụ, dụng cụ',
        'bss229':'Cầm cố, thế chấp, ký quỹ , ký cược ngắn hạn',
        'bss230':'Dự phòng suy giảm giá trị TSNH khác',
        'bss231':'Tài sản tài chính dài hạn',
        'bss232':'Đánh giá TSCĐHH theo giá trị hợp lý',
        'bss233':'Đánh giá TSCĐTTC theo giá trị hợp lý',
        'bss234':'Đánh giá TSCĐVH theo giá trị hợp lý',
        'bss235':'Đánh giá BĐSĐT theo giá trị hợp lý',
        'bss236':'Cầm cố, thế chấp, kỹ quỹ, Ký cược dài hạn',
        'bss237':'Dự phòng suy giảm giá trị tài sản dài hạn',
        'bss239':'Nợ thuê tài sản tài chính ngắn hạn',
        'bss240':'Vay tài sản tài chính ngắn hạn',
        'bss241':'Trái phiếu chuyển đổi ngắn hạn - Cấu phần nợ',
        'bss242':'Trái phiếu phát hành ngắn hạn',
        'bss243':'Vay Quỹ Hỗ trợ thanh toán',
        'bss244':'Phải trả về lỗi giao dịch các tài sản tài chính',
        'bss245':'Các khoản trích nộp phúc lợi nhân viên',
        'bss246':'Nhận ký quỹ, ký cược ngắn hạn',

        'bss248':'Nợ thuê tài chính dài hạn',
        'bss249':'Vay tài sản tài chính dài hạn',
        'bss250':'Trái phiếu phát hành dài hạn',
        'bss251':'Nhận ký quỹ, ký cược dài hạn',
        'bss252':'Vốn đầu tư của chủ sở hữu',
        'bss253':'Quỹ dự trữ bổ sung vốn điều lệ',
        'bss254':'Lợi nhuận đã thực hiện',
        'bss255':'Lợi nhuận chưa thực hiện',
        'nos355':'Tài sản cố định thuê ngoài',
        'nos356':'Chứng chỉ có giá nhận giữ hộ',
        'nos357':'Tài sản nhận thế chấp',
        'nos358':'Nợ khó đòi đã xử lý',
        'nos359':'Ngoại tệ các loại',
        'nos360':'Cổ phiếu đang lưu hành (Số lượng)',
        'nos361':'Cổ phiếu quỹ (Số lượng)',
        'nos362':'Tài sản tài chính niêm yết/đăng ký giao dịch tại VSD của CTCK',
        'nos370':'Tài sản tài chính đã lưu ký tại VSD và chưa giao dịch của CTCK',
        'nos375':'Tài sản tài chính chờ về của CTCK',
        'nos376':'Tài sản tài chính sửa lỗi giao dịch của CTCK',
        'nos377':'Tài sản tài chính chưa lưu ký tại VSD của CTCK',
        'nos378':'Tài sản tài chính được hưởng quyền của CTCK',
        'nos379':'Tài sản tài chính niêm yết/đăng ký giao dịch tại VSD của NĐT',
        'nos380':'Tài sản tài chính giao dịch tự do chuyển nhượng',
        'nos381':'Tài sản tài chính hạn chế chuyển nhượng',
        'nos382':'Tài sản tài chính giao dịch cầm cố',
        'nos383':'Tài sản tài chính phong tỏa, tạm giữ',
        'nos384':'Tài sản tài chính chờ thanh toán',
        'nos385':'Tài sản tài chính chờ cho vay',
        'nos386':'Tài sản tài chính đã lưu ký tại VSD và chưa giao dịch của NĐT',
        'nos387':'Tài sản tài chính đã lưu ký tại VSD và chưa giao dịch, tự do chuyển nhượng',
        'nos388':'Tài sản tài chính đã lưu ký tại VSD và chưa giao dịch, hạn chế chuyển nhượng',
        'nos389':'Tài sản tài chính đã lưu ký tại VSD và chưa giao dịch, cầm cố',
        'nos390':'Tài sản tài chính đã lưu ký tại VSD và chưa giao dịch, phong tỏa, tạm giữ',
        'nos391':'Tài sản tài chính chờ về của NĐT',
        'nos392':'Tài sản tài chính sửa lỗi giao dịch của NĐT',
        'nos393':'Tài sản tài chính chưa lưu ký tại VSD của NĐT',
        'nos394':'Tài sản tài chính được hưởng quyền của Nhà đầu tư',
        'nos395':'Tiền gửi của khách hàng',
        'nos396':'Tiền gửi của Nhà đầu tư về giao dịch chứng khoán',
        'nos399':'Tiền gửi tổng hợp giao dịch chứng khoán cho khách hàng',
        'nos410':'Phải trả Tổ chức phát hành chứng khoán',
        'nos411':'Phải thu/phải trả của khách hàng về lỗi giao dịch các tài sản tài chính',
        'nos412':'Phải trả vay CTCK',
        'nos413':'Phải trả cổ tức, gốc và lãi trái phiếu',
        'nos607':'Tiền gửi bù trừ và thanh toán giao dịch chứng khoán',
        'nos608':'Tiền gửi bù trừ và thanh toán giao dịch chứng khoán Nhà đầu tư trong nước',
        'nos609':'Tiền gửi bù trừ và thanh toán giao dịch chứng khoán Nhà đầu tư nước ngoài',
        'nos610':'Tiền gửi của Tổ chức phát hành chứng khoán',
        'nos614':'Phải trả Nhà đầu tư về tiền gửi giao dịch chứng khoán theo phương thức CTCK quản lý',
        'nos615':'Phải trả Nhà đầu tư trong nước về tiền gửi giao dịch chứng khoán theo phương thức CTCK quản lý',
        'nos616':'Phải trả Nhà đầu tư nước ngoài về tiền gửi giao dịch chứng khoán theo phương thức CTCK quản lý'
        }

    stock=["AGR", "APS", "ART", "BSI", "BVS", "CTS", "FSC", "HCM", "IVS",
        "MBS", "ORS", "PSI", "SHS", "SSI", "TVB", "TVS", "VDS", "VND",
        "VPS", "VIX", "WSS", "DNSE", "YSVN", "TCSC", "APG", "EVS", "VCI","TCI"]
    bank=["ACB", "BAB", "BID", "BVB", "CTG", "EIB", "HDB", "KLB", "LPB", "MBB",
        "MSB", "NAB", "NVB", "OCB", "PGB", "SGB", "SHB", "STB", "TPB", "VCB",
        "VAB", "VBB", "VIB", "VietA", "VPB", "SEAB", "SCB", "ABB"]
    
    rename_stock = {
                'bsa12':'Phải thu về XDCB (Trước năm 2016)',
                'bsa14':'Dự phòng nợ khó đòi (Trước năm 2016)',
                'bsa15':'Hàng tồn kho, ròng (Trước năm 2016)',
                'bsa159':'Phải thu về cho vay ngắn hạn (Trước năm 2016)',
                'bsa16':'Hàng tồn kho (Trước năm 2016)',
                'bsa161':'Trả trước người bán dài hạn (Trước năm 2016)',
                'bsa162':'Phải thu về cho vay dài hạn (Trước năm 2016)',
                'bsa168':'Quỹ bình ổn giá (Trước năm 2016)',
                'bsa17':'Dự phòng giảm giá HTK (Trước năm 2016)',
                'bsa172':'Phải trả nội bộ về vốn kinh doanh (Trước năm 2016)',
                'bsa173':'Trái phiếu chuyển đổi dài hạn - Cấu phần nợ',
                'bsa174':'Cổ phiếu ưu đãi (Trước năm 2016)',
                'bsa175':'Cổ phiếu phổ thông có quyền biểu quyết',
                'bsa176':'Quyền chọn chuyển đổi trái phiếu - Cấu phần vốn',
                'bsa22':'Tài sản ngắn hạn khác',
                'bsa26':'Phải thu nội bộ dài hạn (Trước năm 2016)',
                'bsa27':'Phải thu dài hạn khác (Trước năm 2016)',
                'bsa28':'Dự phòng phải thu dài hạn (Trước năm 2016)',
                'bsa40':'Bất động sản đầu tư',
                'bsa6':'Các tài sản tài chính ghi nhận thông qua lãi lỗ (FVTPL)',
                'bsa63':'Phải trả về xây dựng cơ bản (Trước năm 2016)',
                'bsa73':'Dự phòng trợ cấp thôi việc (Trước năm 2016)',
                'bsa80':'Vốn góp của chủ sở hữu',
                'bsa86':'Quỹ đầu tư và phát triển (Trước năm 2016)',
                'bsa9':'Phải thu khách hàng (Trước năm 2016)',
                'bsa92':'Nguồn kinh phí và quỹ khác',
                'bsa95':'LỢI ÍCH CỦA CỔ ĐÔNG KHÔNG KIỂM SOÁT (trước 2015)',
                'bsi141':'Tài sản thiếu chờ xử lý (Trước năm 2016)',
                'bss134':'Vốn kinh doanh ở các đơn vị trực thuộc (Trước năm 2016)',
                'bss238':'Vay ngắn hạn',
                'bsa56':'Vay và nợ thuê tài sản tài chính ngắn hạn',
                'bss247':'Vay dài hạn',
                'bsa71':'Vay và nợ thuê tài sản tài chính dài hạn',     
            }
    
    rename_bank = {
                'bsa210':'Lợi ích của cổ đông thiểu số',
                    'bsa30':'Tài sản cố định hữu hình',
                    'bsa40':'Bất động sản đầu tư',
                    'bsa41':'Nguyên giá bất động sản đầu tư',
                    'bsa42':'Hao mòn bất động sản đầu tư',
                    'bsa80':'Vốn điều lệ',
                    'bsa95':'Lợi ích của cổ đông thiểu số (trước 2015)'
            }
 
    rename_other = {
                    'bsa12':'Phải thu hợp đồng xây dựng đang thực hiện',
                    'bsa14':'Dự phòng nợ khó đòi',
                    'bsa15':'Hàng tồn kho, ròng',
                    'bsa159':'Phải thu cho vay ngắn hạn',
                    'bsa16':'Hàng tồn kho',
                    'bsa161':'Trả trước người bán dài hạn',
                    'bsa162':'Phải thu cho vay dài hạn',
                    'bsa168':'Quỹ bình ổn giá',
                    'bsa17':'Dự phòng giảm giá hàng tồn kho',
                    'bsa172':'Phải trả nội bộ về vốn kinh doanh',
                    'bsa173':'Trái phiếu chuyển đổi',
                    'bsa174':'Cổ phiếu ưu đãi',
                    'bsa175':'Cổ phiếu phổ thông',
                    'bsa176':'Quyền chọn chuyển đổi trái phiếu',
                    'bsa210':'Lợi ích cổ đông không kiểm soát',
                    'bsa22':'Tài sản lưu động khác',
                    'bsa26':'Phải thu nội bộ dài hạn',
                    'bsa27':'Phải thu dài hạn khác',
                    'bsa28':'Dự phòng phải thu dài hạn',
                    'bsa30':'GTCL TSCĐ hữu hình',
                    'bsa40':'Giá trị ròng tài sản đầu tư',
                    'bsa41':'Nguyên giá tài sản đầu tư',
                    'bsa42':'Khấu hao lũy kế tài sản đầu tư',
                    'bsa6':'Đầu tư ngắn hạn',
                    'bsa63':'Phải trả về xây dựng cơ bản',
                    'bsa73':'Dự phòng trợ cấp thôi việc',
                    'bsa80':'Vốn góp',
                    'bsa86':'Quỹ đầu tư và phát triển',
                    'bsa9':'Phải thu khách hàng',
                    'bsa92':'Vốn Ngân sách nhà nước và quỹ khác',
                    'bsa95':'Lợi ích của cổ đông thiểu số',
                    'bsi141':'Tài sản thiếu cần xử lý',
                    'bss134':'Vốn kinh doanh ở các đơn vị trực thuộc',
                    'bsa56':'Vay ngắn hạn',
                    'bsa71':'Vay dài hạn',

                }

    if symbol in stock:
        rename_dict = {**rename_common, **rename_stock}
    elif symbol in bank:
        rename_dict = {**rename_common, **rename_bank}
    else:
        rename_dict = {**rename_common, **rename_other}

    # ==== Đổi tên và chỉ giữ các cột có trong rename_dict ====
    data = data.rename(columns=rename_dict)
    data = data[[col for col in data.columns if col in rename_dict.values()]]

    datat=data.T
    datat.reset_index(inplace=True)
    datat.columns=datat.loc[0]
    datat=datat[1:]
    for col in datat.columns[1:]:
        datat[col] = pd.to_numeric(datat[col], errors='raise').astype('Int64')

    pd.set_option('display.max_rows', None)
    return datat
  except Exception as e:
    print(f"❌ Không có dữ liệu '{symbol}': {e}")
    return pd.DataFrame()

# Bảng báo cáo kết quả kinh doanh
def income_statement(symbol,time):
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

    url = f"https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol}/financial-statement?section=INCOME_STATEMENT"
    response = requests.get(url, headers=headers)
    data=response.json()['data'][time]
    data=pd.DataFrame(data)
    data=data.loc[:,data.sum()!=0]
    if time == "quarters":
      data['Quý']='Q'+ data['lengthReport'].astype(str) +" "+ data['yearReport'].astype(str)
      quater=data.pop('Quý')
      data.insert(1,'Quý',quater)
      data.drop(["organCode","ticker","createDate","updateDate","publicDate",'lengthReport','yearReport'],axis=1,inplace=True)
    else:
      data.drop(["organCode","ticker","createDate","updateDate","lengthReport","publicDate"],axis=1,inplace=True)

    rename_dict = {
      'yearReport' : 'Năm',
      'isa1' : 'Doanh thu bán hàng và cung cấp dịch vụ',	
      'isa2' : 'Các khoản giảm trừ doanh thu',	
      'isa3' : 'Doanh thu thuần',	
      'isa4' : 'Giá vốn hàng bán',	
      'isa5' : 'Lợi nhuận gộp',	
      'isa6' : 'Doanh thu hoạt động tài chính',	
      'isa7' : 'Chi phí tài chính',	
      'isa8' : 'Chi phí lãi vay',	
      'isa9' : 'Chi phí bán hàng',	
      'isa10' : 'Chi phí quản lý doanh nghiệp',	
      'isa11' : 'Lãi/(lỗ) từ hoạt động kinh doanh',	
      'isa12' : 'Thu nhập khác',	
      'isa13' : 'Chi phí khác',	
      'isa14' : 'Thu nhập khác, ròng',	
      'isa15' : 'Lãi/(lỗ) từ công ty liên doanh',	
      'isa16' : 'Lãi/(lỗ) trước thuế',	
      'isa17' : 'Thuế thu nhập doanh nghiệp - hiện thời',	
      'isa18' : 'Thuế thu nhập doanh nghiệp - hoãn lại',	
      'isa19' : 'Chi phí thuế thu nhập doanh nghiệp',	
      'isa20' : 'Lãi/(lỗ) thuần sau thuế',	
      'isa21' : 'Lợi ích của cổ đông thiểu số',	
      'isa22' : 'Lợi nhuận của Cổ đông của Công ty mẹ',	
      'isa23' : 'Lãi cơ bản trên cổ phiếu (VND)',	
      'isa24' : 'Lãi trên cổ phiếu pha loãng (VND)',	
      'isb25' : 'Thu nhập lãi và các khoản thu nhập tương tự',	
      'isb26' : 'Chi phí lãi và các chi phí tương tự',	
      'isb27' : 'Thu nhập lãi thuần',	
      'isb28' : 'Thu nhập từ dịch vụ',	
      'isb29' : 'Chi phí dịch vụ',	
      'isb30' : 'Lãi/Lỗ thuần từ hoạt động dịch vụ',	
      'isb31' : 'Lãi/(lỗ) thuần từ hoạt động kinh doanh ngoại hối và vàng',	
      'isb32' : 'Lãi/(lỗ) thuần từ mua bán chứng khoán kinh doanh',	
      'isb33' : 'Lãi/(lỗ) thuần từ mua bán chứng khoán đầu tư',	
      'isb34' : 'Thu nhập khác',	
      'isb35' : 'Chi phí khác',	
      'isb36' : 'Lãi/(lỗ) thuần từ hoạt động khác',	
      'isb37' : 'Thu nhập từ cổ tức',	
      'isb38' : 'Tổng thu nhập hoạt động',	
      'isb39' : 'Chi phí quản lý doanh nghiệp',	
      'isb40' : 'Lợi nhuận thuần hoạt động trước khi trích lập dự phòng tổn thất tín dụng',	
      'isb41' : 'Trích lập dự phòng tổn thất tín dụng',	
      'iss42' : 'Doanh thu nghiệp vụ môi giới chứng khoán',	
      'iss43' : 'Doanh thu hoạt động đầu tư chứng khoán, góp vốn (Trước năm 2016)',	
      'iss44' : 'Doanh thu nghiệp vụ bảo lãnh phát hành chứng khoán',	
      'iss46' : 'Doanh thu nghiệp vụ tư vấn đầu tư chứng khoán',	
      'iss47' : 'Doanh thu lưu ký chứng khoán',	
      'iss48' : 'Doanh thu hoạt động ủy thác, đấu giá (Trước năm 2016)',	
      'iss49' : 'Thu cho thuê sử dụng tài sản (Trước năm 2016)',	
      'iss50' : 'Doanh thu khác',	
      'isa102' : 'Lãi/(lỗ) từ công ty liên doanh (từ năm 2015)',	
      'iss115' : 'Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ ( FVTPL)',	
      'iss116' : 'Lãi bán các tài sản tài chính FVTPL',	
      'iss117' : 'Chênh lệch tăng đánh giá lại các TSTC thông qua lãi/lỗ',	
      'iss118' : 'Cổ tức, tiền lãi phát sinh từ tài sản tài chính FVTPL',	
      'iss119' : 'Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn',	
      'iss120' : 'Lãi từ các khoản cho vay và phải thu',	
      'iss121' : 'Lãi từ các tài sản tài chính sẵn sàng để bán',	
      'iss122' : 'Lãi từ các công cụ phát sinh phòng ngừa rủi ro',	
      'iss123' : 'Doanh thu hoạt động tư vấn tài chính',	
      'iss124' : 'Lỗ các tài sản tài chính ghi nhận thông qua lãi lỗ (FVTPL)',	
      'iss125' : 'Lỗ bán các tài sản tài chính',	
      'iss126' : 'Chênh lệch giảm đánh giá lại các TSTC thông qua lãi/lỗ',	
      'iss127' : 'Chi phí giao dịch mua các tài sản tài chính FVTPL',	
      'iss128' : 'Lỗ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)',	
      'iss129' : 'Chi Phí Lãi Vay, Lỗ Từ Các Khoản Cho Vay Và Phải Thu (Trước Năm 2016)',	
      'iss130' : 'Lỗ Và Ghi Nhận Chênh Lệch Đánh Giá Theo Giá Trị Hợp Lý Tài Sản Tài Chính Sẵn Sàng Để Bán (Afs) Khi Phân Loại Lại',	
      'iss168' : 'Cp Dự Phòng Tstc, Xử Lý Tổn Thất Các Khoản Phải Thu Khó Đòi Là Lỗ Suy Giảm Tstc Và Cp Đi Vay',	
      'iss131' : 'Lỗ Từ Các Tài Sản Tài Chính Phái Sinh Phòng Ngừa Rủi Ro',	
      'iss132' : 'Chi phí hoạt động tự doanh',	
      'iss133' : 'Chi phí nghiệp vụ môi giới chứng khoán',	
      'iss134' : 'chi phí nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán',	
      'iss135' : 'Chi phí nghiệp vụ tư vấn đầu tư chứng khoán',	
      'iss136' : 'Chí phí hoạt động đấu giá, ủy thác',	
      'iss137' : 'Chi phí nghiệp vụ lưu ký chứng khoán',	
      'iss138' : 'Chi phí hoạt động tư vấn tài chính',	
      'iss139' : 'Chi phí các dịch vụ khác',	
      'iss140' : 'Chi phí sửa lỗi giao dịch chứng khoán, lỗi khác',	
      'iss141' : 'Doanh thu từ hoạt động tài chính',	
      'iss142' : 'Chênh Lệch Lãi Tỷ Giá Hối Đoái Đã Và Chưa Thực Hiện',	
      'iss143' : 'Doanh Thu, Dự Thu Cổ Tức, Lãi Tiền Gửi Không Cố Định Phát Sinh Trong Kỳ',	
      'iss144' : 'Lãi Bán, Thanh Lý Các Khoản Đầu Tư Vào Công Ty Con, Liên Kết, Liên Doanh',	
      'iss145' : 'Doanh thu khác về đầu tư',	
      'iss146' : 'Chi phí tài chính',	
      'iss147' : 'Chênh Lệch Lỗ Tỷ Giá Hối Đoái Đã Và Chưa Thực Hiện',	
      'iss148' : 'Chi phí lãi vay',	
      'iss149' : 'Lỗ Bán, Thanh Lý Các Khoản Đầu Tư Vào Công Ty Con, Liên Kết, Liên Doanh',	
      'iss150' : 'Chi Phí Dự Phòng Suy Giảm Giá Trị Các Khoản Đầu Tư Tài Chính Dài Hạn',	
      'iss151' : 'Chi phí đầu tư khác',	
      'iss152' : 'Chi phí bán hàng',	
      'iss153' : 'Lợi nhuận đã thực hiện',	
      'iss154' : 'Lợi nhuận chưa thực hiện',	
      'iss155' : 'Lnst Trích Các Quỹ Dự Trữ Điều Lệ, Quỹ Dự Phòng Tài Chính Và Rủi Ro Nghề Nghiệp',	
      'iss156' : 'Lãi/(Lỗ) Từ Đánh Giá Lại Các Các Khoản Đầu Tư Giữ Đến Ngày Đáo Hạn',	
      'iss157' : 'Lãi/(Lỗ) Từ Đánh Giá Lại Các Tài Sản Tài Chính Sẵn Sàng Để Bán',	
      'iss158' : 'Lãi/(Lỗ) Toàn Diện Khác Được Chia Từ Hoạt Động Đầu Tư Vào Công Ty Con, Đầu Tư Liên Kết, Liên Doanh',	
      'iss159' : 'Lãi/(Lỗ) Từ Đánh Giá Lại Các Công Cụ Tài Chính Phái Sinh',	
      'iss160' : 'Lãi/(Lỗ) Chênh Lệch Tỷ Giá Của Hoạt Động Tại Nước Ngoài',	
      'iss161' : 'Lãi/(Lỗ) Từ Các Khoản Đầu Tư Vào Công Ty Con. Công Ty Liên Kết, Liên Doanh Chưa Chia',	
      'iss162' : 'Lãi/(lỗ) đánh giá công cụ phái sinh',	
      'iss163' : 'Lãi/(Lỗ) Đánh Giá Lại Tài Sản Cố Định Theo Mô Hình Giá Trị Hợp Lý',	
      'iss164' : 'Tổng thu nhập toàn diện',	
      'iss165' : 'Thu Nhập Toàn Diện Phân Bổ Cho Chủ Sở Hữu',	
      'iss166' : 'Thu Nhập Toàn Diện Phân Bổ Cho Cổ Đông Không Nắm Quyền Kiểm Soát',	
      'iss167' : 'Thu Nhập Thuần Trên Cổ Phiếu Phổ Thông',	
      'iss174' : 'Thu nhập (lỗ) toàn diện khác sau thuế'	

    }

    data=data.rename(columns=rename_dict)
    data = data[[col for col in data.columns if col in rename_dict.values() or col == 'Quý']]

    if time=='quarters':
      data[data.columns[1:]]=data[data.columns[1:]].astype(int)
      data=data.T
    else:
      data=data.astype(int).T

    data.reset_index(inplace=True)
    data.columns=data.loc[0]
    data=data[1:]

    return data
  except Exception as e:
    print(f"❌ Không có dữ liệu '{symbol}': {e}")
    return pd.DataFrame()

# Báo cáo lưu chuyển tiền tệ
def cash_flow(symbol,time):
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

    url=f'https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol.upper()}/financial-statement?section=CASH_FLOW'
    response=requests.get(url,headers=headers)

    if time=='years':
        data=response.json()['data']['years']
        data=pd.json_normalize(data)
        data=data.loc[:,data.sum()!=0]
        cols=['organCode','ticker','createDate','updateDate','lengthReport','publicDate','cfs222','cfa44','cfa45','cfs107','cfs108','cfs109','cfs110','cfs111','cfs112']
        col_drop=[col for col in cols if col in data.columns]
        data=data.drop(columns=col_drop)
        data['yearReport']=data['yearReport'].astype(str)

    else:
        data=response.json()['data']['quarters']
        data=pd.json_normalize(data)
        data['Quý']='Q'+ data['lengthReport'].astype(str) +" "+ data['yearReport'].astype(str)
        quater=data.pop('Quý')
        data.insert(1,'Quý',quater)
        data=data.loc[:,data.sum()!=0]
        cols=['organCode','ticker','createDate','updateDate','publicDate','yearReport','lengthReport','cfs222','cfa44','cfa45','cfs107','cfs108','cfs109','cfs110','cfs111','cfs112']
        col_drop=[col for col in cols if col in data.columns]
        data=data.drop(columns=col_drop)


    #data=data.rename(columns={
    rename_common={
        'yearReport':'Năm',
        'cfa1':'Lợi nhuận/(lỗ) trước thuế',
        'cfa103':'Phân bổ lợi thế thương mại',
        'cfa104':'Các khoản điều chỉnh khác',
        'cfa105':'(Tăng)/giảm chi phí trả trước',
        'cfa19':'Tiền chi để mua sắm, xây dựng TSCĐ, BĐSĐT và các tài sản dài hạn khác',
        'cfa2':'Khấu hao TSCĐ và BĐSĐT',
        'cfa20':'Tiền thu từ thanh lý, nhượng bán TSCĐ, BĐSĐT và các tài sản dài hạn khác',
        'cfa21':'Tiền chi cho vay, mua các công cụ nợ của đơn vị khác',
        'cfa22':'Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác',
        'cfa23':'Tiền chi đầu tư góp vốn vào công ty con, công ty liên doanh, liên kết và đầu tư khác',
        'cfa24':'Tiền thu hồi các khoản đầu tư góp vốn vào công ty con, công ty liên doanh, liên kết và đầu tư khác',
        'cfa25':'Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia',
        'cfa26':'Lưu chuyển tiền thuần từ hoạt động đầu tư',
        'cfa27':'Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu',
        'cfa28':'Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành',
        'cfa29':'Tiền thu được các khoản đi vay',
        'cfa3':'Chi phí dự phòng',
        'cfa30':'Tiền trả nợ gốc vay',
        'cfa31':'Tiền trả nợ gốc thuê tài chính',
        'cfa32':'Cổ tức, lợi nhuận đã trả cho chủ sở hữu',
        'cfa33':'Tiền lãi đã nhận',
        'cfa34':'Lưu chuyển tiền thuần từ hoạt động tài chính',
        'cfa35':'Lưu chuyển tiền thuần trong kỳ',
        'cfa36':'Tiền và tương đương tiền đầu kỳ',
        'cfa37':'Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ',
        'cfa38':'Tiền và tương đương tiền cuối kỳ',
        'cfa4':'Lãi/lỗ chênh lệch tỷ giá hối đoái do đánh giá lại các khoản mục tiền tệ có gốc ngoại tệ',
        'cfa43':'Tiền thuế thu nhập thực nộp trong kỳ',
        'cfa5':'Lãi/(lỗ) từ thanh lý tài sản cố định',
        'cfa6':'(Lãi)/lỗ từ hoạt động đầu tư',
        'cfa7':'Chi phí lãi vay',
        'cfa8':'Thu lãi và cổ tức',
        'cfa9':'Lưu chuyển tiền thuần từ hoạt động kinh doanh trước những thay đổi về tài sản và vốn lưu động',
        'cfb106':'Tiền thu các khoản nợ đã được xử lý, xóa, bù đắp bằng nguồn rủi ro',
        'cfb221':'Chênh lệch số tiền thực thu/thực chi từ hoạt động kinh doanh',
        'cfb48':'Tiền gửi tại NHNN',
        'cfb49':'Tăng/giảm các khoản tiền gửi và cho vay các tổ chức tín dụng khác',
        'cfb50':'Tăng/giảm các khoản về kinh doanh chứng khoán',
        'cfb51':'Tăng/giảm các công cụ tài chính phái sinh và các tài sản tài chính khác',
        'cfb52':'Tăng/giảm các khoản cho vay khách hàng',
        'cfb53':'(Tăng)/Giảm lãi, phí phải thu',
        'cfb54':'Tăng/giảm nguồn dự phòng để bù đắp tổn thất các khoản',
        'cfb55':'Tăng/giảm khác về tài sản hoạt động',
        'cfb56':'Tăng/(Giảm) các khoản nợ chính phủ và NHNN',
        'cfb57':'Tăng/(Giảm) các khoản tiền gửi và vay các TCTD khác',
        'cfb58':'Tăng/(Giảm) tiền gửi của khách hàng',
        'cfb59':'Tăng/(Giảm) các công cụ tài chính phái sinh và các khoản nợ tài chính khác',
        'cfb60':'Tăng/(Giảm) vốn tài trợ, uỷ thác đầu tư của chính phủ và các TCTD khác',
        'cfb61':'Tăng/(Giảm) phát hành giấy tờ có giá',
        'cfb62':'Tăng/(Giảm) lãi, phí phải trả',
        'cfb63':'Tăng/(Giảm) khác về công nợ hoạt động',
        'cfb64':'Lưu chuyển tiền thuần từ hoạt động kinh doanh trước thuế thu nhập DN',
        'cfb65':'Chi từ các quỹ của TCTD',
        'cfb66':'Thu được từ nợ khó đòi',
        'cfb67':'Tiền chi từ thanh lý, nhượng bán TSCĐ',
        'cfb68':'Mua sắm Bất động sản đầu tư',
        'cfb69':'Tiền thu từ bán, thanh lý bất động sản đầu tư',
        'cfb70':'Tiền chi ra do bán, thanh lý bất động sản đầu tư',
        'cfb71':'Tiền thu từ phát hành giấy tờ có giá dài hạn đủ điều kiện tính vào vốn tự có và các khoản vốn vay dài hạn khác',
        'cfb72':'Tiền chi thanh toán giấy tờ có giá dài hạn đủ điều kiện tính vào vốn tự có và các khoản vốn vay dài hạn khác',
        'cfb73':'Tiền chi ra mua cổ phiếu quỹ',
        'cfb74':'Tiền thu được do bán cổ phiếu quỹ',
        'cfb75':'Thu nhập lãi và các khoản thu nhập tương tự nhận được',
        'cfb76':'Chi phí lãi và các chi phí tương tự đã trả',
        'cfb77':'Thu nhập từ hoạt động dịch vụ nhận được',
        'cfb78':'Thu nhập thuần từ hoạt động kinh doanh ngoại hối và vàng',
        'cfb79':'Thu nhập từ hoạt động kinh doanh chứng khoán',
        'cfb80':'Thu nhập khác',
        'cfb81':'Tiền chi trả cho nhân viên và hoạt động quản lý, cộng cụ',
        'cfs113':'Tiền vay Quỹ Hỗ trợ thanh toán',
        'cfs114':'Tiền vay khác',
        'cfs115':'Tiền chi trả gốc vay Quỹ Hỗ trợ thanh toán',
        'cfs116':'Tiền chi trả nợ gốc vay tài sản tài chính',
        'cfs117':'Tiền chi trả gốc nợ vay khác',
        'cfs118':'Tiền mặt, tiền gửi ngân hàng đầu kỳ',
        'cfs119':'Tiền gửi ngân hàng cho hoạt động CTCK (đầu kỳ)',
        'cfs120':'Các khoản tương đương tiền (Lưu chuyển thuần trong kỳ) (Đầu kỳ)',
        'cfs121':'Tiền mặt, tiền gửi ngân hàng cuối kỳ',
        'cfs122':'Tiền gửi ngân hàng cho hoạt động CTCK (Cuối kỳ)',
        'cfs123':'Các khoản tương đương tiền (Lưu chuyển thuần trong kỳ) (Cuối kỳ)',
        'cfs124':'Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ (Lưu chuyển thuần trong kỳ) (Cuối kỳ)',
        'cfs125':'Tiền thu bán chứng khoán môi giới cho khách hàng',
        'cfs126':'Tiền chi mua chứng khoán môi giới cho khách hàng',
        'cfs127':'Tiền thu bán chứng khoán ủy thác của khách hàng',
        'cfs128':'Tiền chi bán chứng khoán ủy thác của khách hàng',
        'cfs129':'Thu tiền từ tài khoản vãng lai của khách hàng (Trước năm 2016)',
        'cfs130':'Chi tiền từ tài khoản vãng lai của khách hàng (Trước năm 2016)',
        'cfs131':'Thu vay Quỹ Hỗ trợ thanh toán',
        'cfs132':'Chi trả vay Quỹ Hỗ trợ thanh toán',
        'cfs133':'Nhận tiền gửi để thanh toán giao dịch chứng khoán của khách hàng',
        'cfs134':'Nhận tiền gửi của Nhà đầu tư cho hoạt động ủy thác đầu tư của khách hàng',
        'cfs135':'Chi trả phí lưu ký chứng khoán của khách hàng',
        'cfs136':'Thu lỗi giao dịch chứng khoán',
        'cfs137':'Chi lỗi giao dịch chứng khoán',
        'cfs138':'Tiền thu của Tổ chức phát hành chứng khoán',
        'cfs139':'Tiền chi trả Tổ chức phát hành chứng khoán',
        'cfs140':'Lưu chuyển tiền hoạt động môi giới, ủy thác của khách hàng',
        'cfs142':'Tiền gửi ngân hàng đầu kỳ',
        'cfs143':'Tiền gửi của NĐT về GDCK theo phương thức CTCK quản lý (Đầu kỳ)',
        'cfs144':'Tiền gửi của NĐT về GDCK theo phương thức CTCK quản lý (Đầu kỳ): có kỳ hạn',
        'cfs145':'Tiền gửi tổng hợp GDCK cho khách hàng (Đầu kỳ)',
        'cfs146':'Tiền gửi bù trừ và thanh toán GDCK (đầu kỳ)',
        'cfs147':'Tiền gửi của tổ chức phát hành (đầu kỳ)',
        'cfs148':'Tiền gửi của tổ chức phát hành (Đầu kỳ): có kỳ hạn',
        'cfs149':'Tiền gửi của NĐT về GDCK theo phương thức NHTM quản lý (Đầu kỳ) (Trước năm 2016)',
        'cfs150':'Tiền gửi của NĐT về GDCK theo phương thức NHTM quản lý (Đầu kỳ): có kỳ hạn (Trước năm 2016)',
        'cfs151':'Các khoản tương đương tiền ( hoạt động môi giới, ủy thác của khách hàng) (Đầu kỳ)',
        'cfs152':'Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ (Đầu kỳ)',
        'cfs154':'Tiền gửi ngân hàng cuối kỳ',
        'cfs155':'Tiền gửi của NĐT về GDCK theo phương thức CTCK quản lý (Cuối kỳ)',
        'cfs156':'Tiền gửi của NĐT về GDCK theo phương thức CTCK quản lý (Cuối kỳ): có kỳ hạn',
        'cfs157':'Tiền gửi của NĐT về GDCK theo phương thức NHTM quản lý (Cuối kỳ) (Trước năm 2016)',
        'cfs158':'Tiền gửi của NĐT về GDCK theo phương thức NHTM quản lý (Cuối kỳ): có kỳ hạn (Trước năm 2016)',
        'cfs159':'Tiền gửi tổng hợp GDCK cho khách hàng (Cuối kỳ)',
        'cfs160':'Tiền gửi bù trừ và thanh toán GDCK (Cuối kỳ)',
        'cfs161':'Tiền gửi của tổ chức phát hành (Cuối kỳ)',
        'cfs162':'Tiền gửi của tổ chức phát hành (Cuối kỳ): có kỳ hạn',
        'cfs163':'Các khoản tương đương tiền ( hoạt động môi giới, ủy thác của khách hàng) (Cuối kỳ)',
        'cfs164':'Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ (hoạt động môi giới, ủy thác của khách hàng) (Cuối kỳ)',
        'cfs165':'Điều chỉnh cho các khoản',
        'cfs166':'Chi phí phải trả, chi phí trả trước',
        'cfs167':'Tăng các chi phí phi tiền tệ',
        'cfs168':'Lỗ đánh giá giá trị các tài sản tài chính ghi nhận thông qua lãi/lỗ FVTPL',
        'cfs169':'Lỗ đánh giá giá trị các công nợ tài chính ghi nhận thông qua KQKD (Trước năm 2016)',
        'cfs170':'Lỗ đánh giá giá trị các công cụ tài chính phái sinh (Trước năm 2016)',
        'cfs171':'Lỗ từ thanh lý các tài sản tài chính sẵn sàng để bán (Trước năm 2016)',
        'cfs172':'Suy giảm giá trị của các tài sản tài chính sẵn sàng để bán (Trước năm 2016)',
        'cfs173':'Lỗ suy giảm giá trị các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)',
        'cfs174':'Lỗ suy giảm giá trị các khoản cho vay',
        'cfs175':'Lỗ về ghi nhận chênh lệch đánh giá theo giá trị hợp lý tài sản tài chính sẵn sàng để bán AFS khi phân loại lại',
        'cfs176':'Lỗ đánh giá giá các công cụ tài chính phát sinh cho mục đích phòng ngừa rủi ro (Trước năm 2016)',
        'cfs177':'Lỗ từ thanh lý TSCĐ (Trước năm 2016)',
        'cfs178':'Suy giảm giá trị của các tài sản cố định, BĐSĐT',
        'cfs179':'Chi phí dự phòng suy giảm giá trị các khoản đầu tư tài chính dài hạn',
        'cfs180':'Lỗ từ thanh lý các khoản đầu tư vào công ty con và công ty liên doanh, liên kết (Trước năm 2016)',
        'cfs181':'Lỗ khác',
        'cfs182':'Giảm các doanh thu phi tiền tệ',
        'cfs183':'Lãi đánh giá giá trị các tài sản chính ghi nhận thông qua lãi/lỗ FVTPL',
        'cfs184':'Lãi đánh giá giá trị các công nợ tài chính thông qua kết quả kinh doanh (Trước năm 2016)',
        'cfs185':'Lãi từ thanh lý các tài sản tài chính sẵn sàng để bán (Trước năm 2016)',
        'cfs186':'Hoàn nhập suy giảm giá trị của các tài sản tài chính sẵn sàng để bán (Trước năm 2016)',
        'cfs187':'Lãi về ghi nhận chệnh lệch đánh giá theo giá trị hợp lý tài sản tài chính sẵn sàng để bán AFS khi phân loại lại',
        'cfs188':'Lãi đánh giá giá trị các công cụ tài chính phái sinh cho mục đích phòng ngừa',
        'cfs189':'Lãi từ thanh lý các khoản cho vay và phải thu',
        'cfs190':'Hoàn nhập chi phí dự phòng',
        'cfs191':'Lãi từ thanh lý tài sản cố định, BĐSĐT',
        'cfs192':'Lãi từ thanh lý các khoản đầu tư vào công ty con và công ty liên doanh, liên kết',
        'cfs193':'Lãi khác',
        'cfs194':'Thay đổi tài sản và nợ phải trả hoạt động (Trước năm 2016)',
        'cfs195':'Tăng (giảm) tài sản tài chính ghi nhận thông qua lãi/ lỗ (FVTPL)',
        'cfs196':'Tăng (giảm) các khoản đầu tư giữ đến ngày đáo hạn (HTM)',
        'cfs197':'Tăng(giảm) các khoản cho vay',
        'cfs198':'Tăng (giảm) tài sản tài chính sẵn sàng để bán AFS',
        'cfs199':'Tăng/giảm các tài sản khác',
        'cfs200':'Tăng/giảm các khoản phải thu (Trước năm 2016)',
        'cfs201':'Tăng/giảm vay và nợ thuê tài sản tài chính (Trước năm 2016)',
        'cfs202':'Tăng/giảm vay tài sản tài chính (Trước năm 2016)',
        'cfs203':'Tăng/giảm Trái phiếu chuyển đổi-Cấu phần nợ (Trước năm 2016)',
        'cfs204':'Tăng/giảm Trái phiếu phát hành (Trước năm 2016)',
        'cfs205':'Tăng/giảm vay Quỹ Hỗ trợ thanh toán (Trước năm 2016)',
        'cfs206':'(-) Tăng, (+) giảm phải thu bán các tài sản tài chính',
        'cfs207':'(-) Tăng, (+) giảm phải thu và dự thu cổ tức, tiền lãi các tài sản tài chính',
        'cfs208':'(-) Tăng, (+) giảm các khoản phải thu các dịch vụ CTCK cung cấp',
        'cfs209':'(-) Tăng, (+) giảm các khoản phải thu về lỗi giao dịch các TSTC',
        'cfs210':'(+) Tăng, (-) giảm phải trả cho người bán',
        'cfs211':'(+) Tăng, (-) giảm phải trả Tổ chức phát hành chứng khoán (Trước năm 2016)',
        'cfs212':'(+) Tăng, (-) giảm các khoản trích nộp phúc lợi nhân viên',
        'cfs213':'(+) Tăng, (-) giảm thuế và các khoản phải nộp Nhà nước',
        'cfs214':'(+) Tăng, (-) giảm phải trả người lao động',
        'cfs215':'(+) Tăng, (-) giảm phải trả về lỗi giao dịch các tài sản tài chính',
        'cfs216':'Tiền lãi đã thu',
        'cfs217':'Tiền thu khác',
        'cfs220':'Các khoản chi khác',
        'cfs223':'(-) Tăng, (+) giảm chi phí phải trả (không bao gồm chi phí lãi vay)',
        'cfs224':'Chi trả thanh toán giao dịch chứng khoán của khách hàng',
        'cfs225':'Chi trả cho hoạt động ủy thác đầu tư của khách hàng',
        'cfs141':'Tiền và các khoản tương đương tiền đầu kỳ của khách hàng',
        'cfs153':'Tiền và các khoản tương đương tiền cuối kỳ của khách hàng'
      }

    stock=["AGR", "APS", "ART", "BSI", "BVS", "CTS", "FSC", "HCM", "IVS",
    "MBS", "ORS", "PSI", "SHS", "SSI", "TVB", "TVS", "VDS", "VND",
    "VPS", "VIX", "WSS", "DNSE", "YSVN", "TCSC", "APG", "EVS", "VCI"]
    bank=["ACB", "BAB", "BID", "BVB", "CTG", "EIB", "HDB", "KLB", "LPB", "MBB",
    "MSB", "NAB", "NVB", "OCB", "PGB", "SGB", "SHB", "STB", "TPB", "VCB",
    "VAB", "VBB", "VIB", "VietA", "VPB", "SEAB", "SCB", "ABB"]
    
    rename_stock={
      'cfa10':'(-) Tăng, (+) giảm các khoản phải thu khác',
      'cfa11':'Tăng/giảm hàng tồn kho (Trước năm 2016)',
      'cfa12':'(+) Tăng, (-) giảm các khoản phải trả, phải nộp khác',
      'cfa13':'Tăng/giảm chi phí trả trước',
      'cfa14':'Tiền lãi vay đã trả',
      'cfa15':'Thuế TNDN CTCK đã nộp',
      'cfa16':'Tiền thu khác từ hoạt động kinh doanh',
      'cfa17':'Tiền chi khác cho hoạt động kinh doanh',
      'cfa18':'Lưu chuyển thuần từ hoạt động kinh doanh'
    }
    
    rename_elsestock={
      'cfa10':'Lợi nhuận/(lỗ) từ hoạt động kinh doanh trước những thay đổi vốn lưu động',
      'cfa11':'(Tăng)/giảm các khoản phải thu',
      'cfa12':'(Tăng)/giảm hàng tồn kho',
      'cfa13':'Tăng/(giảm) các khoản phải trả',
      'cfa14':'(Tăng)/giảm chứng khoán kinh doanh',
      'cfa16':'Thuế thu nhập doanh nghiệp đã nộp',
      'cfa17':'Tiền thu khác từ hoạt động kinh doanh',
      'cfa18':'Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh'
    }

    rename_bank={
      'cfa15':'Thuế thu nhập doanh nghiệp đã trả'
    }

    rename_elsebank={
      'cfa15':'Tiền lãi vay đã trả'
    } 
    
    rename_dict = rename_common.copy()
    if symbol in stock:
      rename_dict.update(rename_stock)
    else:
      rename_dict.update(rename_elsestock)
      if symbol in bank:
          rename_dict.update(rename_bank)
      else:
          rename_dict.update(rename_elsebank)
    
    data = data.rename(columns=rename_dict)
    data = data[[col for col in data.columns if col in rename_dict.values() or col==' ']]
    datat=data.T
    datat.reset_index(inplace=True)
    datat.columns=datat.loc[0]
    datat = datat.drop(index=0).reset_index(drop=True)
    for col in datat.columns[1:]:
        datat[col] = pd.to_numeric(datat[col], errors='raise').astype('Int64')
    df=datat.fillna(0)
    pd.set_option('display.max_rows', None)
    return df
  except Exception as e:
    print(f"❌ Không có dữ liệu '{symbol}': {e}")
    return pd.DataFrame()

