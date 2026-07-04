from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests

from data_pipeline.build_train_table import PROJECT_ROOT

# ssl_verify → SSL 인증서 검증 설정 / SSL 인증서 검증 설정을 최종적으로 결정하는 함수
def resolve_ssl_verify(ca_bundle: str | Path | bool | None = None, no_ssl_verify: bool = False) -> str | bool | None:
    # 사용할 CA 인증서 파일 ca_bundle : 상대방의 신원을 검증하기 위해서 사용하는 파일 
    if no_ssl_verify:
        return False
    
    if isinstance(ca_bundle, bool) :
        return ca_bundle
    
    if ca_bundle:
        return _resolve_ca_path(ca_bundle)
    
    env_value = os.getenv("DT_TRAFFIC_CA_BUNDLE") or os.getenv("REQUESTS_CA_BUNDLE") or os.getenv("CURL_CA_BUNDLE")

    if env_value:
        return _resolve_ca_path(env_value)
    
    return None

def apply_ssl_verify(session: Any, verify: str | bool | None) -> None:
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