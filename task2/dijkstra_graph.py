import heapq


# ==========================================
# TOPIC 1: THE GRAPH ABSTRACT DATA TYPE (ADT)
# ==========================================
class GraphADT:
    def __init__(self):
        # We use an Adjacency List (a dictionary of lists) instead of a Matrix.
        # This saves memory (O(V + E) space complexity) and improves CPU cache locality.
        self.adjacency_list = {}

    def add_vertex(self, vertex):
        """Inserts a new vertex into the graph."""
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []

    def add_edge(self, source, destination, weight):
        """
        Inserts a directed, weighted edge.
        For an undirected graph, you would add the reverse edge as well.
        """
        self.add_vertex(source)
        self.add_vertex(destination)
        # We store tuples of (weight, destination) for easy integration with heapq later
        self.adjacency_list[source].append((weight, destination))

    # ==========================================
    # TOPIC 2: DIJKSTRA'S ALGORITHM
    # ==========================================
    def dijkstra(self, start_vertex):
        """
        Finds the shortest path from the start_vertex to all other vertices.
        Time Complexity: O((V + E) log V)
        """
        # STEP 1: Initialization
        # Set all distances to infinity, except the starting node which is 0.
        distances = {vertex: float('inf') for vertex in self.adjacency_list}
        distances[start_vertex] = 0

        # STEP 2: The Min-Heap (Priority Queue)
        # This ensures we always greedily process the closest known node in O(log V) time.
        pq = [(0, start_vertex)]

        while pq:
            # Pop the vertex with the smallest known distance
            current_distance, current_vertex = heapq.heappop(pq)

            # STEP 3: The "Stale Entry" Filter (Lazy Deletion)
            # Because Python's heapq lacks a 'decrease-key' function, we might have
            # pushed multiple distance records for the same node. If we pop a record
            # that is larger than our currently known shortest distance, we discard it.
            if current_distance > distances[current_vertex]:
                continue

            # STEP 4: The "Relaxation" Step
            # Check every neighboring city connected to our current city.
            for edge_weight, neighbor in self.adjacency_list[current_vertex]:
                # Calculate the detour distance
                new_distance = current_distance + edge_weight

                # If this new detour is shorter than the neighbor's current recorded distance,
                # we 'relax' the tension, update the record, and push it to the heap.
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(pq, (new_distance, neighbor))

        return distances


# ==========================================
# MAIN EXECUTION: RUNNING THE CLASSIC SCENARIO
# ==========================================
if __name__ == "__main__":
    # Create an instance of our Graph ADT
    network = GraphADT()

    # Build the exact scenario from Appendix B of the Study Report
    # Nodes: A, B, C, D
    # Edges: A->B(4), A->C(2), C->B(1), B->D(5)
    network.add_edge('A', 'B', 4)
    network.add_edge('A', 'C', 2)
    network.add_edge('C', 'B', 1)
    network.add_edge('B', 'D', 5)

    # Calculate shortest paths starting from Node A
    source_node = 'A'
    shortest_paths = network.dijkstra(source_node)

    # Print the results
    print(f"--- Dijkstra's Algorithm Results (Source: {source_node}) ---")
    for destination, cost in shortest_paths.items():
        if cost == float('inf'):
            print(f"Path to {destination}: Unreachable")
        else:
            print(f"Shortest path cost to {destination}: {cost}")

    # Expected Output:
    # A: 0
    # B: 3 (Because A -> C -> B is 2 + 1 = 3, which is shorter than the direct A -> B route of 4)
    # C: 2
    # D: 8 (Because A -> C -> B -> D is 2 + 1 + 5 = 8)