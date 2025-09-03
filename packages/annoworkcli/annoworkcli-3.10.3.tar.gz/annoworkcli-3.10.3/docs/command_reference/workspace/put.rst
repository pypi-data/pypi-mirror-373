=========================================
workspace put
=========================================

Description
=================================
ワークスペースを作成/更新します。


Examples
=================================

以下のコマンドは、ワークスペースID ``org`` のワークスペースを作成します。

.. code-block:: 

    $ annoworkcli workspace put --workspace_id org --email "alice@example.com" 



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace.put_workspace.add_parser
   :prog: annoworkcli workspace put
   :nosubcommands:
   :nodefaultconst: