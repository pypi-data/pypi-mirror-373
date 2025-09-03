=========================================
workspace_member delete
=========================================

Description
=================================
メンバーを削除します。



Examples
=================================


以下のコマンドは、ユーザalice, bobをワークスペース`org`のメンバーから削除します。

.. code-block:: 

    $ annoworkcli my list_workspace_member delete --workspace_id org \
     --user_id alice bob



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.delete_workspace_member.add_parser
   :prog: annoworkcli workspace_member delete
   :nosubcommands:
   :nodefaultconst: