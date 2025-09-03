=========================================
annofab visualize_statistics
=========================================

Description
=================================
Annofabの統計情報を実績作業時間と組み合わせて可視化します。



Examples
=================================

以下のコマンドは、ジョブID ``job`` の実績作業時間と、ジョブに紐づくAnnofabプロジェクトの統計情報を組み合わせて、生産性に関する情報を可視化したファイルを出力します。


.. code-block:: 

   $ annoworkcli annofab visualize_statistics --workspace_id org --job_id job \
     --output_dir out

   $ tree out
   out
   ├── MOON.json
   ├── histogram
   │   ├── ヒストグラム-作業時間.html
   │   └── ヒストグラム.html
   ├── line-graph
   │   ├── 教師付者用
   │   │   ├── 折れ線-横軸_教師付開始日-縦軸_アノテーション単位の指標-教師付者用.html
   │   │   ├── 折れ線-横軸_教師付開始日-縦軸_入力データ単位の指標-教師付者用.html
   │   │   ├── 累積折れ線-横軸_アノテーション数-教師付者用.html
   │   │   ├── 累積折れ線-横軸_タスク数-教師付者用.html
   │   │   └── 累積折れ線-横軸_入力データ数-教師付者用.html
   │   ├── 検査者用
   │   │   ├── 折れ線-横軸_検査開始日-縦軸_アノテーション単位の指標-検査者用.html
   │   │   └── 折れ線-横軸_検査開始日-縦軸_入力データ単位の指標-検査者用.html
   │   ├── 受入者用
   │   │   ├── 累積折れ線-横軸_アノテーション数-受入者用.html
   │   │   └── 累積折れ線-横軸_入力データ数-受入者用.html
   │   ├── 折れ線-横軸_教師付開始日-全体.html
   │   ├── 折れ線-横軸_日-全体.html
   │   ├── 累積折れ線-横軸_日-縦軸_作業時間.html
   │   └── 累積折れ線-横軸_日-全体.html
   ├── scatter
   │   ├── 散布図-アノテーションあたり作業時間と品質の関係-計測時間-教師付者用.html
   │   ├── 散布図-アノテーションあたり作業時間と品質の関係-実績時間-教師付者用.html
   │   ├── 散布図-アノテーションあたり作業時間と累計作業時間の関係-計測時間.html
   │   ├── 散布図-アノテーションあたり作業時間と累計作業時間の関係-実績時間.html
   │   └── 散布図-教師付者の品質と作業量の関係.html
   ├── タスクlist.csv
   ├── メンバごとの生産性と品質.csv
   ├── ユーザ_日付list-作業時間.csv
   ├── 教師付開始日毎の生産量と生産性.csv
   ├── 教師付者_教師付開始日list.csv
   ├── 受入者_受入開始日list.csv
   ├── 全体の生産性と品質.csv
   └── 日毎の生産量と生産性.csv



AnnofabプロジェクトのIDは、``--annofab_project_id`` で指定できます。

.. code-block:: 

   $ annoworkcli annofab visualize_statistics --workspace_id org --annofab_project_id prj \
     --output_dir out



このコマンドは、内部で ``annofabcli statistics visualize`` コマンドを実行しています。``annofabcli statistics visualize`` に渡すオプションは ``--annofabcli_options`` 以降に指定してください。

.. code-block:: 

   $ annoworkcli annofab visualize_statistics --workspace_id org --job_id job \
    --output_dir out --annofabcli_options --task_query '{"status":"complete"}' --minimal


コマンドの使い方は、`annofabcli statistics visualize <https://annofab-cli.readthedocs.io/ja/latest/command_reference/statistics/visualize.html>`_ のドキュメントを参照してください。


Usage Details
=================================

.. argparse::
   :ref: annoworkcli.annofab.visualize_statistics.add_parser
   :prog: annoworkcli annofab visualize_statistics
   :nosubcommands:
   :nodefaultconst:
