class AnnoworkCliException(Exception):  # noqa: N818
    """
    annoworkcliに関するException
    """


class CommandLineArgumentError(AnnoworkCliException):
    """コマンドライン引数が正しくない場合のエラー"""
