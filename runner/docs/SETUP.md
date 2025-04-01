### Python Version

This benchmark has been tested with `Python 3.10.15`.

### Docker (optional)

We provide a docker container that will automatically create a python environment for your convinience. If you use the container, skip the "Install library dependencies" step.

Run the container with
```bash
cd <pandasbench root>
docker compose up
```

For the rest of the setup and when running the benchmark, when executing a python command, prefix it with

```bash
docker exec <pandasbench container name> <python command>
```

where `<pandasbench container name>` is the name of the docker container, obtained from `docker ps`.

Alternatively, start an interactive session in the pandasbench container, and run all python commands from this session:

```bash
docker exec -it <pandasbench container name> bash
```

### Install library dependencies

If you are using docker, skip this step.

Run
```bash
cd <pandasbench root>/runner
pip install -r requirements.txt
```

If benchmarking `koalas`, make sure `java-17` is installed

```bash
java --version
```

Earlier versions of `java` may also work, but `java-21` introduces issues

### (One Time Only) Download and copy the datasets to where the notebooks are
Download and unzip the data from [Google Drive](https://drive.google.com/file/d/1WUX-gUycsXVngCaaoDecLdjAv7hjSoeR/view?usp=sharing). This contains a `data` directory.

# The rest of this section will likely be changed in the future:

First, add the `copier.sh` to the `data` directory:
```bash
cp ~/path/to/pandasbench/scripts/copier.sh ~/path/to/data/
```

`copier.sh` will copy the input data into the notebooks directory. You need to run it from the data folder. You pass it one argument, where the notebooks root directory is. For example:
```bash
./copier.sh ~/path/to/pandasbench/notebooks
```