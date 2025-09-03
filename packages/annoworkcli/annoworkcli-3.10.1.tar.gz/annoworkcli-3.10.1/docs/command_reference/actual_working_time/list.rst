=============================================
actual_working_time list
=============================================

Description
=================================
実績作業時間情報の一覧を出力します。



Examples
=================================

以下のコマンドは、2022-01-01以降の実績作業時間情報を出力します。

.. code-block:: 

    $ annoworkcli actual_working_time list --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_id": "org",
         "actual_working_time_id": "1ed08b23-555e-493d-b8ef-ccb7b05b7522",
         "job_id": "caa0da6f-34aa-40cb-abc0-976c9aab3b40",
         "workspace_member_id": "50c5587a-219a-47d6-9641-0eb273996966",
         "start_datetime": "2022-01-02T01:00:00.000Z",
         "end_datetime": "2022-01-02T03:43:00.000Z",
         "note": "",
         "created_datetime": "2022-01-02T15:10:09.777Z",
         "updated_datetime": "2022-01-02T15:10:09.777Z",
         "actual_working_hours": 2.716666666666667,
         "user_id": "alice",
         "username": "Alice",
         "job_name": "MOON",
         "parent_job_id": "11d73ea0-ed87-4f24-9ef6-68afcb1fdca7",
         "parent_job_name": "PLANET"         
      }
   ]


``--timezone_offset`` は、日付に対するタイムゾーンを指定できます。``--timezone_offset`` を指定しない場合は、ローカルのタイムゾーンを参照します。
以下のコマンドは、日本時間（UTC+9）の2022-01-01以降の実績作業時間情報を出力します。

.. code-block:: 

    $ annoworkcli actual_working_time list --workspace_id org --start_date 2022-01-01 \
     --timezone_offset 9 --format json --output out.json





Usage Details
=================================

.. argparse::
   :ref: annoworkcli.actual_working_time.list_actual_working_time.add_parser
   :prog: annoworkcli actual_working_time list
   :nosubcommands:
   :nodefaultconst: