import argparse
import logging
from typing import Any

from annofabapi.resource import Resource as AnnofabResource
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.annofab.utils import build_annofabapi_resource
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args

logger = logging.getLogger(__name__)


def get_annofab_account_id(external_linkage_info: dict[str, Any]) -> str | None:
    if "annofab" not in external_linkage_info:
        return None

    if "account_id" not in external_linkage_info["annofab"]:
        return None
    return external_linkage_info["annofab"]["account_id"]


class PutAnnofabAccountId:
    def __init__(self, *, annowork_service: AnnoworkResource, annofab_service: AnnofabResource, overwrite: bool) -> None:
        self.annowork_service = annowork_service
        self.annofab_service = annofab_service
        self.overwrite = overwrite

    def put_account_annofab_info_for_user(self, user_id: str, af_account_id: str) -> bool:
        content = self.annowork_service.wrapper.get_account_external_linkage_info_or_none(user_id)
        if content is None:
            logger.warning(f"{user_id=}: 指定したユーザ情報は存在しません。")
            return False

        last_updated_datetime = content["updated_datetime"]

        if tmp := get_annofab_account_id(content["external_linkage_info"]) is not None and not self.overwrite:
            logger.debug(
                f"{user_id=}: 'external_linkage_info.annofab.account_id' は既に '{tmp}' が設定されているので、スキップします。"
                f"上書きする場合は'--overwrite`を指定してください。"
            )
            return False

        request_body = {
            "external_linkage_info": {"annofab": {"account_id": af_account_id}},
        }
        if last_updated_datetime is not None:
            request_body["last_updated_datetime"] = last_updated_datetime

        logger.debug(f"{request_body=}")
        self.annowork_service.api.put_account_external_linkage_info(user_id, request_body=request_body)
        logger.debug(f"{user_id=}: アカウントの外部連携情報に {af_account_id=} を設定しました。")
        return True

    def main(self, af_workspace_name: str, user_id_list: list[str]) -> None:
        af_workspace_member_list = self.annofab_service.wrapper.get_all_organization_members(af_workspace_name)
        af_user_id_account_id_dict: dict[str, str] = {member["user_id"]: member["account_id"] for member in af_workspace_member_list}

        success_count = 0
        for user_id in user_id_list:
            af_account_id = af_user_id_account_id_dict.get(user_id)
            if af_account_id is None:
                logger.warning(f"Annofabのワークスペース '{af_workspace_name}' に {user_id=} のユーザは存在しないので、スキップします。")
                continue

            try:
                result = self.put_account_annofab_info_for_user(user_id=user_id, af_account_id=af_account_id)
                if result:
                    success_count += 1
            except Exception as e:
                logger.warning(f"{user_id=}: アカウントの外部連携情報の設定に失敗しました。:: {e}")

        logger.info(f"{success_count} / {len(user_id_list)} 件、アカウントの外部連携情報の設定しました。")


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    annofab_service = build_annofabapi_resource(
        annofab_login_user_id=args.annofab_user_id,
        annofab_login_password=args.annofab_password,
        annofab_pat=args.annofab_pat,
    )
    user_id_list = get_list_from_args(args.user_id)
    assert user_id_list is not None
    PutAnnofabAccountId(annowork_service=annowork_service, annofab_service=annofab_service, overwrite=args.overwrite).main(
        af_workspace_name=args.annofab_workspace_name, user_id_list=user_id_list
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-u",
        "--user_id",
        type=str,
        nargs="+",
        required=True,
        help="外部連携情報を設定するユーザのuser_id。",
    )

    parser.add_argument(
        "-af_org",
        "--annofab_workspace_name",
        type=str,
        required=True,
        help="対象ユーザが参加しているAnnofabのワークスペース名を指定してください。AnnofabのワークスペースメンバからAnnofabのaccount_idを取得します。",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="上書きする",
    )
    parser.add_argument("--annofab_user_id", type=str, help="Annofabにログインする際のユーザID")
    parser.add_argument("--annofab_password", type=str, help="Annofabにログインする際のパスワード")
    parser.add_argument("--annofab_pat", type=str, help="Annofabにログインする際のパーソナルアクセストークン")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "put_account_external_linkage_info"
    subcommand_help = (
        "アカウントの外部連携情報に、Annofabから取得したaccount_idを設定します。\nAnnofabのuser_idはAnnoworkのuser_idと一致している必要があります。"
    )

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
