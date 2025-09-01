import datetime

import more_itertools

from annoworkcli.actual_working_time.list_actual_working_hours_daily import (
    _create_actual_working_hours_dict,
    create_actual_working_hours_daily_list,
)

ACTUAL_WORKING_TIME_LIST = [
    {
        "workspace_id": "org",
        "actual_working_time_id": "b9256922-f028-4e02-85a5-64cd1d6f6597",
        "job_id": "3e29d3eb-5b29-40b5-a696-678be1ef6b6d",
        "workspace_member_id": "alice",
        "start_datetime": "2021-11-01T10:00:00.000Z",
        "end_datetime": "2021-11-01T11:00:00.000Z",
        "note": "",
        "created_datetime": "2021-11-01T09:26:23.269Z",
        "updated_datetime": "2021-11-01T09:26:23.269Z",
        "actual_working_hours": 1.0,
        "account_id": "04c7749e-25ab-4da7-9602-9264ed52e5be",
        "user_id": "alice",
        "username": "Alice",
        "job_name": "task1",
    },
    {
        "workspace_id": "org",
        "actual_working_time_id": "e13a87a1-3e0b-4502-a832-c8f0bbe40360",
        "job_id": "0dc59bfb-a410-4bb6-b783-4e5afdc4d0aa",
        "workspace_member_id": "alice",
        "start_datetime": "2021-11-01T12:00:00.000Z",
        "end_datetime": "2021-11-01T14:00:00.000Z",
        "note": "",
        "created_datetime": "2021-11-01T09:28:33.285Z",
        "updated_datetime": "2021-11-01T09:28:33.285Z",
        "actual_working_hours": 2.0,
        "account_id": "04c7749e-25ab-4da7-9602-9264ed52e5be",
        "user_id": "alice",
        "username": "Alice",
        "job_name": "task2",
    },
    {
        "workspace_id": "org",
        "actual_working_time_id": "7ca964f7-50a6-483e-bb5b-b339766c0936",
        "job_id": "3e29d3eb-5b29-40b5-a696-678be1ef6b6d",
        "workspace_member_id": "alice",
        "start_datetime": "2021-11-01T14:30:00.000Z",
        "end_datetime": "2021-11-01T15:30:00.000Z",
        "note": "",
        "created_datetime": "2021-11-01T09:28:49.558Z",
        "updated_datetime": "2021-11-01T09:28:49.558Z",
        "actual_working_hours": 1.0,
        "account_id": "04c7749e-25ab-4da7-9602-9264ed52e5be",
        "user_id": "alice",
        "username": "Alice",
        "job_name": "task1",
    },
]


class Test__create_actual_working_hours_dict:
    jtc_tzinfo = datetime.timezone(datetime.timedelta(hours=9))

    def test_evening(self):
        actual = _create_actual_working_hours_dict(ACTUAL_WORKING_TIME_LIST[0], tzinfo=self.jtc_tzinfo)
        expected = {(datetime.date(2021, 11, 1), "alice", "3e29d3eb-5b29-40b5-a696-678be1ef6b6d"): 1.0}
        assert actual == expected

    def test_midnight(self):
        actual = _create_actual_working_hours_dict(ACTUAL_WORKING_TIME_LIST[2], tzinfo=self.jtc_tzinfo)
        expected = {
            (datetime.date(2021, 11, 1), "alice", "3e29d3eb-5b29-40b5-a696-678be1ef6b6d"): 0.5,
            (datetime.date(2021, 11, 2), "alice", "3e29d3eb-5b29-40b5-a696-678be1ef6b6d"): 0.5,
        }
        assert actual == expected


class Test_create_actual_working_hours_daily_list:
    def test_xxx(self):
        actual = create_actual_working_hours_daily_list(ACTUAL_WORKING_TIME_LIST)
        assert len(actual) == 3
        assert more_itertools.first_true(actual, pred=lambda e: e.date == "2021-11-01" and e.job_name == "task1").actual_working_hours == 1.5
        assert more_itertools.first_true(actual, pred=lambda e: e.date == "2021-11-01" and e.job_name == "task2").actual_working_hours == 2.0
        assert more_itertools.first_true(actual, pred=lambda e: e.date == "2021-11-02" and e.job_name == "task1").actual_working_hours == 0.5
