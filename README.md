# What is PandasBench?

PandasBench is a benchmark for Pandas API optimization techniques that evaluates real world `pandas` code in the form of Jupyter notebooks. It evaluates a variety of techniques, such as Pandas API implementations like Modin, Dask, Koalas (now a part of PySpark), along with Pandas API complements like Dias. As a benchmark, PandasBench scales data at a per notebook level instead of a single uniform scale factor across notebooks. Several sets of per notebook scaling factors are provided; these target runtimes were used in the PandasBench paper to evaluate Pandas API optimization techniques on 5, 10, and 20 second target runtimes.

# Overview

`runner/` contains the infrastructure used to run PandasBench.

`notebooks/` contains the `pandas` code that Pandas optimization techniques are evaluated on.

`plots/` and `runner/explore` contains the code used to generate the plots found in the PandasBench paper.

`scripts/` contains additional utilities that may be useful when setting up the benchmark.

# Quick Start

Follow the directions in `runner/docs/README.md`
