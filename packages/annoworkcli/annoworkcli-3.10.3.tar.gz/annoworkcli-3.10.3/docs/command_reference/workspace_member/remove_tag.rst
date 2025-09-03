=========================================
workspace_member remove_tag
=========================================

Description
=================================
ワークスペースメンバからワークスペースタグを削除します。



Examples
=================================

以下のコマンドは、ユーザalice, bobから、ワークスペースタグtag1, tag2を除去します。

.. code-block:: 

    $ annoworkcli my list_workspace_member remove_tag --workspace_id org \
     --user_id alice bob --workspace_tag_id tag1 tag2




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.remove_tag_to_workspace_member.add_parser
   :prog: annoworkcli workspace_member remove_tag
   :nosubcommands:
   :nodefaultconst: