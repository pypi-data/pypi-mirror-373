import argparse
import functools
import itertools
import logging
import multiprocessing
from collections.abc import Collection
from pathlib import Path
from typing import Any

import pandas
import requests
from annofabapi.resource import Resource as AnnofabResource
from annoworkapi.job import get_parent_job_id_from_job_tree
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.actual_working_time.list_actual_working_hours_daily import (
    ActualWorkingHoursDaily,
    create_actual_working_hours_daily_list,
    filter_actual_daily_list,
)
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime
from annoworkcli.annofab.utils import build_annofabapi_resource
from annoworkcli.common.annofab import TIMEZONE_OFFSET_HOURS, get_annofab_project_id_from_job, isoduration_to_hour
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


def fill_missing_job_id(df: pandas.DataFrame) -> pandas.DataFrame:
    """
    以下の列が欠損しないように適切な値を埋めます。

    """

    # job_idからannofab_project_idが一意に決まるように、job_idとjob_nameには、annofab_projectの情報を埋め込む。
    mask = df["job_id"].isna()
    df.loc[mask, "job_id"] = "dummy_job_id__" + df.loc[mask, "annofab_project_id"]
    df.loc[mask, "job_name"] = "dummy_job_name__" + df.loc[mask, "annofab_project_title"]

    df = df.fillna(
        {
            "parent_job_id": "dummy_parent_job_id",
            "parent_job_name": "dummy_parent_job_name",
        }
    )

    return df


def _get_df_working_hours_from_df(
    *,
    df_actual_working_hours: pandas.DataFrame,
    df_user_and_af_account: pandas.DataFrame,
    df_job_and_af_project: pandas.DataFrame,
    df_af_working_hours: pandas.DataFrame,
) -> pandas.DataFrame:
    """
    引数で受け取ったDataFrameをマージしたDataFrameを返します。

    Args:
        df_actual_working_hours: 実績作業時間情報
        df_user_and_af_account: ユーザ情報とAnnofabアカウント情報
        df_job_and_af_project: ジョブ情報とAnnofabプロジェクト情報
        df_af_working_hours: Annofabの作業時間情報
    """
    # annowork側の作業時間情報
    df_aw_working_hours = df_actual_working_hours.merge(df_user_and_af_account[["user_id", "annofab_account_id"]], how="left", on="user_id").merge(
        df_job_and_af_project[["job_id", "annofab_project_id"]],
        how="left",
        on="job_id",
    )

    df_merged = df_aw_working_hours.merge(df_af_working_hours, how="outer", on=["date", "annofab_project_id", "annofab_account_id"])

    TMP_SUFFIX = "_tmp"  # noqa: N806
    # df_merged は outer joinしているため、左側にも欠損値ができる。
    # それを埋めるために、以前に user情報, job情報の一意な dataframe を生成して、欠損値を埋める
    USER_COLUMNS = ["workspace_member_id", "user_id", "username"]  # noqa: N806
    df_merged = df_merged.merge(df_user_and_af_account, how="left", on="annofab_account_id", suffixes=(None, TMP_SUFFIX))
    for user_column in USER_COLUMNS:
        df_merged[user_column] = df_merged[user_column].fillna(df_merged[f"{user_column}{TMP_SUFFIX}"])

    # job_id, job_nameの欠損値を、df_job_and_af_project を使って埋める
    # af_projectに紐付いているジョブとaf_projectのDataFrameを生成して、それを使って欠損値を埋める
    # drop_duplicatesの理由: AnnoworkのジョブとAnnofabのプロジェクトが1対1で紐づくときだけ、df_mergeのjob_idとjob_nameの欠損値を埋めるようにするため
    df_job_id_af_project = df_job_and_af_project[df_job_and_af_project["annofab_project_id"].notna()].drop_duplicates(
        ["annofab_project_id"], keep=False
    )
    df_merged = df_merged.merge(
        df_job_id_af_project[["job_id", "job_name", "annofab_project_id"]],
        how="left",
        on=["annofab_project_id"],
        suffixes=(None, TMP_SUFFIX),
    )
    df_merged["job_id"] = df_merged["job_id"].fillna(df_merged[f"job_id{TMP_SUFFIX}"])
    df_merged["job_name"] = df_merged["job_name"].fillna(df_merged[f"job_name{TMP_SUFFIX}"])

    # annofab_project_titleを結合するために、annofab_projectだけのDataFrameを生成する
    df_af_project = df_job_and_af_project.drop_duplicates(subset=["annofab_project_id"])[["annofab_project_id", "annofab_project_title"]]
    df_merged = df_merged.merge(df_af_project, on="annofab_project_id", how="left")

    df_merged = df_merged.fillna(
        {
            "actual_working_hours": 0.0,
            "annofab_working_hours": 0.0,
        },
    )

    return df_merged[
        [
            "date",
            "job_id",
            "job_name",
            *USER_COLUMNS,
            "actual_working_hours",
            "annofab_project_id",
            "annofab_project_title",
            "annofab_account_id",
            "annofab_working_hours",
            "notes",
        ]
    ]


class ListWorkingHoursWithAnnofab:
    def __init__(
        self,
        *,
        annowork_service: AnnoworkResource,
        workspace_id: str,
        annofab_service: AnnofabResource,
        parallelism: int | None = None,
    ) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id
        self.annofab_service = annofab_service
        self.parallelism = parallelism

        self.all_jobs = self.annowork_service.api.get_jobs(self.workspace_id)
        self.all_workspace_members = self.annowork_service.api.get_workspace_members(
            self.workspace_id, query_params={"includes_inactive_members": True}
        )

        self.list_actual_working_time_obj = ListActualWorkingTime(annowork_service, workspace_id, timezone_offset_hours=TIMEZONE_OFFSET_HOURS)

    def get_actual_working_hours_daily(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        job_ids: Collection[str] | None = None,
        parent_job_ids: Collection[str] | None = None,
        user_ids: Collection[str] | None = None,
    ) -> list[ActualWorkingHoursDaily]:
        actual_working_time_list = self.list_actual_working_time_obj.get_actual_working_times(
            job_ids=job_ids,
            parent_job_ids=parent_job_ids,
            user_ids=user_ids,
            start_date=start_date,
            end_date=end_date,
            is_set_additional_info=False,
        )
        self.list_actual_working_time_obj.set_additional_info_to_actual_working_time(actual_working_time_list)

        result = create_actual_working_hours_daily_list(actual_working_time_list, timezone_offset_hours=TIMEZONE_OFFSET_HOURS)
        result = filter_actual_daily_list(result, start_date=start_date, end_date=end_date)
        return result

    def _get_df_user_and_af_account(self, user_ids: Collection[str]) -> pandas.DataFrame:
        """ユーザ情報とAnnofabのアカウント情報格納されたpandas.DataFrameを返します。
        以下の列を持ちます。
        * user_id
        * username
        * workspace_member_id
        * annofab_account_id
        """
        af_account_list = []
        logger.debug(f"{len(user_ids)} 件のユーザのアカウント外部連携情報を取得します。")
        for user_id in user_ids:
            annofab_account_id = self.annowork_service.wrapper.get_annofab_account_id_from_user_id(user_id)
            if annofab_account_id is None:
                logger.warning(f"{user_id=} の外部連携情報にAnnofabのaccount_idは設定されていませんでした。")
            af_account_list.append({"user_id": user_id, "annofab_account_id": annofab_account_id})

        df_af_account = pandas.DataFrame(af_account_list, columns=["user_id", "annofab_account_id"]).astype("string")

        df_user = pandas.DataFrame(self.all_workspace_members, columns=["user_id", "username", "workspace_member_id"]).astype("string")

        df = df_user.merge(df_af_account, how="inner", on="user_id")
        return df

    def _get_df_job_and_af_project(self, job_ids: Collection[str]) -> pandas.DataFrame:
        """
        job_idとAnnofabのプロジェクト情報が格納されたpandas.DataFrameを返します。

        Returns:
            job_idとAnnofabのプロジェクト情報が格納されたpandas.DataFrame。
            以下の列が存在します。
                * job_id
                * annofab_project_id
                * annofab_project_title
        """

        def get_project_title(project_id: str) -> str | None:
            project = self.annofab_service.wrapper.get_project_or_none(project_id)
            if project is None:
                return None
            return project["title"]

        all_job_dict = {e["job_id"]: e for e in self.all_jobs}

        df_job = pandas.DataFrame(self.all_jobs)

        # dtype="string"を指定する理由: dtypeを指定しないとdtypeがfloatになり、後続のmerge処理でdtypeが一致しないというエラーが発生するため
        # 参考サイト: https://qiita.com/yuji38kwmt/items/74d1990bc8554f8b81ef
        df_af_project = pandas.DataFrame({"job_id": list(job_ids)}, dtype="string")
        df_af_project["annofab_project_id"] = df_af_project["job_id"].apply(lambda e: get_annofab_project_id_from_job(all_job_dict[e]))
        df_af_project["annofab_project_title"] = df_af_project["annofab_project_id"].apply(get_project_title)
        df = df_job.merge(df_af_project, how="inner", on="job_id")
        return df[["job_id", "job_name", "annofab_project_id", "annofab_project_title"]]

    def _get_af_working_hours_from_af_project(self, af_project_id: str, start_date: str | None, end_date: str | None) -> list[dict[str, Any]]:
        try:
            logger.debug(f"annofab_project_id= '{af_project_id}' のAnnofabプロジェクトの作業時間を取得します。:: {start_date=}, {end_date=}")
            account_statistics = self.annofab_service.wrapper.get_account_daily_statistics(af_project_id, from_date=start_date, to_date=end_date)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == requests.codes.not_found:
                logger.warning(f"annofab_project_id= '{af_project_id}' は存在しません。")
            else:
                logger.warning(f"annofab_project_id= '{af_project_id}' の作業時間を取得できませんでした。:: {e}")
            return []

        result = []
        for account_info in account_statistics:
            af_account_id = account_info["account_id"]
            histories = account_info["histories"]
            for history in histories:
                working_hours = isoduration_to_hour(history["worktime"])
                if working_hours > 0:
                    result.append(
                        {
                            "annofab_project_id": af_project_id,
                            "annofab_account_id": af_account_id,
                            "date": history["date"],
                            "annofab_working_hours": working_hours,
                        }
                    )
        return result

    def _get_af_working_hours(self, af_project_ids: Collection[str], start_date: str | None, end_date: str | None) -> pandas.DataFrame:
        """Annofabの作業時間情報が格納されたDataFrameを返す。

        返すDataFrameには以下の列が存在します。
        * date
        * annofab_project_id
        * annofab_account_id
        * annofab_working_hours
        """
        result: list[dict[str, Any]] = []

        logger.debug(f"{len(af_project_ids)} 件のAnnofabプロジェクトの作業時間を取得します。")

        if self.parallelism is not None:
            partial_func = functools.partial(
                self._get_af_working_hours_from_af_project,
                start_date=start_date,
                end_date=end_date,
            )
            with multiprocessing.Pool(self.parallelism) as pool:
                tmp_result = pool.map(partial_func, af_project_ids)
                result = list(itertools.chain.from_iterable(tmp_result))

        else:
            for af_project_id in af_project_ids:
                result.extend(self._get_af_working_hours_from_af_project(af_project_id, start_date=start_date, end_date=end_date))

        if len(result) > 0:
            return pandas.DataFrame(result).astype(
                {"date": "string", "annofab_project_id": "string", "annofab_account_id": "string", "annofab_working_hours": "float64"}
            )

        df = pandas.DataFrame(columns=["date", "annofab_project_id", "annofab_account_id", "annofab_working_hours"]).astype(
            {"annofab_working_hours": "float64", "date": "string", "annofab_project_id": "string", "annofab_account_id": "string"}
        )
        # `astype()`を使用する理由：後続の処理で`fillna()`を実行した際に、「Downcasting object dtype arrays ～」というFutureWarningを発生させないようにするため  # noqa: E501
        # https://qiita.com/yuji38kwmt/items/ba07a25924cfda363e42
        return df

    def _get_df_job_parent_job(self) -> pandas.DataFrame:
        """job_id, parent_job_id, parent_job_nameが格納されたpandas.DataFrameを返します。"""
        all_job_dict = {e["job_id"]: e for e in self.all_jobs}

        df_job = pandas.DataFrame(self.all_jobs)
        df_job["parent_job_id"] = df_job["job_tree"].apply(get_parent_job_id_from_job_tree)

        df_parent_job = pandas.DataFrame({"parent_job_id": df_job["parent_job_id"].unique()})
        df_parent_job["parent_job_name"] = df_parent_job["parent_job_id"].apply(lambda e: all_job_dict[e]["job_name"] if e is not None else None)

        df = df_job.merge(df_parent_job, how="left", on="parent_job_id")
        return df[["job_id", "parent_job_id", "parent_job_name"]]

    @staticmethod
    def _get_required_columns() -> list[str]:
        job_columns = [
            "parent_job_id",
            "parent_job_name",
            "job_id",
            "job_name",
        ]
        user_columns = [
            "workspace_member_id",
            "user_id",
            "username",
        ]
        annofab_columns = ["annofab_project_id", "annofab_project_title", "annofab_account_id", "annofab_working_hours"]

        required_columns = ["date", *job_columns, *user_columns, "actual_working_hours", *annofab_columns]

        required_columns.append("notes")
        return required_columns

    def get_df_working_hours(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        job_ids: Collection[str] | None = None,
        user_ids: Collection[str] | None = None,
    ) -> pandas.DataFrame:
        def _get_af_project_ids(df: pandas.DataFrame) -> list[str]:
            """
            annoworkジョブとannofabプロジェクの情報が格納されたDataFrameから、アクセスできるAnnofabプロジェクトのIDのリストを返す。
            Annofabプロジェクトにアクセスできるかは、`annofab_project_title`が空かどうかで判定します。

            Args:
                df: annoworkジョブとannofabプロジェクの情報が格納されたDataFrame。以下の列を参照します。
                    * annofab_project_id
                    * annofab_project_title


            """
            df = df.drop_duplicates(subset=["annofab_project_id", "annofab_project_title"])
            # 補足：
            #  * annofab_project_idがnaのとき：Annofabプロジェクトに紐付いていないジョブ
            #  * annofab_project_titleがnaのとき：アクセスできないAnnofabプロジェクトに紐付いているジョブ
            df = df[df["annofab_project_id"].notna() & df["annofab_project_title"].notna()]
            # `unique()`を実行する理由：前述の`drop_duplicates`でannofab_project_idはユニークなはずだが、念の為`unique()`を実行した。
            return list(df["annofab_project_id"].unique())

        def _get_start_date(df: pandas.DataFrame) -> str | None:
            min_date = df["date"].min() if len(df) > 0 else None
            if start_date is None:
                return min_date
            if min_date is not None:
                return min(start_date, min_date)
            return None

        def _get_end_date(df: pandas.DataFrame) -> str | None:
            max_date = df["date"].max() if len(df) > 0 else None
            if end_date is None:
                return max_date
            if max_date is not None:
                return max(end_date, max_date)
            return None

        actual_working_hours_daily_list = self.get_actual_working_hours_daily(
            job_ids=job_ids, user_ids=user_ids, start_date=start_date, end_date=end_date
        )
        logger.info(f"実績作業時間は{len(actual_working_hours_daily_list)}件です。")
        df_actual_working_hours = pandas.DataFrame(
            actual_working_hours_daily_list,
            columns=[
                "date",
                "job_id",
                "job_name",
                "workspace_member_id",
                "user_id",
                "username",
                "actual_working_hours",
                "notes",
            ],
        ).astype(
            # astypeを指定する理由：`actual_working_hours_daily_list`が0件だと数値型の`actual_working_hours`のdtypeがobjectになり、
            # 後続の処理で想定外のエラーが発生する恐れがあるため
            {
                "date": "string",
                "job_id": "string",
                "job_name": "string",
                "workspace_member_id": "string",
                "user_id": "string",
                "username": "string",
                "actual_working_hours": "float64",
                "notes": "string",
            }
        )

        # df_actual_working_hours には含まれていないユーザがAnnofabプロジェクトで作業している可能性があるので、
        # user_id_listが指定された場合は、そのユーザのAnnofabアカウント情報も取得する。
        df_user_and_af_account = self._get_df_user_and_af_account(
            set(df_actual_working_hours["user_id"].unique()) | (set(user_ids) if user_ids is not None else set())
        )

        df_job_and_af_project = self._get_df_job_and_af_project(
            set(df_actual_working_hours["job_id"].unique()) | (set(job_ids) if job_ids is not None else set())
        )

        af_project_ids = _get_af_project_ids(df_job_and_af_project)
        df_af_working_hours = self._get_af_working_hours(
            af_project_ids=af_project_ids,
            start_date=_get_start_date(df_actual_working_hours),
            end_date=_get_end_date(df_actual_working_hours),
        )

        df = _get_df_working_hours_from_df(
            df_actual_working_hours=df_actual_working_hours,
            df_user_and_af_account=df_user_and_af_account,
            df_job_and_af_project=df_job_and_af_project,
            df_af_working_hours=df_af_working_hours,
        )
        if user_ids is not None:
            df = df[df["user_id"].isin(set(user_ids))]
        if start_date is not None:
            df = df[df["date"] >= start_date]
        if end_date is not None:
            df = df[df["date"] <= end_date]

        df_job_parent_job = self._get_df_job_parent_job()
        df = df.merge(df_job_parent_job, how="left", on="job_id")

        # 1個のAnnofabプロジェクトが複数のジョブに紐づいている場合、job_id, job_name, parent_job_id, parent_job_nameが欠損値になる可能性がある。
        # （Annofabで作業したがAnnoworkに実績作業時間を入力していない場合）
        # ユーザーはjobやparent_jobが欠損していないことを期待してCSVを出力するので、ダミーの値を設定する
        df = fill_missing_job_id(df)

        df.sort_values(["date", "job_id", "user_id"], inplace=True)
        required_columns = self._get_required_columns()
        return df[required_columns]

    def get_job_id_list_from_parent_job_id_list(self, parent_job_id_list: Collection[str]) -> list[str]:
        return [e["job_id"] for e in self.all_jobs if get_parent_job_id_from_job_tree(e["job_tree"]) in set(parent_job_id_list)]

    def get_job_id_list_from_annofab_project_id_list(self, annofab_project_id_list: list[str]) -> list[str]:
        annofab_project_id_set = set(annofab_project_id_list)

        def _match_job(job: dict[str, Any]) -> bool:
            af_project_id = get_annofab_project_id_from_job(job)
            if af_project_id is None:
                return False
            return af_project_id in annofab_project_id_set

        return [e["job_id"] for e in self.all_jobs if _match_job(e)]


def main(args: argparse.Namespace) -> None:
    job_id_list = get_list_from_args(args.job_id)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    annofab_project_id_list = get_list_from_args(args.annofab_project_id)
    user_id_list = get_list_from_args(args.user_id)
    start_date: str | None = args.start_date
    end_date: str | None = args.end_date

    if all(v is None for v in [job_id_list, parent_job_id_list, annofab_project_id_list, user_id_list, start_date, end_date]):
        logger.warning(
            "'--start_date'や'--job_id'などの絞り込み条件が1つも指定されていません。"
            "WebAPIから取得するデータ量が多すぎて、WebAPIのリクエストが失敗するかもしれません。"
        )

    main_obj = ListWorkingHoursWithAnnofab(
        annowork_service=build_annoworkapi(args),
        workspace_id=args.workspace_id,
        annofab_service=build_annofabapi_resource(
            annofab_login_user_id=args.annofab_user_id,
            annofab_login_password=args.annofab_password,
            annofab_pat=args.annofab_pat,
        ),
        parallelism=args.parallelism,
    )

    # job_id, parent_id, annofab_project_id は排他的なので、このような条件分岐を採用した。
    if parent_job_id_list is not None:
        job_id_list = main_obj.get_job_id_list_from_parent_job_id_list(parent_job_id_list)
    elif annofab_project_id_list is not None:
        job_id_list = main_obj.get_job_id_list_from_annofab_project_id_list(annofab_project_id_list)

    df = main_obj.get_df_working_hours(
        start_date=start_date,
        end_date=end_date,
        job_ids=job_id_list,
        user_ids=user_id_list,
    )

    logger.info(f"{len(df)} 件の作業時間情報を出力します。")

    if OutputFormat(args.format) == OutputFormat.JSON:
        print_json(df.to_dict("records"), is_pretty=True, output=args.output)
    else:
        if len(df) == 0:
            required_columns = main_obj._get_required_columns()
            df = pandas.DataFrame(columns=required_columns)
        print_csv(df, output=args.output)


def parse_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="絞り込み対象のユーザID")

    # parent_job_idとjob_idの両方を指定するユースケースはなさそうなので、exclusiveにする。
    job_id_group = parser.add_mutually_exclusive_group()
    job_id_group.add_argument("-j", "--job_id", type=str, nargs="+", required=False, help="絞り込み対象のジョブID")
    job_id_group.add_argument("-pj", "--parent_job_id", type=str, nargs="+", required=False, help="絞り込み対象の親のジョブID")

    job_id_group.add_argument(
        "-af_p",
        "--annofab_project_id",
        type=str,
        nargs="+",
        required=False,
        help="絞り込み対象であるAnnofabプロジェクトのproject_idを指定してください。",
    )

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

    parser.add_argument("--parallelism", type=int, required=False, help="並列度。指定しない場合は、逐次的に処理します。")
    parser.add_argument("--annofab_user_id", type=str, help="Annofabにログインする際のユーザID")
    parser.add_argument("--annofab_password", type=str, help="Annofabにログインする際のパスワード")
    parser.add_argument("--annofab_pat", type=str, help="Annofabにログインする際のパーソナルアクセストークン")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "list_working_hours"
    subcommand_help = "日ごとの実績作業時間と、ジョブに紐づくAnnofabプロジェクトの作業時間を一緒に出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
