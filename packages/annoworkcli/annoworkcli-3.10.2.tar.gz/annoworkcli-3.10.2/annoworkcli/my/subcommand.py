import argparse

import annoworkcli
import annoworkcli.my.get_my_account
import annoworkcli.my.list_my_workspace_member


def parse_args(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.my.get_my_account.add_parser(subparsers)
    annoworkcli.my.list_my_workspace_member.add_parser(subparsers)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "my"
    subcommand_help = "自分自身に関するサブコマンド"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False)
    parse_args(parser)
    return parser
