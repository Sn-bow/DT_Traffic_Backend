# ITS 실시간 교통/돌발 API 응단을 표준 dict 형태로 바꾼다
from __future__ import annotations

from dataclasses import dataclass # 데이터를 저장하는 클래스를 쉽게 만들어주는 기능
from datetime import datetime
from typing import Any

import requests

from integrations.env import get_env, get_int_env

ITS_TRAFFIC_URL = "https://openapi.its.go.kr:9443/trafficInfo"
ITS_EVENT_URL = "https://openapi.its.go.kr:9443/eventInfo"

class ApiClientError(RuntimeError):
    pass

def _first(item: dict[str,Any], *keys: str) -> Any:
    for key in keys:
        if key in item and item[key] not in {None, ""}:
            return item[key]
    return None

def _to_float(value: Any) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def _parse_created_date(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d %H%M%S"):
        try:
            return datetime.strptime(text, fmt).isoformat()
        except ValueError:
            continue
    return text or None

def extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]: # 실제 데이터가 어디 있는지 찾아주는 함수
    """Extract item rows from common public-data response shapes."""
    candidates: list[Any] = []

    response = payload.get("response")

    if isinstance(response, dict):
        body = response.get("body")
        if isinstance(body, dict):
            candidates.extend([body.get("items"), body.get("item"), body.get("data")])

    body = payload.get("body")
    if isinstance(body, dict):
        candidates.extend([body.get("items"), body.get("item"), body.get("data")])

    candidates.extend(
        [
            payload.get("items"),
            payload.get("item"),
            payload.get("data")
        ]
    )

    for candidate in candidates:
        if candidate is None:
            continue
        if isinstance(candidate, dict) and "item" in candidate:
            candidate = candidate["item"]
        if isinstance(candidate, dict):
            return [candidate]
        if isinstance(candidate, list):
            return [row for row in candidate if isinstance(row, dict)]

    return []

@dataclass(frozen=True)
class BoundingBox:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

class ItsTrafficClient:
    def __init__(self, api_key: str | None = None, timeout: int | None = None, session: requests.Session | None = None, base_url: str | None = None):
        self.api_key = api_key or get_env("ITS_API_KEY" , required = True)
        self.timeout = timeout or get_int_env("API_TIMEOUT_SECONDS", 10)
        self.session = session or requests.Session()
        self.base_url = base_url or get_env("ITS_TRAFFIC_URL", ITS_TRAFFIC_URL) or ITS_TRAFFIC_URL

    def fetch_realtime_traffic(self, road_type: str = "all", route_no: str | None = None, direction_type: str = "all", bbox: BoundingBox | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "apiKey" : self.api_key,
            "type" : road_type,
            "drcType" : direction_type,
            "getType" : "json"
        }
        if route_no:
            params["routeNo"] = route_no
        if bbox:
            params.update(
                {
                    "minX" : bbox.min_x,
                    "maxX" : bbox.max_x,
                    "minY" : bbox.min_y,
                    "maxY" : bbox.max_y
                }
            )

        try:
            response = self.session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequesstException as exc:
            raise ApiClientError(f"ITS traffic API request failed: {exc.__class__.__name__}") from None

        #####