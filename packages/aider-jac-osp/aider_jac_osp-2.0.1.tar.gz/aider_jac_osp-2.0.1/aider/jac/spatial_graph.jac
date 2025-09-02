# spatial_graph.jac
# SpatialGraph implementation for OSP RepoMap

node SpatialGraph {
    has adjacency: dict = {};
    
    # Add a node to the graph
    def add_node(node_name: str) {
        if node_name not in self.adjacency {
            self.adjacency[node_name] = [];
        }
    }

        # Remove a node and all its edges
    def remove_node(node: str) {
        if node in self.adjacency {
            self.adjacency.pop(node);
            for key in self.adjacency {
                neighbors = self.adjacency[key];
                if node in neighbors {
                    neighbors.remove(node);
                }
            }
        }
    }

    # Add an edge between two nodes
    def add_edge(source: str, target: str) {
        if source in self.adjacency and target in self.adjacency {
            neighbors = self.adjacency[source];
            neighbors.append(target);
        }
    }

    # Remove an edge between two nodes
    def remove_edge(source: str, target: str) {
        if source in self.adjacency {
            neighbors = self.adjacency[source];
            if target in neighbors {
                neighbors.remove(target);
            }
        }
    }

    # Get neighbors of a node
    def get_neighbors(node: str) -> list {
        if node in self.adjacency {
            return self.adjacency[node];
        }
        return [];
    }

    # Check if a path exists between two nodes (DFS)
    def has_path(source: str, target: str) -> bool {
        if source not in self.adjacency or target not in self.adjacency {
            return False;
        }
        
        visited = [];
        stack = [source];
        
        while len(stack) > 0 {
            current = stack.pop();
            if current == target {
                return True;
            }
            if current not in visited {
                visited.append(current);
                neighbors = self.adjacency[current];
                for neighbor in neighbors {
                    stack.append(neighbor);
                }
            }
        }
        return False;
    }

    # Get all nodes in the graph
    def get_all_nodes() -> list {
        nodes = [];
        for node in self.adjacency {
            nodes.append(node);
        }
        return nodes;
    }

    # Debug: print adjacency
    def print_graph() {
        for node in self.adjacency {
            neighbors = self.adjacency[node];
            print(node + " -> " + str(neighbors));
        }
    }
}

with entry {
    graph = SpatialGraph();
    
    # Test basic functionality
    graph.add_node("file1.py");
    graph.add_node("file2.py");
    graph.add_node("file3.py");
    
    graph.add_edge("file1.py", "file2.py");
    graph.add_edge("file2.py", "file3.py");
    graph.add_edge("file1.py", "file3.py");
    
    # Test path checking
    has_path_result = graph.has_path("file1.py", "file3.py");
    
    # Display results
    graph.print_graph();
}
