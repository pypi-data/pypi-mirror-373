from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import google.auth.credentials
    import google.oauth2.credentials
    import google.oauth2.service_account

_USER_CREDENTIALS: Optional["google.oauth2.credentials.Credentials"] = None


def _get_jupyterhub_user_id():
    """JupyterHub 사용자 ID를 환경변수에서 가져옵니다.

    Returns:
        Optional[str]: JUPYTERHUB_USER 환경변수가 존재하면 해당 값, 없으면 None
    """
    import os

    return os.environ["JUPYTERHUB_USER"] if "JUPYTERHUB_USER" in os.environ else None


def _get_user_credentials() -> "google.oauth2.credentials.Credentials":
    """OAuth 2.0 플로우를 통해 사용자 인증 자격증명을 가져옵니다.

    브라우저를 통한 OAuth 인증 프로세스를 시작하고, 외부 서버에서 인증 코드를 기다린 후
    Google API에 접근할 수 있는 사용자 자격증명을 반환합니다.

    인증 프로세스:
    1. OAuth URL 생성 및 사용자에게 출력
    2. 외부 인증 서버에서 인증 코드 폴링 (최대 300초)
    3. 인증 코드를 사용하여 토큰 교환

    Returns:
        google.oauth2.credentials.Credentials: Google OAuth2 사용자 자격증명

    Raises:
        ValueError: 300초 내에 인증 코드를 받지 못했을 때
    """
    import os
    import time

    import requests
    from google_auth_oauthlib.flow import InstalledAppFlow

    from skt.vault_utils import get_secrets

    redirect_url = os.getenv(
        "GCP_AUTH_REDIRECT_URL", "https://aim.yks.sktai.io/api/v1/gcp-authorization/oauth2callback"
    )
    oauth_credentials = get_secrets("gcp/sktaic-datahub/aidp-oauth")
    client_id = oauth_credentials["CLIENT_ID"]
    client_secret = oauth_credentials["CLIENT_SECRET"]

    flow = InstalledAppFlow.from_client_config(
        client_config={
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
        redirect_uri=redirect_url,
    )

    url, state = flow.authorization_url()
    print(f"Please visit this URL to authorize this application: {url}")

    stime = time.time()

    oauth_code_url = os.getenv("GCP_AUTH_OAUTH_CODE_URL", "https://aim.yks.sktai.io/api/v1/gcp-authorization/codes")

    code = None
    while stime + 300 > time.time():
        s = requests.Session()

        res = s.get(url=f"{oauth_code_url}/{state}")
        if res.status_code != requests.codes.ok:
            time.sleep(5)
        else:
            code = res.json()["results"]
            break

    if not code:
        raise ValueError("Time out occurred while waiting for authorization code")

    flow.fetch_token(code=code)
    print("Login Successful")
    return flow.credentials


def get_user_credentials() -> "google.oauth2.credentials.Credentials":
    """사용자 OAuth 2.0 자격증명을 가져옵니다 (캐싱 포함).

    전역 변수를 사용하여 자격증명을 캐시하고, 만료된 경우에만 새로 가져옵니다.

    Returns:
        google.oauth2.credentials.Credentials: 유효한 Google OAuth2 사용자 자격증명
    """
    global _USER_CREDENTIALS

    if not _USER_CREDENTIALS or _USER_CREDENTIALS.expired:
        _USER_CREDENTIALS = _get_user_credentials()

    return _USER_CREDENTIALS


def get_service_account_credentials(path: str) -> "google.oauth2.service_account.Credentials":
    """서비스 계정 JSON 파일을 사용하여 GCP 자격증명을 생성합니다.

    지정된 경로의 서비스 계정 JSON 파일을 읽어서 Google Cloud Platform
    전체 권한을 가진 자격증명을 생성합니다.

    Args:
        path (str): 서비스 계정 JSON 파일의 절대 경로 또는 상대 경로

    Returns:
        google.oauth2.service_account.Credentials: cloud-platform 스코프가 적용된 서비스 계정 자격증명

    Raises:
        FileNotFoundError: 지정된 경로에 파일이 없을 때
        ValueError: JSON 파일이 유효한 서비스 계정 키가 아닐 때
    """
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_file(
        filename=path,
    )
    scoped_credentials = credentials.with_scopes(
        [
            "https://www.googleapis.com/auth/cloud-platform",  # User 인증과 동일한 scope 사용
        ]
    )

    return scoped_credentials


def _get_default_google_credentials_json() -> str:
    """기본 Google 자격증명 JSON 파일 경로를 가져옵니다.

    Returns:
        str: 환경변수 GOOGLE_APPLICATION_DEFAULT_CREDENTIALS 값 또는 기본 경로
    """
    import os

    return os.getenv("GOOGLE_APPLICATION_DEFAULT_CREDENTIALS", "/etc/hadoop/conf/google-access-key.json")


def get_gcp_credentials(
    service_account_file_path: Optional[str] = None,
) -> "google.auth.credentials.Credentials":
    """실행 환경에 따라 적절한 GCP 자격증명을 자동으로 선택하여 반환합니다.

    환경 감지 방식:
    - JupyterHub 환경 (JUPYTERHUB_USER 환경변수 존재): OAuth 2.0 사용자 인증 사용
    - 그 외 환경 (로컬, 서버 등): 서비스 계정 인증 사용

    Args:
        service_account_file_path (Optional[str]): 서비스 계정 JSON 파일 경로.
            None인 경우 GOOGLE_APPLICATION_DEFAULT_CREDENTIALS 환경변수 또는
            기본 경로(/etc/hadoop/conf/google-access-key.json)를 사용합니다.

    Returns:
        google.auth.credentials.Credentials: 환경에 적합한 GCP 자격증명 객체

    Note:
        이 함수는 환경을 자동으로 감지하므로 대부분의 경우 추가 설정 없이 사용할 수 있습니다.
    """

    jupyterhub_user_id = _get_jupyterhub_user_id()
    if jupyterhub_user_id:
        return get_user_credentials()
    else:
        service_account_file_path = service_account_file_path or _get_default_google_credentials_json()
        return get_service_account_credentials(service_account_file_path)


def get_gcp_credentials_json_string(
    service_account_file_path: Optional[str] = None,
) -> str:
    """실행 환경에 따라 적절한 GCP 자격증명을 JSON 문자열 형태로 반환합니다.

    환경별 처리 방식:
    - JupyterHub 환경: OAuth 2.0 사용자 자격증명을 JSON으로 직렬화
    - 그 외 환경: 서비스 계정 JSON 파일 내용을 문자열로 읽기

    Args:
        service_account_file_path (Optional[str]): 서비스 계정 JSON 파일 경로.
            None인 경우 GOOGLE_APPLICATION_DEFAULT_CREDENTIALS 환경변수 또는
            기본 경로(/etc/hadoop/conf/google-access-key.json)를 사용합니다.

    Returns:
        str: 자격증명을 나타내는 JSON 문자열

    Raises:
        FileNotFoundError: 서비스 계정 파일이 존재하지 않을 때 (비 JupyterHub 환경)

    Note:
        이 함수는 Google Cloud 클라이언트 라이브러리에서 JSON 형태의 자격증명이
        필요한 경우에 유용합니다.
    """
    jupyterhub_user_id = _get_jupyterhub_user_id()
    if jupyterhub_user_id:
        return get_user_credentials().to_json()
    else:
        service_account_file_path = service_account_file_path or _get_default_google_credentials_json()
        with open(service_account_file_path, "r") as f:
            return f.read()
