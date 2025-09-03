# af2parser: AF2 plots parser



For handling (minimal) dependencies you can use **conda** or **miniconda** environments. Detailed installation instructions for each of them can be found [here](https://docs.conda.io/en/latest/index.html) and [here](https://docs.conda.io/en/latest/miniconda.html). After installing conda (if needed) create and activate an enironment:

```
conda create -n af2plots
conda activate af2plots
```

alternatively, you can use miniconda. It doesn't require any changes to you system and it's fully contained in a local directory. To install it download an installer from [here](https://docs.conda.io/en/latest/miniconda.html) and run the following (linux example):

```
bash Miniconda3-latest-Linux-x86_64.sh -b -p miniconda_af2plots
. miniconda_af2plots/bin/activate
```

Now, you can proceed with the installation instructions below


```
conda install -c conda-forge matplotlib
```

install

```
git clone -b modules --recursive git@git.embl.de:gchojnowski/af2plots.git
cd af2plots
python setup.py install
```

and test

```
af2plots --test
```

to use it in your scripts

```
from af2plots.plotter import plotter
```

basic af2lib usage examples are in af2plots/__main__py
