#  .env를 읽고 문자열/정수/프로젝트 경로를 반환하는 공통 helper

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv # .env 를 환경변수에 등록해주는 method

PROJECT_ROOT = Path(__file__).resolve().parent[1]
load_dotenv(PROJECT_ROOT / ".env")


def get_env(name:str, default:str | None = None, required: bool = False) -> str | None :
    value = os.getenv(name, default)
    
    if required and (value is None or not value.strip()): # required 필수이면서 (True) value 값이 없을 경우 에러 띄워주기 
        raise RuntimeError(f"필수 환경 변수가 누락되었습니다: {name}")
    return value

def get_int_env(name: str, defalut: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip(): # 원시 값이 비어있거나 없을경우 default로 반환
        return defalut
    return int(raw)

def resolve_project_path(path:str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else PROJECT_ROOT / value # value 가 절대 경로인경우 바로 value 값 반환 아니면 PROJECT_ROOT 경로  + value 상대경로 반환