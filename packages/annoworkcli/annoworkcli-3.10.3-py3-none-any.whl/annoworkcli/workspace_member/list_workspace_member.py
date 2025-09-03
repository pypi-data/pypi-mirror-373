import argparse
import logging
from collections.abc import Collection
from enum import Enum
from pathlib import Path
from typing import Any

import more_itertools
import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class WorkspaceMemberStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ListWorkspace:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def set_additional_info(self, workspace_members: list[dict[str, Any]]) -> None:
        logger.debug(f"{len(workspace_members)} 件のメンバのワークスペースタグ情報を取得します。")
        for member in workspace_members:
            workspace_tags = self.annowork_service.api.get_workspace_member_tags(self.workspace_id, member["workspace_member_id"])
            member["workspace_tag_ids"] = [e["workspace_tag_id"] for e in workspace_tags]
            member["workspace_tag_names"] = [e["workspace_tag_name"] for e in workspace_tags]

    def get_workspace_members_from_tags(self, workspace_tag_ids: Collection[str]) -> list[dict[str, Any]]:
        """
        指定したタグに所属するメンバーを取得します。
        複数のタグを指定した場合、指定したすべてのタグに所属するメンバー（AND条件）を返します。
        """
        result_workspace_member_ids: set[str] | None = None

        for tag_id in workspace_tag_ids:
            tmp_members = self.annowork_service.api.get_workspace_tag_members(self.workspace_id, tag_id)
            if result_workspace_member_ids is None:
                # 初回のみ
                result_members = tmp_members
            else:
                result_members = [e for e in tmp_members if e["workspace_member_id"] in result_workspace_member_ids]
            result_workspace_member_ids = {e["workspace_member_id"] for e in result_members}

        return result_members

    @classmethod
    def filter_member_with_user_id(cls, members: list[dict[str, Any]], user_ids: Collection[str]) -> list[dict[str, Any]]:
        """
        メンバ一覧を、指定したuser_idで絞り込みます。

        Args:
            members: 絞り込まれるメンバ一覧
            user_ids: 指定したuser_idで絞り込みます

        Returns:
            絞り込み後のメンバ一覧
        """
        result = []
        for user_id in user_ids:
            member = more_itertools.first_true(
                members,
                pred=lambda e: e["user_id"] == user_id,  # pylint: disable=cell-var-from-loop  # noqa: B023
            )
            if member is not None:
                result.append(member)
            else:
                logger.warning(f"{user_id=}であるメンバは存在しません。")
                continue
        return result

    def main(  # noqa: PLR0912
        self,
        output: Path,
        output_format: OutputFormat,
        workspace_tag_ids: Collection[str] | None,
        user_ids: Collection[str] | None,
        show_workspace_tag: bool,  # noqa: FBT001
        status: WorkspaceMemberStatus | None = None,
    ) -> None:
        # workspace_tag_idsとuser_idsは排他的
        assert workspace_tag_ids is None or user_ids is None
        if workspace_tag_ids is not None:
            # workspace_tag_idの存在確認
            all_workspace_tags = self.annowork_service.api.get_workspace_tags(self.workspace_id)
            all_all_workspace_tag_ids = {e["workspace_tag_id"] for e in all_workspace_tags}
            for tag_id in workspace_tag_ids:
                if tag_id not in all_all_workspace_tag_ids:
                    logger.warning(f"workspace_tag_idが'{tag_id}'であるワークスペースタグは存在しません。")

            # workspace_tag_idに所属するメンバーを取得する
            workspace_members = self.get_workspace_members_from_tags(workspace_tag_ids)
        else:
            workspace_members = self.annowork_service.api.get_workspace_members(self.workspace_id, query_params={"includes_inactive_members": True})
            if user_ids is not None:
                workspace_members = self.filter_member_with_user_id(workspace_members, user_ids)

        if status is not None:
            workspace_members = [e for e in workspace_members if e["status"] == status.value]

        if len(workspace_members) == 0:
            logger.warning("ワークスペースメンバ情報は0件です。")
        else:
            if show_workspace_tag:
                self.set_additional_info(workspace_members)
            workspace_members.sort(key=lambda e: e["user_id"].lower())

        logger.debug(f"{len(workspace_members)} 件のワークスペースメンバ一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(workspace_members, is_pretty=True, output=output)
        else:
            if len(workspace_members) > 0:
                df = pandas.json_normalize(workspace_members)
            else:
                # 最低限のカラムを含めた空のデータフレームを作成
                df = pandas.DataFrame(columns=["workspace_id", "workspace_member_id", "user_id", "username", "status"])
            print_csv(df, output=output)


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    workspace_tag_id_list = get_list_from_args(args.workspace_tag_id)
    user_id_list = get_list_from_args(args.user_id)
    ListWorkspace(annowork_service=annowork_service, workspace_id=args.workspace_id).main(
        output=args.output,
        output_format=OutputFormat(args.format),
        workspace_tag_ids=workspace_tag_id_list,
        user_ids=user_id_list,
        show_workspace_tag=args.show_workspace_tag,
        status=WorkspaceMemberStatus(args.status) if args.status is not None else None,
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument(
        "-wt",
        "--workspace_tag_id",
        nargs="+",
        type=str,
        help="指定したワークスペースタグが付与されたワークスペースメンバを出力します。複数指定した場合は、すべてのワークスペースタグが付与されたワークスペースメンバーを出力します。",
    )

    filter_group.add_argument(
        "-u",
        "--user_id",
        nargs="+",
        type=str,
        help="指定したuser_idで絞り込みます。",
    )

    parser.add_argument(
        "--show_workspace_tag",
        action="store_true",
        help="ワークスペースタグに関する情報も出力します。",
    )

    parser.add_argument(
        "--status",
        type=str,
        choices=[e.value for e in WorkspaceMemberStatus],
        help="ワークスペースメンバーのstatusで絞り込みます。",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=[e.value for e in OutputFormat],
        help="出力先のフォーマット",
        default=OutputFormat.CSV.value,
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "list"
    subcommand_help = "ワークスペースメンバの一覧を出力します。無効化されたメンバも出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
