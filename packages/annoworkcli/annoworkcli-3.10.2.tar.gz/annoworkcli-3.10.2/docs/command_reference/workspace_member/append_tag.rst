=========================================
workspace_member append_tag
=========================================

Description
=================================
ワークスペースメンバにワークスペースタグを追加します。



Examples
=================================


以下のコマンドは、ユーザalice, bobに、ワークスペースタグtag1, tag2を付与します。

.. code-block:: 

    $ annoworkcli my list_workspace_member append_tag --workspace_id org \
     --user_id alice bob --workspace_tag_id tag1 tag2





Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.append_tag_to_workspace_member.add_parser
   :prog: annoworkcli workspace_member append_tag
   :nosubcommands:
   :nodefaultconst: