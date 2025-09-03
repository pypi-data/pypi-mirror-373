"""
注意事項: このスクリプトを実行するには`httpx`をpip installしておく必要があります。
"""

import asyncio

import httpx


async def get_latest_versions(package_names: set[str]) -> dict[str, str]:
    """
    パッケージ名の集合を受け取り、各パッケージの最新バージョンを取得する関数
    戻り値は {パッケージ名: 最新バージョン} の辞書の形です
    この関数はPyPI JSON APIを利用して最新バージョンを取得しています
    """
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(f"https://pypi.org/pypi/{package_name}/json")
            for package_name in package_names
        ]
        results = await asyncio.gather(*tasks)
        results_json = [result.json() for result in results]
    return {
        result_json["info"]["name"] : result_json["info"]["version"]
        for result_json in results_json
    }


async def gen_pyproect_toml() -> None:
    # NOTE: 依存関係を更新したいPythonパッケージ名を下記に追加してください
    latest_versions = await get_latest_versions({
        "jijmodeling",
        "ommx",
        "ommx-fixstars-amplify-adapter",
        "ommx-da4-adapter",
        "ommx-dwave-adapter",
        "ommx-gurobipy-adapter",
        "ommx-highs-adapter",
        "ommx-python-mip-adapter",
        "ommx-openjij-adapter",
        "ommx-pyscipopt-adapter",
        "minto",
        "qamomile",
    })

    # NOTE: pyproect.tomlを変更する場合は以下の文字列を編集すること
    PYPROJECT_TOML = (
f"""[build-system]
requires = ["setuptools>=64", "setuptools-scm"]
build-backend = "setuptools.build_meta"

[project]
name = "jijzept_sdk"
authors = [
    {{name = "Jij Inc.", email = "info@j-ij.com"}},
]
description = "Free development kit provided by JijZept."
readme = "PyPI.md"
requires-python = ">=3.10, <3.13"
classifiers = [
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dynamic = ["version"]
dependencies = [
    "jijmodeling == {latest_versions['jijmodeling']}",
    "ommx == {latest_versions['ommx']}",
]

[project.optional-dependencies]
all = [
    "ommx-fixstars-amplify-adapter == {latest_versions['ommx-fixstars-amplify-adapter']}",
    "ommx-da4-adapter == {latest_versions['ommx-da4-adapter']}",
    "ommx-dwave-adapter == {latest_versions['ommx-dwave-adapter']}",
    "ommx-gurobipy-adapter == {latest_versions['ommx-gurobipy-adapter']}",
    "ommx-highs-adapter == {latest_versions['ommx-highs-adapter']}",
    "ommx-python-mip-adapter == {latest_versions['ommx-python-mip-adapter']}; python_version < '3.12'",
    "ommx-openjij-adapter == {latest_versions['ommx-openjij-adapter']}",
    "ommx-pyscipopt-adapter == {latest_versions['ommx-pyscipopt-adapter']}",
    "minto == {latest_versions['minto']}",
    "qamomile == {latest_versions['qamomile']}",
    "jupyterlab",
]
amplify = [
    "ommx-fixstars-amplify-adapter == {latest_versions['ommx-fixstars-amplify-adapter']}"
]
da4 = [
    "ommx-da4-adapter == {latest_versions['ommx-da4-adapter']}"
]
dwave = [
    "ommx-dwave-adapter == {latest_versions['ommx-dwave-adapter']}"
]
gurobi = [
    "ommx-gurobipy-adapter == {latest_versions['ommx-gurobipy-adapter']}"
]
highs = [
    "ommx-highs-adapter == {latest_versions['ommx-highs-adapter']}"
]
mip = [
    "ommx-python-mip-adapter == {latest_versions['ommx-python-mip-adapter']}"
]
openjij = [
    "ommx-openjij-adapter == {latest_versions['ommx-openjij-adapter']}"
]
scip = [
    "ommx-pyscipopt-adapter == {latest_versions['ommx-pyscipopt-adapter']}"
]
minto = [
    "minto == {latest_versions['minto']}"
]
qamomile = [
    "qamomile == {latest_versions['qamomile']}"
]
lab = [
    "jupyterlab"
]

[project.scripts]
jijzept_sdk = "jijzept_sdk:run"

[tool.setuptools_scm]
version_file = "src/jijzept_sdk/_version.py"
"""
    )

    with open("pyproject.toml", "w") as f:
        f.write(PYPROJECT_TOML)


if __name__ == "__main__":
    asyncio.run(gen_pyproect_toml())
