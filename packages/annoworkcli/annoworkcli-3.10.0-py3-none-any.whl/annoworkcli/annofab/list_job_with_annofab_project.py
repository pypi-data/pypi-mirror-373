import argparse
import logging
import multiprocessing
from pathlib import Path
from typing import Any

import pandas
from annofabapi.resource import Resource as AnnofabResource
from annoworkapi.annofab import get_annofab_project_id_from_url
from annoworkapi.job import get_parent_job_id_from_job_tree
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.annofab.utils import build_annofabapi_resource
from annoworkcli.common.annofab import get_annofab_project_id_from_job
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.job.list_job import ListJob

logger = logging.getLogger(__name__)


def get_annofab_project_ids(job_list: list[dict[str, Any]]) -> set[str]:
    """job_listから, annofab project_idの集合を取得する。"""
    # annofabプロジェクトの取得は時間がかかるので、並列化する
    af_project_id_set = set()
    for job in job_list:
        url = job["external_linkage_info"].get("url")
        if url is None:
            continue
        af_project_id = get_annofab_project_id_from_url(url)
        if af_project_id is None:
            continue
        af_project_id_set.add(af_project_id)
    return af_project_id_set


class ListJobWithAnnofabProject:
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
        self.list_job_obj = ListJob(annowork_service, workspace_id)

    def get_af_project_dict(self, job_list: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """
        keyがAnnofabのproject_id, valueがAnnofabプロジェクトのdictを返します。
        """
        # annofabプロジェクトの取得は時間がかかるので、並列化する
        af_project_ids = get_annofab_project_ids(job_list)

        logger.info(f"{len(af_project_ids)} 件のAnnofabプロジェクトの情報を取得します。")
        if self.parallelism is not None:
            with multiprocessing.Pool(self.parallelism) as pool:
                af_project_list = pool.map(self.annofab_service.wrapper.get_project_or_none, af_project_ids)
            return {e["project_id"]: e for e in af_project_list if e is not None}
        else:
            result = {}
            for index, af_project_id in enumerate(af_project_ids):
                af_project = self.annofab_service.wrapper.get_project_or_none(af_project_id)
                if af_project is None:
                    logger.warning(f"annofab_project_id='{af_project_id}'のAnnofabプロジェクトは存在しません。")
                    continue
                result[af_project["project_id"]] = af_project
                if (index + 1) % 100 == 0:
                    logger.debug(f"{index + 1}件のAnnofabプロジェクト情報を取得しました。")

            return result

    def get_job_list_added_annofab_project(
        self,
        job_id_list: list[str] | None = None,
        parent_job_id_list: list[str] | None = None,
        annofab_project_id_list: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        job_list = self.list_job_obj.get_job_list(
            job_id_list=job_id_list,
            parent_job_id_list=parent_job_id_list,
        )

        if annofab_project_id_list is not None:
            job_list = [job for job in job_list if get_annofab_project_id_from_job(job) in set(annofab_project_id_list)]

        all_job_dict = {e["job_id"]: e for e in self.annowork_service.api.get_jobs(self.workspace_id)}

        af_project_dict = self.get_af_project_dict(job_list)

        for job in job_list:
            parent_job_id = get_parent_job_id_from_job_tree(job["job_tree"])
            parent_job_name = all_job_dict[parent_job_id]["job_name"] if parent_job_id is not None else None
            job["parent_job_id"] = parent_job_id
            job["parent_job_name"] = parent_job_name

            external_linkage_info_url = job["external_linkage_info"].get("url")
            if external_linkage_info_url is None:
                job["annofab"] = None
                continue

            af_project_id = get_annofab_project_id_from_url(external_linkage_info_url)
            if af_project_id is None:
                job["annofab"] = None
                continue

            af_project = af_project_dict.get(af_project_id)
            if af_project is None:
                logger.warning(f"annofab_project_id='{af_project_id}' のAnnofabプロジェクトを取得できませんでした。:: job_id={job['job_id']}")
                job["annofab"] = None
                continue

            job["annofab"] = {
                "project_id": af_project["project_id"],
                "project_title": af_project["title"],
                "project_status": af_project["project_status"],
                "input_data_type": af_project["input_data_type"],
            }
        return job_list


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    annofab_project_id_list = get_list_from_args(args.annofab_project_id)

    main_obj = ListJobWithAnnofabProject(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
        annofab_service=build_annofabapi_resource(
            annofab_login_user_id=args.annofab_user_id,
            annofab_login_password=args.annofab_password,
            annofab_pat=args.annofab_pat,
        ),
        parallelism=args.parallelism,
    )
    job_list = main_obj.get_job_list_added_annofab_project(
        job_id_list=job_id_list,
        parent_job_id_list=parent_job_id_list,
        annofab_project_id_list=annofab_project_id_list,
    )

    if len(job_list) == 0:
        logger.warning("ジョブの一覧が0件です。")

    logger.info(f"{len(job_list)} 件のジョブの一覧を出力します。")

    if OutputFormat(args.format) == OutputFormat.JSON:
        print_json(job_list, is_pretty=True, output=args.output)
    else:
        if len(job_list) > 0:
            df = pandas.json_normalize(job_list)
        else:
            # 空のDataFrameを作成（最低限の列を含める）
            df = pandas.DataFrame(
                columns=["workspace_id", "job_id", "job_name", "parent_job_id", "parent_job_name", "annofab_project_id", "annofab_project_title"]
            )
        print_csv(df, output=args.output)


def parse_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    job_id_group = parser.add_mutually_exclusive_group()
    job_id_group.add_argument(
        "-j",
        "--job_id",
        type=str,
        nargs="+",
        help="絞り込み対象であるジョブのjob_idを指定してください。",
    )

    job_id_group.add_argument(
        "-pj",
        "--parent_job_id",
        type=str,
        nargs="+",
        help="絞り込み対象である親のジョブのjob_idを指定してください。",
    )

    parser.add_argument(
        "-af_p",
        "--annofab_project_id",
        type=str,
        nargs="+",
        required=False,
        help="絞り込み対象であるAnnofabプロジェクトのproject_idを指定してください。",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.add_argument("-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value)

    parser.add_argument("--parallelism", type=int, required=False, help="並列度。指定しない場合は、逐次的に処理します。")

    parser.add_argument("--annofab_user_id", type=str, help="Annofabにログインする際のユーザID")
    parser.add_argument("--annofab_password", type=str, help="Annofabにログインする際のパスワード")
    parser.add_argument("--annofab_pat", type=str, help="Annofabにログインする際のパーソナルアクセストークン")
    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "list_job"
    subcommand_help = "ジョブとジョブに紐づくAnnofabプロジェクトの情報を一緒に出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
