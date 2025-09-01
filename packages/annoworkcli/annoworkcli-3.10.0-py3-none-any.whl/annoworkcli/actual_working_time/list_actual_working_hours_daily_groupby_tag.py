import argparse
import logging
from collections import defaultdict
from collections.abc import Collection, Sequence
from pathlib import Path
from typing import Any

import pandas
from annoworkapi.job import get_parent_job_id_from_job_tree
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.actual_working_time.list_actual_working_hours_daily import (
    ActualWorkingHoursDaily,
    create_actual_working_hours_daily_list,
    filter_actual_daily_list,
)
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class ListActualWorkingTimeGroupbyTag:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str, timezone_offset_hours: int):  # noqa: ANN204
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id
        self.timezone_offset_hours = timezone_offset_hours

    def add_parent_job_info(self, daily_list: list[dict[str, Any]]):  # noqa: ANN201
        """引数daily_listに、parent_job情報を追加する。"""
        all_job_list = self.annowork_service.api.get_jobs(self.workspace_id)
        all_job_dict = {e["job_id"]: e for e in all_job_list}
        parent_job_id_set = {get_parent_job_id_from_job_tree(e["job_tree"]) for e in all_job_list}
        parent_job_id_set.discard(None)

        for elm in daily_list:
            job = all_job_dict[elm["job_id"]]
            parent_job_id = get_parent_job_id_from_job_tree(job["job_tree"])
            parent_job_name = all_job_dict[parent_job_id]["job_name"] if parent_job_id is not None else None
            elm["parent_job_id"] = parent_job_id
            elm["parent_job_name"] = parent_job_name

    def get_actual_working_times_groupby_tag(
        self,
        actual_working_hours_daily: list[ActualWorkingHoursDaily],
        target_workspace_tag_ids: Collection[str] | None = None,
        target_workspace_tag_names: Collection[str] | None = None,
    ) -> list[dict[str, Any]]:
        """実績作業時間のlistから、ワークスペースタグごとに集計したlistを返す。"""
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

        # keyはtuple[date, job_id, org_tag]のdict
        dict_hours: dict[tuple[str, str, str], float] = defaultdict(float)

        # ワークスペースタグごと日毎の時間を集計する
        for workspace_tag in workspace_tags:
            workspace_tag_name = workspace_tag["workspace_tag_name"]
            members = self.annowork_service.api.get_workspace_tag_members(self.workspace_id, workspace_tag["workspace_tag_id"])
            member_ids = {e["workspace_member_id"] for e in members}
            for elm in actual_working_hours_daily:
                if elm.workspace_member_id in member_ids:
                    dict_hours[(elm.date, elm.job_id, workspace_tag_name)] += elm.actual_working_hours

        # 全体の時間を日毎に集計する

        # key:job_id, value:job_nameのdict
        job_dict: dict[str, str] = {}
        for elm in actual_working_hours_daily:
            dict_hours[(elm.date, elm.job_id, "total")] += elm.actual_working_hours
            job_dict[elm.job_id] = elm.job_name

        dict_date: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
        for (date, job_id, org_tag), hours in dict_hours.items():
            dict_date[(date, job_id)].update({org_tag: hours})

        results = []

        for (date, job_id), value in dict_date.items():
            e = {"date": date, "job_id": job_id, "job_name": job_dict.get(job_id), "actual_working_hours": value}
            results.append(e)

        results.sort(key=lambda e: (e["date"], e["job_id"]))

        self.add_parent_job_info(results)

        return results

    def get_actual_working_hours_daily(
        self,
        job_ids: Collection[str] | None = None,
        parent_job_ids: Collection[str] | None = None,
        user_ids: Collection[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[ActualWorkingHoursDaily]:
        list_actual_working_time_obj = ListActualWorkingTime(
            annowork_service=self.annowork_service,
            workspace_id=self.workspace_id,
            timezone_offset_hours=self.timezone_offset_hours,
        )
        actual_working_time_list = list_actual_working_time_obj.get_actual_working_times(
            job_ids=job_ids,
            parent_job_ids=parent_job_ids,
            user_ids=user_ids,
            start_date=start_date,
            end_date=end_date,
            is_set_additional_info=False,
        )

        logger.debug(f"{len(actual_working_time_list)} 件の実績作業時間情報を日ごとに集約します。")
        actual_working_hours_daily_list: Sequence[ActualWorkingHoursDaily] = create_actual_working_hours_daily_list(
            actual_working_time_list, timezone_offset_hours=self.timezone_offset_hours, show_notes=False
        )

        actual_working_hours_daily_list = filter_actual_daily_list(actual_working_hours_daily_list, start_date=start_date, end_date=end_date)
        return actual_working_hours_daily_list

    def main(
        self,
        *,
        output: Path,
        output_format: OutputFormat,
        job_ids: Collection[str] | None = None,
        parent_job_ids: Collection[str] | None = None,
        user_ids: Collection[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        target_workspace_tag_ids: Collection[str] | None = None,
        target_workspace_tag_names: Collection[str] | None = None,
    ) -> None:
        actual_working_hours_daily_list = self.get_actual_working_hours_daily(
            job_ids=job_ids, parent_job_ids=parent_job_ids, user_ids=user_ids, start_date=start_date, end_date=end_date
        )
        if len(actual_working_hours_daily_list) == 0:
            logger.warning("日ごとの実績作業時間情報は0件です。")
            results = []
        else:
            results = self.get_actual_working_times_groupby_tag(
                actual_working_hours_daily_list,
                target_workspace_tag_ids=target_workspace_tag_ids,
                target_workspace_tag_names=target_workspace_tag_names,
            )

        logger.info(f"{len(results)} 件のワークスペースタグで集計した実績作業時間の一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(results, is_pretty=True, output=output)
        else:
            required_columns = [
                "date",
                "parent_job_id",
                "parent_job_name",
                "job_id",
                "job_name",
                "actual_working_hours.total",
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
    job_id_list = get_list_from_args(args.job_id)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    user_id_list = get_list_from_args(args.user_id)
    start_date: str | None = args.start_date
    end_date: str | None = args.end_date

    if all(v is None for v in [job_id_list, parent_job_id_list, user_id_list, start_date, end_date]):
        logger.warning(
            "'--start_date'や'--job_id'などの絞り込み条件が1つも指定されていません。WebAPIから取得するデータ量が多すぎて、WebAPIのリクエストが失敗するかもしれません。"
        )

    workspace_tag_id_list = get_list_from_args(args.workspace_tag_id)
    workspace_tag_name_list = get_list_from_args(args.workspace_tag_name)

    ListActualWorkingTimeGroupbyTag(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
        timezone_offset_hours=args.timezone_offset,
    ).main(
        job_ids=job_id_list,
        parent_job_ids=parent_job_id_list,
        user_ids=user_id_list,
        start_date=args.start_date,
        end_date=args.end_date,
        target_workspace_tag_ids=workspace_tag_id_list,
        target_workspace_tag_names=workspace_tag_name_list,
        output=args.output,
        output_format=OutputFormat(args.format),
    )


def parse_args(parser: argparse.ArgumentParser):  # noqa: ANN201
    required_group = parser.add_mutually_exclusive_group(required=True)

    required_group.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        help="対象のワークスペースID",
    )

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="絞り込み対象のユーザID")

    # parent_job_idとjob_idの両方を指定するユースケースはなさそうなので、exclusiveにする。
    job_id_group = parser.add_mutually_exclusive_group()
    job_id_group.add_argument("-j", "--job_id", type=str, nargs="+", required=False, help="絞り込み対象のジョブID")
    job_id_group.add_argument("-pj", "--parent_job_id", type=str, nargs="+", required=False, help="絞り込み対象の親のジョブID")

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

    parser.add_argument(
        "--timezone_offset",
        type=float,
        help="日付に対するタイムゾーンのオフセット時間。例えばJSTなら '9' です。指定しない場合はローカルのタイムゾーンを参照します。",
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
    subcommand_name = "list_daily_groupby_tag"
    subcommand_help = "日ごとの実績作業時間を、ワークスペースタグで集計した値を出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
