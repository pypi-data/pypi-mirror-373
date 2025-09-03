"""
Command Line Interfaceの共通部分
"""

import argparse
import getpass
import json
import logging
import os
from enum import Enum
from typing import Any

import annoworkapi
from annoworkapi.api import DEFAULT_ENDPOINT_URL
from annoworkapi.exceptions import CredentialsNotFoundError
from more_itertools import first_true

from annoworkcli.common.exeptions import CommandLineArgumentError
from annoworkcli.common.utils import get_file_scheme_path, read_lines_except_blank_line

logger = logging.getLogger(__name__)

COMMAND_LINE_ERROR_STATUS_CODE = 2


class OutputFormat(Enum):
    CSV = "csv"
    JSON = "json"


class PrettyHelpFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    def _format_action(self, action: argparse.Action) -> str:
        return super()._format_action(action) + "\n"

    def _get_help_string(self, action):  # noqa: ANN001, ANN202
        """引数説明用のメッセージを生成する。
        不要なデフォルト値（--debug や オプショナルな引数）を表示させないようにする.
        `argparse.ArgumentDefaultsHelpFormatter._get_help_string` をオーバライドしている。

        Args:
            action ([type]): [description]

        Returns:
            [type]: [description]
        """
        # ArgumentDefaultsHelpFormatter._get_help_string の中身を、そのまま持ってきた。
        # https://qiita.com/yuji38kwmt/items/c7c4d487e3188afd781e 参照

        # 必須な引数には、引数の説明の後ろに"(required)"を付ける
        help = action.help  # pylint: disable=redefined-builtin  # noqa: A001
        if action.required:
            help += " (required)"  # noqa: A001

        if "%(default)" not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    # 以下の条件だけ、annoworkcli独自の設定
                    if action.default is not None and not action.const:
                        help += " (default: %(default)s)"  # noqa: A001
        return help


def add_parser(
    subparsers: argparse._SubParsersAction | None,
    command_name: str,
    command_help: str,
    description: str | None = None,
    is_subcommand: bool = True,  # noqa: FBT001, FBT002
    epilog: str | None = None,
) -> argparse.ArgumentParser:
    """
    サブコマンド用にparserを追加する

    Args:
        subparsers: Noneの場合はsubparserを生成します。
        command_name:
        command_help: 1階層上のコマンドヘルプに表示される コマンドの説明（簡易的な説明）
        description: ヘルプ出力に表示される説明（詳細な説明）
        is_subcommand: サブコマンドかどうか. `annoworkcli job`はコマンド、`annoworkcli job list`はサブコマンドとみなす。
        epilog: ヘルプ出力後に表示される内容。デフォルトはNoneです。

    Returns:
        サブコマンドのparser

    """
    GLOBAL_OPTIONAL_ARGUMENTS_TITLE = "global optional arguments"  # noqa: N806

    def create_parent_parser() -> argparse.ArgumentParser:
        """
        共通の引数セットを生成する。
        """
        parent_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        group = parent_parser.add_argument_group(GLOBAL_OPTIONAL_ARGUMENTS_TITLE)
        group.add_argument(
            "--debug", action="store_true", help="HTTPリクエストの内容やレスポンスのステータスコードなど、デバッグ用のログが出力されます。"
        )

        group.add_argument(
            "--annowork_user_id",
            type=str,
            help="Annoworkにログインする際のユーザーIDを指定します。",
        )
        group.add_argument(
            "--annowork_password",
            type=str,
            help="Annoworkにログインする際のパスワードを指定します。",
        )

        group.add_argument(
            "--endpoint_url",
            type=str,
            help=f"Annowork WebAPIのエンドポイントを指定します。指定しない場合は ``{DEFAULT_ENDPOINT_URL}`` です。",
        )

        return parent_parser

    if subparsers is None:
        # ヘルプページにコマンドラインオプションを表示する`sphinx-argparse`ライブラリが実行するときは、subparsersがNoneになる。
        subparsers = argparse.ArgumentParser(allow_abbrev=False).add_subparsers()
    parents = [create_parent_parser()] if is_subcommand else []

    parser = subparsers.add_parser(
        command_name,
        parents=parents,
        description=description if description is not None else command_help,
        help=command_help,
        epilog=epilog,
        formatter_class=PrettyHelpFormatter,
    )
    parser.set_defaults(command_help=parser.print_help)

    # 引数グループに"global optional group"がある場合は、"--help"オプションをデフォルトの"optional"グループから、"global optional arguments"グループに移動する  # noqa: E501
    # https://ja.stackoverflow.com/a/57313/19524
    global_optional_argument_group = first_true(parser._action_groups, pred=lambda e: e.title == GLOBAL_OPTIONAL_ARGUMENTS_TITLE)
    if global_optional_argument_group is not None:
        # optional グループの 0番目が help なので取り出す
        help_action = parser._optionals._group_actions.pop(0)
        assert help_action.dest == "help"
        # global optional group の 先頭にhelpを追加
        global_optional_argument_group._group_actions.insert(0, help_action)

    return parser


def get_list_from_args(str_list: list[str] | None = None) -> list[str] | None:
    """
    文字列のListのサイズが1で、プレフィックスが`file://`ならば、ファイルパスとしてファイルを読み込み、行をListとして返す。
    そうでなければ、引数の値をそのまま返す。

    Args:
        str_list: コマンドライン引数で指定されたリスト、またはfileスキームのURL

    Returns:
        コマンドライン引数で指定されたリスト。
    """
    if str_list is None or len(str_list) == 0:
        return None

    if len(str_list) > 1:
        return str_list

    str_value = str_list[0]
    path = get_file_scheme_path(str_value)
    if path is not None:
        return read_lines_except_blank_line(path)
    else:
        return str_list


def get_json_from_args(target: str | None = None) -> Any:  # noqa: ANN401
    """
    JSON形式をPythonオブジェクトに変換する。
    プレフィックスが`file://`ならば、ファイルパスとしてファイルを読み込み、Pythonオブジェクトを返す。
    """

    if target is None:
        return None

    path = get_file_scheme_path(target)
    if path is not None:
        with open(path, encoding="utf-8") as f:  # noqa: PTH123
            return json.load(f)
    else:
        return json.loads(target)


def prompt_yesno(msg: str) -> bool:
    """
    標準入力で yes, noを選択できるようにする。
    Args:
        msg: 確認メッセージ

    Returns:
        True: Yes, False: No

    """
    while True:
        choice = input(f"{msg} [y/N] : ")
        if choice == "y":
            return True

        elif choice == "N":
            return False


def prompt_yesnoall(msg: str) -> tuple[bool, bool]:
    """
    標準入力で yes, no, all(すべてyes)を選択できるようにする。
    Args:
        msg: 確認メッセージ

    Returns:
        Tuple[yesno, is_all]. yesno:Trueならyes. is_all: Trueならall.

    """
    while True:
        choice = input(f"{msg} [y/N/ALL] : ")
        if choice == "y":
            return True, False

        elif choice == "N":
            return False, False

        elif choice == "ALL":
            return True, True


def _get_annowork_user_id_from_stdin() -> str:
    """標準入力からAnnoworkにログインする際のユーザーIDを取得します。"""
    login_user_id = ""
    while login_user_id == "":
        login_user_id = input("Enter Annowork User ID: ")
    return login_user_id


def _get_annowork_password_from_stdin() -> str:
    """標準入力からAnnoworkにログインする際のパスワードを取得します。"""
    login_password = ""
    while login_password == "":
        login_password = getpass.getpass("Enter Annowork Password: ")
    return login_password


def _get_endpoint_url_from_args_or_envvar(args: argparse.Namespace) -> str:
    """
    コマンドライン引数`--endpoint_url`または環境変数`ANNOWORK_ENDPOINT_URL`から、AnnoworkのエンドポイントURLを取得します。

    優先順位は次の通りです。
    1. コマンドライン引数 `--endpoint_url`
    2. 環境変数 `ANNOWORK_ENDPOINT_URL`
    """
    endpoint_url = annoworkapi.api.DEFAULT_ENDPOINT_URL

    if "ANNOWORK_ENDPOINT_URL" in os.environ:
        endpoint_url = os.environ["ANNOWORK_ENDPOINT_URL"]

    if args.endpoint_url is not None:
        endpoint_url = args.endpoint_url

    return endpoint_url


def build_annoworkapi(args: argparse.Namespace) -> annoworkapi.resource.Resource:
    """annoworkapiのインスタンスを生成します。

    annoworkのendpoint_urlは次の順序で優先されます。
     1. コマンドライン引数 `--endpoint_url`
     2. 環境変数 `ANNOWORK_ENDPOINT_URL`

    Args:
        args (argparse.Namespace): コマンドライン引数の情報

    Returns:
        annoworkapi.resource.Resource: annoworkapiのインスタンス
    """
    endpoint_url = _get_endpoint_url_from_args_or_envvar(args)

    # エンドポイントURLがデフォルトでない場合は、気付けるようにするためログに出力する
    if endpoint_url != annoworkapi.api.DEFAULT_ENDPOINT_URL:
        logger.info(f"endpoint_url='{endpoint_url}'")

    if args.annowork_user_id is not None and args.annowork_password is not None:
        return annoworkapi.build(login_user_id=args.annowork_user_id, login_password=args.annowork_password, endpoint_url=endpoint_url)

    elif args.annowork_user_id is not None and args.annowork_password is None:
        # コマンドライン引数でユーザーIDのみ指定された場合は、パスワードを標準入力から取得する
        login_password = _get_annowork_password_from_stdin()
        return annoworkapi.build(login_user_id=args.annowork_user_id, login_password=login_password, endpoint_url=endpoint_url)

    elif args.annowork_user_id is None and args.annowork_password is not None:
        # コマンドライン引数でパスワードのみ指定された場合は、エラーにする
        raise CommandLineArgumentError("`--annowork_password`を指定する際は、`--annowork_user_id`も指定してください。")

    # コマンドライン引数でユーザーID、パスワードが指定されていない場合
    try:
        return annoworkapi.build(endpoint_url=endpoint_url)
    except CredentialsNotFoundError:
        # 環境変数, netrcフィアルに認証情報が設定されていなかったので、標準入力から認証情報を入力させる。
        login_user_id = _get_annowork_user_id_from_stdin()
        login_password = _get_annowork_password_from_stdin()
        return annoworkapi.build(endpoint_url=endpoint_url, login_user_id=login_user_id, login_password=login_password)
