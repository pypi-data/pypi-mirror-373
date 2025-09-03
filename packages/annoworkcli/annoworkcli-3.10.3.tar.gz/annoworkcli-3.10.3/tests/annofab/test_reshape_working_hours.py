import os
from pathlib import Path

import pandas

from annoworkcli.annofab.reshape_working_hours import ReshapeDataFrame

# プロジェクトトップに移動する
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../")

data_dir = Path("./tests/data/annofab/reshape_working_hours")
out_dir = Path("./tests/out/annofab/reshape_working_hours")
out_dir.mkdir(exist_ok=True, parents=True)


class TestReshapeDataFrame:
    main_obj: ReshapeDataFrame

    @classmethod
    def setup_class(cls):
        cls.main_obj = ReshapeDataFrame()

    def test_get_df_total(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))

        df = self.main_obj.get_df_total(df_actual=df_actual, df_assigned=df_assigned)
        df.to_csv(out_dir / "out-total.csv", index=False)

    def test_get_df_total_by_user(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))
        df_user_company = pandas.read_csv(str(data_dir / "user_company.csv"))

        df = self.main_obj.get_df_total_by_user(df_actual=df_actual, df_assigned=df_assigned, df_user_company=df_user_company)
        df.to_csv(out_dir / "out-total_by_user.csv", index=False)

    def test_get_df_total_by_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))

        df = self.main_obj.get_df_total_by_job(df_actual=df_actual)
        df.to_csv(out_dir / "out-total_by_job.csv", index=False)

    def test_get_df_total_by_parent_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))

        df = self.main_obj.get_df_total_by_parent_job(
            df_actual=df_actual,
            df_assigned=df_assigned,
        )
        df.to_csv(out_dir / "out-total_by_parent_job.csv", index=False)

    def test_get_df_total_by_user_parent_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))

        df = self.main_obj.get_df_total_by_user_parent_job(
            df_actual=df_actual,
            df_assigned=df_assigned,
        )
        df.to_csv(out_dir / "out-total_by_user_parent_job.csv", index=False)

    def test_get_df_total_by_user_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))

        df = self.main_obj.get_df_total_by_user_job(df_actual=df_actual)
        df.to_csv(out_dir / "out-total_by_user_job.csv", index=False)

    def test_get_df_details(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))

        df = self.main_obj.get_df_details(df_actual=df_actual, df_assigned=df_assigned)
        df.to_csv(out_dir / "out-details.csv", index=False)

    def test_get_df_list_by_date_user_parent_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))

        df = self.main_obj.get_df_list_by_date_user_parent_job(df_actual=df_actual)
        df.to_csv(out_dir / "list_by_date_user_parent_job.csv")

    def test_get_df_list_by_date_user_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df = self.main_obj.get_df_list_by_date_user_job(df_actual=df_actual)
        df.to_csv(out_dir / "list_by_date_user_job.csv")
