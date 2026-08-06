# BnF OpsFit System

BnF OpsFit là đồ án quản lý và phân tích dữ liệu vận hành F&B.

## Công nghệ dự kiến

- Backend: Python
- Frontend: HTML, CSS và JavaScript
- Dữ liệu đầu vào: Excel
- Môi trường chạy: Docker

Repository hiện có cấu trúc khởi tạo cho backend, frontend, kiểm thử,
file Excel mẫu và trình đọc dữ liệu Excel.

## Cấu trúc

```text
backend/
├── api/                       API backend
├── importers/
│   └── excel_reader.py        Đọc và kiểm tra dữ liệu Excel
├── schemas/                   Cấu trúc dữ liệu
├── services/                  Nghiệp vụ ứng dụng
└── utils/                     Tiện ích dùng chung
data/
└── templates/
    └── BnF_Opsfit_System.xlsx File Excel mẫu
frontend/
├── css/                       Giao diện
└── js/                        Xử lý phía trình duyệt
tests/                         Kiểm thử
```
