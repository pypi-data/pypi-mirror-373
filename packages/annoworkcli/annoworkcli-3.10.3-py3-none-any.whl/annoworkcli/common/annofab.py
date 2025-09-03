"""
annofabに関するutil関係の関数
"""

from typing import Any

import isodate
from annoworkapi.annofab import get_annofab_project_id_from_url

TIMEZONE_OFFSET_HOURS = 9
"""Annofabのタイムゾーンのオフセット時間。AnnofabはJSTに固定されているので、9を指定する"""


def get_annofab_project_id_from_job(job: dict[str, Any]) -> str | None:
    url = job["external_linkage_info"].get("url")
    if url is None:
        return None

    return get_annofab_project_id_from_url(url)


def isoduration_to_hour(duration: str) -> float:
    """
    ISO 8601 duration を 時間に変換する
    Args:
        duration (str): ISO 8601 Durationの文字

    Returns:
        変換後の時間。

    """
    return isodate.parse_duration(duration).total_seconds() / 3600
