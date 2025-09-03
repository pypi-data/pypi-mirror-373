import argparse
import logging
from pathlib import Path

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class ListExternalLinkageInfo:
    def __init__(self, annowork_service: AnnoworkResource) -> None:
        self.annowork_service = annowork_service

    def main(self, user_id_list: list[str], output: Path | None, output_format: OutputFormat) -> None:
        logger.info(f"{len(user_id_list)} 件のアカウント外部連携情報を取得します。")

        results = []
        for user_id in user_id_list:
            info = self.annowork_service.wrapper.get_account_external_linkage_info_or_none(user_id)
            if info is None:
                logger.warning(f"user_id={user_id} のアカウント外部連携情報は存在しません。")
            info["user_id"] = user_id
            results.append(info)

        if len(results) == 0:
            logger.warning("アカウント外部連携情報は0件です。")

        logger.info(f"{len(results)} 件のアカウント外部連携情報を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(results, is_pretty=True, output=output)
        else:
            if len(results) > 0:
                df = pandas.json_normalize(results)
            else:
                # 空のDataFrameを作成（最低限の列を含める）
                df = pandas.DataFrame(columns=["user_id", "account_id"])
            print_csv(df, output=output)


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    assert user_id_list is not None
    ListExternalLinkageInfo(annowork_service=annowork_service).main(
        user_id_list=user_id_list, output=args.output, output_format=OutputFormat(args.format)
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-u",
        "--user_id",
        type=str,
        nargs="+",
        required=True,
        help="出力対象ユーザのuser_id",
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
    subcommand_name = "list_external_linkage_info"
    subcommand_help = "アカウント外部連携情報取得の一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser
