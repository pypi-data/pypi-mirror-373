from __future__ import annotations

import copy
import logging
import os
import time
from abc import ABC, abstractmethod
from functools import reduce
from typing import Any

import awkward as ak
import networkx as nx
import numpy as np

from f9columnar.utils.helpers import handle_plot_exception


class ProcessorsGraph:
    def __init__(
        self,
        copy_processors: bool = True,
        prune_results: bool = True,
        global_attributes: dict[str, Any] | None = None,
        identifier: str = "",
    ):
        """Direct Acyclic Graph (DAG) composer for processors. Each node is executed sequentially by the `fit` method
        in the order given by the topological sort of the graph. Processor node recieves the results of its predecessors
        as input arguments.

        Parameters
        ----------
        copy_processors : bool
            Flag to copy processors on each fit. Should generally be set to True to avoid side effects.
        prune_results : bool
            Flag to prune results of the processors after each fit. Prune removes _results from the processor if all its
            dependencies (all the connected nodes that are not needed anymore) are met.
        global_attributes : dict
            Dictionary of global attributes to be used in the processors.
        identifier : str
            Identifier string to add to all node names, by default "".

        Other parameters
        ----------------
        processors : dict
            Dictionary of processors objects.
        processors_edges : list of size 2 tuples of str
            List of edges connecting processors nodes.
        graph : nx.DiGraph
            NetworkX directed graph object.
        topo_sorted : list of str
            List of topologically sorted nodes.

        Methods
        -------
        add(*processors)
            Add processors nodes to the graph.
        connect(processor_edges=None)
            Connect processors nodes given edges. If no edges are given, the previously connected edges are used.
        chain()
            Connect processors nodes in a chain (linear order).
        extend(other_graph, extend_node)
            Extend the graph with another graph starting from a node.
        insert(other_graph, insert_node)
            Insert another graph into the graph starting from a node and then reconnecting.
        fit(arrays, reports, event_iterator_worker, **kwargs)
            Fit the processors in the graph.
        style_graph(fillcolor)
            Style the graph. Should be called before draw. Needs pygraphviz installed.
        draw(file_path, fontsize=10, jupyter=False, **kwargs)
            Draw the graph and save it to a file.

        Example
        -------

               | --- p2 --- |
        p1 --- |            | --- p4
               | --- p3 --- |

        graph = ProcessorsGraph()

        p1 = Proc1(name="p1", arg1="foo")
        p2 = Proc2(name="p2", arg2="bar")
        p3 = Proc3(name="p3")
        p4 = Proc4(name="p4")

        graph.add(p1, p2, p3, p4)
        graph.connect([("p1", "p2"), ("p1", "p3"), ("p2", "p4"), ("p3", "p4")])
        graph.fit()

        References
        ----------
        [1] - https://networkx.org/documentation/stable/reference/algorithms/dag.html
        [2] - https://networkx.org/nx-guides/content/algorithms/dag/index.html
        [3] - https://graphviz.org/doc/info/attrs.html
        [4] - https://graphviz.org/docs/layouts/
        [5] - https://github.com/bermanmaxim/Pytorch-DAG

        """
        self.copy_processors = copy_processors
        self.prune_results = prune_results
        self.global_attributes = global_attributes
        self.identifier = identifier

        self.processors: dict[str, Processor] = {}
        self.processors_edges: list[tuple[str, str]] = []
        self.graph = nx.DiGraph()
        self.topo_sorted: list[str] = []

        self._node_predecessors: dict[str, list[str]] = {}
        self._node_successors: dict[str, list[str]] = {}
        self._dependencies: dict[str, set[str]] = {}

    def __getitem__(self, name: str) -> Processor:
        return self.processors[name]

    @property
    def last_node(self) -> str | list[str]:
        nodes = [node for node in self.graph.nodes() if self.graph.out_degree(node) == 0]
        if len(nodes) == 1:
            return nodes[0]
        else:
            return nodes

    def add(self, *processors: Processor) -> ProcessorsGraph:
        for processor in processors:
            if processor.name not in self.processors:
                name = f"{processor.name}{self.identifier}"
                self.processors[name] = processor
                processor.name = name
            else:
                raise ValueError(f"Node {processor.name} already exists. Node names must be unique!")

            if self.global_attributes is not None and processor.name in self.global_attributes:
                raise RuntimeError(f"Node {processor.name} already exists in global!")

        return self

    def __add__(self, other: Any) -> ProcessorsGraph:
        if type(other) is list:
            return self.add(*other)
        else:
            return self.add(other)

    def connect(self, processor_edges: list[tuple[str, str]] | None = None):
        if self.identifier != "" and processor_edges is not None:
            for i, edge in enumerate(processor_edges):
                processor_edges[i] = (f"{edge[0]}{self.identifier}", f"{edge[1]}{self.identifier}")

        if processor_edges is None:
            if self.processors_edges is None:
                raise ValueError("No edges to connect processors!")

            processor_edges = self.processors_edges
        else:
            if len(self.processors_edges) != 0:
                self.processors_edges += processor_edges
            else:
                self.processors_edges = processor_edges

        for edge in processor_edges:
            parent, child = edge[0], edge[1]

            if parent not in self.graph:
                self.graph.add_node(parent)

            if child not in self.graph:
                self.graph.add_node(child)

            self.graph.add_edge(parent, child)

        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Graph is not a DAG!")

        self.topo_sorted = list(nx.topological_sort(self.graph))

        logging.debug(f"Topological sort: {self.topo_sorted}")

        self._node_predecessors = {name: list(self.graph.predecessors(name)) for name in self.topo_sorted}
        self._node_successors = {name: list(self.graph.successors(name)) for name in self.topo_sorted}
        self._dependencies = {name: set(self._node_successors[name]) for name in self.topo_sorted}

        return self

    def chain(self) -> ProcessorsGraph:
        processor_names = [name for name in self.processors.keys()]

        chain = []
        for i in range(1, len(processor_names)):
            chain.append((processor_names[i - 1], processor_names[i]))

        self.processors_edges += chain
        self.connect()

        return self

    def _validate_nodes(self, other_graph: ProcessorsGraph) -> bool:
        self_names = [name for name in self.processors.keys()]
        other_names = [name for name in other_graph.processors.keys()]

        for self_name in self_names:
            if self_name in other_names:
                raise ValueError(f"Found duplicate node {self_name} graphs. Node names must be unique!")

        return True

    def _extend_edges(self, other_graph: ProcessorsGraph, extend_node: str) -> list[tuple[str, str]]:
        self._validate_nodes(other_graph)

        self_edges, other_edges = self.processors_edges, other_graph.processors_edges

        extend_idx = []
        for i, edge in enumerate(self_edges):
            if edge[1] == extend_node:
                extend_idx.append(i)

        if len(extend_idx) != 1:
            raise ValueError(f"Found {len(extend_idx)} extendable nodes in graph. Must be exactly 1!")

        _extend_idx = extend_idx[0]

        new_edges = copy.deepcopy(self_edges)
        new_edges.insert(_extend_idx + 1, (self_edges[_extend_idx][1], other_edges[0][0]))
        new_edges[_extend_idx + 2 : _extend_idx + 2] = other_edges

        return new_edges

    def extend(self, other_graph, extend_node) -> ProcessorsGraph:
        new_edges = self._extend_edges(other_graph, extend_node)
        new_graph = self.__class__(copy_processors=self.copy_processors)

        new_graph.add(*self.processors.values(), *other_graph.processors.values())
        new_graph.connect(new_edges)

        return new_graph

    def _insert_edges(self, other_graph: ProcessorsGraph, insert_node: str) -> list[tuple[str, str]]:
        self._validate_nodes(other_graph)

        self_edges, other_edges = self.processors_edges, other_graph.processors_edges

        last_node = self.last_node

        if type(last_node) is str:
            last_node = [last_node]
        elif type(last_node) is list:
            last_node = last_node
        else:
            raise TypeError(f"Unsupported type {type(last_node)} for last_node.")

        if insert_node in last_node + [self_edges[0][0]]:
            raise ValueError(f"Cannot insert at node {insert_node}!")

        insert_idx = []
        for i, edge in enumerate(self_edges):
            if edge[0] == insert_node:
                insert_idx.append(i)

        if len(insert_idx) != 1:
            raise ValueError(f"Found {len(insert_idx)} insertable nodes in graph. Must be exactly 1!")

        _insert_idx = insert_idx[0]

        new_edges = copy.deepcopy(self_edges)

        left_edges, right_edges = self_edges[:_insert_idx], self_edges[_insert_idx + 1 :]

        new_node_in = (new_edges[_insert_idx][0], other_edges[0][0])
        new_node_out = (other_edges[-1][1], new_edges[_insert_idx][1])

        to_insert = [new_node_in] + other_edges + [new_node_out]

        new_edges = left_edges + to_insert + right_edges

        return new_edges

    def insert(self, other_graph: ProcessorsGraph, insert_node: str) -> ProcessorsGraph:
        new_edges = self._insert_edges(other_graph, insert_node)
        new_graph = self.__class__(copy_processors=self.copy_processors)

        new_graph.add(*self.processors.values(), *other_graph.processors.values())
        new_graph.connect(new_edges)

        return new_graph

    def fit(self, *args: Any, **kwargs: Any) -> dict[str, Processor]:
        if self.copy_processors:
            processors = {}
            for name, processor in self.processors.items():
                if processor.allow_copy:
                    processors[name] = copy.deepcopy(processor)
                else:
                    processors[name] = processor
        else:
            processors = self.processors

        previous_nodes: set[str] = set()
        for i, node in enumerate(self.topo_sorted):
            processor = processors[node]

            processor.previous_processors = {name: processors[name] for name in previous_nodes}
            previous_nodes.add(processor.name)

            logging.debug(f"Running node {node} at step {i}.")

            if self.global_attributes is not None:
                global_keys = set(self.global_attributes.keys())
                processor_keys = set(processor.__dict__.keys())

                global_processor_keys = global_keys.intersection(processor_keys)

                for key in global_processor_keys:
                    setattr(processor, key, self.global_attributes[key])
            else:
                global_processor_keys = set()

            if i == 0:
                processor._run(*args, **kwargs)
            else:
                inputs = [processors[name]._results for name in self._node_predecessors[node]]
                input_args: list[Any] = list(filter(None, inputs))

                if len(input_args) == 0:
                    processor._run(*inputs)
                else:
                    input_kwargs = reduce(lambda a, b: {**a, **b}, input_args)
                    processor._run(**input_kwargs)

                if self.prune_results:
                    for prune_node, prune_node_dependencies in self._dependencies.items():
                        if len(prune_node_dependencies) == 0 or processors[prune_node]._results is None:
                            continue
                        if prune_node_dependencies.issubset(previous_nodes):
                            processors[prune_node]._results = None
                            logging.debug(f"Pruning node {prune_node} from node {node} at step {i}.")

            for key in global_processor_keys:
                setattr(processor, key, None)

        return processors

    def style_graph(self, fillcolor: str, identifier: str | None = None) -> ProcessorsGraph:
        for node in self.graph.nodes:
            if identifier is None or node.endswith(identifier):
                self.graph.nodes[node]["fillcolor"] = fillcolor
                self.graph.nodes[node]["style"] = "filled"

        return self

    @handle_plot_exception
    def draw(self, file_path: str, fontsize: float = 10.0, jupyter: bool = False, **kwargs: Any) -> str:
        A = nx.nx_agraph.to_agraph(self.graph)
        A.graph_attr.update(fontsize=fontsize, **kwargs)
        A.layout(prog="dot")

        if jupyter:
            from IPython.core.display import SVG, display

            A.draw(file_path, format="svg")
            display(SVG(file_path))
        else:
            A.draw(file_path, format="pdf")

        logging.info(f"Saved graph to {file_path}")

        return A.to_string()


class Processor(ABC):
    def __init__(self, name: str, allow_copy: bool = True) -> None:
        """Base class for processors. All processors should inherit from this class. Run method gets called in the `fit`
        method of the ProcessorsGraph.

        Parameters
        ----------
        name : str
            Name of the processor.

        Other parameters
        ----------------
        worker_id : int
            Initialized by Dataloader.
        previous_processors : dict
            Predecessors of this processor in the DAG.
        delta_time : float
            Time taken to run the processor.
        _results : dict
            Results of the processor.
        _reports : dict
            Reports returned by the iterator.
        _is_data : bool
            Flag to check if the data is MC.

        Note
        ----
        Run is executed inside the ROOTLoaderGenerator after batch arrays have been collected by the uproot iterartor.

        """
        self.name = name
        self.allow_copy = allow_copy

        self.worker_id: int | None = None
        self.previous_processors: dict[str, Processor] | None = None
        self.delta_time: float = 0.0

        self._results: dict[str, Any] | None = None

        self._reports: dict[str, Any] | None = None
        self._is_data: bool | None = None

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any):
        """Needs to be implemented by every processor object. Must return a dictionary with keys for argument names!"""
        pass

    def _run(self, *args: Any, **kwargs: Any) -> Processor:
        """Internal run method."""
        start_time = time.time()

        args, kwargs = copy.deepcopy(args), copy.deepcopy(kwargs)
        self._results = self.run(*args, **kwargs)

        self.delta_time = time.time() - start_time

        return self

    @property
    def reports(self) -> dict[str, Any] | None:
        prev_proc = self.previous_processors

        if prev_proc is not None and "input" in prev_proc:
            self._reports = prev_proc["input"].reports
        else:
            self._reports = None

        return self._reports

    @property
    def is_data(self) -> bool | None:
        prev_proc = self.previous_processors

        if prev_proc is not None and "input" in prev_proc:
            self._is_data = prev_proc["input"].is_data
        else:
            self._is_data = None

        return self._is_data

    def save(self) -> Any:
        """Save results of the processor. Should be implemented by the postprocessor."""
        pass


class CheckpointProcessor(Processor):
    def __init__(self, name: str, save_arrays: bool = False) -> None:
        """Checkpoint processor that acts as input/output node for the ProcessorsGraph. Also used to save arrays at nodes.

        Parameters
        ----------
        name : str
            Name of the processor.
        save_arrays : bool
            Flag to save arrays at this node.

        Other parameters
        ----------------
        reports : dict
            Reports returned by the iterator.
        n_events : int
            Number of events in the arrays.
        arrays : ak.Array or np.ndarray
            Arrays at this node.

        """
        super().__init__(name)
        self.save_arrays = save_arrays

        self.arrays: ak.Array | np.ndarray | None = None
        self._reports: dict[str, Any] | None = None
        self._is_data: bool | None = None
        self.n_events: int | None = None

    def run(
        self, arrays: ak.Array | np.ndarray, reports: dict[str, Any] | None = None
    ) -> dict[str, ak.Array | np.ndarray]:
        self._reports = reports

        if self._reports is not None:
            self._is_data = self._reports.get("is_data", None)

        self.n_events = len(arrays)

        if self.save_arrays:
            self.arrays = arrays

        return {"arrays": arrays}

    @property
    def reports(self) -> dict[str, Any] | None:
        return self._reports

    @property
    def is_data(self) -> bool | None:
        return self._is_data


class PostprocessorsGraph(ProcessorsGraph):
    def __init__(self) -> None:
        """Postprocessors graph to process the results of the processors.

        Note
        ----
        Takes the fitted processors dictionary returned by the ProcessorsGraph and processes it. The key difference is
        that the PostprocessorsGraph does not copy its processors allowing for the accumulation of results in each
        postprocessor. This is useful for plotting and saving results. Note that this does not allow for
        multiprocessing.

        """
        super().__init__()
        self.copy_processors = False

    def fit(self, input_processors: dict[str, Processor], *args: Any, **kwargs: Any) -> dict[str, Processor]:
        return super().fit(input_processors, *args, **kwargs)


class Postprocessor(Processor):
    def __init__(self, name: str, save_path: str | None = None, allow_copy: bool = False) -> None:
        """Postprocessor base class. All postprocessors should inherit from this class.

        Parameters
        ----------
        name : str
            Name of the postprocessor.
        save_path : str, optional
            Path with file name to save the postprocessor results in the save method, by default None.
        """
        super().__init__(name, allow_copy)

        if save_path is not None:
            os.makedirs("/".join(save_path.split("/")[:-1]), exist_ok=True)

        self.save_path = save_path


class CheckpointPostprocessor(Postprocessor):
    def __init__(self, name: str, save_input_processors: bool = False) -> None:
        """Checkpoint postprocessor."""
        super().__init__(name)
        self.save_input_processors = save_input_processors

        self.input_processors: list[dict[str, Processor]] = []
        self._is_data: bool | None = None

    def run(self, processors: dict[str, Processor], is_data: bool | None = None) -> dict[str, dict[str, Processor]]:
        if self.save_input_processors:
            self.input_processors.append(processors)

        self._is_data = is_data

        return {"processors": processors}

    @property
    def is_data(self) -> bool | None:
        return self._is_data
