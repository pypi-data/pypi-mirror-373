import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import COMMAND_LINE_ERROR_STATUS_CODE, OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class ListExpectedWorkingTime:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str):  # noqa: ANN204
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id
        self.workspace_members = self.annowork_service.api.get_workspace_members(self.workspace_id, query_params={"includes_inactive_members": True})

    def get_expected_working_times_by_user_id(
        self, user_id_list: list[str], *, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict[str, Any]]:
        workspace_member_dict = {e["user_id"]: e["workspace_member_id"] for e in self.workspace_members}

        query_params = {}
        if start_date is not None:
            query_params["term_start"] = start_date
        if end_date is not None:
            query_params["term_end"] = end_date

        result = []
        for user_id in user_id_list:
            workspace_member_id = workspace_member_dict.get(user_id)
            if workspace_member_id is None:
                logger.warning(f"{user_id=} に該当するワークスペースメンバが存在しませんでした。")
                continue

            logger.debug(f"予定稼働時間情報を取得します。{query_params=}")
            tmp = self.annowork_service.api.get_expected_working_times_by_workspace_member(
                self.workspace_id, workspace_member_id, query_params=query_params
            )
            result.extend(tmp)
        return result

    def get_expected_working_times(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        query_params = {}
        if start_date is not None:
            query_params["term_start"] = start_date
        if end_date is not None:
            query_params["term_end"] = end_date

        logger.debug(f"予定稼働時間情報を取得します。{query_params=}")
        return self.annowork_service.api.get_expected_working_times(self.workspace_id, query_params=query_params)

    def set_member_info_to_working_times(self, working_times: list[dict[str, Any]]):  # noqa: ANN201
        workspace_member_dict = {e["workspace_member_id"]: e for e in self.workspace_members}
        for elm in working_times:
            workspace_member_id = elm["workspace_member_id"]
            member = workspace_member_dict.get(workspace_member_id)
            if member is None:
                logger.warning(f"{workspace_member_id=} であるワークスペースメンバは存在しません。 :: date={elm['date']}")
                continue

            elm.update(
                {
                    "user_id": member["user_id"],
                    "username": member["username"],
                }
            )

    def main(
        self,
        *,
        output: Path,
        output_format: OutputFormat,
        user_id_list: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> None:
        if user_id_list is not None:
            result = self.get_expected_working_times_by_user_id(user_id_list=user_id_list, start_date=start_date, end_date=end_date)
        else:
            result = self.get_expected_working_times(start_date=start_date, end_date=end_date)

        self.set_member_info_to_working_times(result)

        logger.info(f"{len(result)} 件の予定稼働時間情報を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(result, is_pretty=True, output=output)
        else:
            required_columns = [
                "workspace_id",
                "date",
                "workspace_member_id",
                "user_id",
                "username",
                "expected_working_hours",
            ]
            if len(result) > 0:
                df = pandas.json_normalize(result)
                remaining_columns = list(set(df.columns) - set(required_columns))
                columns = required_columns + remaining_columns
            else:
                columns = required_columns
                df = pandas.DataFrame(columns=columns)
            print_csv(df[columns], output=output)


def main(args):  # noqa: ANN001, ANN201
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    start_date: str | None = args.start_date
    end_date: str | None = args.end_date

    command = " ".join(sys.argv[0:3])
    if all(v is None for v in [user_id_list, start_date, end_date]):
        print(f"{command}: error: '--start_date'や'--user_id'などの絞り込み条件を1つ以上指定してください。", file=sys.stderr)  # noqa: T201
        sys.exit(COMMAND_LINE_ERROR_STATUS_CODE)

    ListExpectedWorkingTime(annowork_service=annowork_service, workspace_id=args.workspace_id).main(
        user_id_list=user_id_list,
        start_date=args.start_date,
        end_date=args.end_date,
        output=args.output,
        output_format=OutputFormat(args.format),
    )


def parse_args(parser: argparse.ArgumentParser):  # noqa: ANN201
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="集計対象のユーザID")

    parser.add_argument("--start_date", type=str, required=False, help="集計開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=False, help="集計終了日(YYYY-mm-dd)")

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
    subcommand_help = "予定稼働時間の一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
