===============================
job delete
===============================

Description
=================================
ジョブを削除します。



Examples
=================================
以下のコマンドは、ジョブID ``job`` のジョブを削除します。


.. code-block:: 

    $ annoworkcli job delete --workspace_id org --job_id job 




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.job.delete_job.add_parser
   :prog: annoworkcli job delete
   :nosubcommands:
   :nodefaultconst: