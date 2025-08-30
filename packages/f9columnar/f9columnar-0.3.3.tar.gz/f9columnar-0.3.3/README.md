# F9 Columnar

<div align="center">

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![python](https://img.shields.io/badge/-Python_3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pytorch](https://img.shields.io/badge/-PyTorch_2.7-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![pytorch](https://img.shields.io/pypi/v/f9columnar)](https://pypi.org/project/f9columnar/)

</div>

A lightweight Python package for batch processing of ROOT and HDF5 event data.

### Project description

This package is designed for efficient handling of large datasets. Built on PyTorch, Awkward Array, and Uproot, it utilizes PyTorch's DataLoader with an IterableDataset to enable parallel processing. It implements a columnar event loop, returning batches of events in a format compatible with standard PyTorch training loops over multiple epochs.

Optimized for machine learning applications, the package provides `RootDataLoader` and `Hdf5DataLoader` classes for data loading from ROOT and HDF5 files. Additionally, it supports parallel data processing through a modular pipeline of processor classes, allowing users to chain operations for complex computations and histogramming.

##  Setup

### Install with PyTorch GPU

```shell
pip install f9columnar[torch]
```

### Install with PyTorch CPU (recommended)

```shell
pip install f9columnar
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Install without PyTorch

```shell
pip install f9columnar
```

## Getting started example

The following example demonstrates how to load data from multiple ROOT files, apply a simple filter to select two branches, define variables, apply a cut, and create a histogram.

```python
from f9columnar.root_dataloader import get_root_dataloader

def filter_branch(branch):
    # select only these two branches
    return branch == "tau_p4" or branch == "lephad_p4"

# root_dataloader is an instance of a torch DataLoader that uses an IterableDataset
root_dataloader, total = get_root_dataloader(
    name="data", # name identifier
    files=ntuple_files, # root files
    key="NOMINAL", # root file tree name
    step_size=10**5, # number of events per array batch to read into memory
    num_workers=12, # number of workers for parallel processing
    processors=None, # arbitrary calculations on arrays
    filter_name=filter_branch, # filter branches
)

# loop over batches of events from .root file(s), each batch is an awkward array
for events in root_dataloader:
    arrays, report = events
    # ... do something with the arrays
```

Calculations on arrays within worker processes can be performed using a `Processor`. Multiple processors can be linked together in a `ProcessorsGraph`, forming a directed acyclic graph (DAG). These processors are applied to arrays in the sequence determined by the DAG’s topological order.

Each worker executes the same processor graph on batches of event data and returns the results to the event loop once processing is complete. In the example above, 12 (`num_workers`) processor graphs would be running in parallel, each handling small batches of events. Below is an example demonstrating how to calculate the tau visible mass and apply a cut to this variable.

```python
from f9columnar.processors import ProcessorsGraph, CheckpointProcessor
from f9columnar.object_collections import Variable, VariableCollection, Cut, CutCollection
from f9columnar.histograms import HistogramProcessor

class VisibleMass(Variable): # Variable is a Processor
    name = "vis_mass" # processor name
    branch_name = "lephad_p4" # name of the branch in the .root file

    def __init__(self):
        super().__init__()

    def run(self, arrays): # each processor must implement a run method
        lephad_p4 = arrays[self.branch_name] # branch_name is the name of the field in the ak array
        v = get_kinematics_vector(lephad_p4) # use vector with px, py, pz and E

        arrays["tau_vis_mass"] = v.m # add a new field to the arrays

        return {"arrays": arrays} # return the arrays (can also return None if no changes are made)

class CutVisibleMass(Cut): # Cut is a Processor
    name = "vis_mass_cut"
    branch_name = None # is not a branch in ntuples but was defined in the VisibleMass processor

    def __init__(self, cut_lower, cut_upper): # argumnets of the processor
        super().__init__()
        self.cut_lower = cut_lower
        self.cut_upper = cut_upper

    def run(self, arrays):
        mask = (arrays["tau_vis_mass"] > self.cut_lower) & (arrays["tau_vis_mass"] < self.cut_upper)
        arrays = arrays[mask] # apply the cut

        return {"arrays": arrays} # return must be a dictionary with key name for the argument of the next processor

class Histograms(HistogramProcessor):
    def __init__(self, name="histograms"):
        super().__init__(name)

        self.make_hist1d("tau_vis_mass", 20, 80.0, 110.0) # make a histogram with 20 bins from 80 to 110 GeV

    def run(self, arrays):
        return super().run(arrays) # auto fills histograms if array names match histogram names

var_collection = VariableCollection(VisibleMass, init=False) # will initialize later
cut_collection = CutCollection(CutVisibleMass, init=False)

collection = var_collection + cut_collection # add collections of objects together
branch_filter = collection.branch_name_filter # defines the branches that the processors depend on

graph = ProcessorsGraph() # graph has a fit method that gets called inside the root_dataloader

# add nodes to the graph
graph.add(
    CheckpointProcessor("input"), # input node
    var_collection["vis_mass"](), # initialize the processor
    cut_collection["vis_mass_cut"](cut_lower=90.0, cut_upper=100.0),
    CheckpointProcessor("output", save_arrays=True), # saves final arrays
    Histograms(),
)

# build a processor graph
graph.connect(
    [
        ("input", "vis_mass"),
        ("vis_mass", "vis_mass_cut"),
        ("vis_mass_cut", "output"),
        ("output", "histograms"),
    ]
)

# plot the graph
graph.draw("graph.pdf")

# ... pass into the root_dataloader with the processors argument (e.g. processors=graph)
# in this case the dataloader will return a fitted graph
for processed_graph in dataloader:
    histograms = processed_graph["histograms"].hists
    arrays = processed_graph["output"].arrays
    # ... do something with the histograms and arrays
```

A higher level of abstraction is also possible using the [`ColumnarEventLoop`](f9columnar/run.py) class. See benchmark [examples](benchmark/f9columnar_benchmark.py) for some more details.
