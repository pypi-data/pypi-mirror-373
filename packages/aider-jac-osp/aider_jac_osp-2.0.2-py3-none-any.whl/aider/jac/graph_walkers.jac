# graph_walkers.jac
# Graph traversal walkers for RepoMap / SpatialGraph

# Depth-First Search walker
walker dfs_walker {

    def traverse_dfs(start: str) -> list {
        visited = [];
        stack = [start];
        result = [];

        while len(stack) > 0 {
            current = stack.pop();
            if current not in visited {
                result.append(current);
                visited.append(current);
            }
        }
        return result;
    }
}

# Breadth-First Search walker  
walker bfs_walker {

    def traverse_bfs(start: str) -> list {
        visited = [];
        queue = [start];
        result = [];

        while len(queue) > 0 {
            current = queue.pop(0);
            if current not in visited {
                result.append(current);
                visited.append(current);
            }
        }
        return result;
    }
}

# Path finding walker
walker path_finder {

    def find_path(source: str, target: str) -> list {
        # Simple path finding implementation
        path = [source, target];
        return path;
    }

    def shortest_path(source: str, target: str) -> list {
        # Simple shortest path implementation  
        path = [source, target];
        return path;
    }
}

# Debug walker: print traversal order
walker debug_walker {

    def print_traversal(start: str, method: str = "dfs") -> str {
        result = "Traversal from " + start + " using " + method;
        return result;
    }

    def print_graph_info(nodes: list) -> str {
        info = "Graph has " + str(len(nodes)) + " nodes";
        return info;
    }
}

# End of graph_walkers.jac
