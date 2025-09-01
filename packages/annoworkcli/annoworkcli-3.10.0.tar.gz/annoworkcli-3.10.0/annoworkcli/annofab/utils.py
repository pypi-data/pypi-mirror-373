import getpass

import annofabapi
from annofabapi import build as build_annofabapi
from annofabapi.exceptions import CredentialsNotFoundError


def _get_annofab_user_id_from_stdin() -> str:
    """標準入力からAnnofabにログインする際のユーザーIDを取得します。"""
    login_user_id = ""
    while login_user_id == "":
        login_user_id = input("Enter Annofab User ID: ")
    return login_user_id


def _get_annofab_password_from_stdin() -> str:
    """標準入力からAnnofabにログインする際のパスワードを取得します。"""
    login_password = ""
    while login_password == "":
        login_password = getpass.getpass("Enter Annofab Password: ")
    return login_password


def build_annofabapi_resource(
    *,
    annofab_login_user_id: str | None = None,
    annofab_login_password: str | None = None,
    annofab_pat: str | None = None,
) -> annofabapi.Resource:
    """
    annofabapi.Resourceインスタンスを生成する。

    Args:
        args: コマンドライン引数の情報

    Returns:
        annofabapi.Resourceインスタンス

    """
    try:
        service = build_annofabapi(annofab_login_user_id, annofab_login_password, pat=annofab_pat, input_mfa_code_via_stdin=True)
    except CredentialsNotFoundError:
        # 環境変数, netrcフィアルに認証情報が設定されていなかったので、標準入力から認証情報を入力させる。
        stdin_login_user_id = _get_annofab_user_id_from_stdin()
        stdin_login_password = _get_annofab_password_from_stdin()
        service = build_annofabapi(stdin_login_user_id, stdin_login_password)

    return service
