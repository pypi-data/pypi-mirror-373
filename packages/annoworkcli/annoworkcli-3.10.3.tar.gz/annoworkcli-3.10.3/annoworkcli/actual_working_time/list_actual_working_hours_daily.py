import argparse
import datetime
import json
import logging
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas
from annoworkapi.job import get_parent_job_id_from_job_tree
from annoworkapi.resource import Resource as AnnoworkResource
from annoworkapi.utils import str_to_datetime
from dataclasses_json import DataClassJsonMixin

import annoworkcli
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)

ActualWorkingHoursDict = dict[tuple[datetime.date, str, str], float]
"""実績作業時間の日ごとの情報を格納する辞書
key: (date, workspace_member_id, job_id), value: 実績作業時間
"""

ActualWorkingTimeNoteDict = dict[tuple[datetime.date, str, str], list[str]]
"""実績作業の備考を格納する辞書
key: (date, workspace_member_id, job_id), value: 備考のlist
dateは実績のstart_datetimeから算出する
"""


@dataclass
class ActualWorkingHoursDaily(DataClassJsonMixin):
    date: str
    job_id: str
    job_name: str
    workspace_member_id: str
    user_id: str
    username: str
    actual_working_hours: float
    notes: list[str] | None


@dataclass
class ActualWorkingHoursDailyWithParentJob(ActualWorkingHoursDaily):
    parent_job_id: str | None
    parent_job_name: str | None


@dataclass
class SimpleJob(DataClassJsonMixin):
    job_id: str
    job_name: str


@dataclass
class SimpleWorkspaceMember(DataClassJsonMixin):
    workspace_member_id: str
    user_id: str
    username: str


def _create_actual_working_hours_dict(actual: dict[str, Any], tzinfo: datetime.timezone) -> ActualWorkingHoursDict:
    results_dict: ActualWorkingHoursDict = {}

    dt_local_start_datetime = str_to_datetime(actual["start_datetime"]).astimezone(tzinfo)
    dt_local_end_datetime = str_to_datetime(actual["end_datetime"]).astimezone(tzinfo)

    workspace_member_id = actual["workspace_member_id"]
    job_id = actual["job_id"]

    if dt_local_start_datetime.date() == dt_local_end_datetime.date():
        actual_working_hours = (dt_local_end_datetime - dt_local_start_datetime).total_seconds() / 3600
        results_dict[(dt_local_start_datetime.date(), workspace_member_id, job_id)] = actual_working_hours
    else:
        dt_tmp_local_start_datetime = dt_local_start_datetime

        # 実績作業時間が24時間を超えることはないが、24時間を超えても計算できるような処理にする
        while dt_tmp_local_start_datetime.date() < dt_local_end_datetime.date():
            dt_next_date = dt_tmp_local_start_datetime.date() + datetime.timedelta(days=1)
            dt_tmp_local_end_datetime = datetime.datetime(year=dt_next_date.year, month=dt_next_date.month, day=dt_next_date.day, tzinfo=tzinfo)
            actual_working_hours = (dt_tmp_local_end_datetime - dt_tmp_local_start_datetime).total_seconds() / 3600
            results_dict[(dt_tmp_local_start_datetime.date(), workspace_member_id, job_id)] = actual_working_hours
            dt_tmp_local_start_datetime = dt_tmp_local_end_datetime

        actual_working_hours = (dt_local_end_datetime - dt_tmp_local_start_datetime).total_seconds() / 3600
        results_dict[(dt_local_end_datetime.date(), workspace_member_id, job_id)] = actual_working_hours

    return results_dict


def create_actual_working_hours_daily_list(
    actual_working_time_list: list[dict[str, Any]],
    timezone_offset_hours: float | None = None,
    show_notes: bool = True,  # noqa: FBT001, FBT002
) -> list[ActualWorkingHoursDaily]:
    results_dict: ActualWorkingHoursDict = defaultdict(float)
    notes_dict: ActualWorkingTimeNoteDict = defaultdict(list)

    job_dict: dict[str, SimpleJob] = {}
    member_dict: dict[str, SimpleWorkspaceMember] = {}

    # none 判定
    if timezone_offset_hours is not None:
        tzinfo = datetime.timezone(datetime.timedelta(hours=timezone_offset_hours))
    else:
        tzinfo = datetime.datetime.now().astimezone().tzinfo  # type: ignore[assignment]

    for actual in actual_working_time_list:
        tmp_results = _create_actual_working_hours_dict(actual, tzinfo=tzinfo)

        for key, value in tmp_results.items():
            results_dict[key] += value

        if actual["workspace_member_id"] not in member_dict:
            member_dict[actual["workspace_member_id"]] = SimpleWorkspaceMember(
                workspace_member_id=actual["workspace_member_id"],
                user_id=actual["user_id"],
                username=actual["username"],
            )

        if actual["job_id"] not in job_dict:
            job_dict[actual["job_id"]] = SimpleJob(
                job_id=actual["job_id"],
                job_name=actual["job_name"],
            )

    # 備考情報を取得
    if show_notes:
        for actual in actual_working_time_list:
            date = str_to_datetime(actual["start_datetime"]).astimezone(tzinfo).date()
            if actual["note"] is not None and actual["note"] != "":
                notes_dict[(date, actual["workspace_member_id"], actual["job_id"])].append(actual["note"])

    results_list: list[ActualWorkingHoursDaily] = []
    for (date, workspace_member_id, job_id), actual_working_hours in results_dict.items():
        if actual_working_hours == 0:
            # 実績作業時間が0の情報は不要なので、出力しないようにする
            continue

        job = job_dict[job_id]
        member = member_dict[workspace_member_id]
        results_list.append(
            ActualWorkingHoursDaily(
                date=str(date),
                workspace_member_id=workspace_member_id,
                job_id=job_id,
                actual_working_hours=actual_working_hours,
                job_name=job.job_name,
                user_id=member.user_id,
                username=member.username,
                notes=notes_dict.get((date, workspace_member_id, job_id)),
            )
        )

    return results_list


def get_actual_working_time_list_from_input_file(input_file: Path) -> list[dict[str, Any]]:
    """input_fileから実績作業時間情報を取得する。
    拡張子がjsonかcsvかで読み込み方法を変更する。

    Args:
        input_file (Path): [description]

    Returns:
        list[dict[str,Any]]: [description]
    """
    if input_file.suffix.lower() == ".json":
        with input_file.open(encoding="utf-8") as f:
            return json.load(f)

    elif input_file.suffix.lower() == ".csv":
        df = pandas.read_csv(str(input_file))
        return df.to_dict("records")

    else:
        raise RuntimeError(f" '--input' に指定したファイル '{input_file}' の拡張子はサポート対象外です。拡張子はcsv,jsonのみサポートしています。")


def filter_actual_daily_list(
    actual_daily_list: Sequence[ActualWorkingHoursDaily], start_date: str | None, end_date: str | None
) -> list[ActualWorkingHoursDaily]:
    if start_date is None and end_date is None:
        return list(actual_daily_list)

    def is_match(elm: ActualWorkingHoursDaily) -> bool:
        result = True
        if start_date is not None:
            result = result and elm.date >= start_date
        if end_date is not None:
            result = result and elm.date <= end_date
        return result

    return [e for e in actual_daily_list if is_match(e)]


class ListActualWorkingHoursDaily:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def add_parent_job_info(self, daily_list: Sequence[ActualWorkingHoursDaily]) -> list[ActualWorkingHoursDailyWithParentJob]:
        all_job_list = self.annowork_service.api.get_jobs(self.workspace_id)
        all_job_dict = {e["job_id"]: e for e in all_job_list}
        parent_job_id_set = {get_parent_job_id_from_job_tree(e["job_tree"]) for e in all_job_list}
        parent_job_id_set.discard(None)

        result = []
        for elm in daily_list:
            job = all_job_dict[elm.job_id]
            parent_job_id = get_parent_job_id_from_job_tree(job["job_tree"])
            parent_job_name = all_job_dict[parent_job_id]["job_name"] if parent_job_id is not None else None
            d = elm.to_dict()
            d["parent_job_id"] = parent_job_id
            d["parent_job_name"] = parent_job_name
            tmp = ActualWorkingHoursDailyWithParentJob.from_dict(d)
            result.append(tmp)
        return result


def get_required_columns() -> list[str]:
    required_columns = [
        "date",
        "parent_job_id",
        "parent_job_name",
        "job_id",
        "job_name",
        "workspace_member_id",
        "user_id",
        "username",
        "actual_working_hours",
        "notes",
    ]
    return required_columns


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    user_id_list = get_list_from_args(args.user_id)
    start_date: str | None = args.start_date
    end_date: str | None = args.end_date

    if all(v is None for v in [job_id_list, parent_job_id_list, user_id_list, start_date, end_date]):
        logger.warning(
            "'--start_date'や'--job_id'などの絞り込み条件が1つも指定されていません。"
            "WebAPIから取得するデータ量が多すぎて、WebAPIのリクエストが失敗するかもしれません。"
        )

    main_obj = ListActualWorkingHoursDaily(annowork_service, args.workspace_id)

    list_actual_working_time_obj = ListActualWorkingTime(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
        timezone_offset_hours=args.timezone_offset,
    )
    actual_working_time_list = list_actual_working_time_obj.get_actual_working_times(
        job_ids=job_id_list,
        parent_job_ids=parent_job_id_list,
        user_ids=user_id_list,
        start_date=args.start_date,
        end_date=args.end_date,
        is_set_additional_info=False,
    )
    list_actual_working_time_obj.set_additional_info_to_actual_working_time(actual_working_time_list)

    logger.debug(f"{len(actual_working_time_list)} 件の実績作業時間情報を日ごとに集約します。")
    result: Sequence[ActualWorkingHoursDaily] = create_actual_working_hours_daily_list(
        actual_working_time_list, timezone_offset_hours=args.timezone_offset, show_notes=True
    )

    result = filter_actual_daily_list(result, start_date=start_date, end_date=end_date)
    result = main_obj.add_parent_job_info(result)
    logger.info(f"{len(result)} 件の日ごとの実績作業時間情報を出力します。")

    if OutputFormat(args.format) == OutputFormat.JSON:
        # `.schema().dump(many=True)`を使わない理由：使うと警告が発生するから
        # https://qiita.com/yuji38kwmt/items/a3625b2011aff1d9901b
        dict_result = []
        for elm in result:
            dict_result.append(elm.to_dict())  # noqa: PERF401

        print_json(dict_result, is_pretty=True, output=args.output)
    else:
        required_columns = get_required_columns()
        if len(result) > 0:
            df = pandas.DataFrame(result)
        else:
            df = pandas.DataFrame(columns=required_columns)
        print_csv(df[required_columns], output=args.output)


def parse_args(parser: argparse.ArgumentParser) -> None:
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
    subcommand_name = "list_daily"
    subcommand_help = "実績作業時間を日ごとに集約した情報を一覧として出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
