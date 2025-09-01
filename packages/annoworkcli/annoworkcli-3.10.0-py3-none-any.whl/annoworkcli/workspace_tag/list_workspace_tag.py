import argparse
import logging
from pathlib import Path

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class ListWorkspaceTag:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str):  # noqa: ANN204
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def main(self, output: Path, output_format: OutputFormat):  # noqa: ANN201
        workspace_tags = self.annowork_service.api.get_workspace_tags(self.workspace_id)

        if len(workspace_tags) == 0:
            logger.warning("ワークスペースタグ情報は0件です。")

        logger.debug(f"{len(workspace_tags)} 件のタグ一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(workspace_tags, is_pretty=True, output=output)
        else:
            required_columns = [
                "workspace_id",
                "workspace_tag_id",
                "workspace_tag_name",
            ]
            if len(workspace_tags) > 0:
                df = pandas.json_normalize(workspace_tags)
                remaining_columns = list(set(df.columns) - set(required_columns))
                columns = required_columns + remaining_columns
            else:
                df = pandas.DataFrame(columns=required_columns)
                columns = required_columns
            print_csv(df[columns], output=output)


def main(args):  # noqa: ANN001, ANN201
    annowork_service = build_annoworkapi(args)
    ListWorkspaceTag(annowork_service=annowork_service, workspace_id=args.workspace_id).main(
        output=args.output, output_format=OutputFormat(args.format)
    )


def parse_args(parser: argparse.ArgumentParser):  # noqa: ANN201
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
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
    subcommand_name = "list"
    subcommand_help = "ワークスペースタグの一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
