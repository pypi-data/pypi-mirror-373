=========================================
workspace_member list
=========================================

Description
=================================
メンバの一覧を出力します。無効化されたメンバも出力します。


Examples
=================================

以下のコマンドは、メンバーの一覧を出力します。

.. code-block:: 

    $ annoworkcli workspace_member list --workspace_id ws \
     --format json --output out.json


.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "e2d334cf-dfe8-411e-acd6-fe4e39687fea",
         "workspace_id": "org",
         "account_id": "b7d76c01-4a10-438e-a516-d5768afb7709",
         "user_id": "alice",
         "username": "Alice",
         "role": "manager",
         "status": "active",
         "created_datetime": "2021-10-31T14:49:59.841Z",
         "updated_datetime": "2021-11-02T05:28:36.714Z"
      }
   ]


``--show_workspace_tag`` を付けると、メンバーに付与されているタグの情報も出力します。

.. code-block:: 

    $ annoworkcli workspace_member list --show_workspace_tag \
     --format json --output out.json



.. code-block:: json
   :caption: out.json

   [
      {
         "workspace_member_id": "e2d334cf-dfe8-411e-acd6-fe4e39687fea",
         "workspace_id": "org",
         "account_id": "b7d76c01-4a10-438e-a516-d5768afb7709",
         "user_id": "alice",
         "username": "Alice",
         "role": "manager",
         "status": "active",
         "created_datetime": "2021-10-31T14:49:59.841Z",
         "updated_datetime": "2021-11-02T05:28:36.714Z",
         "workspace_tag_ids": [
            "tag"
         ],
         "workspace_tag_names": [
            "TAG"
         ]         
      }
   ]








Usage Details
=================================

.. argparse::
   :ref: annoworkcli.workspace_member.list_workspace_member.add_parser
   :prog: annoworkcli workspace_member list
   :nosubcommands:
   :nodefaultconst: