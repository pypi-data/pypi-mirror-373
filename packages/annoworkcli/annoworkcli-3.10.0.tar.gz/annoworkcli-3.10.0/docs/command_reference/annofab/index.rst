==================================================
annofab
==================================================

Description
=================================
Annofabにアクセスするサブコマンドです。
Annofabの認証情報を事前に設定しておく必要があります。


Available Commands
=================================

.. toctree::
   :maxdepth: 1
   :titlesonly:

   list_job
   list_working_hours
   put_account_external_linkage_info
   put_job
   reshape_working_hours
   visualize_statistics

Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.subcommand.add_parser
   :prog: annoworkcli annofab
   :nosubcommands: