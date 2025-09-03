==============================================================
actual_working_time list_daily_groupby_tag
==============================================================

Description
=================================
日ごとの実績作業時間を、ワークスペースタグで集計した値を出力します。


Examples
=================================

以下のコマンドは、2022-01-01以降の日ごとの実績作業時間情報を、ワークスペースタグで集計した値を出力します。

.. code-block:: 

    $ annoworkcli actual_working_time list_daily_groupby_tag --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "job_id": "caa0da6f-34aa-40cb-abc0-976c9aab3b40",
         "job_name": "MOON",
         "actual_working_hours": {
            "type:acceptor": 4,
            "type:monitored": 5,
            "total": 10
         },
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "parent_job_name": "PLANET"         
      }
   ]


.. note::

   ``actual_working_hours.total`` は、ワークスペースタグを無視して集計した値です。
   ``actual_working_hours.total`` 以外の値の合計値ではないことに、注意してください。
   
   たとえば上記の出力結果だと、``actual_working_hours.total ≠ actual_working_hours.type:acceptor + actual_working_hours.type:monitored`` です。

   



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.actual_working_time.list_actual_working_hours_daily_groupby_tag.add_parser
   :prog: annoworkcli actual_working_time list_daily_groupby_tag
   :nosubcommands:
   :nodefaultconst: