=========================================
annofab put_job
=========================================

Description
=================================
Annofabプロジェクトからジョブを作成します。



Examples
=================================


以下のコマンドは、AnnofabのプロジェクトID ``af_prj`` のプロジェクトを、ジョブID ``pjob`` のジョブ配下に追加します。
具体的には、以下の通りジョブの情報が追加されます。

* job_name: Annofabプロジェクトの名前
* url: AnnofabプロジェクトのURL
* job_id: ``--job_id`` に指定した値。未指定の場合はAnnofabプロジェクトのプロジェクトID


.. code-block:: 

    $ annoworkcli annofab put_job --workspace org --parent_job_id pjob --annofab_project_id af_prj
     





Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.put_job_from_annofab_project.add_parser
   :prog: annoworkcli annofab put_job
   :nosubcommands:
   :nodefaultconst: