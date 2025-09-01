from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import google.auth.credentials
    import google.oauth2.credentials
    import google.oauth2.service_account


def _get_jupyterhub_user_id():
    """JupyterHub 사용자 ID를 환경변수에서 가져옵니다.

    Returns:
        Optional[str]: JUPYTERHUB_USER 환경변수가 존재하면 해당 값, 없으면 None
    """
    import os

    return os.environ["JUPYTERHUB_USER"] if "JUPYTERHUB_USER" in os.environ else None


def _get_user_credentials() -> "google.oauth2.credentials.Credentials":
    """OAuth 2.0 플로우를 통해 사용자 인증 자격증명을 가져옵니다.

    브라우저를 통한 OAuth 인증 프로세스를 시작하고, 인증 코드를 기다린 후
    Google API에 접근할 수 있는 사용자 자격증명을 반환합니다.

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


def _get_service_account_credentials(path: str) -> "google.oauth2.service_account.Credentials":
    """서비스 계정 파일을 사용하여 GCP 자격증명을 가져옵니다.

    Args:
        path (str): 서비스 계정 JSON 파일 경로

    Returns:
        google.oauth2.service_account.Credentials: 서비스 계정 자격증명
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
        str: 환경변수 DEFAULT_GOOGLE_CREDENTIALS_JSON 값 또는 기본 경로
    """
    import os

    return os.getenv("DEFAULT_GOOGLE_CREDENTIALS_JSON", "/etc/hadoop/conf/google-access-key.json")


def get_gcp_credentials(
    service_account_file_path: Optional[str] = None,
) -> "google.auth.credentials.Credentials":
    """환경에 따라 적절한 GCP 자격증명을 가져옵니다.

    JupyterHub 환경에서는 OAuth 2.0 사용자 인증을 사용하고,
    그 외 환경에서는 서비스 계정 인증을 사용합니다.

    Args:
        service_account_file_path (Optional[str]): 서비스 계정 JSON 파일 경로.
            None인 경우 기본 경로를 사용합니다.

    Returns:
        google.auth.credentials.Credentials: GCP 자격증명
    """

    jupyterhub_user_id = _get_jupyterhub_user_id()
    if jupyterhub_user_id:
        return _get_user_credentials()
    else:
        service_account_file_path = service_account_file_path or _get_default_google_credentials_json()
        return _get_service_account_credentials(service_account_file_path)


def get_gcp_credentials_json_string(
    service_account_file_path: Optional[str] = None,
) -> str:
    """환경에 따라 적절한 GCP 자격증명을 JSON 문자열로 반환합니다.

    JupyterHub 환경에서는 OAuth 2.0 사용자 자격증명을 JSON으로 변환하고,
    그 외 환경에서는 서비스 계정 JSON 파일을 읽어서 반환합니다.

    Args:
        service_account_file_path (Optional[str]): 서비스 계정 JSON 파일 경로.
            None인 경우 기본 경로를 사용합니다.

    Returns:
        str: 자격증명을 나타내는 JSON 문자열
    """
    jupyterhub_user_id = _get_jupyterhub_user_id()
    if jupyterhub_user_id:
        return _get_user_credentials().to_json()
    else:
        service_account_file_path = service_account_file_path or _get_default_google_credentials_json()
        with open(service_account_file_path, "r") as f:
            return f.read()
