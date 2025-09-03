import argparse
import logging
from collections import defaultdict
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas
from annoworkapi.resource import Resource as AnnoworkResource
from dataclasses_json import DataClassJsonMixin

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.schedule.list_schedule import ExpectedWorkingHoursDict, ListSchedule, create_assigned_hours_dict

logger = logging.getLogger(__name__)


@dataclass
class AssignedHoursDaily(DataClassJsonMixin):
    """
    日ごとのアサイン時間情報を格納するクラス

    Notes:
        job_name, user_id, usernameがOptional型である理由
            存在しないjob_id, workspace_member_idである可能性があるため。レアケースだが、このようなアサインデータはAnnowork画面で作成できる。

    """

    date: str
    job_id: str
    job_name: str | None
    workspace_member_id: str
    user_id: str | None
    username: str | None
    assigned_working_hours: float


AssignedHoursDict = dict[tuple[str, str, str], float]
"""アサイン時間の日ごとの情報を格納する辞書
key: (date, workspace_member_id, job_id), value: アサイン時間
"""


def _get_min_max_date_from_schedule_list(schedule_list: list[dict[str, Any]]) -> tuple[str, str]:
    min_date = "9999-99-99"
    max_date = "0000-00-00"
    for schedule in schedule_list:
        min_date = min(min_date, schedule["start_date"])
        max_date = max(max_date, schedule["end_date"])
    return min_date, max_date


class ListAssignedHoursDaily:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id
        self.list_schedule_obj = ListSchedule(annowork_service, workspace_id)

    def get_expected_working_hours_dict(self, schedule_list: list[dict[str, Any]]) -> ExpectedWorkingHoursDict:
        min_date, max_date = _get_min_max_date_from_schedule_list(schedule_list)
        query_params = {"term_start": min_date, "term_end": max_date}
        logger.debug(f"予定稼働時間を取得します。 :: {query_params=}")
        expected_working_times = self.annowork_service.api.get_expected_working_times(self.workspace_id, query_params=query_params)
        return {(e["date"], e["workspace_member_id"]): e["expected_working_hours"] for e in expected_working_times}

    def get_assigned_hours_daily_list(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        job_ids: Collection[str] | None = None,
        user_ids: Collection[str] | None = None,
    ) -> list[AssignedHoursDaily]:
        schedule_list = self.list_schedule_obj.get_schedules(start_date=start_date, end_date=end_date, job_ids=job_ids, user_ids=user_ids)

        if len(schedule_list) == 0:
            return []

        result_dict: AssignedHoursDict = defaultdict(float)
        expected_working_hours_dict = self.get_expected_working_hours_dict(schedule_list)

        for schedule in schedule_list:
            workspace_member_id = schedule["workspace_member_id"]
            job_id = schedule["job_id"]

            tmp = create_assigned_hours_dict(schedule, expected_working_hours_dict)

            for date, assigned_hours in tmp.items():
                result_dict[(date, workspace_member_id, job_id)] += assigned_hours

        all_members_dict = {e["workspace_member_id"]: e for e in self.list_schedule_obj.workspace_members}
        all_jobs = self.annowork_service.api.get_jobs(self.workspace_id)
        all_jobs_dict = {e["job_id"]: e for e in all_jobs}

        result_list: list[AssignedHoursDaily] = []
        for (date, workspace_member_id, job_id), assigned_hours in result_dict.items():
            if assigned_hours == 0:
                # アサイン時間が0の情報は不要なので、出力しないようにする
                continue

            if start_date is not None and not date >= start_date:
                continue
            if end_date is not None and not date <= end_date:
                continue

            job = all_jobs_dict.get(job_id)
            if job is None:
                logger.warning(f"{job_id=} であるジョブは存在しません。 :: date='{date}', workspace_member_id='{workspace_member_id}'")

            member = all_members_dict.get(workspace_member_id)
            if member is None:
                logger.warning(f"{workspace_member_id=} であるメンバーは存在しません。 :: date='{date}', job_id='{job_id}'")

            result_list.append(
                AssignedHoursDaily(
                    date=date,
                    workspace_member_id=workspace_member_id,
                    job_id=job_id,
                    assigned_working_hours=assigned_hours,
                    job_name=job["job_name"] if job is not None else None,
                    user_id=member["user_id"] if member is not None else None,
                    username=member["username"] if member is not None else None,
                )
            )

        return result_list

    def main(
        self,
        *,
        output: Path,
        output_format: OutputFormat,
        start_date: str | None,
        end_date: str | None,
        job_id_list: list[str] | None,
        user_id_list: list[str] | None,
    ) -> None:
        result = self.get_assigned_hours_daily_list(
            start_date=start_date,
            end_date=end_date,
            job_ids=job_id_list,
            user_ids=user_id_list,
        )
        if len(result) > 0:
            result.sort(key=lambda e: e.date)
        else:
            logger.warning("アサイン時間情報は0件です。")

        logger.info(f"{len(result)} 件のアサイン時間情報を出力します。")

        if output_format == OutputFormat.JSON:
            # `.schema().dump(many=True)`を使わない理由：使うと警告が発生するから
            # https://qiita.com/yuji38kwmt/items/a3625b2011aff1d9901b
            dict_result = []
            for elm in result:
                dict_result.append(elm.to_dict())  # noqa: PERF401
            print_json(dict_result, is_pretty=True, output=output)
        else:
            if len(result) > 0:
                df = pandas.DataFrame(result)
            else:
                # 空のデータフレームを作成（属性情報を含める）
                df = pandas.DataFrame(columns=["date", "job_id", "job_name", "workspace_member_id", "user_id", "username", "assigned_working_hours"])
            print_csv(df, output=output)


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    user_id_list = get_list_from_args(args.user_id)

    start_date: str | None = args.start_date
    end_date: str | None = args.end_date

    if all(v is None for v in [job_id_list, user_id_list, start_date, end_date]):
        logger.warning(
            "'--start_date'や'--job_id'などの絞り込み条件が1つも指定されていません。"
            "WebAPIから取得するデータ量が多すぎて、WebAPIのリクエストが失敗するかもしれません。"
        )

    ListAssignedHoursDaily(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
    ).main(
        job_id_list=job_id_list,
        user_id_list=user_id_list,
        start_date=start_date,
        end_date=end_date,
        output=args.output,
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

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="絞り込み対象のユーザID")

    parser.add_argument("-j", "--job_id", type=str, nargs="+", required=False, help="取得対象のジョブID")

    parser.add_argument("--start_date", type=str, required=False, help="取得する範囲の開始日")
    parser.add_argument("--end_date", type=str, required=False, help="取得する範囲の終了日")

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
    subcommand_name = "list_daily"
    subcommand_help = "作業計画から求めたアサイン時間を日ごとに出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
