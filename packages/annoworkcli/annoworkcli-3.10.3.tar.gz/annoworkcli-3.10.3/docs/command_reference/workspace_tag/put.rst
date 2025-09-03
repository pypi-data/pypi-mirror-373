=========================================
workspace_tag put
=========================================

Description
=================================
ワークスペースタグを作成または更新します。



Examples
=================================

以下のコマンドは、``company:来栖川電算`` という名前のワークスペースタグを作成します。

.. code-block:: 

    $ annoworkcli workspace_tag put --workspace_id ws \
     --workspace_tag_name "company:来栖川電算" --workspace_tag_id company_kurusugawa

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_tag.put_workspace_tag.add_parser
   :prog: annoworkcli workspace_tag put
   :nosubcommands:
   :nodefaultconst: