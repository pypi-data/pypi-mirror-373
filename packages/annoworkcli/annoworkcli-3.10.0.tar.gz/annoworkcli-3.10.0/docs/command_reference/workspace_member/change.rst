=========================================
workspace_member change
=========================================

Description
=================================
メンバの情報（ロールなど）を変更します。


Examples
=================================

以下のコマンドは、ユーザalice, bobのロールを"ワーカ"に変更します。

.. code-block:: 

    $ annoworkcli my list_workspace_member change --workspace_id org \
     --user_id alice bob --role worker



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.change_workspace_member_properties.add_parser
   :prog: annoworkcli workspace_member change
   :nosubcommands:
   :nodefaultconst: