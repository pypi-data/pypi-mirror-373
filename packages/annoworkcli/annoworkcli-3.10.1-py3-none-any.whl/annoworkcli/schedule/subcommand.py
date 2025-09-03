import argparse

import annoworkcli
import annoworkcli.schedule.delete_schedule
import annoworkcli.schedule.list_assigned_hours_daily
import annoworkcli.schedule.list_assigned_hours_daily_groupby_tag
import annoworkcli.schedule.list_schedule


def parse_args(parser: argparse.ArgumentParser):  # noqa: ANN201
    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.schedule.delete_schedule.add_parser(subparsers)
    annoworkcli.schedule.list_schedule.add_parser(subparsers)
    annoworkcli.schedule.list_assigned_hours_daily.add_parser(subparsers)
    annoworkcli.schedule.list_assigned_hours_daily_groupby_tag.add_parser(subparsers)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "schedule"
    subcommand_help = "作業計画関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False)
    parse_args(parser)
    return parser
