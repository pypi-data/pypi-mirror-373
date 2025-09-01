==============================================================
actual_working_time list_daily
==============================================================

Description
=================================
実績作業時間を日ごとに集約した情報を一覧として出力します。




Examples
=================================

以下のコマンドは、2022-01-01以降の日ごとの実績作業時間情報を出力します。

.. code-block:: 

    $ annoworkcli actual_working_time list_daily --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "job_id": "caa0da6f-34aa-40cb-abc0-976c9aab3b40",
         "job_name": "MOON",
         "workspace_member_id": "50c5587a-219a-47d6-9641-0eb273996966",
         "user_id": "alic3",
         "username": "Alice",
         "actual_working_hours": 2.716666666666667,
         "notes": null,
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "parent_job_name": "PLANET"
      },
   ]





Usage Details
=================================

.. argparse::
   :ref: annoworkcli.actual_working_time.list_actual_working_hours_daily.add_parser
   :prog: annoworkcli actual_working_time list_daily
   :nosubcommands:
   :nodefaultconst: