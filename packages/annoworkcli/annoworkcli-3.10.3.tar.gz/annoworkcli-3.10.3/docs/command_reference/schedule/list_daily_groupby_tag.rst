=========================================
schedule list_daily_groupby_tag
=========================================

Description
=================================
日ごとのアサイン時間を、ワークスペースタグで集計した値を出力します。



Examples
=================================

以下のコマンドは、2022-01-01以降の日毎のアサイン時間を、ワークスペースタグで集計した値を出力します。

.. code-block:: 

    $ annoworkcli schedule list_daily_groupby_tag --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "job_name": "MOON",
         "assigned_working_hours": {
            "type_acceptor": 6.0,
            "type:monitored": 8.0,
            "total": 8.0
      }
   ]


.. note::

   ``assigned_working_hours.total`` は、ワークスペースタグを無視して集計した値です。
   ``assigned_working_hours.total`` 以外の値の合計値ではないことに、注意してください。

   たとえば上記の出力結果だと、``assigned_working_hours.total ≠ assigned_working_hours.type:acceptor + assigned_working_hours.type:monitored`` です。




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_assigned_hours_daily_groupby_tag.add_parser
   :prog: annoworkcli schedule list_daily_groupby_tag
   :nosubcommands:
   :nodefaultconst: