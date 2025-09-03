import os
import time
import jwt
from datetime import datetime, timedelta
from typing import Dict, Awaitable, Annotated, Literal, Any, Optional
from cryptography.hazmat.primitives import serialization

import httpx
from fastmcp import FastMCP
from pydantic import Field
import logging
import dotenv

# --- Configuration ---
# Find the directory of the current script to locate the .env file reliably.
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ENV_PATH = os.path.join(_CURRENT_DIR, '.env')
# We no longer load .env here. All configuration is driven by __main__.py
# dotenv.load_dotenv(dotenv_path=_ENV_PATH)

mcp = FastMCP("mcp_server_weather_cuhksz")

# 全局变量
_global_cache: Dict[str, Dict] = {}

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp_weather_server')

# The global mode and host variables are removed to prevent import-time snapshot issues.
# Each function will now fetch the latest configuration from the environment at runtime.

# Credentials for direct mode. In unified mode, these will be empty but are not used.
qweather_key_id = os.getenv("QWEATHER_KEY_ID")
qweather_project_id = os.getenv("QWEATHER_PROJECT_ID")
qweather_private_key = os.getenv("QWEATHER_PRIVATE_KEY")


def generate_jwt() -> str:
    """Generates a JWT for QWeather API authentication. Only used in direct API mode."""
    if not all([qweather_key_id, qweather_project_id, qweather_private_key]):
        # This check is primarily for direct mode. In unified mode, it will pass if creds are empty.
        # The logic calling this function is responsible for ensuring it's only called in direct mode.
        raise ValueError("QWeather credentials for direct mode are not fully configured.")

    payload = {
        'iat': int(time.time()) - 30,
        'exp': int(time.time()) + 900,  # 15 minutes expiration
        'sub': qweather_project_id
    }
    headers = {
        'kid': qweather_key_id,
        'alg': 'EdDSA'
    }

    try:
        private_key_obj = serialization.load_pem_private_key(
            qweather_private_key.encode('utf-8'),
            password=None
        )
        encoded_jwt = jwt.encode(payload, private_key_obj, algorithm='EdDSA', headers=headers)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error generating JWT: {e}")
        raise


async def _get_cached_or_fetch_async(cache_key: str, fetch_coro: Awaitable, ttl_seconds: int) -> str:
    """
    Retrieves data from cache if available and not expired, otherwise fetches it.
    """
    now = datetime.now()
    if cache_key in _global_cache:
        cached_item = _global_cache[cache_key]
        if now - cached_item['timestamp'] < timedelta(seconds=ttl_seconds):
            logger.info(f"Cache hit for key: {cache_key}")
            return cached_item['data']
        else:
            logger.info(f"Cache expired for key: {cache_key}")
    else:
        logger.info(f"Cache miss for key: {cache_key}")

    try:
        data = await fetch_coro
        _global_cache[cache_key] = {
            'data': data,
            'timestamp': now
        }
        return data
    except Exception as e:
        raise Exception(f"Error fetching data for {cache_key}: {str(e)}")


async def make_request(client: httpx.AsyncClient, url: str, params: dict, headers: dict = None) -> dict:
    response = await client.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data.get("code") != "200":
        raise Exception(f"API Error: {data.get('code')} - {data.get('message', 'Unknown error')}")
    return data

async def get_request_volume_stats(
    project: Optional[str] = None,
    credential: Optional[str] = None,
    cache_ttl: int = 300,
    include_raw: bool = False,
) -> Dict[str, Any]:
    """
    获取"最近24小时 API 请求量统计"（/metrics/v1/stats）。

    参数：
      - project:   可选，按项目ID过滤。与 credential 互斥。
      - credential:可选，按凭据ID过滤。与 project 互斥。
      - cache_ttl: 缓存秒数，默认 300。
      - include_raw: 返回结果中是否附带原始 JSON，默认 False。

    返回：
      返回字典结构：
        {
          "asOf": "...",
          "scope": "...",  # 查询范围描述
          "summary": {
            "total_success": int,
            "total_errors": int,
            "apis": {
              "<API名>": {
                "success_total": int,
                "error_total": int,
                "success_series": [int, ...],  # 最近24小时逐小时
                "error_series": [int, ...]
              },
              ...
            }
          },
          "raw": {...}  # include_raw=True 时提供
        }

    备注：
      - 该接口不返回 "code" 字段，因此不要用 make_request()。
      - 使用前需在控制台为凭据开通相应"指标和统计"权限。
    """
    # --- 校验互斥条件 ---
    if project and credential:
        raise ValueError("`project` 与 `credential` 互斥，不能同时指定。")

    # --- 组合缓存键 ---
    cache_key = f"metrics_stats::{project or ''}::{credential or ''}"

    async def _fetch():
        api_host = os.getenv("WEATHER_API_HOST")
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "mcp-server-weather/1.0",
        }
        if os.getenv("IS_UNIFIED_API", 'false').lower() != 'true':
            token = generate_jwt()
            headers["Authorization"] = f"Bearer {token}"
        
        params = {}
        if project:
            params["project"] = project
        if credential:
            params["credential"] = credential

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{api_host}/metrics/v1/stats", headers=headers, params=params)
            resp.raise_for_status()
            # 注意：本接口没有业务 code 字段
            return resp.json()

    # --- 读取缓存或抓取 ---
    data = await _get_cached_or_fetch_async(cache_key, _fetch(), ttl_seconds=cache_ttl)

    # --- 解析与汇总 ---
    as_of = data.get("asOf", "")
    success = data.get("success", []) or []
    errors = data.get("errors", []) or []

    def _to_map(items):
        # 形如 [{"api":"Weather","hours":[...]}, ...] -> { "Weather":[...], ... }
        out: Dict[str, list] = {}
        for it in items:
            api_name = it.get("api", "")
            if not api_name:
                continue
            out[api_name] = it.get("hours", []) or []
        return out

    succ_map = _to_map(success)
    err_map = _to_map(errors)
    api_names = sorted(set(succ_map.keys()) | set(err_map.keys()))

    apis_summary: Dict[str, Any] = {}
    total_success = 0
    total_errors = 0

    for api in api_names:
        s_series = [int(x) for x in succ_map.get(api, [])]
        e_series = [int(x) for x in err_map.get(api, [])]
        s_sum = sum(s_series)
        e_sum = sum(e_series)
        apis_summary[api] = {
            "success_total": s_sum,
            "error_total": e_sum,
            "success_series": s_series,
            "error_series": e_series,
        }
        total_success += s_sum
        total_errors += e_sum

    summary = {
        "total_success": total_success,
        "total_errors": total_errors,
        "apis": apis_summary,
    }

    # 确定查询范围描述
    scope = {
        "project": project,
        "credential": credential,
    }

    result: Dict[str, Any] = {
        "asOf": as_of,
        "scope": scope,
        "summary": summary
    }
    if include_raw:
        result["raw"] = data
    return result

async def get_finance_summary(
    cache_ttl: int = 300,      # 缓存有效期（秒）
    include_raw: bool = False  # 返回结果中是否附带原始 JSON
) -> Dict[str, Any]:
    """
    功能：调用 /finance/v1/summary 获取财务与计费汇总信息，返回结构化字典。
    依赖：全局可用的 generate_jwt()、_get_cached_or_fetch_async()、api_host。
    说明：该接口不返回业务 code 字段，因此不可复用 make_request()。
    返回示例键：
      {
        "asOf": "...",
        "currency": "CNY",
        "balance": -17.54,
        "accruedCharges": {...},
        "pendingBills": [...],
        "availableSavingsPlans": [...],
        "availableResourcePlans": [...],
        "totals": {
          "pendingBills": {
            "count": 2,
            "unpaid_count": 2,
            "totalAmount": 2535.1,
            "totalAmountDue": 2017.54,
            "overdue_count": 1
          }
        },
        "raw": {...}  # 当 include_raw=True 时
      }
    """

    # --- 组合缓存键 ---
    cache_key = "finance_summary"

    # --- 内部时间解析（兼容以 Z 结尾的 UTC 表示） ---
    def _parse_dt(s: Optional[str]) -> Optional[datetime]:
        if not s or not isinstance(s, str):
            return None
        try:
            if s.endswith("Z"):
                s = s.replace("Z", "+00:00")
            return datetime.fromisoformat(s)
        except Exception:
            return None

    async def _fetch():
        api_host = os.getenv("WEATHER_API_HOST")
        # 准备认证与请求头
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "mcp-server-weather/1.0",
        }
        if os.getenv("IS_UNIFIED_API", 'false').lower() != 'true':
            token = generate_jwt()
            headers["Authorization"] = f"Bearer {token}"
            
        # 发起请求（不使用 make_request，因为无 code 字段）
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{api_host}/finance/v1/summary", headers=headers)
            resp.raise_for_status()
            return resp.json()

    # --- 读取缓存或抓取并写缓存 ---
    data = await _get_cached_or_fetch_async(cache_key, _fetch(), ttl_seconds=cache_ttl)

    # --- 基础字段提取，保证缺省为合理空值 ---
    as_of = data.get("asOf", "")
    currency = data.get("currency", "")
    balance = data.get("balance", 0)
    accrued = data.get("accruedCharges", {}) or {}
    pending_bills = data.get("pendingBills", []) or []
    savings = data.get("availableSavingsPlans", []) or []
    resource_plans = data.get("availableResourcePlans", []) or []

    # --- 汇总统计（便于上层直接使用） ---
    total_amount_due = 0.0
    total_amount = 0.0
    unpaid_count = 0
    overdue_count = 0

    as_of_dt = _parse_dt(as_of)

    for b in pending_bills:
        # 金额字段容错为 0
        amt_due = float(b.get("amountDue", 0) or 0)
        amt_all = float(b.get("amount", 0) or 0)
        total_amount_due += amt_due
        total_amount += amt_all

        # 未支付计数
        status = (b.get("status") or "").lower()
        if status == "unpaid":
            unpaid_count += 1

        # 逾期判断（如果能解析 dueDate 且 asOf 可用）
        due_dt = _parse_dt(b.get("dueDate"))
        if as_of_dt and due_dt and due_dt < as_of_dt and status == "unpaid" and amt_due > 0:
            overdue_count += 1

    result: Dict[str, Any] = {
        "asOf": as_of,
        "currency": currency,
        "balance": balance,
        "accruedCharges": {
            "previousDay": float(accrued.get("previousDay", 0) or 0),
            "thisMonth": float(accrued.get("thisMonth", 0) or 0),
            "sinceLastBill": float(accrued.get("sinceLastBill", 0) or 0),
        },
        "pendingBills": pending_bills,
        "availableSavingsPlans": savings,
        "availableResourcePlans": resource_plans,
        "totals": {
            "pendingBills": {
                "count": len(pending_bills),
                "unpaid_count": unpaid_count,
                "totalAmount": total_amount,
                "totalAmountDue": total_amount_due,
                "overdue_count": overdue_count,
            }
        },
    }

    if include_raw:
        result["raw"] = data

    return result

@mcp.tool(
    description="调用和风天气城市搜索 /geo/v2/city/lookup，返回含 Location ID 的中文可读列表（包括行政区、国家、经纬度、时区等信息）；支持模糊搜索与行政区/国家过滤。注意⚠️: 在调用其他工具时必须先调用此工具获取Location ID。"
)
async def get_location_id(
    # 必填：城市名 / 'lon,lat' / LocationID / Adcode
    location: Annotated[str, Field(description="查询关键字（必须参数）：城市名称、'经度,纬度'、LocationID 或 Adcode （中国的“行政区划代码”），如 '北京' 或 '116.41,39.92' 或 '101010100'")],
    # 可选：上级行政区
    adm: Annotated[str | None, Field(description="上级行政区过滤（可选参数，默认不使用），如 'beijing' 或 '江西省'")] = None,
    # 可选：范围（ISO 3166 国家代码），注意外部参数名为 search_range，实际传给 API 的参数名为 range
    search_range: Annotated[str | None, Field(description="搜索范围（可选参数，默认不使用），ISO 3166 国家/地区代码，如 'cn'")] = None,
    # 可选：返回数量，限制在 [1, 20]
    number: Annotated[int, Field(ge=1, le=20, description="返回数量（可选参数，默认 1），取值 1-20")] = 1,
    # 仅允许 'zh' 或 'en'，默认 'zh'
    lang: Annotated[Literal['zh', 'en'], Field(description="多语言（可选参数，默认 'zh'），仅支持 'zh' 或 'en'")] = 'zh',
    # # 缓存 TTL 秒数
    # cache_ttl: Annotated[int, Field(ge=0, description="缓存有效期（秒），默认 3600")] = 3600,
) -> str:
    """
    功能：调用 /geo/v2/city/lookup，按接口规范组装查询参数，使用 JWT Bearer 认证发起请求，
          对返回业务 code 做校验，并将候选城市格式化为中文多行文本，便于复制 Location ID。

    说明：
    - 入参与说明均使用 Annotated[...] + Field(...) 描述（中文），便于生成参数 schema 与校验。
    - 启用了 gzip。
    - 使用全局缓存，缓存键包含所有会影响结果的参数。
    - 严格检查 HTTP 状态与业务 code='200'（依赖 make_request 函数的校验逻辑）。
    """

    # --- 入参基础校验（location 必填；number 范围已由 Field ge/le 约束；lang 由 Literal 约束） ---
    if not location or not isinstance(location, str):
        raise ValueError("location 为必填字符串。")

    # --- 组合缓存键（包含所有影响结果的参数） ---
    cache_key = f"geo_lookup::{location}::{adm or ''}::{search_range or ''}::{int(number)}::{lang}"

    async def _fetch():
        api_host = os.getenv("WEATHER_API_HOST")
        # 生成 JWT，并组装请求头（gzip + Bearer）
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "mcp-server-weather/1.0",
        }
        if os.getenv("IS_UNIFIED_API", 'false').lower() != 'true':
            token = generate_jwt()
            headers["Authorization"] = f"Bearer {token}"

        # 组装查询参数（range 参数名与 Python 内置重复，因此对外暴露为 search_range）
        params = {
            "location": location,
            "number": str(int(number)),  # 部分接口更偏好字符串，这里统一转为字符串
            "lang": lang,
        }
        if adm:
            params["adm"] = adm
        if search_range:
            params["range"] = search_range

        # 发起请求：make_request 内部会做状态与业务码校验，超时时间30秒
        async with httpx.AsyncClient(timeout=30.0) as client:
            result = await make_request(
                client,
                f"{api_host}/geo/v2/city/lookup",
                params,
                headers,
            )

        # 只返回 location 数组，格式化放到缓存之后
        return result.get("location", [])

    # --- 读取缓存或拉取并写入缓存 ---
    locations = await _get_cached_or_fetch_async(cache_key, _fetch(), ttl_seconds=36000)

    # --- 无结果提示 ---
    if not locations:
        return f"未找到与“{location}”匹配的城市结果。"

    # --- 格式化输出（中文，便于复制 ID） ---
    lines = []
    for i, item in enumerate(locations, 1):
        name = item.get("name", "")
        _id = item.get("id", "")
        adm1 = item.get("adm1", "")
        adm2 = item.get("adm2", "")
        country = item.get("country", "")
        lat = item.get("lat", "")
        lon = item.get("lon", "")
        tz = item.get("tz", "")
        utc = item.get("utcOffset", "")
        rank = item.get("rank", "")
        ttype = item.get("type", "")
        lines.append(f"index:{i}. 地区/城市名称:{name}｜地区/城市ID:{_id}｜地区/城市所属一级/上级行政区域:{adm1}/{adm2}\n"
                    f"地区/城市所属国家:{country}｜地区/城市经纬度: ({lat},{lon})｜城市/地区所属时区: {tz}({utc})\n"
                    f"地区/城市评分: {rank}｜地区/城市属性: {ttype}")

    header = (
        f"查询成功，共返回 {len(locations)} 条；"
        f"复制所需 Location ID 用于后续天气查询：\n"
    )
    return header + "\n".join(lines)

@mcp.tool(
    description="调用和风天气每日天气预报 /v7/weather/{days}，返回格式化列表（包括日期、白天/夜间、日出/日落、月出/月落、温度、风、降水、湿度/紫外线、能见度、气压、云量）；支持多语言与单位制。"
)
async def get_daily_weather(
    # 预报天数，仅允许 3d/7d/10d/15d/30d
    days: Annotated[
        Literal['3d', '7d', '10d', '15d', '30d'],
        Field(description="预报天数：'3d'|'7d'|'10d'|'15d'|'30d'")
    ],
    # 地理位置（LocationID 或 '经度,纬度'）
    location: Annotated[
        str,
        Field(description="位置参数：LocationID 或 'lon,lat'（十进制坐标），如 '101010100' 或 '116.41,39.92'")
    ],
    # 语言，仅支持中文或英文
    lang: Annotated[
        Literal['zh', 'en'],
        Field(description="多语言参数：'zh' 或 'en'；默认 'zh'")
    ] = 'zh',
    # 单位制，仅支持公制 m 或英制 i
    unit: Annotated[
        Literal['m', 'i'],
        Field(description="单位制：'m'（公制，默认）或 'i'（英制）")
    ] = 'm',
    # # 缓存有效期（秒）
    # cache_ttl: Annotated[
    #     int,
    #     Field(ge=0, description="缓存有效期（秒），默认 900")
    # ] = 900,
) -> str:
    """
    功能：调用 /v7/weather/{days} 获取未来 3~30 天逐日预报。
    行为：
      - 参数校验（days/lang/unit 采用 Literal 限定）
      - 使用 JWT Bearer 认证
      - 开启 gzip
      - 使用全局缓存（缓存键包含 days/location/lang/unit）
      - 业务 code == '200' 严格校验
      - 输出格式化多行文本，便于直接给终端用户查看或复制
    """

    # --- 组合缓存键 ---
    cache_key = f"daily::{days}::{location}::{lang}::{unit}"

    async def _fetch():
        api_host = os.getenv("WEATHER_API_HOST")
        # 生成 JWT 并设置请求头
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "mcp-server-weather/1.0",
        }
        if os.getenv("IS_UNIFIED_API", 'false').lower() != 'true':
            token = generate_jwt()
            headers["Authorization"] = f"Bearer {token}"

        # 组装查询参数
        params = {
            "location": location,
            "lang": lang,
            "unit": unit,
        }

        # 发起请求（HTTP/2 + gzip；失败由 make_request 抛出）
        async with httpx.AsyncClient(timeout=30.0) as client:
            result = await make_request(
                client,
                f"{api_host}/v7/weather/{days}",
                params,
                headers,
            )
        # 返回完整结果，便于后续格式化时使用 updateTime/fxLink/daily
        return result

    # --- 读取缓存或拉取并写缓存 ---
    result = await _get_cached_or_fetch_async(cache_key, _fetch(), ttl_seconds=36000)

    # --- 基本字段提取 ---
    daily = result.get("daily", []) or []
    update_time = result.get("updateTime", "")
    # fx_link = result.get("fxLink", "")

    if not daily:
        return f"未获取到“{location}”（{days}）的每日预报数据。"

    # --- 单位提示（仅用于友好展示；数值以接口返回为准） ---
    if unit == 'm':
        temp_unit = "°C"
        wind_unit = "km/h"
        precip_unit = "mm"
        vis_unit = "km"
        pressure_unit = "hPa"
        unit_hint = "公制"
    else:
        temp_unit = "°F"
        wind_unit = "mph"
        precip_unit = "in"
        vis_unit = "mi"
        pressure_unit = "inHg"
        unit_hint = "英制"

    # --- 逐日格式化 ---
    lines = []
    for d in daily:
        fx_date = d.get("fxDate", "")
        text_day = d.get("textDay", "")
        text_night = d.get("textNight", "")
        tmax = d.get("tempMax", "")
        tmin = d.get("tempMin", "")
        sunrise = d.get("sunrise", "")
        sunset = d.get("sunset", "")
        moonrise = d.get("moonrise", "")
        moonset = d.get("moonset", "")
        wind_dir_day = d.get("windDirDay", "")
        wind_speed_day = d.get("windSpeedDay", "")
        wind_scale_day = d.get("windScaleDay", "")
        wind_dir_night = d.get("windDirNight", "")
        wind_speed_night = d.get("windSpeedNight", "")
        wind_scale_night = d.get("windScaleNight", "")
        precip = d.get("precip", "")
        humidity = d.get("humidity", "")
        uv = d.get("uvIndex", "")
        pressure = d.get("pressure", "")
        vis = d.get("vis", "")
        cloud = d.get("cloud", "")

        # 结构：日期｜白天/夜间｜日出/日落｜月出/月落｜温度｜风｜降水｜湿度/紫外线｜能见度/气压｜云量｜
        lines.append(
            f"预报日期：{fx_date}｜白天天气状况预报: {text_day}｜夜间天气状况预报: {text_night}｜气温: {tmin}~{tmax}{temp_unit}｜"
            f"日出/日落时间: {sunrise}/{sunset}｜月出/月落时间: {moonrise}/{moonset}｜"
            f"白天风向: {wind_dir_day} 风速: {wind_speed_day}{wind_unit} 风力等级: {wind_scale_day}级｜夜间风向: {wind_dir_night} 风速: {wind_speed_night}{wind_unit} 风力等级: {wind_scale_night}级｜"
            f"当天总降水: {precip}{precip_unit}｜相对湿度: {humidity}%｜紫外线强度: {uv}｜"
            f"能见度: {vis}{vis_unit}｜气压: {pressure} {pressure_unit}｜云量: {cloud}｜"
        )

    header = []
    header.append(f"查询成功，数据更新时间：{update_time}；单位：{unit_hint}；接口：{days}")
    # if fx_link:
    #     header.append(f"参考页面：{fx_link}")

    return "\n".join(header) + "\n" + "\n".join(lines)

@mcp.tool(
    description="调用和风天气逐小时预报 /v7/weather/{hours}，返回格式化列表（包括时间、天气、温度、露点温度、风、湿度、降水、概率、气压、云量）；支持多语言与单位制。"
)
async def get_hourly_weather(
    # 预报小时数：仅允许 24h/72h/168h
    hours: Annotated[
        Literal['24h', '72h', '168h'],
        Field(description="预报小时数：'24h'|'72h'|'168h'")
    ],
    # 地理位置（LocationID 或 '经度,纬度'）
    location: Annotated[
        str,
        Field(description="位置参数：LocationID 或 'lon,lat'（十进制坐标），如 '101010100' 或 '116.41,39.92'")
    ],
    # 语言，仅支持中文或英文
    lang: Annotated[
        Literal['zh', 'en'],
        Field(description="多语言参数：'zh' 或 'en'；默认 'zh'")
    ] = 'zh',
    # 单位制，仅支持公制 m 或英制 i
    unit: Annotated[
        Literal['m', 'i'],
        Field(description="单位制：'m'（公制，默认）或 'i'（英制）")
    ] = 'm',
    # # 缓存有效期（秒）
    # cache_ttl: Annotated[
    #     int,
    #     Field(ge=0, description="缓存有效期（秒），默认 600")
    # ] = 600,
) -> str:
    """
    功能：调用 /v7/weather/{hours} 获取未来 24/72/168 小时逐小时预报。
    行为：
      - 参数校验（hours/lang/unit 采用 Literal 强约束）
      - 使用 JWT Bearer 认证
      - 启用 gzip
      - 使用全局缓存（缓存键包含 hours/location/lang/unit）
      - 严格校验业务 code == '200'（依赖 make_request）
      - 输出格式化多行文本，便于直接给终端用户查看或复制
    """

    # --- 组合缓存键 ---
    cache_key = f"hourly::{hours}::{location}::{lang}::{unit}"

    async def _fetch():
        api_host = os.getenv("WEATHER_API_HOST")
        # 生成 JWT 并设置请求头
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "mcp-server-weather/1.0",
        }
        if os.getenv("IS_UNIFIED_API", 'false').lower() != 'true':
            token = generate_jwt()
            headers["Authorization"] = f"Bearer {token}"

        # 组装查询参数
        params = {
            "location": location,
            "lang": lang,
            "unit": unit,
        }

        # 发起请求（gzip；失败由 make_request 抛出）
        async with httpx.AsyncClient(timeout=30.0) as client:
            result = await make_request(
                client,
                f"{api_host}/v7/weather/{hours}",
                params,
                headers,
            )
        # 返回完整结果，后续用于格式化输出
        return result

    # --- 读取缓存或拉取并写缓存 ---
    result = await _get_cached_or_fetch_async(cache_key, _fetch(), ttl_seconds=36000)

    # --- 提取核心字段 ---
    hourly = result.get("hourly", []) or []
    update_time = result.get("updateTime", "")
    # fx_link = result.get("fxLink", "")

    if not hourly:
        return f"未获取到“{location}”（{hours}）的逐小时预报数据。"

    # --- 单位提示（仅用于友好展示；数值以接口返回为准） ---
    if unit == 'm':
        temp_unit = "°C"
        wind_unit = "km/h"
        precip_unit = "mm"
        pressure_unit = "hPa"
        unit_hint = "公制"
    else:
        temp_unit = "°F"
        wind_unit = "mph"
        precip_unit = "in"
        pressure_unit = "inHg"
        unit_hint = "英制"

    # --- 百分号字段的安全格式化 ---
    def _pct(v):
        return f"{v}%" if (v is not None and v != "") else "—"

    # --- 逐小时格式化 ---
    lines = []
    for h in hourly:
        fx_time = h.get("fxTime", "")
        temp = h.get("temp", "")
        text = h.get("text", "")
        wind_dir = h.get("windDir", "")
        wind_speed = h.get("windSpeed", "")
        wind_scale = h.get("windScale", "")
        humidity = _pct(h.get("humidity", ""))
        pop = _pct(h.get("pop", ""))
        precip = h.get("precip", "")
        pressure = h.get("pressure", "")
        cloud = _pct(h.get("cloud", ""))
        dew = h.get("dew", "")

        # 结构：时间｜天气｜温度/露点｜风｜湿度/降水/概率｜气压/云量
        lines.append(
            f"预报时间: {fx_time}｜天气状况: {text}｜温度: {temp}{temp_unit}（露点温度: {dew}{temp_unit}）｜"
            f"风向: {wind_dir} 风速: {wind_speed}{wind_unit} 风力等级: {wind_scale}级｜"
            f"湿度: {humidity}｜当前小时累计降水量: {precip}{precip_unit}｜逐小时预报降水概率: {pop}｜"
            f"气压: {pressure} {pressure_unit}｜云量: {cloud}"
        )

    header = []
    header.append(f"查询成功，数据更新时间：{update_time}；单位：{unit_hint}；接口：{hours}")
    # if fx_link:
    #     header.append(f"参考页面：{fx_link}")

    return "\n".join(header) + "\n" + "\n".join(lines)


@mcp.tool(
    description="调用和风天气灾害预警 /v7/warning/now，返回格式化的实时预警信息（包括标题、严重等级/颜色、状态、时间段、发布单位、类型、紧迫/确定性、正文、关联预警、唯一标识）；支持多语言设置。"
)
async def get_weather_warning_now(
    # 位置：LocationID 或 '经度,纬度'
    location: Annotated[
        str,
        Field(description="位置参数：LocationID 或 'lon,lat'（十进制），如 '101010100' 或 '116.41,39.92'")
    ],
    # 语言：仅支持 zh 或 en
    lang: Annotated[
        Literal['zh', 'en'],
        Field(description="多语言参数：'zh' 或 'en'；默认 'zh'")
    ] = 'zh',
    # 缓存：秒
    cache_ttl: Annotated[
        int,
        Field(ge=0, description="缓存有效期（秒），默认 180")
    ] = 180,
) -> str:
    """
    功能：调用 /v7/warning/now 获取实时气象灾害预警。
    行为：
      - 使用 Annotated+Field 进行参数描述与校验（中文）
      - 使用 JWT Bearer 认证
      - 启用 gzip
      - 利用全局缓存（键包含 location/lang）
      - 严格校验业务 code == '200'（依赖 make_request）
      - 将预警列表格式化为格式化多行文本；若无预警，返回友好提示
    """

    # --- 组合缓存键 ---
    cache_key = f"warning_now::{location}::{lang}"

    async def _fetch():
        api_host = os.getenv("WEATHER_API_HOST")
        # 生成 JWT 并设置请求头
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "mcp-server-weather/1.0",
        }
        if os.getenv("IS_UNIFIED_API", 'false').lower() != 'true':
            token = generate_jwt()
            headers["Authorization"] = f"Bearer {token}"

        # 组装查询参数
        params = {
            "location": location,
            "lang": lang,
        }

        # 发起请求：gzip；HTTP/状态码/业务码校验在 make_request 内完成
        async with httpx.AsyncClient(timeout=30.0) as client:
            result = await make_request(
                client,
                f"{api_host}/v7/warning/now",
                params,
                headers,
            )
        return result

    # --- 读取缓存或抓取并写缓存 ---
    result = await _get_cached_or_fetch_async(cache_key, _fetch(), ttl_seconds=36000)

    # --- 提取核心字段 ---
    warnings = result.get("warning", []) or []
    update_time = result.get("updateTime", "")
    # fx_link = result.get("fxLink", "")

    # --- 无预警场景 ---
    if not warnings:
        header = f"查询成功，数据更新时间：{update_time}。当前地区无气象灾害预警。"
        # if fx_link:
        #     header += f"\n参考页面：{fx_link}"
        return header

    # --- 逐条格式化 ---
    lines = []
    for i, w in enumerate(warnings, 1):
        wid = w.get("id", "")
        sender = w.get("sender", "") or "—"
        pub_time = w.get("pubTime", "") or "—"
        title = w.get("title", "") or "—"
        start_time = w.get("startTime", "") or "—"
        end_time = w.get("endTime", "") or "—"
        status = w.get("status", "") or "—"
        severity = w.get("severity", "") or "—"
        severity_color = w.get("severityColor", "") or "—"
        wtype_name = w.get("typeName", "") or "—"
        wtype = w.get("type", "") or "—"
        urgency = w.get("urgency", "") or "—"
        certainty = w.get("certainty", "") or "—"
        text = w.get("text", "") or "—"
        related = w.get("related", "") or "—"

        # 展示结构：标题｜严重等级/颜色｜状态｜时间段｜发布单位｜类型｜紧迫/确定性｜正文｜关联ID｜唯一标识
        lines.append(
            f"index: {i}｜标题: {title}｜"
            f"严重等级/颜色: {severity}/{severity_color}｜状态: {status}｜"
            f"时间: {start_time} ～ {end_time}（发布时间: {pub_time}｜"
            f"发布单位: {sender}｜"
            f"类型: {wtype_name}（ID: {wtype}）｜紧迫: {urgency}｜确定性: {certainty}｜"
            f"内容: {text}｜"
            f"关联预警: {related}｜"
            f"唯一标识: {wid}"
        )

    header = [f"查询成功，数据更新时间：{update_time}。共 {len(warnings)} 条预警。"]
    # if fx_link:
    #     header.append(f"参考页面：{fx_link}")

    return "\n".join(header) + "\n" + "\n\n".join(lines)

@mcp.tool(
    description="调用和风天气生活指数 /v7/indices/{days}，内部固定 type=0（获取全部指数），返回格式化列表（包括日期、名称、类型、等级、级别、建议）。"
)
async def get_weather_indices(
    # 预报天数：仅允许 1d/3d
    days: Annotated[
        Literal['1d', '3d'],
        Field(description="预报天数：'1d'（1天）或 '3d'（3天）")
    ],
    # 地理位置（LocationID 或 '经度,纬度'）
    location: Annotated[
        str,
        Field(description="位置参数：LocationID 或 'lon,lat'（十进制），如北京可以使用 '101010100' 或 '116.41,39.92'")
    ],
    # 语言，仅支持中文或英文
    lang: Annotated[
        Literal['zh', 'en'],
        Field(description="多语言参数：'zh' 或 'en'；默认 'zh'")
    ] = 'zh',
    # # 缓存有效期（秒）
    # cache_ttl: Annotated[
    #     int,
    #     Field(ge=0, description="缓存有效期（秒），默认 600")
    # ] = 600,
) -> str:
    """
    功能：调用 /v7/indices/{days} 获取生活指数预报；不暴露 type，内部固定为 type=0（获取该地点支持的全部指数）。
    行为：
      - 使用 Annotated+Field（中文）描述与校验；days/lang 为 Literal 强约束。
      - 使用 JWT Bearer 认证；启用 gzip 与 HTTP/2（若对端不支持会自动回退）。
      - 使用全局缓存（键包含 days/location/lang）。
      - 依赖 make_request 严格校验业务 code == '200'。
      - 输出中文多行文本：日期、名称、等级/级别、详细建议；无数据给出友好提示。

    说明：
      - 按和风天气规则，type=0 表示“拉取全部指数类型”，不同国家/地区可用指数集合可能不同。
      - 各项指数并非适用于所有城市，返回为空属于正常情况。
    """

    # --- 组合缓存键 ---
    cache_key = f"indices::{days}::{location}::{lang}"

    async def _fetch():
        api_host = os.getenv("WEATHER_API_HOST")
        # 生成 JWT 并设置请求头
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "mcp-server-weather/1.0",
        }
        if os.getenv("IS_UNIFIED_API", 'false').lower() != 'true':
            token = generate_jwt()
            headers["Authorization"] = f"Bearer {token}"

        # 组装查询参数：固定 type=0 以获取全部指数类型
        params = {
            "location": location,
            "type": "0",   # 关键：不暴露给调用方；内部固定为 0（全部指数）
            "lang": lang,
        }

        # 发起请求 + gzip；HTTP/状态码/业务码校验在 make_request 内完成
        async with httpx.AsyncClient(timeout=30.0) as client:
            result = await make_request(
                client,
                f"{api_host}/v7/indices/{days}",
                params,
                headers,
            )
        return result

    # --- 读取缓存或抓取并写缓存 ---
    result = await _get_cached_or_fetch_async(cache_key, _fetch(), ttl_seconds=36000)

    # --- 提取核心字段 ---
    daily = result.get("daily", []) or []
    update_time = result.get("updateTime", "")
    # fx_link = result.get("fxLink", "")

    # --- 无数据场景 ---
    if not daily:
        header = f"查询成功（code=200），数据更新时间：{update_time}。当前地区暂无可用的生活指数。"
        # if fx_link:
        #     header += f"\n参考页面：{fx_link}"
        return header

    # --- 逐条格式化 ---
    lines = []
    for i, it in enumerate(daily, 1):
        date = it.get("date", "") or "—"
        name = it.get("name", "") or "—"
        type_id = it.get("type", "") or "—"
        level = it.get("level", "") or "—"
        category = it.get("category", "") or "—"
        text = it.get("text", "") or "—"

        # 展示：日期｜名称（type）｜等级/级别｜建议
        lines.append(
            f"index:{i}｜日期: {date}｜名称: {name}（type: {type_id}）｜等级: {level}｜级别: {category}｜"
            f"建议: {text}"
        )

    header = [f"查询成功，数据更新时间：{update_time}；接口：{days}；共 {len(daily)} 条。"]
    # if fx_link:
    #     header.append(f"参考页面：{fx_link}")

    return "\n".join(header) + "\n" + "\n\n".join(lines)
