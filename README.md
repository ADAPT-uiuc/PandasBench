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

1) **Full**: This image contains _everything_ that is necessary to run PandasBench, including the Python environment and the datasets. You just download it and you move to the next section on how to run PandasBench.
2) **Lite**: This image contains the Python environment and the data used for
   the benchmark, but it does not contain the code. You ∑will need to download
   this repository and bind it when you run the image.
3) **Base**: This image contains _only_ the Python environment. You will need to download both the data and this repository, and bind both when running the benchmark.

### Which image should I use?

Basically the trade-off in different images is how up-to-date they are. For
example, since **Full** contains everything, this means that we may contain a
slightly outdated version of the data or the code. Because we generally try to
keep this repository, the data, and the images in sync, we recommend that you
download **Full** because it offers the easiest experience. But if you want to
be sure you are using the latest version of everything, you can check the latest
update dates in the images and compare it with the latest commit in this
repository.

### How to download and run the Docker images

**Full**: For the Full image, you just immediately run it, for example:

```
docker run -it --rm baziotis/pandasbench:1.0.0-full
```

**Lite**: For the Lite configuration you'll need to download this repository and
then bind it when running the image. For example, clone the repository:

```
git clone https://github.com/ADAPT-uiuc/PandasBench/
```

and then run the image as follows:

```
docker run -it --rm baziotis/pandasbench:1.0.0-lite -v ./PandasBench:/home/ubuntu/PandasBench
```

Inside the image, you'll need to copy the datasets to the directories of the
notebook that uses them. We provide a script for that, so you can just:
```
cp ./PandasBench/scripts/copier.sh ./data
cd data
./copier.sh ../PandasBench/notebooks
```

**Base**: In this setup you'll need to download and bind both the code and the
data. First, clone the repository:

```
git clone https://github.com/ADAPT-uiuc/PandasBench/
```

Then, download the data (you can alternatively use [this Google Drive
link](https://drive.google.com/file/d/1WUX-gUycsXVngCaaoDecLdjAv7hjSoeR/view?usp=sharing) to download the data):
```
wget https://uofi.box.com/shared/static/dcnyw761chg8hh14vp13wyilrobk0qb3 -O PandasBench_data.zip
# This should create a directory named PandasBench_data
unzip PandasBench_data.zip
```

Now, you'll need to copy the datasets to the directories of the notebook that
uses them. We provide a script for that, so you can just:

```
cp ./PandasBench/scripts/copier.sh ./PandasBench_data
cd PandasBench_data
./copier.sh ../PandasBench/notebooks
```

Finally, you can run the image and bind the PandasBench directory:
```
docker run -it --rm baziotis/pandasbench:1.0.0-base -v ./PandasBench:/home/ubuntu/PandasBench
```

## Manual Setup

Follow the directions in `runner/docs/README.md`
