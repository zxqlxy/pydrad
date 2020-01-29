# hydrad_tools

[![Build Status](https://travis-ci.org/rice-solar-physics/hydrad_tools.svg?branch=master)](https://travis-ci.org/rice-solar-physics/hydrad_tools)
[![Coverage Status](https://coveralls.io/repos/github/rice-solar-physics/hydrad_tools/badge.svg?branch=master)](https://coveralls.io/github/rice-solar-physics/hydrad_tools?branch=master)

Some Python tools to help configure and parse the HYDRAD code for coronal loop dynamics.

## Install

To install the package and the needed dependencies with the [Anaconda Python distribution](https://www.anaconda.com/download/),

```
$ git clone https://github.com/rice-solar-physics/hydrad_tools.git
$ cd hydrad_tools
$ conda env create -f environment.yml
$ source activate hydrad_tools
$ python setup.py install
```

To run the tests and confirm that everything is working alright,
```
$ pytest
``` 

See the [docs](https://rice-solar-physics.github.io/hydrad_tools/) for more info. Additionally, you will need access to the HYDRAD source code.

## Help
Create an issue if you run into any problems. Submit a PR if you would like to add any functionality.
