# VNSFintech
`VNSFintech` là thư viện Python cung cấp dữ liệu và công cụ hỗ trợ tài chính cho các nhà đầu tư và phân tích thị trường chứng khoán.

## Cài đặt

- **Cài đặt thư viện:**  
  ```bash
  pip install VNSFintech
  ```

- **Cập nhật thư viện bản mới nhất:**  
  ```bash
  pip install --upgrade VNSFintech
  ```

- **Sử dụng thư viện:**  
  ```python
  from VNSFintech import *
  ```

## Hướng dẫn sử dụng thư viện VNSFintech

## `Dữ liệu cổ phiếu`
#### 1. Dữ liệu xếp hạng cổ phiếu:
Truy vấn dữ liệu 10 cổ phiếu có tỷ lệ thay đổi giá tăng hoặc giảm của 3 sàn chứng khoán việt nam:
- **Mã tăng:**
  ```python
  stock = top_stock(exchange='HNX', type='up')
  ```
  ```python
  stock = top_stock(exchange='HOSE', type='up')
  ```
    ```python
  stock = top_stock(exchange='UPCOM', type='up')
  ```

- **Mã giảm:**
  ```python
  stock = top_stock(exchange='HNX', type='down')
  ```
  ```python
  stock = top_stock(exchange='HOSE', type='down')
  ```
    ```python
  stock = top_stock(exchange='UPCOM', type='down')
  ```

#### 2. Thông tin mã cổ phiếu: 
Câu lệnh truy vấn dữ liệu theo mã cổ phiếu là:
```python
stock = stock_info(symbol='HPG')
```

Câu lệnh truy vấn dữ liệu theo sàn là:
```python
stock = stock_info(exchange='HNX')
```

Câu lệnh đầy đủ truy vấn dữ liệu đầy đủ là:
```python
stock = stock_info()
```

#### 3. Lịch sử dữ liệu giá giao dịch cổ phiếu: 
Câu lệnh đầy đủ truy vấn dữ liệu lịch sử là:
```python
stock = history(symbol='HPG', start='2020-01-01', end='2023-01-01', time='days')
```

Nếu không để `time`, mặc định của `time` sẽ là `'days'`:
```python
stock = history(symbol='HPG', start='2020-01-01', end='2023-01-01')
```

Để truy vấn các lịch sử dữ liệu theo các khoảng thời gian khác, `time` có thể là:
- `minutes`: 1 phút
- `hours`: 1 giờ
- `days`: 1 ngày
- `months`: 1 tháng


#### 4. Lịch sử chi tiết giá giao dịch cổ phiếu: 
Câu lệnh đầy đủ truy vấn dữ liệu là:
```python
stock = price_history(symbol='HPG',time='days', start='2020-01-01', end='2023-01-01')
```

Để truy vấn các lịch sử dữ liệu theo các khoảng thời gian khác, `time` có thể là:
- `days`: Ngày
- `months`: Tháng
- `quarters`: Quý
- `years`: Năm

#### 5. Tổng hợp dữ liệu giá giao dịch cổ phiếu: 
Câu lệnh đầy đủ truy vấn dữ liệu lịch sử là:
```python
stock = price_history_summary(symbol='HPG')
```

#### 6. Lịch sử giao dịch nước ngoài của cổ phiếu: 
Câu lệnh đầy đủ truy vấn dữ liệu lịch sử là:
```python
stock = foreign_history(symbol='HPG',time='days', start='2020-01-01', end='2023-01-01')
```

Để truy vấn các lịch sử dữ liệu theo các khoảng thời gian khác, `time` có thể là:
- `days`: Ngày
- `months`: Tháng
- `quarters`: Quý
- `years`: Năm

#### 7. Tổng hợp dữ liệu giao dịch nước ngoài của cổ phiếu: 
Câu lệnh đầy đủ truy vấn dữ liệu lịch sử là:
```python
stock = foreign_history_summary(symbol='HPG')
```

#### 8. Lịch sử giao dịch tự doanh của cổ phiếu: 
Câu lệnh đầy đủ truy vấn dữ liệu lịch sử là:
```python
stock = proprietary_history(symbol='HPG',time='days', start='2020-01-01', end='2023-01-01')
```

Để truy vấn các lịch sử dữ liệu theo các khoảng thời gian khác, `time` có thể là:
- `days`: Ngày
- `months`: Tháng
- `quarters`: Quý
- `years`: Năm

#### 9. Tổng hợp dữ liệu giao dịch tự doanh của cổ phiếu: 
Câu lệnh đầy đủ truy vấn dữ liệu lịch sử là:
```python
stock = proprietary_history_summary(symbol='HPG',time='days')
```

Câu lệnh truy vấn dữ liệu tổng đến hiện tại và dữ liệu trung bình theo các khoảng thời gian khác, `time` có thể là:
- `days`: Ngày
- `months`: Tháng
- `quarters`: Quý
- `years`: Năm

#### 10. Lịch sử cung cầu giao dịch của cổ phiếu: 
Câu lệnh đầy đủ truy vấn dữ liệu lịch sử là:
```python
stock = demand_history(symbol='HPG',time='days', start='2020-01-01', end='2023-01-01')
```

Để truy vấn các lịch sử dữ liệu theo các khoảng thời gian khác, `time` có thể là:
- `days`: Ngày
- `months`: Tháng
- `quarters`: Quý
- `years`: Năm

#### 11. Sổ lệnh giao dịch trong ngày:
Truy vấn dữ liệu sổ lệnh theo mã cổ phiếu:
```python
stock = intraday(symbol='HPG')
```

#### 12. Sổ lệnh giao dịch chi tiết:
Truy vấn dữ liệu sổ lệnh gộp và phân loại dòng tiền:
```python
stock = intraday_order(symbol='HPG')
```

#### 13. Dữ liệu tin tức cổ phiếu:
Dữ liệu tin tức của mã cổ phiếu
```python
stock = news(symbol='HPG')
```

#### 14. Dữ liệu cổ tức cổ phiếu:
Dữ liệu cổ tức và phát hành cổ phần của mã cổ phiếu
```python
stock = dividend(symbol='HPG')
```

#### 15. Dữ liệu thông tin họp cổ đông của cổ phiếu:
Dữ liệu tin tức của mã cổ phiếu
```python
stock = general_meeting(symbol='HPG')
```

#### 16. Dữ liệu tin tức khác của cổ phiếu:
Dữ liệu tin tức khác của mã cổ phiếu
```python
stock = other_event(symbol='HPG')
```

#### 17. Dữ liệu lịch sử thị trường và Nước ngoài Mua/Bán
Dữ liệu lịch sử thị trường có sẵn cho các chỉ số: `'VNINDEX'`, `'VN30'`, `'HNXINDEX'`, `'UPINDEX'`.
```python
stock = overview_market(market="VNINDEX", start="2025-03-18", end="2025-04-25")
```

#### 18. Dữ liệu các sàn giao dịch chứng khoán Việt Nam:
Dữ liệu các sàn giao dịch bao gồm: `'HOSE'`, `'HNX'`, `'UPCOM'`, `'VN30'`, `'VNMIDCAP'`, `'HNX30'`, `'HDTL'`
```python
stock = stock_exchange(exchange='HOSE')
```

#### 19. Dữ liệu các sàn giao dịch khác:
Dữ liệu các sàn giao dịch bao gồm: `'Ethereum'`, `'Bitcoin'`, `'Vàng'`, `'Bạc'`, ...
```python
stock = exchange_other()
```

## `Dữ liệu chỉ số tài chính`
#### 1. Chỉ số tài chính:
Truy vấn các chỉ số tài chính của công ty theo quý hoặc năm:
- **Theo năm:**
  ```python
  finance = finance_ratio(symbol='HPG', time='years')
  ```

- **Theo quý:**
  ```python
  finance = finance_ratio(symbol='HPG', time='quarters')
  ```

#### 2. Bản Cân Đối Kế Toán:
Truy vấn bản cân đối kế toán theo năm hoặc quý:
- **Theo năm:**
  ```python
  finance = balance_sheet(symbol='HPG', time='years')
  ```

- **Theo quý:**
  ```python
  finance = balance_sheet(symbol='HPG', time='quarters')
  ```

#### 3. Báo cáo kết quả hoạt động kinh doanh:
Truy vấn bảng kết quả hoạt động kinh doanh theo năm hoặc quý:
- **Theo năm:**
  ```python
  finance = income_statement(symbol='HPG', time='years')
  ```

- **Theo quý:**
  ```python
  finance = income_statement(symbol='HPG', time='quarters')
  ```

#### 4. Báo cáo lưu chuyển tiền tệ:
Truy vấn dữ liệu lưu chuyển tiền tệ theo năm hoặc quý:
- **Theo năm:**
  ```python
  finance = cash_flow(symbol='HPG', time='years')
  ```

- **Theo quý:**
  ```python
  finance = cash_flow(symbol='HPG', time='quarters')
  ```


## `Dữ liệu cổ đông` 
#### 1. Thông tin cổ đông:
Truy vấn danh sách các cổ đông của công ty cùng với lượng nắm giữ và phần trăm nắm giữ:
```python
shareholders = shareholders_info(symbol='HPG')
```

#### 2. Cấu trúc cổ đông:
Truy vấn cấu trúc cổ đông bao gồm số lượng cổ phiếu lưu hành, tỉ lệ nhà nước, tỉ lệ nước ngoài, tỉ lệ nhóm đối tượng khác,...:
```python
shareholders = shareholders_structure(symbol='HPG')
```

#### 3. Các công ty liên quan:
Truy vấn danh sách các công ty con và cty liên kết, bao gồm số lượng, tỉ lệ nắm giữ,... :
```python
shareholders = shareholders_relationship(symbol='HPG')
```

#### 4. Giao dịch nội bộ:
Truy vấn dữ liệu giao dịch của các thành viên hay tổ chức thuộc nội bộ công ty:
```python
shareholders = insider_trans(symbol='HPG')
```

## `Dữ liệu về chứng chỉ quỹ`
#### 1. Tổng quan danh sách các chứng chỉ quỹ:
Truy vấn thông tin của các chứng chỉ quỹ hiện có trên thị trường:
```python
funds = fund_market()
```

#### 2. Tăng trưởng tài sản ròng (NAV) của quỹ:
Truy vấn thông tin tăng trưởng của quỹ theo thời gian:
  ```python
  funds = NAV_grown(fund='BMFF',start='2020-01-25', end='2023-01-25')
  ```

Thay vì truy vấn bằng tên quỹ `fund='BMFF'` ta có thể thay bằng id tương ứng của quỹ trong danh sách quỹ `fund='87'`.

#### 3. Danh mục đầu tư lớn:
Truy vấn các danh mục đầu tư lớn của chứng chỉ quỹ:
  ```python
  funds = top_holding(fund='BMFF')
  ```

#### 4. Phân bổ quỹ theo tài sản nắm giữ:
Truy vấn danh sách tài sản quỹ đang nắm giữ (cổ phiếu, trái phiếu, tiền mặt,...):
  ```python
  funds = asset_holding(fund='BMFF')
  ```

#### 5. Phân bổ quỹ theo ngành:
Truy vấn danh sách tài sản quỹ đang nắm giữ thuộc ngành nào (ngân hàng, bất động sản, bán lẻ,...):
  ```python
  funds = indusstries_holding(fund='BMFF')
  ```

## `Dữ liệu chỉ số vĩ mô`
Truy vấn thông tin của các chỉ số vĩ mô trên thị trường theo mốc thời gian:
- **Theo Ngày:**
```python
macro_eco = macro_eco(indicator='GDP',time='days',start='2020-01-25', end='2023-03-31')
```
- **Theo Tháng:**
```python
macro_eco = macro_eco(indicator='GDP',time='months',start='2020-02', end='2023-03')
```
- **Theo Quý:**
```python
macro_eco = macro_eco(indicator='GDP',time='quarters',start='2020', end='2023')
```
- **Theo Năm:**
```python
macro_eco = macro_eco(indicator='GDP',time='years',start='2021', end='2024')
```

Thay vì truy vấn bằng tên chỉ số `indicator='GDP'` ta có thể thay bằng id tương ứng của chỉ số trong danh sách chỉ số `indicator='43'`.
Danh sách các chỉ số vĩ mô và ID tương ứng:
- `43`:`GDP`
- `52`:`CPI`
- `46`:`Sản xuất công nghiệp`
- `47`:`Bán lẻ`
- `48`:`Xuất nhập khẩu`
- `50`:`FDI`
- `51`:`Tín dụng`
- `53`:`Lãi suất`
- `55`:`Dân số và lao động`                

## Giấy phép
Thư viện này được phát hành theo giấy phép MIT. Vui lòng xem tệp LICENSE để biết thêm chi tiết.