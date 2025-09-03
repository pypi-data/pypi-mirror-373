import os
from pathlib import Path

import pandas

from annoworkcli.annofab.list_working_hours import _get_df_working_hours_from_df

# プロジェクトトップに移動する
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../")

data_dir = Path("./tests/data/annofab/list_working_hours")
out_dir = Path("./tests/out/annofab/list_working_hours")
out_dir.mkdir(exist_ok=True, parents=True)


class Test__get_df_working_hours_from_df:
    def test_normal(self):
        df_user_and_af_account = pandas.read_csv(str(data_dir / "user_and_af_account.csv"))
        df_job_and_af_project = pandas.read_csv(str(data_dir / "job_and_af_project.csv"))
        df_af_working_hours = pandas.read_csv(str(data_dir / "af_working_hours.csv"))
        df_actual_working_hours = pandas.read_csv(str(data_dir / "actual_working_hours.csv"))

        df = _get_df_working_hours_from_df(
            df_actual_working_hours=df_actual_working_hours,
            df_user_and_af_account=df_user_and_af_account,
            df_job_and_af_project=df_job_and_af_project,
            df_af_working_hours=df_af_working_hours,
        )

        df.to_csv(out_dir / "out.csv", index=False)
