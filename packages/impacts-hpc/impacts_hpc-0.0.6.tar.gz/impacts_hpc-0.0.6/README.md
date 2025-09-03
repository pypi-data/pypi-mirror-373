[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# ImpactsHPC

ImpactsHPC is a Python library designed to estimate the environmental impacts of jobs on data centers. Its main features include:

- Providing explainable, sourced, and replicable results
- Uncertainty computation
- Support for different levels of precision in input data
- Multicriteria analysis (not fully supported yet)
- Whole lifecycle assessment (not fully supported yet)

The estimations provided by this library are approximate and not always accurate. Therefore, you should not rely solely on them; it is recommended to provide the explanations produced by the library along with the estimations.

Currently, it supports the estimation of usage impact (energy consumption and its impact) for the extraction, production, and distribution phases. The library computes the environmental impact based on three criteria: global warming potential (GWP, in gCO₂eq), abiotic resource depletion (ADPE, in gSbeq), and primary energy use (PE, in MJ).


## Documentation

See the [Documentation](https://impacthpc-cc8227.pages.in2p3.fr/index.html)

### OR

Build the doc :

```bash
make html
open docs/build/html/index.html
````
