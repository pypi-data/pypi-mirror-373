import argparse
import logging
from typing import Any

import more_itertools
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, prompt_yesno

logger = logging.getLogger(__name__)


class DeleteExpectedWorkingTime:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str):  # noqa: ANN204
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def delete_expected_working_times(self, expected_working_times: list[dict[str, Any]]):  # noqa: ANN201
        for expected in expected_working_times:
            self.annowork_service.api.delete_expected_working_time_by_workspace_member(
                self.workspace_id,
                workspace_member_id=expected["workspace_member_id"],
                date=expected["date"],
            )

    def get_expected_working_times(self, *, user_id: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        workspace_members = self.annowork_service.api.get_workspace_members(self.workspace_id, query_params={"includes_inactive_members": True})
        member = more_itertools.first_true(workspace_members, pred=lambda e: e["user_id"] == user_id)
        if member is None:
            logger.warning(f"{user_id=} のユーザはワークスペースメンバに存在しませんでした。")
            return []

        query_params = {
            "term_start": start_date,
            "term_end": end_date,
        }
        workspace_member_id = member["workspace_member_id"]
        logger.debug(f"予定稼働情報を取得します。{workspace_member_id=}, {query_params=}")
        return self.annowork_service.api.get_expected_working_times_by_workspace_member(
            self.workspace_id, workspace_member_id=workspace_member_id, query_params=query_params
        )

    def main(self, *, user_id: str, start_date: str, end_date: str):  # noqa: ANN201
        expected_working_times = self.get_expected_working_times(user_id=user_id, start_date=start_date, end_date=end_date)
        if len(expected_working_times) == 0:
            logger.info("削除する予定稼働時間情報はありませんでした。")
            return

        yesno = prompt_yesno(
            f"user_id={user_id}, start_date={start_date}, end_date={end_date} の"
            f"予定稼働時間情報 {len(expected_working_times)} 件を削除します。よろしいですか？"
        )
        if yesno:
            self.delete_expected_working_times(expected_working_times)


def main(args):  # noqa: ANN001, ANN201
    annowork_service = build_annoworkapi(args)
    DeleteExpectedWorkingTime(annowork_service=annowork_service, workspace_id=args.workspace_id).main(
        user_id=args.user_id,
        start_date=args.start_date,
        end_date=args.end_date,
    )


def parse_args(parser: argparse.ArgumentParser):  # noqa: ANN201
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument("-u", "--user_id", type=str, required=True, help="削除対象のユーザID")
    parser.add_argument("--start_date", type=str, required=True, help="削除対象の開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=True, help="削除対象の終了日(YYYY-mm-dd)")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "delete"
    subcommand_help = "予定稼働時間を削除します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
