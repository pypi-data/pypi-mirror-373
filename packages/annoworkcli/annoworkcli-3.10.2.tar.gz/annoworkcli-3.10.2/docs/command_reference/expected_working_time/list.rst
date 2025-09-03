=========================================
expected_working_time list
=========================================

Description
=================================
予定稼働時間の一覧を出力します。



Examples
=================================

以下のコマンドは、2022-01-01以降の予定稼働時間を出力します。

.. code-block:: 

    $ annoworkcli expected_working_time list --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_id": "org",
         "workspace_member_id": "57ba0a2a-37a3-47cf-bbb6-f1087c5c5f9a",
         "date": "2022-01-02",
         "expected_working_hours": 3,
         "created_datetime": "2021-11-24T22:14:31.030Z",
         "updated_datetime": "2021-11-24T22:14:31.030Z",
         "user_id": "alice",
         "username": "Alice"
      },
   ]




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.expected_working_time.list_expected_working_time.add_parser
   :prog: annoworkcli expected_working_time list
   :nosubcommands:
   :nodefaultconst:
