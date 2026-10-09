# BnF OpsFit System — Project Context

## 1. Tổng quan

- **Tên:** BnF OpsFit System
- **Mục tiêu:** Chuẩn hóa dữ liệu vận hành F&B, tính hiệu quả tài chính món ăn, phân tích menu và hỗ trợ quyết định tối ưu vận hành.
- **Ngôn ngữ:** Python.
- **Backend dự kiến:** FastAPI.
- **Frontend dự kiến:** HTML, CSS và JavaScript thuần.
- **Dữ liệu đầu vào:** Workbook Excel tại `data/templates/BnF_Opsfit_System.xlsx`.

### Trạng thái hiện tại

Repo có Excel importer tại `backend/importers/excel_reader.py`, chuyển đổi đơn vị tại `backend/utils/unit_conversion.py`, công thức tài chính thuần tại `backend/services/formula.py`, workbook mẫu và module tối ưu một biến ban đầu tại `backend/services/optimal_profit_point.py`.

**Trạng thái: Phase 1 và luồng tính toán cơ bản của Phase 2 hoàn tất.** Workbook template có đủ sheet theo phạm vi; importer đọc và kiểm tra `costs`/`sales`, chuẩn hóa định phí và khấu hao về tháng, ánh xạ doanh số theo `food_id`, đồng thời ủy quyền quy đổi đơn vị cho `unit_conversion.py`. Các công thức tài chính và phân loại món dùng type hints; tính toán tiền/lãi góp dùng `Decimal`. `calculator.py` ghép dữ liệu importer với công thức, trả kết quả theo món và tổng hợp theo tháng. Kiểm thử importer, công thức, quy đổi đơn vị, phân loại menu và calculator nằm trong `tests/` với workbook fixture tại `data/tests/`.

## 2. Phân công và ranh giới trách nhiệm

Dự án có hai vai trò phát triển. Có thể một người kiêm nhiều vai trò, nhưng ranh giới module vẫn giữ như sau:

- **Dev 1 — Data Engineer & Fullstack:** đọc workbook hoặc dữ liệu UI, kiểm tra cấu trúc và giá trị đầu vào, chuẩn hóa đơn vị, cung cấp dữ liệu theo Data Contract, lưu trữ dữ liệu, xây dựng API và UI. Dev 1 không triển khai công thức tài chính.
- **Dev 2 — Core Engine & Analytics:** triển khai công thức tài chính, điểm hòa vốn, phân loại menu và tối ưu hóa. Dev 2 nhận dữ liệu đã chuẩn hóa theo Data Contract, không tự đọc workbook hoặc xử lý định dạng Excel.
- **Phối hợp:** Dev 2 đề xuất trường dữ liệu còn thiếu kèm ý nghĩa và kiểu dữ liệu; Dev 1 cập nhật importer/contract. Hai bên cùng thống nhất thay đổi contract trước khi đổi cấu trúc dữ liệu.

## 3. Kiến trúc và cấu trúc thư mục mục tiêu

```text
backend/
├── api/                         # FastAPI routes và request/response
├── importers/
│   └── excel_reader.py          # Đọc Excel và kiểm tra dữ liệu nguồn (Dev 1)
├── schemas/                     # Pydantic/API schemas và data models
├── services/
│   ├── formula.py               # Công thức tài chính và phân loại món (Dev 2)
│   ├── optimal_profit_point.py  # Tối ưu sản lượng theo lãi góp và công suất an toàn
│   ├── calculation_service.py   # Ghép contract đầu vào với công thức
│   └── calculator.py            # Entry point với hàm main
└── utils/
    └── unit_conversion.py       # Quy đổi đơn vị (Dev 1)
frontend/
├── css/
└── js/
tests/                           # Kiểm thử unit, integration và API
data/templates/BnF_Opsfit_System.xlsx
```

Không đặt công thức tài chính trong `importers/`. Importer chịu trách nhiệm đọc, kiểm tra cấu trúc và chuẩn hóa dữ liệu nguồn; service tài chính chỉ làm việc với dữ liệu theo contract.

### Dependencies

Các thư viện dự kiến: `openpyxl`, `pydantic`, `fastapi`, `scipy`. Chưa chốt phiên bản. Trước khi chạy ứng dụng, cần khai báo phiên bản tương thích trong file dependency của repo (ví dụ `requirements.txt` hoặc `pyproject.toml`) và cập nhật file này khi lựa chọn được chốt.

## 4. Workbook và Data Contract

### 4.1. Workbook

Workbook hiện có các sheet sau (tên sheet dạng chữ thường):

| Sheet | Vai trò | Trạng thái |
|---|---|---|
| `menu` | Mã món, tên, size, giá bán | Có trong workbook |
| `recipe` | Món, nguyên liệu, định lượng và đơn vị | Có trong workbook |
| `ingredients` | Giá gói, lượng trong gói, đơn vị và hao hụt | Có trong workbook |
| `units` | Nhóm đơn vị, đơn vị chuẩn, hệ số và alias | Có trong workbook |
| `costs` | Chi phí cố định/biến đổi và khấu hao | Có trong workbook |
| `sales` | Sản lượng bán theo món theo tháng | Có trong workbook |

Importer phải kiểm tra tên sheet/cột và báo lỗi có vị trí nguồn khi dữ liệu bắt buộc bị thiếu hoặc không hợp lệ. Tên hiển thị có thể chứa tiếng Việt; code ánh xạ về tên trường chuẩn bằng `snake_case`.

### 4.2. Contract chuẩn hóa

`excel_reader.py` cung cấp cấu trúc dữ liệu Python ổn định để service sử dụng. API có thể chuyển cấu trúc này sang JSON. Không để service phụ thuộc trực tiếp vào tên sheet hoặc vị trí cột Excel.

Contract cần mô tả tối thiểu các thực thể sau:

```text
menu_items:      food_id, food_name, food_size, food_price
recipes:         food_id, ingredient_id, ingredient_quantity, ingredient_unit
ingredients:     ingredient_id, ingredient_name, package_price,
                 package_quantity, package_unit, waste_rate
costs:           cost_id, cost_category, cost_name, cost_type, amount,
                 period_months, useful_life_months, allocation_method
sales:           item_code (ánh xạ food_id), quantity_sold_monthly
```

Quy tắc chuẩn hóa của importer:

- `cost_id` là khóa duy nhất, được nhập trong workbook.
- Chi phí thông thường cần `period_months > 0`; `monthly_amount = amount / period_months`.
- Khấu hao dùng `amount` làm nguyên giá và `useful_life_months > 0`; `monthly_amount = amount / useful_life_months`. Một dòng chỉ dùng `period_months` hoặc `useful_life_months`.
- `cost_type` nhận `FIXED` hoặc `VARIABLE`. Hai loại được giữ riêng; chi phí `VARIABLE` được chuẩn hóa tháng nhưng chưa phân bổ vào món.
- Lợi nhuận vận hành giai đoạn này trừ COGS và `FIXED` costs. `VARIABLE` costs đang được nhập/chuẩn hóa và báo riêng, chưa cộng vào lợi nhuận vì chưa có quy tắc phân bổ.
- `sales.item_code` phải khớp chính xác `food_id` trong menu; `quantity_sold_monthly` được cung cấp cho service dưới tên `quantity_sold`, kỳ `monthly`.
- Workbook template và workbook kiểm thử có header mã trường trong ngoặc; importer kiểm tra các trường bắt buộc và báo sheet/dòng khi dữ liệu không hợp lệ.

Workbook kiểm thử dùng `data/tests/BnF_Opsfit_Test_Data.xlsx`; các trường hợp dữ liệu lỗi được tạo thành workbook tạm trong quá trình chạy tests.

Kiểu dữ liệu kết quả của importer:

| Thực thể | Trường | Kiểu | Quy tắc |
|---|---|---|---|
| `costs` | `cost_id`, `cost_category`, `cost_name`, `cost_type`, `allocation_method` | `str` | `cost_id` duy nhất; `cost_type` là `FIXED` hoặc `VARIABLE` |
| `costs` | `amount`, `monthly_amount` | `float` | Không âm; `monthly_amount` là số tiền sau phân bổ tháng |
| `costs` | `period_months`, `useful_life_months` | `float \| None` | Chỉ một trường có giá trị trên mỗi dòng; trường có giá trị phải lớn hơn 0 |
| `sales` | `food_id`, `period` | `str` | `food_id` tồn tại trong menu; `period` hiện là `monthly` |
| `sales` | `quantity_sold` | `float` | Sản lượng tháng, hữu hạn và không âm |

Ví dụ kết quả đã chuẩn hóa:

```python
{"cost_id": "COST_RENT", "cost_type": "FIXED", "amount": 6000000,
 "period_months": 1, "useful_life_months": None, "monthly_amount": 6000000}
{"food_id": "COM_TAM_L", "period": "monthly", "quantity_sold": 1350}
```

Quy ước dữ liệu:

- Tên biến Python dùng `snake_case`; ID được chuẩn hóa nhất quán và không trùng.
- Số lượng phải hữu hạn và không âm; định lượng trong recipe phải lớn hơn 0.
- Giá tiền được tính bằng `Decimal`, không làm tròn trong các bước trung gian; khi hiển thị VND làm tròn half-up đến đồng gần nhất bằng `round_money`. Tỷ lệ được giữ nguyên trong phép tính và hiển thị 4 chữ số thập phân.
- `waste_rate` được chuẩn hóa về tỷ lệ từ `0` đến nhỏ hơn `1`; số lớn hơn `1` đến `100` được hiểu là phần trăm (ví dụ `10` thành `0.10`). Giá trị `1` biểu diễn 100% và bị từ chối; nhập tỷ lệ 1% bằng `0.01`.
- Đơn vị trong recipe phải cùng nhóm đo lường với đơn vị nguyên liệu và được đổi về đơn vị chuẩn trước khi tính cost.
- `unit_conversion.py` sở hữu kiểm tra tương thích và chuyển đổi số lượng/đơn vị; importer gọi helper này và chỉ đưa kết quả vào contract.
- Lỗi dữ liệu đầu vào thuộc trách nhiệm importer và phải chỉ rõ sheet, dòng, cột hoặc trường gây lỗi.

## 5. Quy tắc tính toán và phân tích

### 5.1. Công thức tài chính

Các công thức trong `backend/services/formula.py` là hàm nghiệp vụ thuần, có type hints và không đọc Excel. Công thức dự kiến gồm:

- **Số lượng sử dụng được:** `usable_quantity = package_quantity * (1 - waste_rate)`.
- **Giá vốn đơn vị chuẩn có tính hao hụt:** `effective_unit_cost = package_price / usable_quantity`.
- **Giá vốn một món:** tổng `ingredient_quantity * effective_unit_cost` trên các nguyên liệu của recipe.
- **Lãi góp một món:** `unit_margin = food_price - unit_cogs`.
- **Doanh thu:** tổng `quantity_sold * food_price`.
- **COGS:** tổng `quantity_sold * unit_cogs`.
- **Lãi góp:** `revenue - cogs`.
- **Lợi nhuận vận hành:** `contribution_margin - total_fixed_cost`.
- **Chi phí tháng:** chi phí phân bổ theo kỳ; khấu hao tháng dựa trên nguyên giá và thời gian sử dụng hữu ích.

Các hàm phải xác thực điều kiện toán học tối thiểu: mẫu số lớn hơn 0, `usable_quantity > 0`, tỷ lệ hao hụt hợp lệ, doanh thu khác 0 khi tính tỷ lệ margin/profit. Không tự quy ước kết quả cho trường hợp không xác định nếu chưa ghi trong contract.

### 5.2. Menu Engineering

Phân loại theo ma trận độ phổ biến và lãi góp (menu engineering), không gọi là ma trận BCG nếu không dùng đúng mô hình BCG.

- `avg_units_sold_per_item = total_units_sold / số món được đưa vào phân tích`.
- `avg_margin_per_unit = total_contribution_margin / total_units_sold`.
- **STAR:** sản lượng và lãi góp đơn vị đều lớn hơn hoặc bằng mốc.
- **PLOWHORSE:** sản lượng lớn hơn hoặc bằng mốc, lãi góp đơn vị thấp hơn mốc.
- **PUZZLE:** sản lượng thấp hơn mốc, lãi góp đơn vị lớn hơn hoặc bằng mốc.
- **DOG:** cả hai thấp hơn mốc.
- Các hàm ngưỡng và `menu_classification()` nằm cùng `backend/services/formula.py` với phần công thức được dùng chung. `menu_classification()` nhận sản lượng và lãi góp đơn vị theo cùng thứ tự món; ngưỡng lãi góp được tính bằng tổng lãi góp chia tổng sản lượng.
- So sánh bằng ngưỡng được tính là đạt (>=). Menu rỗng trả về danh sách rỗng; menu có món nhưng tổng sản lượng bằng 0 bị từ chối vì không xác định được ngưỡng lãi góp bình quân. Thiếu lãi góp cho bất kỳ món nào chưa được hỗ trợ; hai danh sách đầu vào phải khớp độ dài.

Phải quy định cách xử lý món không bán được, món thiếu giá vốn, kỳ không có doanh số và tập món dùng để tính trung bình. Insight là gợi ý cho người quản lý; không tự động xóa món hoặc thay đổi giá.

### 5.3. Tối ưu hóa lợi nhuận

SLSQP là phương án dự kiến cho bài toán có ràng buộc, cần chốt dữ liệu và giả định trước khi triển khai:

- Biến quyết định: `optimal_quantity[i]` cho từng món. Chốt xem kết quả là lượng liên tục hay số nguyên; SLSQP trả nghiệm liên tục nên cần quy tắc chuyển sang số lượng bán được.
- Mục tiêu: tối đa hóa `sum(quantity[i] * unit_margin[i]) - total_fixed_cost`. Vì định phí là hằng số, nó ảnh hưởng lợi nhuận báo cáo nhưng không tự thay đổi nghiệm tối ưu.
- Công suất: `sum(quantity[i] * prep_time[i]) <= 0.8 * peak_capacity`. Cần đơn vị thời gian, dữ liệu thời gian chế biến từng món và định nghĩa kỳ công suất.
- Nhu cầu: cần giới hạn hoặc mô hình cầu/giá cho từng món để nghiệm phản ánh khả năng bán thực tế.
- ICC: chỉ đưa vào khi xác định được biến lương, thưởng, nỗ lực tối thiểu, đơn vị đo và cách ràng buộc với sản lượng. Nếu chưa có dữ liệu này, để ngoài scope của optimizer ban đầu.
- Kết quả phải kiểm tra trạng thái hội tụ, tính khả thi của ràng buộc và báo lỗi/không khả thi rõ ràng.

#### Phiên bản khởi đầu: một món, một biến

Module `backend/services/optimal_profit_point.py` triển khai mô hình một biến theo yêu cầu hiện tại:

- `unit_net_margin = avg_food_price - avg_unit_cogs - staff_bonus_per_unit`.
- `profit(Q) = Q * unit_net_margin - total_fixed_cost`.
- Miền khả thi: `0 <= Q <= max_capacity_units * 0.8` mặc định.
- `is_within_safe_capacity` là hàm kiểm tra boolean cho kết quả; ràng buộc đưa vào SciPy phải trả về slack số học `safe_capacity_limit - Q` (không dùng boolean làm constraint cho solver).
- Module import trực tiếp `scipy.optimize.minimize` và dùng SLSQP; SciPy là dependency bắt buộc để nạp module và chạy optimizer. Với mô hình tuyến tính một biến, nghiệm kỳ vọng ở biên: nếu lãi góp sau thưởng dương thì chọn giới hạn công suất an toàn; nếu không dương thì chọn `Q = 0`. Solver vẫn được chạy và kiểm tra trạng thái hội tụ/ràng buộc.
- `staff_bonus_per_unit` hiện bị trừ trên **mọi** sản phẩm theo công thức đã yêu cầu. Nếu chỉ thưởng cho sản phẩm vượt điểm hòa vốn, cần thêm `break_even_quantity` và thay hàm mục tiêu thành piecewise trước khi đổi logic.
- Sản lượng được trả dạng số liên tục. Chưa có ràng buộc nhu cầu hoặc quy tắc làm tròn sang số ly nguyên; kết quả chỉ là baseline toán học theo công suất, không phải dự báo bán hàng.

## 6. Lộ trình và tiêu chí nghiệm thu

### Phase 1 — Data pipeline và nền tảng công thức (hoàn tất)

- Workbook có `costs`/`sales` và các trường phân bổ đã chốt.
- Importer kiểm tra sheet/cột, khóa và quan hệ món trong doanh số; chuẩn hóa đơn vị và chi phí về tháng.
- Data Contract, các kiểu trường, quy tắc phân bổ, tỷ lệ hao hụt và lỗi được ghi rõ ở trên.
- Công thức nền tảng có type hints, dùng `Decimal` cho tiền, kiểm tra mẫu số/tỷ lệ không hợp lệ.
- Kiểm thử importer và công thức chạy trên workbook fixture, gồm dữ liệu hợp lệ và các trường hợp dữ liệu sai/biên.
- Luồng mẫu từ template đến COGS, doanh thu, lãi góp và lợi nhuận vận hành đã được kiểm tra.

**Phase 1 hoàn tất. Phase 2 hoàn tất ở mức luồng tính toán cơ bản; xử lý lỗi ứng dụng và tích hợp API vẫn thuộc các phase sau.**

### Phase 2 — Calculator runner và luồng tính toán

- `backend/services/calculator.py` có hàm `calculate()` thuần nhận dữ liệu importer đã chuẩn hóa, gọi `formula.py` để tính COGS, doanh thu, lãi góp, lợi nhuận và phân loại menu.
- Định phí và biến phí tháng được tách riêng; lợi nhuận vận hành hiện trừ COGS và định phí theo contract.
- `main()` nạp contract từ `excel_reader`, in kết quả từng món và tổng hợp tháng; chạy từ thư mục gốc repo bằng `python -m backend.services.calculator`.
- Chưa bổ sung bắt lỗi ở calculator; validation đầu vào vẫn thuộc importer và validation công thức thuộc `formula.py`.

`calculation_service.py` sẽ được cân nhắc khi cần ghép contract với các công thức thành luồng ứng dụng.

### Phase 3 — Analytics

- Mở rộng menu engineering với insight; baseline phân loại STAR/PLOWHORSE/PUZZLE/DOG đã có trong `formula.py`.
- Hoàn thiện optimizer theo các giả định đã chốt.
- Kiểm tra ràng buộc, dữ liệu biên và trạng thái solver; trả lý do khi không có nghiệm phù hợp.

### Phase 4 — API và giao diện

- Xây FastAPI upload/validate/calculate endpoints và response schema.
- Xây UI để tải dữ liệu lên, xem lỗi, bảng kết quả, insight và biểu đồ.

### Phase 5 — Hoàn thiện và bàn giao

- Bổ sung kiểm thử end-to-end, xử lý lỗi, hướng dẫn cài đặt/chạy, ví dụ workbook và giới hạn của mô hình.
- Kiểm tra hiệu năng và solver theo kích thước dữ liệu thực tế; không coi “ngăn vòng lặp vô hạn” là tiêu chí duy nhất.

## 7. Từ điển biến số

| Biến | Ý nghĩa |
|---|---|
| `quantity_sold` | Số lượng bán thực tế của một món trong một kỳ |
| `unit_cogs` | Giá vốn một đơn vị món |
| `unit_margin` | Lãi góp đơn vị: giá bán trừ giá vốn |
| `total_units_sold` | Tổng sản lượng bán của tập món/kỳ đang phân tích |
| `total_contribution_margin` | Tổng lãi góp của tập món/kỳ |
| `total_fixed_cost` | Tổng định phí quy về kỳ phân tích |
| `avg_units_sold_per_item` | Mốc phổ biến trung bình của menu |
| `avg_margin_per_unit` | Mốc lãi góp đơn vị bình quân theo sản lượng |
| `break_even_revenue` | Doanh thu hòa vốn theo giả định đã nêu |
| `break_even_units` | Sản lượng hòa vốn; chỉ dùng trực tiếp khi giả định cơ cấu bán phù hợp |
| `optimal_quantity` | Sản lượng đề xuất từ optimizer |
| `prep_time` | Thời gian chế biến cần thiết cho một đơn vị món |
| `peak_capacity` | Công suất bếp trong kỳ, cùng đơn vị với tổng thời gian chế biến |
| `staff_bonus_per_unit` | Thưởng biến đổi theo đơn vị nếu ICC nằm trong scope |

## 8. Quy tắc code

1. Mọi hàm mới/cập nhật phải có type hints và tên biến `snake_case`.
2. Dùng `Decimal` cho tiền trong core calculations; chỉ chuyển kiểu ở ranh giới được quy định rõ.
3. Tách đọc/validate Excel khỏi logic tài chính. Không để `services` đọc workbook.
4. Thay đổi Data Contract phải cập nhật schema, ví dụ và tests liên quan.
5. Mỗi công thức nghiệp vụ cần có ví dụ số đầu vào/đầu ra đã xác nhận để đối chiếu.
6. Không đưa ra khuyến nghị vận hành có tác động lớn như xóa món chỉ dựa trên nhãn tự động; kết quả cần trình bày như gợi ý có giải thích.
