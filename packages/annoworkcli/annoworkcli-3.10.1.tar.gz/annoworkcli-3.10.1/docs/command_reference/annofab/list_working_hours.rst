=========================================
annofab list_working_hours
=========================================

Description
=================================
日ごとの実績作業時間と、ジョブに紐づくAnnofabプロジェクトの作業時間を一緒に出力します。



Examples
=================================

以下のコマンドは、ジョブID ``job`` の実績作業時間と、そのジョブに紐づくAnnofabプロジェクトでの作業時間を出力します。



.. code-block:: 

    $ annoworkcli annofab list_working_hours --workspace_id org --job_id job \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "date": "2021-11-05",
         "job_id": "job",
         "job_name": "MOON",
         "workspace_member_id": "58005ead-f85b-45d8-931b-54ba2837d7b1",
         "user_id": "alice",
         "username": "Alice",
         "actual_working_hours": 1.1666666666666667,
         "annofab_project_id": "af_project",
         "annofab_account_id": "4f275f74-5c58-4d35-a700-2475de20d2da",
         "annofab_working_hours": 0.5,
         "notes": null
      }
   ]

.. note:: 

   Annofabプロジェクトでの作業時間は、具体的にはアノテーションエディタ画面で作業している時間です。この時間は自動的に計測されます。
   Annoworkの実績作業時間とAnnofabの作業時間を比較することで、アノテーションエディタ画面以外の作業にかかった時間を算出することができます。たとえば、コミュニケーションの時間やアノテーションルールを理解している時間などです。


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.list_working_hours.add_parser
   :prog: annoworkcli annofab list_working_hours
   :nosubcommands:
   :nodefaultconst: