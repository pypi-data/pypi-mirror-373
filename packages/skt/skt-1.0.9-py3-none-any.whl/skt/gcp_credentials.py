"""GCP 자격증명 관리 모듈.

이 모듈은 다양한 실행 환경에서 Google Cloud Platform 자격증명을 자동으로 감지하고
적절한 인증 방식을 제공하는 유틸리티 함수들을 포함합니다.

Supported Authentication Methods:
    - JupyterHub 환경: OAuth 2.0 사용자 인증
    - 기타 환경: 서비스 계정 인증 (JSON key file)

Main Functions:
    - get_gcp_credentials(): 환경에 적합한 자격증명 객체 반환
    - get_gcp_credentials_json_string(): 자격증명을 JSON 문자열로 반환
    - authorize_user(): 사용자 OAuth 2.0 인증 수행

Environment Variables:
    - GOOGLE_APPLICATION_CREDENTIALS: 서비스 계정 JSON 파일 경로
    - JUPYTERHUB_API_URL: JupyterHub API URL (JupyterHub 환경 감지용)
    - JUPYTERHUB_API_TOKEN: JupyterHub API 토큰 (JupyterHub 환경 감지용)
    - GCP_AUTH_REDIRECT_URL: OAuth 인증 리다이렉트 URL
    - GCP_AUTH_OAUTH_CODE_URL: OAuth 인증 코드 폴링 URL
"""

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    import google.auth.credentials
    import google.oauth2.credentials
    import google.oauth2.service_account

_APPLICATION_DEFAULT_CREDENTIALS_JSON = "application_default_credentials.json"
_GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS"


def _is_in_jupyterhub() -> bool:
    """현재 환경이 JupyterHub에서 실행 중인지 확인합니다.

    Returns:
        bool: JUPYTERHUB_API_URL과 JUPYTERHUB_API_TOKEN 환경변수가 존재하면 True, 아니면 False
    """
    import os

    return bool(os.getenv("JUPYTERHUB_API_URL") and os.getenv("JUPYTERHUB_API_TOKEN"))


def authorize_user() -> "google.oauth2.credentials.Credentials":
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
    from google_auth_oauthlib.flow import Flow

    from .vault_utils import get_secrets

    redirect_url = os.getenv(
        "GCP_AUTH_REDIRECT_URL", "https://aim.yks.sktai.io/api/v1/gcp-authorization/oauth2callback"
    )
    oauth_credentials = get_secrets("gcp/sktaic-datahub/aidp-oauth")
    client_id = oauth_credentials["CLIENT_ID"]
    client_secret = oauth_credentials["CLIENT_SECRET"]

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "project_id": "sktaic-datahub",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
        redirect_uri=redirect_url,
    )

    url, state = flow.authorization_url(access_type="offline", prompt="consent")

    print(f"Please visit this URL to authorize this application: {url}")

    stime = time.time()

    oauth_code_url = os.getenv("GCP_AUTH_OAUTH_CODE_URL", "https://aim.yks.sktai.io/api/v1/gcp-authorization/codes")

    code = None
    while stime + 300 > time.time():
        s = requests.Session()

        res = s.get(url=f"{oauth_code_url}/{state}")
        if res.status_code != requests.codes.ok:
            time.sleep(1)
        else:
            code = res.json()["results"]
            break

    if not code:
        raise ValueError("Timeout occurred while waiting for authorization code. Please try again.")

    flow.fetch_token(code=code)
    print("Authentication successful")

    return flow.credentials


def _get_user_credentials(create: bool = True) -> Tuple["google.oauth2.credentials.Credentials", str]:
    """로컬 저장소에서 사용자 자격증명을 가져오거나 필요시 새로 생성합니다.

    Args:
        create (bool): 기존 자격증명이 없거나 유효하지 않을 때 새로 생성할지 여부. 기본값: True

    Returns:
        Tuple[google.oauth2.credentials.Credentials, str]:
            - 사용자 자격증명 객체
            - 자격증명 파일 경로

    Raises:
        FileNotFoundError: 자격증명 파일이 존재하지 않고 create=False일 때
        ValueError: 자격증명 파일이 유효하지 않고 create=False일 때
    """
    import io
    import json
    import os
    import warnings

    import google.oauth2.credentials

    if os.getenv(_GOOGLE_APPLICATION_CREDENTIALS):
        import warnings

        warnings.warn(
            "Existing GOOGLE_APPLICATION_CREDENTIALS environment variable will be invalidated and removed to create user credentials.",
            UserWarning,
        )
        del os.environ[_GOOGLE_APPLICATION_CREDENTIALS]

    config_path = os.path.join(os.path.expanduser("~"), ".config", "gcloud")
    credentials_file_path = os.path.join(config_path, _APPLICATION_DEFAULT_CREDENTIALS_JSON)

    try:
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(credentials_file_path)
        return credentials, credentials_file_path
    except (FileNotFoundError, ValueError) as e:
        if create:
            warnings.warn(
                f"Failed to load authorized user credentials from {credentials_file_path}. Creating new credentials.",
                UserWarning,
            )

            if os.path.exists(credentials_file_path):
                os.remove(credentials_file_path)
            else:
                os.makedirs(config_path, exist_ok=True)

            credentials = authorize_user()

            adc = {
                "account": credentials.account,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "refresh_token": credentials.refresh_token,
                "type": "authorized_user",
                "universe_domain": credentials.universe_domain,
            }

            with io.open(credentials_file_path, mode="w", encoding="utf-8") as fp:
                json.dump(adc, fp=fp)

            return _get_user_credentials(create=False)
        else:
            raise e


def _get_service_account_credentials() -> Tuple["google.oauth2.service_account.Credentials", str]:
    """서비스 계정 JSON 파일을 사용하여 GCP 자격증명을 생성합니다.

    환경변수 GOOGLE_APPLICATION_CREDENTIALS 또는 기본 경로에서 서비스 계정 JSON 파일을
    읽어서 Google Cloud Platform API 접근을 위한 자격증명을 생성합니다.

    파일 경로 우선순위:
    1. GOOGLE_APPLICATION_CREDENTIALS 환경변수
    2. /etc/hadoop/conf/google-access-key.json (기본값)

    Returns:
        Tuple[google.oauth2.service_account.Credentials, str]:
            - 서비스 계정 자격증명 객체
            - 서비스 계정 JSON 파일 경로

    Raises:
        FileNotFoundError: 지정된 파일 경로가 존재하지 않을 때
        ValueError: JSON 파일이 유효한 서비스 계정 키가 아닐 때
    """
    import os

    import google.oauth2.service_account

    # 환경변수에서 서비스 계정 파일 경로 가져오기 (기본값: Hadoop 설정 경로)
    path = os.getenv(_GOOGLE_APPLICATION_CREDENTIALS, "/etc/hadoop/conf/google-access-key.json")
    credentials = google.oauth2.service_account.Credentials.from_service_account_file(path)
    return credentials, path


def _get_gcp_credentials() -> Tuple["google.auth.credentials.Credentials", str]:
    """실행 환경에 따라 적절한 GCP 자격증명을 자동으로 선택하여 반환합니다.

    환경 감지 방식:
    - JupyterHub 환경 (JUPYTERHUB_API_URL, JUPYTERHUB_API_TOKEN 환경변수 존재): OAuth 2.0 사용자 인증
    - 그 외 환경 (로컬, 서버 등): 서비스 계정 인증

    Returns:
        Tuple[google.auth.credentials.Credentials, str]:
            - 환경에 적합한 GCP 자격증명 객체
            - 자격증명 파일 경로

    Note:
        이 함수는 내부용으로 환경을 자동 감지하여 자격증명과 파일 경로를 모두 반환합니다.
    """

    # JupyterHub 환경인지 확인하여 적절한 인증 방식 선택
    if _is_in_jupyterhub():
        return _get_user_credentials()
    else:
        return _get_service_account_credentials()


def get_gcp_credentials() -> "google.auth.credentials.Credentials":
    """실행 환경에 따라 적절한 GCP 자격증명을 자동으로 선택하여 반환합니다.

    환경 감지 방식:
    - JupyterHub 환경 (JUPYTERHUB_API_URL, JUPYTERHUB_API_TOKEN 환경변수 존재): OAuth 2.0 사용자 인증
    - 그 외 환경 (로컬, 서버 등): 서비스 계정 인증

    Returns:
        google.auth.credentials.Credentials: 환경에 적합한 GCP 자격증명 객체

    Examples:
        >>> credentials = get_gcp_credentials()
        >>> # BigQuery 클라이언트에서 사용
        >>> from google.cloud import bigquery
        >>> client = bigquery.Client(credentials=credentials)

    Note:
        이 함수는 환경을 자동으로 감지하므로 대부분의 경우 추가 설정 없이 사용할 수 있습니다.
    """
    credentials, _ = _get_gcp_credentials()
    return credentials


def get_gcp_credentials_json_string() -> str:
    """실행 환경에 따라 적절한 GCP 자격증명을 JSON 문자열 형태로 반환합니다.

    환경별 처리 방식:
    - JupyterHub 환경: OAuth 2.0 사용자 자격증명을 JSON으로 직렬화
    - 그 외 환경: 서비스 계정 JSON 파일 내용을 문자열로 읽기

    Returns:
        str: 자격증명을 나타내는 JSON 문자열

    Raises:
        FileNotFoundError: 서비스 계정 파일이 존재하지 않을 때 (비 JupyterHub 환경)
        UnicodeDecodeError: JSON 파일을 읽을 수 없을 때

    Examples:
        >>> json_str = get_gcp_credentials_json_string()
        >>> # pandas-gbq에서 사용
        >>> import pandas_gbq
        >>> df = pandas_gbq.read_gbq('SELECT * FROM dataset.table', credentials=json_str)

    Note:
        이 함수는 Google Cloud 클라이언트 라이브러리에서 JSON 형태의 자격증명이
        필요한 경우에 유용합니다.
    """
    import io

    # 환경에 맞는 자격증명 파일 경로 가져오기
    _, credentials_file_path = _get_gcp_credentials()
    # JSON 파일 내용을 UTF-8로 읽어서 반환
    with io.open(credentials_file_path, mode="r", encoding="utf-8") as f:
        return f.read()
