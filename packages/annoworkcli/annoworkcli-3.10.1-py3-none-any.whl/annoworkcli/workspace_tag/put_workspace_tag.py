import argparse
import logging
import uuid

from annoworkapi.resource import Resource as AnnoworkResource
from more_itertools import first_true

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi

logger = logging.getLogger(__name__)


class PutWorkspaceTag:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str):  # noqa: ANN204
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def main(self, workspace_tag_name: str, workspace_tag_id: str | None):  # noqa: ANN201
        workspace_tags = self.annowork_service.api.get_workspace_tags(self.workspace_id)

        if workspace_tag_id is None:
            workspace_tag_id = str(uuid.uuid4())

        old_workspace_tag = first_true(workspace_tags, pred=lambda e: e["workspace_tag_id"] == workspace_tag_id)
        request_body = {"workspace_tag_name": workspace_tag_name}
        if old_workspace_tag is not None:
            request_body["last_updated_datetime"] = old_workspace_tag["updated_datetime"]

        content = self.annowork_service.api.put_workspace_tag(self.workspace_id, workspace_tag_id, request_body=request_body)
        logger.debug(f"{workspace_tag_name=} を登録しました。{content=}")


def main(args):  # noqa: ANN001, ANN201
    annowork_service = build_annoworkapi(args)
    PutWorkspaceTag(annowork_service=annowork_service, workspace_id=args.workspace_id).main(
        workspace_tag_name=args.workspace_tag_name, workspace_tag_id=args.workspace_tag_id
    )


def parse_args(parser: argparse.ArgumentParser):  # noqa: ANN201
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument(
        "--workspace_tag_name",
        type=str,
        required=True,
        help="登録対象のワークスペースタグの名前",
    )

    parser.add_argument(
        "-wt",
        "--workspace_tag_id",
        type=str,
        required=True,
        help="登録対象のワークスペースタグのID",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "put"
    subcommand_help = "ワークスペースタグを作成または更新します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
