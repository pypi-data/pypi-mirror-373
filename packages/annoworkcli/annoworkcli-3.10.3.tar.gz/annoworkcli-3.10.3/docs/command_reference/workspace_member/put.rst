=========================================
workspace_member put
=========================================

Description
=================================
ワークスペースメンバを登録します。



Examples
=================================

以下のコマンドは、ユーザalice, bobをワークスペース`org`のメンバーに追加します。

.. code-block:: 

    $ annoworkcli my list_workspace_member put --workspace_id org \
     --user_id alice bob 



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.put_workspace_member.add_parser
   :prog: annoworkcli workspace_member put
   :nosubcommands:
   :nodefaultconst: