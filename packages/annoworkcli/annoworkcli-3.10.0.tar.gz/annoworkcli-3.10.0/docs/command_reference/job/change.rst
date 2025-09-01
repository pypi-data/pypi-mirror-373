=======================================
job change
=======================================

Description
=================================
ジョブのステータスを変更します。



Examples
=================================

以下のコマンドは、ジョブID ``job1`` , ``job2`` のステータスをアーカイブに変更します。


.. code-block:: 

    $ annoworkcli job change --workspace_id org --job_id job --status archived




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.job.change_job_properties.add_parser
   :prog: annoworkcli job change
   :nosubcommands:
   :nodefaultconst: