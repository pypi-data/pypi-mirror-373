=========================================
schedule list
=========================================

Description
=================================
作業計画の一覧を出力します。



Examples
=================================

以下のコマンドは、2022-01-01以降の作業計画情報を出力します。

.. code-block:: 

    $ annoworkcli schedule list --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "schedule_id": "b3fa6635-b6ea-49dc-b1cd-c23a50ed26f1",
         "workspace_id": "org",
         "job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "workspace_member_id": "53ba2c39-5c02-4df4-abdb-eab0143ac0c7",
         "start_date": "2021-12-28",
         "end_date": "2022-01-03",
         "type": "percentage",
         "value": 100,
         "created_datetime": "2021-12-27T08:14:45.882Z",
         "updated_datetime": "2021-12-27T08:19:16.352Z",
         "user_id": "alice",
         "username": "Alice",
         "job_name": "MOON",
         "assigned_working_hours": 10.0
      }
   ]









Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.list_schedule.add_parser
   :prog: annoworkcli schedule list
   :nosubcommands:
   :nodefaultconst: