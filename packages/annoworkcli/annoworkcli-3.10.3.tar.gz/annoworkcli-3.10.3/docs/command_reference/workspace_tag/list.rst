=========================================
workspace_tag list
=========================================

Description
=================================
ワークスペースタグの一覧を出力します。



Examples
=================================

以下のコマンドは、ワークスペースタグの一覧を出力します。

.. code-block:: 

    $ annoworkcli workspace_tag list --workspace_id ws \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_tag_id": "company_kurusugawa",
         "workspace_id": "ws",
         "workspace_tag_name": "company:来栖川電算",
         "created_datetime": "2022-03-14T04:15:05.243Z",
         "updated_datetime": "2022-03-14T04:15:05.243Z"
      }
   ]


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_tag.list_workspace_tag.add_parser
   :prog: annoworkcli workspace_tag list
   :nosubcommands:
   :nodefaultconst: