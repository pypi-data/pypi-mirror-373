===================================================
expected_working_time delete
===================================================

Description
=================================
予定稼働時間を削除します。



Examples
=================================

以下のコマンドは、ユーザー ``alice`` の2022-01-01から2021-01-03の予定稼働時間を削除します。

.. code-block:: 

    $ annoworkcli expected_working_time delete --workspace_id org \
     --start_date 2022-01-01 --end_date 2022-01-03 --user_id alice 


.. warning::

   広い期間の予定稼働時間を削除するときは、慎重に実行してください。
   一度削除した予定稼働時間は、元に戻せません。
   また、削除する前に、``annoworkcli expected_working_hours list`` コマンドでバックアップを取得することをおすすめします。
   



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.expected_working_time.delete_expected_working_time.add_parser
   :prog: annoworkcli expected_working_time delete
   :nosubcommands:
   :nodefaultconst:
