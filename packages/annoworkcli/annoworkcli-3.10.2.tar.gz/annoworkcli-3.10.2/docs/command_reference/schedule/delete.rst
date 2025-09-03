=========================================
schedule delete
=========================================

Description
=================================
作業計画情報を削除します。



Examples
=================================

``--schedul_id`` に削除したい作業計画のschedule_idを指定します。

.. code-block::

    $ annoworkcli schedule delete --workspace_id org --schedule_id id1 id2





Usage Details
=================================

.. argparse::
   :ref: annoworkcli.schedule.delete_schedule.add_parser
   :prog: annoworkcli schedule delete
   :nosubcommands:
   :nodefaultconst: