import argparse

import annoworkcli
import annoworkcli.annofab.list_job_with_annofab_project
import annoworkcli.annofab.list_working_hours
import annoworkcli.annofab.put_account_external_linkage_info
import annoworkcli.annofab.put_job_from_annofab_project
import annoworkcli.annofab.reshape_working_hours
import annoworkcli.annofab.visualize_statistics


def parse_args(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.annofab.list_job_with_annofab_project.add_parser(subparsers)
    annoworkcli.annofab.list_working_hours.add_parser(subparsers)
    annoworkcli.annofab.visualize_statistics.add_parser(subparsers)
    annoworkcli.annofab.reshape_working_hours.add_parser(subparsers)
    annoworkcli.annofab.put_account_external_linkage_info.add_parser(subparsers)
    annoworkcli.annofab.put_job_from_annofab_project.add_parser(subparsers)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "annofab"
    subcommand_help = "Annofabにアクセスするサブコマンド"
    description = "Annofabにアクセスするサブコマンド\nAnnofabの認証情報を事前に設定しておく必要があります。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=description, is_subcommand=False)
    parse_args(parser)
    return parser
