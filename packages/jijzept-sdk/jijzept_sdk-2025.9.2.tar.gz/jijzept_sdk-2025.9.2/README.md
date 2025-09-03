# JijZeptSDK

JijZeptSDKとは、Jijが提供する無償のパッケージ群をまとめてインストールできるPythonパッケージです。使い方は [PyPI.md](PyPI.md) を、含まれるPythonパッケージは [pyproject.toml](pyproject.toml) を参照してください。

## 依存関係の自動更新について

JijZeptSDKの依存関係は日本時間の毎週水曜日8時に自動で更新されます。具体的には、 [`update_dependencies.yaml`](.github/workflows/update_dependencies.yaml) で依存関係を更新しており、その更新処理の本体は [`gen_pyproject_toml.py`](gen_pyproject_toml.py) というPythonスクリプトです。

> [!WARNING]
> `pyproject.toml` の内容を書き換える際は、 `gen_pyproject_toml.py` 内にあるf-stringを変更してください。

> [!NOTE]
> 本来ならばDependabotを使うほうが良いが、pyproject.tomlのproject.optional-dependenciesの更新が不安定だったため、独自のスクリプトとワークフローを実行する形に変更した。将来的にDependabotに戻すようにしてほしい。

## リリースについて

JijZeptSDKのリリースは日本時間の毎週水曜日8時半に自動で行われます。具体的には、 [`weekly_release.yaml`](.github/workflows/weekly_release.yaml) でリリースを行っています。
