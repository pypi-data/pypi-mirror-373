# LImA 2 Client library

This project provides a Python interface to the LImA 2 distributed system.

Checkout the [documentation here](https://limagroup.gitlab-pages.esrf.fr/lima2-client/).

### Development setup

In order to install lima2-client in a new conda environment:

```sh
conda create -n l2c -c esrf-bcu python==3.10 pytango pytango-db
pip install .[dev]
```
The `dev` extra dependency adds linting, formatting, static analysis and testing tools.
It also installs `ipython` required to run the `lima2_shell`.

### Quickstart with blissdemo

With `bliss-demo-servers` running, you can run an interactive Lima2 client shell to manipulate the
Lima2 simulator devices and test the client API:

```sh
export TANGO_HOST="localhost:10000"  # Assuming you are running bliss-demo-servers locally
lima2_shell
```

The `lima2_shell` utility instantiates a `Client` object using config from `l2c_config.yaml`,
creates a set of default control, acquisition and processing parameters, and starts an ipython session.

### Bootstrapping the documentation

The source for the documentation is in the `docs` folder. Here are the instructions to built and read it locally. The documentation is built with [Doxygen](http://www.doxygen.org/) and [Sphinx](http://www.sphinx-doc.org). The sphinx template is from [Sphinx Material](https://bashtage.github.io/sphinx-material/).

```
    conda create -n doc --file docs/requirements.txt -c conda-forge
    conda activate doc
    cd docs
    make html
```

The html documentation is generated in `docs/.build/html`.
