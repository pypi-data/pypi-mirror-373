=========================================
workspace list
=========================================

Description
=================================
ワークスペースの一覧を出力します。


Examples
=================================


以下のコマンドは、自分自身が所属しているワークスペースの一覧を出力します。

.. code-block:: 

    $ annoworkcli workspace list \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_id": "org",
         "workspace_name": "SANDBOX",
         "email": "foo@example.com",
         "created_datetime": "2022-01-11T08:16:58.373Z",
         "updated_datetime": "2022-01-11T08:16:58.373Z"
      }
   ]



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace.list_workspace.add_parser
   :prog: annoworkcli workspace list
   :nosubcommands:
   :nodefaultconst: