import argparse
import copy
import logging
import sys
from collections.abc import Sequence

import pandas

import annoworkcli
import annoworkcli.account.subcommand
import annoworkcli.actual_working_time.subcommand
import annoworkcli.annofab.subcommand
import annoworkcli.expected_working_time.subcommand
import annoworkcli.job.subcommand
import annoworkcli.my.subcommand
import annoworkcli.schedule.subcommand
import annoworkcli.workspace.subcommand
import annoworkcli.workspace_member.subcommand
import annoworkcli.workspace_tag.subcommand
from annoworkcli.common.cli import PrettyHelpFormatter
from annoworkcli.common.utils import set_default_logger

logger = logging.getLogger(__name__)


def warn_pandas_copy_on_write() -> None:
    """
    pandas2.2以上ならば、Copy-on-Writeの警告を出す。
    pandas 3.0で予期しない挙動になるのを防ぐため。
    https://pandas.pydata.org/docs/user_guide/copy_on_write.html
    """
    major, minor, _ = pandas.__version__.split(".")
    if int(major) >= 2 and int(minor) >= 2:
        pandas.options.mode.copy_on_write = "warn"


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Command Line Interface for Annowork", formatter_class=PrettyHelpFormatter, allow_abbrev=False)
    parser.add_argument("--version", action="version", version=f"annoworkcli {annoworkcli.__version__}")
    parser.set_defaults(command_help=parser.print_help)

    subparsers = parser.add_subparsers(dest="command_name")

    annoworkcli.account.subcommand.add_parser(subparsers)
    annoworkcli.actual_working_time.subcommand.add_parser(subparsers)
    annoworkcli.annofab.subcommand.add_parser(subparsers)
    annoworkcli.expected_working_time.subcommand.add_parser(subparsers)
    annoworkcli.job.subcommand.add_parser(subparsers)
    annoworkcli.my.subcommand.add_parser(subparsers)
    annoworkcli.workspace.subcommand.add_parser(subparsers)
    annoworkcli.workspace_member.subcommand.add_parser(subparsers)
    annoworkcli.workspace_tag.subcommand.add_parser(subparsers)
    annoworkcli.schedule.subcommand.add_parser(subparsers)

    return parser


def mask_sensitive_value_in_argv(argv: list[str]) -> list[str]:
    """
    `argv`にセンシティブな情報が含まれている場合は、`***`に置き換える。
    """
    tmp_argv = copy.deepcopy(argv)
    for masked_option in ["--annowork_user_id", "--annowork_password", "--annofab_user_id", "--annofab_password", "--annofab_pat"]:
        try:
            start_index = 0
            # `--annowork_password a --annowork_password b`のように複数指定された場合でもマスクできるようにする
            while True:
                index = tmp_argv.index(masked_option, start_index)
                tmp_argv[index + 1] = "***"
                start_index = index + 2

        except ValueError:
            continue
    return tmp_argv


def main(arguments: Sequence[str] | None = None) -> None:
    """
    annoworkcli コマンドのメイン処理

    Args:
        arguments: コマンドライン引数。テストコード用

    """
    warn_pandas_copy_on_write()
    parser = create_parser()
    if arguments is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arguments)

    if hasattr(args, "subcommand_func"):
        try:
            set_default_logger(is_debug_mode=args.debug)
            argv = sys.argv
            if arguments is not None:
                argv = ["annoworkcli", *list(arguments)]
            logger.info(f"args={mask_sensitive_value_in_argv(argv)}")
            args.subcommand_func(args)
        except Exception as e:
            logger.exception(e)
            raise e

    else:
        # 未知のサブコマンドの場合はヘルプを表示
        args.command_help()


if __name__ == "__main__":
    main()
