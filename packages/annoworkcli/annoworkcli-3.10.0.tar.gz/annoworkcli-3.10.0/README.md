
# annowork-cli
AnnoworkのCLIです。


[![Build Status](https://app.travis-ci.com/kurusugawa-computer/annowork-cli.svg?branch=main)](https://app.travis-ci.com/kurusugawa-computer/annowork-cli)
[![CodeQL](https://github.com/kurusugawa-computer/annowork-cli/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/kurusugawa-computer/annowork-cli/actions/workflows/codeql-analysis.yml)
[![PyPI version](https://badge.fury.io/py/annoworkcli.svg)](https://badge.fury.io/py/annoworkcli)
[![Python Versions](https://img.shields.io/pypi/pyversions/annoworkcli.svg)](https://pypi.org/project/annoworkcli/)
[![Documentation Status](https://readthedocs.org/projects/annowork-cli/badge/?version=latest)](https://annowork-cli.readthedocs.io/ja/latest/?badge=latest)


# Requirements
* Python3.9+


# Install
```
$ pip install annoworkcli
```


# Usage


## 認証情報の設定

### `.netrc`

`$HOME/.netrc`ファイルに以下を記載する。

```
machine annowork.com
login annowork_user_id
password annowork_password
```


### 環境変数
* 環境変数`ANNOWORK_USER_ID` , `ANNOWORK_PASSWORD`

### `annoworkcli annofab`コマンドを利用する場合
`annoworkcli annofab`コマンドはannofabのwebapiにアクセスするため、annofabのwebapiの認証情報を指定する必要があります。
* 環境変数`ANNOFAB_USER_ID` , `ANNOFAB_PASSWORD`または`ANNOFAB_PAT`



## コマンドの使い方


```
# CSV出力
$ annoworkcli actual_working_time list_daily --workspace_id foo \
 --start_date 2022-05-01 --end_date 2022-05-10 --output out.csv

$ cat out.csv
date,job_id,job_name,workspace_member_id,user_id,username,actual_working_hours,notes
2022-05-02,5c39a2e8-90dd-4f20-b0a6-39d7f5129e3d,MOON,52ff73fb-c1d6-4ad6-a185-64386ee7169f,alice,Alice,11.233333333333334,
2022-05-02,5c39a2e8-90dd-4f20-b0a6-39d7f5129e3d,MARS,c66acd58-c893-4908-bdcc-1414978bf06b,bob,Bob,8.0,

```







# 開発者向けの情報
https://github.com/kurusugawa-computer/annowork-cli/blob/main/README_for_developer.md