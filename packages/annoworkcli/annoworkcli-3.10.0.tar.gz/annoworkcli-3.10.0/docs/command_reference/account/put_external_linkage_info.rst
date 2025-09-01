========================================
account put_external_linkage_info
========================================

Description
=================================
アカウント外部連携情報取得を更新します。



Examples
=================================


以下のコマンドは、ユーザID'alice'の外部連携情報を出力します。

.. code-block:: 

    $ annoworkcli account put_external_linkage_info  --user_id alice \
     --external_linkage_info '{"annofab": {"account_id": "xxx"}}}'






Usage Details
=================================

.. argparse::
   :ref: annoworkcli.account.put_external_linkage_info.add_parser
   :prog: annoworkcli account put_external_linkage_info
   :nosubcommands:
   :nodefaultconst: