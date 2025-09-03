import os
from pathlib import Path

import pytest

from annoworkcli.expected_working_time.list_expected_working_time_weekly import get_weekly_expected_working_hours_df

# モジュールレベルでpytestのmarkerを付ける
pytestmark = pytest.mark.access_webapi


# プロジェクトトップに移動する
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../")

data_dir = Path("./tests/data/expected_working_time")
out_dir = Path("./tests/out/expected_working_time")
out_dir.mkdir(exist_ok=True, parents=True)


EXPECTED_WORKING_TIMES = [
    {
        "workspace_member_id": "alice",
        "date": "2022-03-05",
        "expected_working_hours": 1,
    },
    {
        "workspace_member_id": "alice",
        "date": "2022-03-06",
        "expected_working_hours": 2,
    },
    {
        "workspace_member_id": "alice",
        "date": "2022-03-12",
        "expected_working_hours": 3,
    },
    {
        "workspace_member_id": "bob",
        "date": "2022-02-06",
        "expected_working_hours": 4,
    },
    {
        "workspace_member_id": "bob",
        "date": "2022-03-13",
        "expected_working_hours": 0,
    },
]


workspace_MEMBERS = [{"workspace_member_id": "alice", "user_id": "alice", "username": "ALICE"}]


def test_get_weekly_expected_working_hours_df():
    actual = get_weekly_expected_working_hours_df(EXPECTED_WORKING_TIMES, workspace_MEMBERS)
    assert len(actual) == 3
    assert actual.query("workspace_member_id == 'alice' and start_date == '2022-03-06'").iloc[0]["expected_working_hours"] == 5
