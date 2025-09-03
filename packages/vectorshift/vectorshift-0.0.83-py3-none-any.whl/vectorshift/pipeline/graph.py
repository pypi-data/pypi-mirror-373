from collections import deque
import networkx as nx
from pydantic import BaseModel
from vectorshift.pipeline.node import Node

class NodeCoordinates(BaseModel):
    x: float
    y: float

class NodeCanvasMetadata(BaseModel):
    advancedOutputs: bool
    position: NodeCoordinates
    zIndex: int
    sidePanelOpen: bool
    input_mode: str


class Edge(BaseModel):
    id: str
    source_handle: str
    target_handle: str
    source: str
    target: str
    
    def __init__(self, **data):
        super().__init__(**data)

    @classmethod
    def new(cls, source: str, target: str) -> 'Edge':
        source_handle = f"{source}-outputs"
        target_handle = f"{target}-inputs"
        id = f"reactflow__edge-{source}{source_handle}-{target}{target_handle}"
        return cls(id=id, source_handle=source_handle, target_handle=target_handle, source=source, target=target)
    

class PipelineGraph:
    def __init__(self, graph: nx.MultiDiGraph, node_canvas_metadata: dict[str, NodeCanvasMetadata], graph_without_loops: nx.MultiDiGraph, edges: list[Edge], indegree: dict[str, int], sources: list[str]):
        self.graph = graph
        self.node_canvas_metadata = node_canvas_metadata
        self.graph_without_loops = graph_without_loops
        self.edges = edges
        self.indegree = indegree
        self.sources = sources

    @classmethod
    def new(cls, nodes: list[Node]) -> 'PipelineGraph':
        graph = nx.MultiDiGraph()
        graph_without_loops = nx.MultiDiGraph()
        edges = []
        edges_without_loops = []
        indegree = {}
        sources = []
        for node in nodes:
            non_cyclic_dependencies, dependencies = node.get_dependencies()
            indegree[node.id] = len(dependencies)
            edges.extend([Edge.new(dependency, node.id) for dependency in dependencies])
            edges_without_loops.extend([Edge.new(dependency, node.id) for dependency in non_cyclic_dependencies])
            if indegree[node.id] == 0:
                sources.append(node.id)
            graph.add_node(node.id)
            graph_without_loops.add_node(node.id)

        graph.add_edges_from([(edge.source, edge.target) for edge in edges])
        graph_without_loops.add_edges_from([(edge.source, edge.target) for edge in edges_without_loops])
        return cls(graph, {}, graph_without_loops, edges, indegree, sources)
    
    def validate(self) -> bool:
        if not nx.is_directed_acyclic_graph(self.graph_without_loops):
            raise Exception("Loop-creating inputs detected in inputs. Inputs that create loops in the pipeline should be added to cyclic_inputs using the add_cyclic_input method.")
        
        sccs = list(nx.strongly_connected_components(self.graph))
        for scc in sccs:
            if not self.validate_scc(scc):
                return False
        return True

    def validate_scc(self, scc: set[str]) -> bool:
        if len(scc) == 1:
            return True
        
        #Check for single entry point in the scc
        entry_point = None
        for node in scc:
            for predecessor in self.graph.predecessors(node):
                if predecessor not in scc:
                    if entry_point is not None:
                        raise Exception("More than one entry point in a cycle")
                    entry_point = node
                    break

        if entry_point is None:
            raise Exception("Entry point not found in a cycle")

        edges_to_remove = []

        #Create a subgraph containing only the nodes present in the scc
        scc_subgraph_view = nx.subgraph(self.graph, scc)
        scc_subgraph = nx.MultiDiGraph()
        scc_subgraph.add_edges_from(scc_subgraph_view.edges())

        for predecessor in scc_subgraph.predecessors(entry_point):
            edges_to_remove.append((predecessor, entry_point))
            self.indegree[entry_point] -= 1

        scc_subgraph.remove_edges_from(edges_to_remove)
        if not nx.is_directed_acyclic_graph(scc_subgraph):
            raise Exception("Cycle is not well-ordered")

        self.graph.remove_edges_from(edges_to_remove)

        return True
    
    def populate_node_canvas_metadata(self):
        queue = deque(self.sources)
        topo_sort_level = 0
        z_index = 0
        while len(queue) > 0:
            number_of_elements_in_level = len(queue)
            successors_to_append = []
            for  vertical_level, node_id in enumerate(queue):
                self.node_canvas_metadata[node_id] = NodeCanvasMetadata(
                    advancedOutputs=False,
                    position=NodeCoordinates(x=topo_sort_level * 1200, y=vertical_level * 600),
                    zIndex=z_index,
                    sidePanelOpen=True,
                    input_mode="inputs"
                )

                z_index += 1
                
                for successor in self.graph.successors(node_id):
                    self.indegree[successor] -= 1
                    if self.indegree[successor] == 0:
                        successors_to_append.append(successor)

            queue.extend(successors_to_append)

            for _ in range(number_of_elements_in_level):
                queue.popleft()

            topo_sort_level += 1


    def visualize(self) -> str:
        """Visualize the pipeline graph in the terminal using ASCII art."""
        from collections import defaultdict
        import math

        # Get node positions using a simple layout algorithm
        positions = {}
        levels = defaultdict(list)
        
        # First, do a topological sort to get levels
        visited = set()
        temp_visited = set()
        
        def visit(node):
            if node in temp_visited:
                return
            if node in visited:
                return
            temp_visited.add(node)
            for neighbor in self.graph.successors(node):
                visit(neighbor)
            temp_visited.remove(node)
            visited.add(node)
            # Calculate level based on longest path from source
            level = 0
            for pred in self.graph.predecessors(node):
                if pred in positions:
                    level = max(level, positions[pred][1] + 1)
            positions[node] = (0, level)  # x will be adjusted later
            levels[level].append(node)
        
        # Visit all nodes
        for node in self.graph.nodes():
            if node not in visited:
                visit(node)
        
        # Adjust x positions within each level
        for level in levels:
            nodes = levels[level]
            width = len(nodes)
            for i, node in enumerate(nodes):
                x = i - width // 2
                positions[node] = (x, positions[node][1])
        
        # Create the visualization
        if not positions:
            return "Empty graph"
            
        # Find bounds
        min_x = min(x for x, _ in positions.values())
        max_x = max(x for x, _ in positions.values())
        min_y = min(y for _, y in positions.values())
        max_y = max(y for _, y in positions.values())
        
        # Create the canvas
        width = (max_x - min_x + 1) * 4 + 1
        height = (max_y - min_y + 1) * 2 + 1
        canvas = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw edges
        for edge in self.edges:
            start = positions[edge.source]
            end = positions[edge.target]
            
            # Calculate positions in canvas coordinates
            start_x = (start[0] - min_x) * 4 + 2
            start_y = (start[1] - min_y) * 2 + 1
            end_x = (end[0] - min_x) * 4 + 2
            end_y = (end[1] - min_y) * 2 + 1
            
            # Draw vertical line
            for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
                if canvas[y][start_x] == ' ':
                    canvas[y][start_x] = '│'
            
            # Draw horizontal line
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                if canvas[end_y][x] == ' ':
                    canvas[end_y][x] = '─'
            
            # Draw corners
            canvas[end_y][start_x] = '└'
            if start_x < end_x:
                canvas[end_y][end_x] = '┐'
            else:
                canvas[end_y][end_x] = '┌'
        
        # Draw nodes
        for node, (x, y) in positions.items():
            canvas_x = (x - min_x) * 4 + 2
            canvas_y = (y - min_y) * 2 + 1
            
            # Draw node box
            node_display = f"[{node}]"
            for i, char in enumerate(node_display):
                if 0 <= canvas_x - 1 + i < width:
                    canvas[canvas_y][canvas_x - 1 + i] = char
        
        # Convert canvas to string
        return '\n'.join(''.join(row) for row in canvas)