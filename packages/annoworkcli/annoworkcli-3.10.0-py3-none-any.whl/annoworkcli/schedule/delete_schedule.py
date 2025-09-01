import argparse
import logging
from collections.abc import Collection

import requests
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import (
    build_annoworkapi,
    get_list_from_args,
    prompt_yesnoall,
)

logger = logging.getLogger(__name__)


class DeleteSchedule:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
        workspace_id: str,
        *,
        all_yes: bool,
    ) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

        self.all_yes = all_yes

    def delete_schedule(
        self, schedule_ids: Collection[str], *, target_user_ids: Collection[str] | None = None, target_job_ids: Collection[str] | None = None
    ) -> None:
        all_jobs = self.annowork_service.api.get_jobs(self.workspace_id)
        all_job_dict = {e["job_id"]: e for e in all_jobs}
        all_members = self.annowork_service.api.get_workspace_members(self.workspace_id, query_params={"includes_inactive_members": True})
        all_member_dict = {e["workspace_member_id"]: e for e in all_members}

        target_user_ids = set(target_user_ids) if target_user_ids is not None else None
        target_job_ids = set(target_job_ids) if target_job_ids is not None else None

        success_count = 0
        for index, schedule_id in enumerate(schedule_ids):
            try:
                schedule = self.annowork_service.api.get_schedule(self.workspace_id, schedule_id)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == requests.codes.not_found:
                    logger.warning(f"schedule_id='{schedule_id}'の作業計画情報は存在しません。作業計画情報の削除をスキップします。")
                    continue
                raise e

            if target_job_ids is not None:
                if schedule["job_id"] in target_job_ids:
                    continue

            job = all_job_dict.get(schedule["job_id"])
            member = all_member_dict.get(schedule["workspace_member_id"])
            job_name = job["job_name"] if job is not None else None
            user_id = member["user_id"] if member is not None else None

            if target_user_ids is not None:
                if user_id != target_user_ids:
                    continue

            if not self.all_yes:
                message = (
                    f"schedule_id='{schedule_id}', start_date='{schedule['start_date']}, end_date='{schedule['end_date']}, "
                    f"user_id='{user_id}', job_name='{job_name}' である作業計画情報を削除しますか？"
                )
                is_yes, all_yes = prompt_yesnoall(message)
                if not is_yes:
                    continue
                if all_yes:
                    self.all_yes = all_yes

            try:
                self.annowork_service.api.delete_schedule(self.workspace_id, schedule_id)
                logger.debug(
                    f"{index + 1} 件目: 作業計画情報を削除しました。:: "
                    f"schedule_id='{schedule_id}', start_date='{schedule['start_date']}, end_date='{schedule['end_date']}, "
                    f"user_id='{user_id}', job_name='{job_name}'"
                )
                success_count += 1
            except requests.exceptions.HTTPError:
                logger.debug(
                    f"{index + 1} 件目: 作業計画情報の削除に失敗しました。:: "
                    f"schedule_id='{schedule_id}', start_date='{schedule['start_date']}, end_date='{schedule['end_date']}, "
                    f"user_id='{user_id}', job_name='{job_name}'",
                    exc_info=True,
                )
                continue

        logger.info(f"{success_count} / {len(schedule_ids)} 件の作業計画情報を削除しました。")


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)

    schedule_id_list = get_list_from_args(args.schedule_id)
    assert schedule_id_list is not None
    user_id_list = get_list_from_args(args.user_id)
    job_id_list = get_list_from_args(args.job_id)
    DeleteSchedule(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
        all_yes=args.yes,
    ).delete_schedule(schedule_ids=schedule_id_list, target_job_ids=job_id_list, target_user_ids=user_id_list)


def parse_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument(
        "--schedule_id",
        type=str,
        nargs="+",
        required=True,
        help="削除したい作業計画の`schedule_id`を指定してください。",
    )

    parser.add_argument("-j", "--job_id", type=str, required=False, nargs="+", help="指定したjob_idに一致する作業計画情報のみ削除します。")
    parser.add_argument("-u", "--user_id", type=str, required=False, nargs="+", help="指定したuser_idに一致する作業計画情報のみ削除します。")

    parser.add_argument("-y", "--yes", type=str, help="すべてのプロンプトに自動的に 'yes' と答えます。")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "delete"
    subcommand_help = "作業計画情報を削除します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
