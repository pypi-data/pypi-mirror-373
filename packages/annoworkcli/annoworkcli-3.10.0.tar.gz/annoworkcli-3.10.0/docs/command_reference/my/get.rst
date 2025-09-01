=========================================
my get
=========================================

Description
=================================
ログイン中のアカウント情報を出力します。



Examples
=================================

以下のコマンドは、自分自身のアカウント情報を出力します。

.. code-block:: 

    $ annoworkcli my get \
     --output out.json


.. code-block:: json
   :caption: out.json

   {
      "account_id": "0a998d6f-9b53-4d96-ba89-14edccd9ce0b",
      "user_id": "alice",
      "username": "Alice",
      "email": "alice@example.com",
      "locale": "ja-JP",
      "authority": "user",
      "created_datetime": "2021-10-27T13:55:37.749Z",
      "updated_datetime": "2021-10-29T00:46:19.964Z",
      "external_linkage_info": {
         "annofab": {
            "account_id": "00589ed0-dd63-40db-abb2-dfe5e13c8299"
         }
      }
   }



Usage Details
=================================

.. argparse::
   :ref: annoworkcli.my.get_my_account.add_parser
   :prog: annoworkcli my get
   :nosubcommands:
   :nodefaultconst: