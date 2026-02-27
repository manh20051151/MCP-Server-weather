"""
Weather MCP Server
------------------
Custom MCP server đọc dữ liệu thời tiết thực thời từ Open-Meteo API.
- Miễn phí, không cần API key
- Hỗ trợ giao thức stdio (tích hợp Claude Desktop, Cursor, v.v.)

Các tool cung cấp:
  - geocode_city       : Tìm tọa độ (lat/lon) từ tên thành phố
  - get_current_weather: Thời tiết hiện tại tại tọa độ cho trước
  - get_forecast       : Dự báo thời tiết tối đa 7 ngày
"""

import httpx
from mcp.server.fastmcp import FastMCP

# ─── Khởi tạo MCP server ───────────────────────────────────────────────────
mcp = FastMCP(
    name="weather",
    instructions=(
        "Server thời tiết sử dụng Open-Meteo API (miễn phí, không cần API key). "
        "Dùng geocode_city để tìm tọa độ thành phố trước, sau đó truyền lat/lon "
        "vào get_current_weather hoặc get_forecast."
    ),
)

# ─── Bảng mô tả mã thời tiết WMO ───────────────────────────────────────────
WEATHER_CODES: dict[int, str] = {
    0: "Trời quang (Clear sky)",
    1: "Phần lớn quang (Mainly clear)",
    2: "Có mây rải rác (Partly cloudy)",
    3: "Nhiều mây (Overcast)",
    45: "Sương mù (Fog)",
    48: "Sương mù đóng băng (Depositing rime fog)",
    51: "Mưa phùn nhẹ (Light drizzle)",
    53: "Mưa phùn vừa (Moderate drizzle)",
    55: "Mưa phùn dày (Dense drizzle)",
    61: "Mưa nhẹ (Slight rain)",
    63: "Mưa vừa (Moderate rain)",
    65: "Mưa to (Heavy rain)",
    71: "Tuyết nhẹ (Slight snow)",
    73: "Tuyết vừa (Moderate snow)",
    75: "Tuyết dày (Heavy snow)",
    77: "Hạt tuyết nhỏ (Snow grains)",
    80: "Mưa rào nhẹ (Slight rain showers)",
    81: "Mưa rào vừa (Moderate rain showers)",
    82: "Mưa rào mạnh (Violent rain showers)",
    85: "Mưa tuyết nhẹ (Slight snow showers)",
    86: "Mưa tuyết nặng (Heavy snow showers)",
    95: "Dông (Thunderstorm)",
    96: "Dông kèm mưa đá nhẹ (Thunderstorm with slight hail)",
    99: "Dông kèm mưa đá to (Thunderstorm with heavy hail)",
}


def describe_weather_code(code: int) -> str:
    """Trả về mô tả thời tiết theo mã WMO."""
    return WEATHER_CODES.get(code, f"Không xác định (mã {code})")


def validate_coordinates(latitude: float, longitude: float) -> str | None:
    """
    Kiểm tra tính hợp lệ của tọa độ địa lý.
    Trả về None nếu hợp lệ, hoặc thông báo lỗi nếu không hợp lệ.
    """
    if not (-90 <= latitude <= 90):
        return (
            f"❌ Vĩ độ (latitude) không hợp lệ: {latitude}\n"
            f"   Vĩ độ phải nằm trong khoảng -90 đến 90.\n"
            f"   Ví dụ Hà Nội: latitude=21.0285 (không phải 210285 hay 21285)\n"
            f"   Gợi ý: Dùng geocode_city để lấy tọa độ chính xác."
        )
    if not (-180 <= longitude <= 180):
        return (
            f"❌ Kinh độ (longitude) không hợp lệ: {longitude}\n"
            f"   Kinh độ phải nằm trong khoảng -180 đến 180.\n"
            f"   Ví dụ Hà Nội: longitude=105.8542\n"
            f"   Gợi ý: Dùng geocode_city để lấy tọa độ chính xác."
        )
    return None


# ─── Tool 1: Tìm tọa độ thành phố ──────────────────────────────────────────
@mcp.tool()
async def geocode_city(city_name: str) -> str:
    """
    Tìm tọa độ địa lý (latitude, longitude) của một thành phố.

    Args:
        city_name: Tên thành phố (ví dụ: "Hanoi", "Ho Chi Minh", "Da Nang")

    Returns:
        Danh sách các địa điểm khớp với tên thành phố (tên đầy đủ, quốc gia, lat, lon).
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 5,
        "language": "vi",
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results")
    if not results:
        return f"Không tìm thấy địa điểm nào khớp với '{city_name}'."

    lines = [f"Kết quả tìm kiếm cho '{city_name}':\n"]
    for i, r in enumerate(results, 1):
        name = r.get("name", "N/A")
        country = r.get("country", "N/A")
        admin1 = r.get("admin1", "")
        lat = r.get("latitude", 0)
        lon = r.get("longitude", 0)
        elevation = r.get("elevation", "N/A")

        location_str = f"{name}"
        if admin1:
            location_str += f", {admin1}"
        location_str += f", {country}"

        lines.append(
            f"{i}. {location_str}\n"
            f"   📍 Tọa độ : lat={lat:.4f}, lon={lon:.4f}\n"
            f"   🏔  Độ cao  : {elevation} m\n"
        )

    return "\n".join(lines)


# ─── Tool 2: Thời tiết hiện tại ─────────────────────────────────────────────
@mcp.tool()
async def get_current_weather(latitude: float, longitude: float) -> str:
    """
    Lấy thông tin thời tiết hiện tại tại vị trí cho trước.

    Args:
        latitude : Vĩ độ (ví dụ: 21.0285 cho Hà Nội)
        longitude: Kinh độ (ví dụ: 105.8542 cho Hà Nội)

    Returns:
        Thông tin thời tiết hiện tại gồm: nhiệt độ, cảm giác thực, độ ẩm,
        tốc độ gió, hướng gió, áp suất, tầm nhìn, tình trạng trời.
    """
    err = validate_coordinates(latitude, longitude)
    if err:
        return err

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "weather_code",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "visibility",
        ],
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    cur = data.get("current", {})
    units = data.get("current_units", {})
    tz = data.get("timezone", "Unknown")
    time_str = cur.get("time", "N/A")

    temp = cur.get("temperature_2m", "N/A")
    feels = cur.get("apparent_temperature", "N/A")
    humidity = cur.get("relative_humidity_2m", "N/A")
    precip = cur.get("precipitation", 0)
    code = cur.get("weather_code", -1)
    pressure = cur.get("surface_pressure", "N/A")
    wind_speed = cur.get("wind_speed_10m", "N/A")
    wind_dir = cur.get("wind_direction_10m", "N/A")
    wind_gust = cur.get("wind_gusts_10m", "N/A")
    visibility = cur.get("visibility", "N/A")
    is_day = cur.get("is_day", 1)

    day_night = "☀️ Ban ngày" if is_day else "🌙 Ban đêm"
    weather_desc = describe_weather_code(code)

    # Chuyển hướng gió sang mô tả
    def wind_direction_label(deg) -> str:
        if deg is None:
            return "N/A"
        directions = ["Bắc", "Đông Bắc", "Đông", "Đông Nam",
                      "Nam", "Tây Nam", "Tây", "Tây Bắc"]
        idx = round(deg / 45) % 8
        return f"{directions[idx]} ({deg}°)"

    result = (
        f"🌤 Thời tiết hiện tại tại tọa độ ({latitude:.4f}, {longitude:.4f})\n"
        f"   🕐 Thời gian : {time_str} ({tz})\n"
        f"   {day_night}\n\n"
        f"   🌡  Nhiệt độ   : {temp}{units.get('temperature_2m', '°C')}\n"
        f"   🤔 Cảm giác   : {feels}{units.get('apparent_temperature', '°C')}\n"
        f"   💧 Độ ẩm      : {humidity}{units.get('relative_humidity_2m', '%')}\n"
        f"   🌧  Lượng mưa  : {precip}{units.get('precipitation', 'mm')}\n"
        f"   🔵 Áp suất    : {pressure}{units.get('surface_pressure', 'hPa')}\n"
        f"   💨 Tốc độ gió : {wind_speed}{units.get('wind_speed_10m', 'km/h')}\n"
        f"   🧭 Hướng gió  : {wind_direction_label(wind_dir)}\n"
        f"   🌪  Gió giật   : {wind_gust}{units.get('wind_gusts_10m', 'km/h')}\n"
        f"   👁  Tầm nhìn   : {visibility} m\n"
        f"   ☁️  Tình trạng : {weather_desc}\n"
    )
    return result


# ─── Tool 3: Dự báo thời tiết ───────────────────────────────────────────────
@mcp.tool()
async def get_forecast(latitude: float, longitude: float, days: int = 7) -> str:
    """
    Lấy dự báo thời tiết theo ngày trong tối đa 7 ngày tới.

    Args:
        latitude : Vĩ độ (ví dụ: 21.0285 cho Hà Nội)
        longitude: Kinh độ (ví dụ: 105.8542 cho Hà Nội)
        days     : Số ngày dự báo (1-7, mặc định: 7)

    Returns:
        Dự báo thời tiết từng ngày gồm: nhiệt độ max/min, lượng mưa,
        xác suất mưa, tốc độ gió max, tình trạng trời.
    """
    err = validate_coordinates(latitude, longitude)
    if err:
        return err

    days = max(1, min(days, 7))

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_direction_10m_dominant",
            "sunrise",
            "sunset",
        ],
        "forecast_days": days,
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data.get("daily", {})
    units = data.get("daily_units", {})
    tz = data.get("timezone", "Unknown")

    dates = daily.get("time", [])
    codes = daily.get("weather_code", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])
    feels_max = daily.get("apparent_temperature_max", [])
    feels_min = daily.get("apparent_temperature_min", [])
    precip_sum = daily.get("precipitation_sum", [])
    precip_prob = daily.get("precipitation_probability_max", [])
    wind_max = daily.get("wind_speed_10m_max", [])
    wind_dir = daily.get("wind_direction_10m_dominant", [])
    sunrises = daily.get("sunrise", [])
    sunsets = daily.get("sunset", [])

    lines = [
        f"📅 Dự báo thời tiết {days} ngày tại ({latitude:.4f}, {longitude:.4f})\n"
        f"   Múi giờ: {tz}\n"
        f"{'─' * 52}\n"
    ]

    for i in range(len(dates)):
        def _get(lst, idx, default="N/A"):
            return lst[idx] if idx < len(lst) else default

        date = _get(dates, i)
        code = _get(codes, i, -1)
        tmax = _get(temp_max, i)
        tmin = _get(temp_min, i)
        fmax = _get(feels_max, i)
        fmin = _get(feels_min, i)
        psum = _get(precip_sum, i)
        pprob = _get(precip_prob, i)
        wmax = _get(wind_max, i)
        wdir = _get(wind_dir, i)
        rise = _get(sunrises, i)
        sset = _get(sunsets, i)

        weather_desc = describe_weather_code(code)

        # Rút gọn thời gian mặt trời (chỉ giờ:phút)
        def short_time(dt_str: str) -> str:
            if "T" in str(dt_str):
                return str(dt_str).split("T")[1][:5]
            return str(dt_str)

        lines.append(
            f"📆 {date}\n"
            f"   ☁️  Tình trạng  : {weather_desc}\n"
            f"   🌡  Nhiệt độ    : {tmin}~{tmax}{units.get('temperature_2m_max', '°C')}"
            f"  (cảm giác {fmin}~{fmax}{units.get('apparent_temperature_max', '°C')})\n"
            f"   🌧  Mưa         : {psum}{units.get('precipitation_sum', 'mm')}"
            f"  (xác suất {pprob}%)\n"
            f"   💨 Gió max     : {wmax}{units.get('wind_speed_10m_max', 'km/h')}"
            f"  hướng {wdir}°\n"
            f"   🌅 Bình minh   : {short_time(rise)}  🌇 Hoàng hôn: {short_time(sset)}\n"
        )

    return "\n".join(lines)


# ─── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
