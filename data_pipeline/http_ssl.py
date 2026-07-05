from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests # python에서 HTTP 요청을 보내는 라이브러리 requests.get("https://www.naver.com") = response | requests.Session() = session => session.get,session.get,session.get,... 계속 연결

from data_pipeline.build_train_table import PROJECT_ROOT

# ssl_verify → SSL 인증서 검증 설정 / SSL 인증서 검증 설정을 최종적으로 결정하는 함수
def resolve_ssl_verify(ca_bundle: str | Path | bool | None = None, no_ssl_verify: bool = False) -> str | bool | None:
    # 사용할 CA 인증서 파일 ca_bundle : 상대방의 신원을 검증하기 위해서 사용하는 파일 | SSL 검증을 끌 것인가? 의 여부 no_ssl_verify = False 가 검증을 하겠다는 뜻임
    if no_ssl_verify:
        return False
    
    if isinstance(ca_bundle, bool) :
        return ca_bundle
    
    if ca_bundle:
        return _resolve_ca_path(ca_bundle) # ca_bundle 가 경로나 str 경로일 경우 절대 경로로 반환 
    
    env_value = os.getenv("DT_TRAFFIC_CA_BUNDLE") or os.getenv("REQUESTS_CA_BUNDLE") or os.getenv("CURL_CA_BUNDLE")

    if env_value:
        return _resolve_ca_path(env_value) # .env에서 인증서 경로가 있을경우 절대 경로로 변환 
    
    return None # 인증서 없을경우 None 반환 

def apply_ssl_verify(session: Any, verify: str | bool | None) -> None: # SSL 검증설정을 적용하는 함수
    if verify is not None and hasattr(session, "verify"):
        session.verify = verify


def ssl_error_message(url: str, error: BaseException, verify: str | bool | None) -> str:
    if verify is None:
        verify_text = "requests default"
    elif verify is False:
        verify_text = "disabled"
    else:
        verify_text = str(verify)

    
    return (
        "ITS HTTPS 인증서 검증에 실패했습니다.\n\n"
        f"요청 URL: {url}\n"
        f"오류 내용: {error}\n\n"
        "이 문제는 일반적으로 Windows/Python의 인증서 신뢰 저장소(Trust Store) 문제이거나, "
        "HTTPS 인증서를 교체하는 네트워크 프록시 환경에서 발생합니다.\n\n"
        "교통/이벤트 ZIP 파일을 수집하기 전에 반드시 이 문제를 해결하세요.\n\n"
        "권장 해결 방법:\n"
        "1. `python -m pip install --upgrade certifi` 명령으로 certifi를 최신 버전으로 업데이트합니다.\n"
        "2. 신뢰할 수 있는 CA 인증서(PEM 파일)를 사용하는 경우 다음과 같이 지정합니다.\n"
        "   - `--ca-bundle C:\\path\\to\\ca-bundle.pem`\n"
        "   - 또는 PowerShell에서\n"
        "     `$env:REQUESTS_CA_BUNDLE='C:\\path\\to\\ca-bundle.pem'`\n"
        "3. `--no-ssl-verify` 옵션은 신뢰할 수 있는 네트워크에서만 "
        "임시로 사용하는 최후의 수단으로 사용하세요.\n\n"
        f"현재 SSL 인증서 검증 설정: {verify_text}"
    )

# SSL 진단 기능이 포함된 HTTP 요청 함수 | method -> Http method ex) GET, POST | URL 요청할 주소 |
# 파라미터에서 * 이후 작성되는 파라미터 값을 전달할때는 이름을 무조건 작성 후 전달해야한다 session, "get", "https://' *이후 timeout = 30, verify=True
# *kwargs = 추가 옵션을 모두 받는다 => headers = , json= , params = ...
def request_with_ssl_diagnostics(session: requests.Session, method: str, url: str, *, timeout: int, verify:str | bool | None, **kwargs: Any) -> requests.Response:
    try: #HTTP 요청을 보내고, SSL 인증서 오류가 발생하면 사용자가 이해하기 쉬운 RuntimeError로 변환 해서 알려주는 함수
        if verify is None: # verify 는 SSL 인증서를 검증(확인)할 것인가 에 대한 여부를 체크 하는 변수 => True = 체크할 것이다, False => 체크 안할것이다
            return session.request(method, url, timeout=timeout, **kwargs)
        return session.request(method, url, timeout=timeout, verify=verify, **kwargs)
    except requests.exceptions.SSLError as exc: #SSL 인증서가 잘못 되었을때 나타나는 에러
        raise RuntimeError(ssl_error_message(url, exc, verify)) from exc # RunTimeError 이르키기 ssl_error_message(url, exc, verify)) from exc
    
def warn_if_ssl_verification_disabled(verify: str | bool | None) -> None: # SSL 검증이 꺼져있으면 경고를 출력하는 함수
    if verify is False:
        print(
            "[경고] SSL 인증서 검증이 비활성화되어 있습니다. "
            "이 옵션은 신뢰할 수 있는 네트워크에서만 임시로 사용하세요. "
            "가능하면 `--ca-bundle` 옵션이나 "
            "`REQUESTS_CA_BUNDLE` 환경 변수를 사용하여 "
            "신뢰할 수 있는 CA 인증서를 지정하는 것을 권장합니다."
        )

def _resolve_ca_path(value: str | Path) -> str: # CA 인증서 파일의 경로를 최종적으로 결정하는 내부 함수
    path = Path(value).expanduser() # expanduser() 메서드는 ~ 를 실제 사용자 홈 폴더로 바꾼다.
    if not path.is_absolute(): # 절대 경로가 아닐경우
        path = PROJECT_ROOT / path # 절대경로로 만들어줌
    if not path.exists(): # exists() 파일이 존재하지 않으면
        raise FileNotFoundError(f"CA bundle file does not exist: {path}") # 에러 발생 시키기 FileNotFoundError
    return str(path)