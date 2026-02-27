# 🌤 Weather MCP Server

> **Custom MCP Server** cung cấp dữ liệu thời tiết thực thời & lịch sử cho các AI Assistant (Claude, Cursor, VS Code Cline…) thông qua giao thức **Model Context Protocol (MCP)**.



---

## ✨ Tính năng

| # | Tool | Mô tả |
|---|------|--------|
| 1 | `geocode_city` | Tìm tọa độ (lat/lon) từ tên thành phố |
| 2 | `get_current_weather` | Thời tiết hiện tại theo tọa độ (nhiệt độ, độ ẩm, gió, áp suất, tầm nhìn…) |
| 3 | `get_forecast` | Dự báo thời tiết theo ngày, tối đa **7 ngày** |
| 4 | `get_weather_by_city` | Thời tiết hiện tại theo **tên thành phố** (tự động geocode, 1 bước) |
| 5 | `get_air_quality` | Chỉ số chất lượng không khí: PM2.5, PM10, CO, NO₂, O₃, SO₂, AQI châu Âu |
| 6 | `get_historical_weather` | Dữ liệu thời tiết lịch sử từ năm **1940 đến nay** |

---

## 🗂 Cấu trúc dự án

```
custom MCP server/
├── weather_server.py   # MCP Server chính (6 tools)
├── requirements.txt    # Các thư viện cần thiết
└── README.md
```

---

## 📋 Yêu cầu hệ thống

- **Python 3.10+**
- **pip**

---

## 🚀 Cài đặt

```powershell
# 1. Di chuyển vào thư mục dự án
cd "e:\TUYENDUNG\custom MCP server"

# 2. (Khuyến nghị) Tạo môi trường ảo
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Cài đặt dependencies
pip install -r requirements.txt
```

---

## 🧪 Chạy thử với MCP Inspector

```powershell
mcp dev weather_server.py
```

Trình duyệt sẽ tự mở tại `http://localhost:5173` — giao diện web để gọi thử từng tool trực tiếp.

---

## ⚙️ Tích hợp vào Claude Desktop

**1. Mở file cấu hình:**

| Hệ điều hành | Đường dẫn |
|--------------|-----------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

**2. Thêm vào mục `mcpServers`:**

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["e:\\TUYENDUNG\\custom MCP server\\weather_server.py"]
    }
  }
}
```

> **Nếu dùng môi trường ảo**, thay `"python"` bằng đường dẫn tuyệt đối:
> ```
> "e:\\TUYENDUNG\\custom MCP server\\.venv\\Scripts\\python.exe"
> ```

**3. Khởi động lại Claude Desktop** — server sẽ được load tự động.

---

## ⚙️ Tích hợp vào Cursor / VS Code (Cline)

Thêm vào file cấu hình MCP của extension:

```json
{
  "weather": {
    "command": "python",
    "args": ["e:\\TUYENDUNG\\custom MCP server\\weather_server.py"]
  }
}
```

---

## 📖 Hướng dẫn sử dụng từng Tool

### 🔍 1. `geocode_city` — Tìm tọa độ thành phố

Tìm vĩ độ (latitude) và kinh độ (longitude) từ tên thành phố.

```
geocode_city("Da Nang")
```

**Kết quả mẫu:**
```
Kết quả tìm kiếm cho 'Da Nang':
1. Đà Nẵng, Thành phố Đà Nẵng, Việt Nam
   📍 Tọa độ : lat=16.0544, lon=108.2022
   🏔  Độ cao  : 10 m
```

---

### 🌡 2. `get_current_weather` — Thời tiết hiện tại theo tọa độ

```
get_current_weather(latitude=16.0544, longitude=108.2022)
```

**Thông tin trả về:** Nhiệt độ, cảm giác thực, độ ẩm, lượng mưa, áp suất, tốc độ & hướng gió, gió giật, tầm nhìn, tình trạng trời.

---

### 📅 3. `get_forecast` — Dự báo thời tiết 1–7 ngày

```
get_forecast(latitude=16.0544, longitude=108.2022, days=3)
```

**Thông tin trả về theo từng ngày:** Nhiệt độ max/min, cảm giác thực, lượng mưa, xác suất mưa, gió max, giờ bình minh/hoàng hôn.

---

### 🏙 4. `get_weather_by_city` — Thời tiết nhanh theo tên thành phố

Gọi 1 bước, không cần tọa độ thủ công.

```
get_weather_by_city("Ho Chi Minh")
```

---

### 💨 5. `get_air_quality` — Chất lượng không khí

```
get_air_quality("Hanoi")
```

**Chỉ số trả về:** PM2.5, PM10, CO, NO₂, SO₂, O₃, bụi sa mạc, **AQI châu Âu** kèm đánh giá mức độ.

| AQI | Mức độ |
|-----|--------|
| 0–20 | 🟢 Rất tốt |
| 21–40 | 🟢 Tốt |
| 41–60 | 🟡 Trung bình |
| 61–80 | 🟠 Kém |
| 81–100 | 🔴 Xấu |
| > 100 | 🟣 Rất xấu |

---

### 📜 6. `get_historical_weather` — Thời tiết lịch sử

Dữ liệu từ **1940 đến nay**, khoảng cách khuyến nghị tối đa 31 ngày/lần gọi.

```
get_historical_weather(
    city_name="Hanoi",
    start_date="2024-01-01",
    end_date="2024-01-07"
)
```

**Thông tin trả về theo từng ngày:** Nhiệt độ max/min, lượng mưa, tốc độ & hướng gió, giờ bình minh/hoàng hôn, tình trạng thời tiết.

---

## 💡 Ví dụ thực tế (luồng đầy đủ)

```python
# Bước 1 — Tìm tọa độ Hà Nội
geocode_city("Ha Noi")
# → lat=21.0285, lon=105.8542

# Bước 2 — Xem thời tiết hiện tại
get_current_weather(21.0285, 105.8542)

# Bước 3 — Xem dự báo 3 ngày tới
get_forecast(21.0285, 105.8542, days=3)

# Hoặc gọn hơn (1 bước)
get_weather_by_city("Ha Noi")

# Chất lượng không khí
get_air_quality("Ha Noi")

# Thời tiết tuần trước
get_historical_weather("Ha Noi", "2024-12-01", "2024-12-07")
```

---

## 🗃 Nguồn dữ liệu

| API | Dùng cho |
|-----|----------|
| [Open-Meteo Forecast API](https://open-meteo.com/en/docs) | Thời tiết hiện tại & dự báo |
| [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) | Tìm tọa độ thành phố |
| [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) | Chất lượng không khí |
| [Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api) | Dữ liệu lịch sử từ 1940 |

Mã thời tiết tuân theo chuẩn **WMO (World Meteorological Organization)**.

---

## 📦 Dependencies

```
mcp[cli]>=1.0.0
httpx>=0.27.0
```
