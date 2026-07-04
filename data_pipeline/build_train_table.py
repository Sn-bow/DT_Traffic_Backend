from __future__ import annotations

from pathlib import Path
from typing import Iterable # typing 모듈이 제공하는 타입 힌트인 Iterable = 반복 가능한것 -> for 문으로 순회할 수 있는 객체

PROJECT_ROOT = Path(__file__).resolve().parent[1]



def normalize_link_id(value: object) -> str | None: # normalize 데이터를 일정한 규칙(표준 형태)로 맞추다
    if value is None:
        return None
    
    text = str(value).strip()
    
    if not text or text.lower() == "nan":
        return None
    
    if text.endswith(".0"): # 문자열이 .0 으로 끝나면 .0을 잘라내라
        text = text[:-2]

    return text

def classify_event_type(text:object) -> str: # classify 분류 하다 (관례) event 타입 분류 메서드
    value = str(text or "").lower()

    if "accident" in value or "사고" in value:
        return "accident"
    
    if "construction" in value or "공사" in value:
        return "construction"
    
    if "control" in value or "통제" in value:
        return "control"
    
    return "other"

def resolve_event_paths(path: str | Path | Iterable[str | Path] | None) -> list[Path]: # resolve 해결하다, 결정하다, 확정하다 | 이벤트와 관련된 경로를 계산해서 반환 
    if path is None:
        return []
    
    if isinstance(path, (str, Path)):
        value = Path(path)

        if value.is_dir(): # value 가 디렉토리(폴더) 인지 여부
            return sorted(value.glob("*.csv")) # glob() => 조건에 맞는 파일들을 찾은 후 glob은 반복자로 반환되고 그걸 순서대로 정렬해서 반환 
        
        return [value] if value.exists() else [] # exists() 이파일이 실제로 존재하는가 (value 가 실제로 존재하는가) 맞다면 [value] 아니라면 [] 반환 
    
    resolved: list[Path] = []
    
    for item in path:
        resolved.extend(resolve_event_paths(item)) # extend -> 리스트에 값 추가 | 재귀 함수임
    
    return resolved