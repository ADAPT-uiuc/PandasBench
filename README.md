# What is PandasBench?

PandasBench is the first systematic effort to create a benchmark for the Pandas
API. This repository contains the collection of notebooks, as well as necessary
information on how to run PandasBench over `pandas` and other Pandas
replacements, like Modin, Dask, and Koalas.

# Structure

- `runner/` contains the infrastructure used to run PandasBench.
- `notebooks/` contains the collection of notebooks. Note that all these are
real-world Kaggle notebooks, and they are saved in this directory using the
original username and kernel slug. So, for example, we have
`./notebooks/akgauravin/gun-violence-data-exploration-and-plotting`, corresponds
to
[https://www.kaggle.com/code/akgauravin/gun-violence-data-exploration-and-plotting](https://www.kaggle.com/code/akgauravin/gun-violence-data-exploration-and-plotting).
- `scripts/` contains utilities used when setting up the benchmark.
- `plots/` and `runner/explore` contains the code used to generate the plots found in the PandasBench paper.

# Setup

To run PandasBench, you will need to: a) the necessary dependencies, b) the
original data used by the notebooks. The easiest way to get both is using one of
our Docker images, which we describe below. But, we also provide information on
how to perform the setup manually.

## Docker

We provide 3 Docker images:

1) **Full**: This image contains _everything_ that is necessary to run
   PandasBench, including the Python environment and the datasets. You just
   download it and you move to the next section on how to run PandasBench.
2) **Lite**: This image contains _only_ the Python environment. You will need to
   download both the data and this repository, and bind both when running the
   benchmark.

### Which image should I use?

Basically the trade-off in different images is how up-to-date are vs how easy
they are to use and how large they are. For example, since **Full** contains
everything, this means that we may contain a slightly outdated version of the
code (or the data). Because we generally try to keep this repository, the data,
and the images in sync, we recommend that you download **Full** because it
offers the easiest experience. But if you want to be sure you are using the
latest version of everything, you can check the latest update dates in the
images and compare it with the latest commit in this repository. Also, **Full**
is much larger than **Lite**, in case this is an issue.

### How to download and run the Docker images

**Full**: For the Full image, you just immediately run it, for example:

```
docker run -it --name pandasbench_c_full --rm baziotis/pandasbench:1.0.0-full bash
```

**Lite**: In this setup you'll need to download and bind both the code and the
data. First, clone the repository:

```
git clone https://github.com/ADAPT-uiuc/PandasBench/
```

Then, download the data _into_ the `PandasBench` directory (you can alternatively use [this Google Drive
link](https://drive.google.com/file/d/1WUX-gUycsXVngCaaoDecLdjAv7hjSoeR/view?usp=sharing) to download the data):
```
wget https://uofi.box.com/shared/static/tipejtwr4khhyzl207uhcwjh2i7k9u8l -O PandasBench_data.zip
# This should create a directory named PandasBench_data
unzip PandasBench_data.zip
```

`PandasBench` should now look like this:
```
├── data
├── Dockerfile.full
├── Dockerfile.lite
├── LICENSE
├── notebooks
├── plots
├── README.md
├── runner
└── scripts
```

Now, you'll need to copy the datasets to the directories of the notebook that
uses them. We provide a script for that, so you can just:

```
cd ./scripts
./docker_data_setup.sh
```

You can now delete the `data/` directory.

Finally, you can run the image and bind the PandasBench directory:
```
docker run -it -v ./:/home/ubuntu/PandasBench --name pandasbench_c_lite --rm baziotis/pandasbench:1.0.0-lite bash
```

## Manual Setup

Follow the directions in `runner/docs/README.md`
