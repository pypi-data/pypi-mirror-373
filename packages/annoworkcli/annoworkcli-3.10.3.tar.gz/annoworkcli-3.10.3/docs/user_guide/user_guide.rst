==========================================
User Guide
==========================================

Command Structure
==========================================

.. code-block::

    $ annoworkcli <command> <subcommand> [options and parameters]

* ``command`` : ``job`` や ``workspace_member`` などのカテゴリに対応します。
* ``subcommand`` : ``list`` や ``delete`` など、実行する操作に対応します。



Version
==========================================

``--version`` を指定すると、annoworkcliのバージョンが表示されます。

.. code-block::

    $ annoworkcli --version
    annoworkcli 1.3.4


Getting Help
==========================================
``--help`` を指定すると、コマンドのヘルプが表示されます。


パラメータの指定
=================================================
複数の値を渡せるコマンドラインオプションと、JSON形式の値を渡すコマンドラインオプションは、 ``file://`` を指定することでファイルの中身を渡すことができます。

.. code-block::
    :caption: job_id.txt

    job1
    job2


.. code-block::

    # 標準入力で指定する
    $ annoworkcli job list --workspace_id org --job_id job1 job2

    # 相対パスでファイルを指定する
    $ annoworkcli job list --workspace_id org --job_id file://job_id.txt




ロギングコントロール
=================================================

ログメッセージは、標準エラー出力とログファイル ``.log/annoworkcli.log`` に出力されます。
``.log/annoworkcli.log`` は、1日ごとにログロテート（新しいログファイルが生成）されます。

``--debug`` を指定すれば、HTTPリクエストも出力されます。


.. code-block::

    $ annoworkcli my get -o out/my.json
    INFO     : 2022-01-12 10:42:52,791 : annoworkcli.__main__           : sys.argv=['annoworkcli', 'my', 'get', '-o', 'out/my.json']
    INFO     : 2022-01-12 10:42:53,390 : annoworkcli.common.utils       : out/my.json に出力しました。

    $ annoworkcli my get -o out/my.json --debug
    INFO     : 2022-01-12 10:43:45,339 : annoworkcli.__main__           : sys.argv=['annoworkcli', 'my', 'get', '-o', 'out/my.json', '--debug']
    DEBUG    : 2022-01-12 10:43:45,339 : annoworkapi.resource           : Create annoworkapi resource instance :: {'login_user_id': 'alice', 'endpoint_url': 'https://annowork.com'}
    DEBUG    : 2022-01-12 10:43:45,615 : annoworkapi.api                : Sent a request :: {'request': {'http_method': 'get', 'url': 'https://annowork.com/api/v1/my/account', 'query_params': None, 'header_params': None, 'request_body': None}, 'response': {'status_code': 401, 'content_length': 26}}
    DEBUG    : 2022-01-12 10:43:46,047 : annoworkapi.api                : Sent a request :: {'requests': {'http_method': 'post', 'url': 'https://annowork.com/api/v1/login', 'query_params': None, 'request_body_json': {'user_id': 'alice', 'password': '***'}, 'request_body_data': None, 'header_params': None}, 'response': {'status_code': 200, 'content_length': 4105}}
    DEBUG    : 2022-01-12 10:43:46,154 : annoworkapi.api                : Sent a request :: {'request': {'http_method': 'get', 'url': 'https://annowork.com/api/v1/my/account', 'query_params': None, 'header_params': None, 'request_body': None}, 'response': {'status_code': 200, 'content_length': 365}}
    INFO     : 2022-01-12 10:43:46,155 : annoworkcli.common.utils       : out/my.json に出力しました。



エンドポイントURLの設定（開発者用）
=================================================
デフォルトのエンドポイントURLは ``https://annowork.com`` ですが、 ``https://localhost`` などを指定することも可能です。

エンドポイントURLは環境変数またはコマンドラインのオプションで指定できます。次の順序で優先されます。
 1. コマンドライン引数 ``--endpoint_url``
 2. 環境変数 ``ANNOWORK_ENDPOINT_URL``

