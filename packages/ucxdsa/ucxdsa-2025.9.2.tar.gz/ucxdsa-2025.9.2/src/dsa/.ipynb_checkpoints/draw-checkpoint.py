from dsa.tree import Tree, TreeNode
from dsa.heap import Heap, MinHeap
from dsa.trie import Trie, TrieNode

import networkx as nx
import matplotlib.pyplot as plt

class Draw:
    def __init__(self):
        self.figsize = (5, 3)
        
    def render(self, **kwargs):
        pass

    def set_figsize(self, figsize):
        self.figsize = figsize

    def save(self, filename, **kwargs):
#        plt.figure(figsize=self.figsize)
        plt = self.render(**kwargs)
        plt.axis('off')
        plt.savefig(filename)

    def draw(self, **kwargs):
#        plt.figure(figsize=self.figsize)
        plt = self.render(**kwargs)
        plt.axis('off')
        plt.show()

class TreeDraw(Draw):
    """
    A class for drawing a tree using networkx
    """
    def __init__(self, tree: Tree):
        """ 
        Args:
            tree: tree structure to draw
        """
        super().__init__()
        self.tree = tree
        
    def add_edges(self, graph, node, pos=None, x=0, y=0, layer=1):
        """
        Helper function to organize nodes in a tree position
    
        Args:
            graph: networkx graph opbject
            node: starting tree node
            pos: dictionary of positions
            x, y: integer starting positions
            layer: level of the node
        """
        if pos is None:
            pos = {}
        if node is not None:
            pos[node.value] = (x, y)
            if node.left:
                graph.add_edge(node.value, node.left.value)
                pos = self.add_edges(graph, node.left, pos=pos, x=x-1/layer, y=y-1, layer=layer+1)
            if node.right:
                graph.add_edge(node.value, node.right.value)
                pos = self.add_edges(graph, node.right, pos=pos, x=x+1/layer, y=y-1, layer=layer+1)
        return pos
    
    def render(self, **kwargs):
        """
        render the tree 
        """
        super().render(**kwargs)
        graph = nx.DiGraph()
#        plt.figure(figsize=figsize)
        pos = self.add_edges(graph, self.tree.root)
        nx.draw(graph, pos, with_labels=True, arrows=False, node_color="tab:blue", node_size=800, font_size=12, font_color="white") 
        return plt

class HeapDraw(Draw):
    """
    A class for drawing a heap with networkx
    """
    def __init__(self, heap: Heap, **kwargs):
        super().__init__(**kwargs)
        self.heap = heap

    def array_to_node(self, index: int, array):
        """
        Helper function to convert an array implementation of a heap to a node
    
        Args:
            index: index of node
            array: array containing node values (organized as a complete tree)
        """
        if index >= len(array):
            return None
        else:
            value = array[index]
            left_index = index * 2 + 1
            right_index = index * 2 + 2
            node = TreeNode(value)
            node.left = self.array_to_node(left_index, array)
            node.right = self.array_to_node(right_index, array)
            return node

    def render(self, **kwargs):
        """
        Draw a heap using networkx
    
        Args:
            heap: heap object to draw
        """
        node = self.array_to_node(0, [node[1] for node in self.heap.enumerate()])
        tree = Tree(node)

        tree_draw = TreeDraw(tree)
        return tree_draw.render(**kwargs)
    
class TrieDraw(Draw):
    """
    A class for drawing a trie with networkx
    """
    def __init__(self, trie: Trie, **kwargs):
        super().__init__(**kwargs)
        self.trie = trie
        
    def _add_edges(self, graph, node, current_path):
        if node is None:
            return
        for char, child in node.children.items():
            new_path = current_path + char
            graph.add_edge(current_path, new_path, label=char)
            self._add_edges(graph, child, new_path)
    
    def to_networkx(self):
        graph = nx.DiGraph()
        self._add_edges(graph, self.trie.root, "")
        return graph
    
    def hierarchical_pos(self, G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
        pos = {}
        if root is None:
            root = next(iter(nx.topological_sort(G)))
    
        def _hierarchical_pos(G, node, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, parsed=[]):
            if pos is None:
                pos = {node: (xcenter, vert_loc)}
            else:
                pos[node] = (xcenter, vert_loc)
    
            children = list(G.neighbors(node))
            if not isinstance(G, nx.DiGraph) and parent is not None:
                children.remove(parent)
    
            if len(children) != 0:
                dx = width / len(children)
                nextx = xcenter - width / 2 - dx / 2
                for child in children:
                    nextx += dx
                    pos = _hierarchical_pos(G, child, width=dx, vert_gap=vert_gap, vert_loc=vert_loc - vert_gap, xcenter=nextx, pos=pos, parent=node, parsed=parsed)
            return pos
    
        return _hierarchical_pos(G, root, width, vert_gap, vert_loc, xcenter)
    
    def render(self, **kwargs):
        super().render(**kwargs)
        trie_graph = self.to_networkx()
        
        pos = self.hierarchical_pos(trie_graph)
        
#        plt.figure(figsize=self.figsize)
        nx.draw_networkx_edges(trie_graph, pos, arrows=True)
        
        ax = plt.gca()
        for node in pos:
            x, y = pos[node]
            rectangle = plt.Rectangle((x - 0.025, y - 0.05), 0.05, 0.1, color="tab:blue")
            ax.add_patch(rectangle)
            plt.text(x, y, node[-1] if node else "", verticalalignment='center', horizontalalignment='center', fontsize=10, color="white")
        return plt


class GraphDraw(Draw):
    """
    A class for drawing graphs with networkx
    """
    def __init__(self, graph, directed=False, weighted=False):
        super().__init__()
        self.graph = graph
        self.directed = directed
        self.weighted = weighted
            
    def render(self, pos=None, show_mst=False, mst_only=False, **kwargs):
        super().render(**kwargs)
        edges = self.graph.edges()

        plt.figure(figsize=(5, 3))
        if self.directed:
            g = nx.DiGraph()
        else:
            g = nx.Graph()

        if self.weighted:
            g.add_weighted_edges_from(edges)
        else:
            g.add_edges_from(edges)
    
        if pos is None:
            pos = nx.shell_layout(g) 

        if mst_only:
            show_mst = True
            nx.draw_networkx_nodes(g, pos, node_color="tab:blue", node_size=800)
            nx.draw_networkx_labels(g, pos, font_size=10, font_color="white")
        else:
            nx.draw(g, pos, with_labels=True, node_color="tab:blue", node_size=800, font_size=10, font_color="white")

        if self.weighted:
            edge_labels = {(u, v): d["weight"] for u, v, d in g.edges(data=True)}
            nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_size=14, label_pos=0.5)

        if show_mst:
            T = nx.minimum_spanning_tree(g)
            nx.draw_networkx_edges(T, pos, edge_color="tab:red", width=2)
        return plt

