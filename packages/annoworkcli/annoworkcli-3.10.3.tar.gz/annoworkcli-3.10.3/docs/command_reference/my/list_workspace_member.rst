=========================================
my list_workspace_member
=========================================

Description
=================================
自身のワークスペースメンバの一覧を出力します。



Examples
=================================


以下のコマンドは、自身のワークスペースメンバの一覧を出力します。

.. code-block:: 

    $ annoworkcli my list_workspace_member \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "a5cd6a09-e740-4c34-8981-fe3d1b0e0bde",
         "workspace_id": "org",
         "account_id": "0a998d6f-9b53-4d96-ba89-14edccd9ce0b",
         "user_id": "alice",
         "username": "Alice",
         "role": "owner",
         "status": "active",
         "created_datetime": "2022-01-11T08:16:58.373Z",
         "updated_datetime": "2022-01-11T08:16:58.373Z"
      }
   ]




Usage Details
=================================

.. argparse::
   :ref: annoworkcli.my.list_my_workspace_member.add_parser
   :prog: annoworkcli my list_workspace_member
   :nosubcommands:
   :nodefaultconst: