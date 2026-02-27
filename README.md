# Weather MCP Server 🌤

Custom MCP server đọc dữ liệu thời tiết thực thời sử dụng **Open-Meteo API** — miễn phí, không cần API key.

## Tính năng

| Tool | Mô tả |
|------|-------|
| `geocode_city` | Tìm tọa độ (lat/lon) từ tên thành phố |
| `get_current_weather` | Thời tiết hiện tại (nhiệt độ, độ ẩm, gió, áp suất, tầm nhìn, v.v.) |
| `get_forecast` | Dự báo thời tiết tối đa 7 ngày |

## Yêu cầu

- Python **3.10+**
- pip

## Cài đặt

```powershell
# 1. Di chuyển vào thư mục dự án
cd "e:\TUYENDUNG\custom MCP server"

# 2. (Tuỳ chọn) Tạo môi trường ảo
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Cài dependencies
pip install -r requirements.txt
```

## Chạy thử với MCP Inspector

```powershell
mcp dev weather_server.py
```

Trình duyệt sẽ tự mở tại `http://localhost:5173` — gọi thử từng tool trong giao diện web.

## Tích hợp vào Claude Desktop

Mở file cấu hình Claude Desktop:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Thêm vào mục `mcpServers`:

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

> **Lưu ý**: Nếu dùng môi trường ảo, thay `python` bằng đường dẫn tuyệt đối tới `.venv\Scripts\python.exe`.

## Tích hợp vào Cursor / VS Code (Cline)

Thêm vào cấu hình MCP của extension:

```json
{
  "weather": {
    "command": "python",
    "args": ["e:\\TUYENDUNG\\custom MCP server\\weather_server.py"]
  }
}
```

## Ví dụ sử dụng

```
# Bước 1: Tìm tọa độ Hà Nội
geocode_city("Ha Noi")
→ lat=21.0285, lon=105.8542

# Bước 2: Lấy thời tiết hiện tại
get_current_weather(21.0285, 105.8542)

# Bước 3: Xem dự báo 3 ngày
get_forecast(21.0285, 105.8542, days=3)
```

## Nguồn dữ liệu

- **Thời tiết & dự báo**: [Open-Meteo Forecast API](https://open-meteo.com/)
- **Tìm tọa độ thành phố**: [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api)
- Mã thời tiết theo chuẩn **WMO (World Meteorological Organization)**
