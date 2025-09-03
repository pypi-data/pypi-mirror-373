=========================================
annofab reshape_working_hours
=========================================

Description
=================================
Annoworkの実績作業時間とアサイン時間、Annofabの作業時間を比較できるようなCSVファイルに成形します。



Examples
=================================

以下のコマンドは、2022-01-01から2022-01-31までの期間で、Annoworkの実績作業時間とアサイン時間、Annofabの作業時間を、ユーザごとに比較したCSVを出力します。
出力結果詳細は後述を参照してください。

.. code-block:: 

    $ annoworkcli annofab reshape_working_hours --workspace_id org --shape_type total_by_user \
     --start_date 2022-01-01 --end_date 2022-01-31 --output total_by_user.csv


``annoworkcli annofab list_working_hours`` コマンドと ``annoworkcli schedule list_daily`` コマンドの出力結果を用いて、``annoworkcli annofab reshape_working_hours`` コマンドを実行することもとできます。


.. code-block:: 

    $ annoworkcli annofab list_working_hours --workspace_id org \
     --start_date 2022-01-01 --end_date 2022-01-31 --output actual.csv

    $ annoworkcli  schedule list_daily --workspace_id org \
     --start_date 2022-01-01 --end_date 2022-01-31 --output assigned.csv

    $ annoworkcli annofab reshape_working_hours --workspace_id org \ 
     --actual_file actual.csv --assigned_file assigned.csv --shape_type total_by_user --output total_by_user.csv



出力結果
=================================

列名
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
列名の内容は以下の通りです。


* assigned_working_hours : Annoworkのアサイン時間
* actual_working_hours : Annoworkの実績時間
* monitored_working_hours : Annofabの作業時間（Annofabのアノテーションエディタで計測された作業時間）
* activity_rate : アサイン時間に対する実績作業時間の比率（ ``= actual_working_hours / assigned_working_hours`` ）
* activity_diff : アサインに対する実績作業時間の差分（ ``= assigned_working_hours - actual_working_hours`` ）
* monitor_rate : 実績作業時間に対する計測作業時間の比率（ ``= monitored_working_hours / actual_working_hours`` ）
* monitor_diff : 実績作業時間に対する計測作業時間の差分（ ``= actual_working_hours - monitored_working_hours`` ）



``--shape_type details``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
日付ごとユーザごとに作業時間を集計したファイルです。
行方向に日付、列方向にユーザが並んでいます。


.. csv-table:: details.csv
   :file: reshape_working_hours/details.csv
   :header-rows: 2


``--shape_type total_by_user``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ユーザごとに作業時間を集計します。


.. csv-table:: total_by_user.csv
   :file: reshape_working_hours/total_by_user.csv
   :header-rows: 1


``--shape_type total_by_job``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ジョブごとに作業時間を集計します。 
ジョブにはアサイン時間が紐付いていないので、アサイン時間に関連する列は出力されません。

.. csv-table:: total_by_job.csv
   :file: reshape_working_hours/total_by_job.csv
   :header-rows: 1


``--shape_type total_by_parent_job``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

親ジョブごとに作業時間を集計します。


.. csv-table:: total_by_parent_job.csv
   :file: reshape_working_hours/total_by_parent_job.csv
   :header-rows: 1


``--shape_type total_by_user_parent_job``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ユーザごと親ジョブごとに作業時間を集計します。


.. csv-table:: total_by_user_parent_job.csv
   :file: reshape_working_hours/total_by_user_parent_job.csv
   :header-rows: 1


``--shape_type total_by_user_job``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ユーザごとジョブごとに作業時間を集計します。

.. csv-table:: total_by_user_job.csv
   :file: reshape_working_hours/total_by_user_job.csv
   :header-rows: 1


``--shape_type total``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

作業時間を合計します。

.. csv-table:: total.csv
   :file: reshape_working_hours/total.csv
   :header-rows: 1





``--shape_type list_by_date_user_job``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
作業時間の一覧を日付、ユーザ、ジョブ単位で出力します。
ジョブはAnnofabプロジェクトと紐づけることが可能なので、Annofabの作業時間も出力されます。

.. csv-table:: list_by_date_user_job.csv
   :file: reshape_working_hours/list_by_date_user_job.csv
   :header-rows: 1



``--shape_type list_by_date_user_parent_job``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
作業時間の一覧を日付、ユーザ、親ジョブ単位で出力します。
ジョブにはアサイン時間が紐付いていないので、アサイン時間に関連する列は出力されません。


.. csv-table:: list_by_date_user_parent_job.csv
   :file: reshape_working_hours/list_by_date_user_parent_job.csv
   :header-rows: 1


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.reshape_working_hours.add_parser
   :prog: annoworkcli annofab reshape_working_hours
   :nosubcommands:
   :nodefaultconst: