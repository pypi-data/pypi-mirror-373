from asyncio import run

from chattr.graph.builder import Graph
from chattr.settings import Settings

graph: Graph = run(Graph.create(Settings()))
