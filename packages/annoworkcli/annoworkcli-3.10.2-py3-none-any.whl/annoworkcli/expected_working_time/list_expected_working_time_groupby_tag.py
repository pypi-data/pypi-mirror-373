import argparse
import logging
import sys
from collections import defaultdict
from collections.abc import Collection
from pathlib import Path
from typing import Any

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import COMMAND_LINE_ERROR_STATUS_CODE, OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.expected_working_time.list_expected_working_time import ListExpectedWorkingTime

logger = logging.getLogger(__name__)


class ListExpectedWorkingTimeGroupbyTag:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def get_expected_working_times_groupby_tag(
        self,
        expected_working_times: list[dict[str, Any]],
        target_workspace_tag_ids: Collection[str] | None = None,
        target_workspace_tag_names: Collection[str] | None = None,
    ) -> list[dict[str, Any]]:
        """予定稼働時間のlistから、ワークスペースタグごとに集計したlistを返す。

        Args:
            expected_working_times (list[dict[str,Any]]): [description]

        Returns:
            list[dict[str,Any]]: [description]
        """
        workspace_tags = self.annowork_service.api.get_workspace_tags(self.workspace_id)

        # target_workspace_tag_idsとtarget_workspace_tag_namesは排他的なので、両方not Noneになることはない
        assert not (target_workspace_tag_ids is not None and target_workspace_tag_names is not None)
        if target_workspace_tag_ids is not None:
            workspace_tags = [e for e in workspace_tags if e["workspace_tag_id"] in set(target_workspace_tag_ids)]
            if len(workspace_tags) != len(target_workspace_tag_ids):
                logger.warning(
                    f"target_workspace_tag_idsに含まれるいくつかのworkspace_tag_idは、存在しません。"
                    f":: {len(target_workspace_tag_ids)=}, {len(workspace_tags)=}"
                )

        if target_workspace_tag_names is not None:
            workspace_tags = [e for e in workspace_tags if e["workspace_tag_name"] in set(target_workspace_tag_names)]
            if len(workspace_tags) != len(target_workspace_tag_names):
                logger.warning(
                    f"target_workspace_tag_namesに含まれるいくつかのworkspace_tag_nameは、存在しません。"
                    f":: {len(target_workspace_tag_names)=}, {len(workspace_tags)=}"
                )

        dict_hours: dict[tuple[str, str], float] = defaultdict(float)

        # ワークスペースタグごと日毎の時間を集計する
        for workspace_tag in workspace_tags:
            workspace_tag_name = workspace_tag["workspace_tag_name"]
            members = self.annowork_service.api.get_workspace_tag_members(self.workspace_id, workspace_tag["workspace_tag_id"])
            member_ids = {e["workspace_member_id"] for e in members}
            for elm in expected_working_times:
                if elm["workspace_member_id"] in member_ids:
                    dict_hours[elm["date"], workspace_tag_name] += elm["expected_working_hours"]

        # 全体の時間を日毎に集計する
        for elm in expected_working_times:
            dict_hours[elm["date"], "total"] += elm["expected_working_hours"]

        dict_date: dict[str, dict[str, float]] = defaultdict(dict)
        for (date, org_tag), hours in dict_hours.items():
            dict_date[date].update({org_tag: hours})

        results = []

        for date, value in dict_date.items():
            elm = {"date": date, "expected_working_hours": value}
            results.append(elm)

        results.sort(key=lambda e: (e["date"]))
        return results

    def main(
        self,
        *,
        output: Path,
        output_format: OutputFormat,
        user_id_list: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        target_workspace_tag_ids: Collection[str] | None = None,
        target_workspace_tag_names: Collection[str] | None = None,
    ) -> None:
        list_obj = ListExpectedWorkingTime(self.annowork_service, self.workspace_id)
        if user_id_list is not None:
            expected_working_times = list_obj.get_expected_working_times_by_user_id(
                user_id_list=user_id_list, start_date=start_date, end_date=end_date
            )
        else:
            expected_working_times = list_obj.get_expected_working_times(start_date=start_date, end_date=end_date)

        if len(expected_working_times) == 0:
            logger.warning("予定稼働時間情報は0件です。")
            results = []
        else:
            results = self.get_expected_working_times_groupby_tag(
                expected_working_times,
                target_workspace_tag_ids=target_workspace_tag_ids,
                target_workspace_tag_names=target_workspace_tag_names,
            )

        logger.info(f"{len(results)} 件のワークスペースタグで集計した予定稼働時間の一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(results, is_pretty=True, output=output)
        else:
            required_columns = [
                "date",
                "expected_working_hours.total",
            ]
            if len(results) > 0:
                df = pandas.json_normalize(results)
                df.fillna(0, inplace=True)
                remaining_columns = list(set(df.columns) - set(required_columns))
                columns = required_columns + sorted(remaining_columns)
            else:
                df = pandas.DataFrame(columns=required_columns)
                columns = required_columns

            print_csv(df[columns], output=output)


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    start_date: str | None = args.start_date
    end_date: str | None = args.end_date

    command = " ".join(sys.argv[0:3])
    if all(v is None for v in [user_id_list, start_date, end_date]):
        print(f"{command}: error: '--start_date'や'--user_id'などの絞り込み条件を1つ以上指定してください。", file=sys.stderr)  # noqa: T201
        sys.exit(COMMAND_LINE_ERROR_STATUS_CODE)

    workspace_tag_id_list = get_list_from_args(args.workspace_tag_id)
    workspace_tag_name_list = get_list_from_args(args.workspace_tag_name)

    ListExpectedWorkingTimeGroupbyTag(annowork_service=annowork_service, workspace_id=args.workspace_id).main(
        user_id_list=user_id_list,
        start_date=args.start_date,
        end_date=args.end_date,
        output=args.output,
        target_workspace_tag_ids=workspace_tag_id_list,
        target_workspace_tag_names=workspace_tag_name_list,
        output_format=OutputFormat(args.format),
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
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

    org_tag_group = parser.add_mutually_exclusive_group()
    org_tag_group.add_argument(
        "-wt",
        "--workspace_tag_id",
        type=str,
        nargs="+",
        help="出力対象のワークスペースタグID。未指定の場合は全てのワークスペースタグを出力します。",
    )

    org_tag_group.add_argument(
        "--workspace_tag_name",
        type=str,
        nargs="+",
        help="出力対象のワークスペースタグ名。未指定の場合は全てのワークスペースタグを出力します。",
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
    subcommand_name = "list_groupby_tag"
    subcommand_help = "ワークスペースタグで集計した予定稼働時間の一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
