### Setup

Use `source ./setup_everything.sh` or do the steps manually by fullowing `SETUP.md`.

### Input Scaling

In `nbs_to_run.py` is a list of pairs of notebook paths and a scale factor. The scale factor is the desired ratio between the size of the input to use for that notebook and the default size of the input.

Before running the benchmark, you must scale the input. Either run

```bash
python3 run_all.py --scale_input_and_exit
```

to just scale the input, or to scale the input and run the benchmark, run

```bash
python3 run_all.py --scale_input
```

### Running

```bash
python3 run_all.py
```

Will run all of the benchmark with `pandas`. To run with an alternative Pandas API implementation, run

```bash
python3 run_all.py --lib <pandas alternative>
```

To run with a Pandas API complement (on top of `pandas` or an otherwise specified base Pandas API implementation), run

```bash
python3 run_all.py --add_on <add on>
```

To see all available options run

```bash
python3 run_all.py --help
```

### How to run with different libraries

To add a new Pandas API implementation, in `setup_import_lib.py` add an "library name, dynamic imports as a string" pair to the `imports` dictionary. To add a new Pandas API complement, do the same thing with the `add_ons` dictionary in `setup_import_lib.py`.
