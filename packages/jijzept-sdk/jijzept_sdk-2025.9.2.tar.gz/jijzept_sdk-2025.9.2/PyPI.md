# JijZeptSDK

JijZeptSDK is a package that allows you to install all the free packages provided by JijZept. Specifically, it includes the following Python packages.

- [jijmodeling](https://pypi.org/project/jijmodeling/)
- [ommx](https://pypi.org/project/ommx/)
- [ommx-fixstars-amplify-adapter](https://pypi.org/project/ommx-fixstars-amplify-adapter/)
- [ommx-da4-adapter](https://pypi.org/project/ommx-da4-adapter/)
- [ommx-dwave-adapter](https://pypi.org/project/ommx-dwave-adapter/)
- [ommx-gurobipy-adapter](https://pypi.org/project/ommx-gurobipy-adapter/)
- [ommx-highs-adapter](https://pypi.org/project/ommx-highs-adapter/)
- [ommx-python-mip-adapter](https://pypi.org/project/ommx-python-mip-adapter/)
- [ommx-openjij-adapter](https://pypi.org/project/ommx-openjij-adapter/)
- [ommx-pyscipopt-adapter](https://pypi.org/project/ommx-pyscipopt-adapter/)
- [minto](https://pypi.org/project/minto/)
- [qamomile](https://pypi.org/project/qamomile/)

## Basic usage

You can install all free JijZept packages available in your environment by executing the following command.

```bash
pip install "jijzept_sdk[all]"
```

You can also start the JupyterLab environment with the following command.

```bash
jijzept_sdk
```

## Advanced usage

You can also install only some packages by specifying options like the following command. However, `jijmodeling` and `ommx` are always included.

```bash
pip install "jijzept_sdk[mip]"
```

The list of options is as follows:

- `amplify`: Install packages for using `ommx-fixstars-amplify-adapter`.
- `da4`: Install packages for using `ommx-da4-adapter`.
- `dwave`: Install packages for using `ommx-dwave-adapter`.
- `gurobi`: Install packages for using `ommx-gurobipy-adapter`.
- `highs`: Install packages for using `ommx-highs-adapter`.
- `mip`: Install packages for using `ommx-python-mip-adapter`.
- `openjij`: Install packages for using `ommx-openjij-adapter`.
- `scip`: Install packages for using `ommx-pyscipopt-adapter`.
- `minto`: Install packages for using `minto`.
- `qamomile`: Install packages for using `qamomile`.
- `lab`: Install packages for using `jupyterlab`.

Note that the `lab` option is required to run the `jijzept_sdk` command.
