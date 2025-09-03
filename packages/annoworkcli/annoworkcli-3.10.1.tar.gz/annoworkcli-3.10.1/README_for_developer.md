# Usage for Developer
開発者用のドキュメントです。
ソースコードの生成、テスト実行、リリース手順などを記載します。

# 開発方法
VSCodeのdevcotainerを利用して開発します。
https://code.visualstudio.com/docs/remote/containers

1. 以下の環境変数を定義する
    * `ANNOFAB_USER_ID`
    * `ANNOFAB_PASSWORD`
    * `ANNOWORK_USER_ID`
    * `ANNOWORK_PASSWORD`
2. VSCodeのdevcontainerを起動します。

# 開発フロー
* mainブランチを元にしてブランチを作成して、プルリクを作成してください。mainブランチへの直接pushすることはGitHub上で禁止しています。

# Release
GitHubのReleasesからリリースしてください。
バージョンはSemantic Versioningに従います。
リリースすると、以下の状態になります。

* ソース内のバージョン情報（`pyproject.toml`, `__version__.py`）は、uv-dynamic-versioning でGitHubのバージョンタグから生成されます。
* 自動でPyPIに公開されます。


# Document
以下のコマンドを実行すると、`docs/_build/html/`にドキュメントが生成されます。

```
$ make docs
```

ドキュメントはReadTheDocsにデプロイしています。
GitHubのmainブランチが更新されると、ReadTheDocsに自動でデプロイされます。


