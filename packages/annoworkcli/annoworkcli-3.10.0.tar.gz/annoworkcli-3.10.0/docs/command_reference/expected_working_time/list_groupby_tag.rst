=========================================
expected_working_time list_groupby_tag
=========================================

Description
=================================
ワークスペースタグで集計した予定稼働時間を出力します。



Examples
=================================

以下のコマンドは、2022-01-01以降の予定稼働時間を、ワークスペースタグで集計した値を出力します。

.. code-block:: 

    $ annoworkcli expected_working_time list_groupby_tag --workspace_id org --start_date 2022-01-01 \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2022-01-02",
         "expected_working_hours": {
            "type:acceptor": 4.0,
            "type:monitored": 5.0,
            "total": 8.0
         }
   ]



.. note::

   ``expected_working_hours.total`` は、ワークスペースタグを無視して集計した値です。
   ``expected_working_hours.total`` 以外の値の合計値ではないことに、注意してください。

   たとえば上記の出力結果だと、``expected_working_hours.total ≠ expected_working_hours.type:acceptor + expected_working_hours.type:monitored`` です。



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.expected_working_time.list_expected_working_time_groupby_tag.add_parser
   :prog: annoworkcli expected_working_time list_groupby_tag
   :nosubcommands:
   :nodefaultconst: