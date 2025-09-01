=========================================
annofab list_job
=========================================

Description
=================================
ジョブとジョブに紐づくAnnofabプロジェクトの情報を一緒に出力します。



Examples
=================================


以下のコマンドは、ジョブID ``job`` の情報と、そのジョブに紐づくAnnofabプロジェクトの情報を出力します。


.. code-block:: 

    $ annoworkcli annofab list_job --workspace_id org --job_id job \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "job_id": "job",
         "job_name": "MOON",
         "job_tree": "org/parent_job/job",
         "status": "unarchived",
         "target_hours": null,
         "workspace_id": "org",
         "note": "",
         "external_linkage_info": {
            "url": "https://annofab.com/projects/af_project_id"
         },
         "created_datetime": "2021-10-27T14:51:20.196Z",
         "updated_datetime": "2021-10-27T14:51:20.196Z",
         "parent_job_id": "5a144b2a-3db0-4086-aa4e-1620109c72e3",
         "parent_job_name": "PLANET",         
         "annofab": {
            "project_id": "af_project_id",
            "project_title": "af_MOON",
            "project_status": "suspended",
            "input_data_type": "image"
         }
      }
   ]





Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.list_job_with_annofab_project.add_parser
   :prog: annoworkcli annofab list_job
   :nosubcommands:
   :nodefaultconst: