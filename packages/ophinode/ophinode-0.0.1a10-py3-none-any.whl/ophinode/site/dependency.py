class DependencyManager:
    def __init__(self):
        self._nodes = {}
        self._ready_nodes = {}
        self._fulfilled_nodes = {}

    def add_node(self, name, value):
        if name in self._nodes:
            node = self._nodes[name]
            if node._is_fulfilled:
                raise ValueError("cannot add a value to a node that is already fulfilled")
            node._values.append(value)
            return node
        node = DependencyNode(name, value)
        self._nodes[name] = node
        self._ready_nodes[name] = node    # new node is ready by default, because it has no dependency yet
        return node

    def add_dependency(self, source_name, target_name):
        source = self._nodes[source_name]
        target = self._nodes[target_name]
        if source._is_fulfilled:
            raise ValueError("cannot add a dependency to a node that is already fulfilled")
        source._depends_on.append(target)
        target._required_by.append(source)
        if source_name in self._ready_nodes and not target._is_fulfilled:
            self._ready_nodes.pop(source_name)

    def fulfill_node(self, name):
        node = self._nodes[name]
        node._is_fulfilled = True
        self._ready_nodes.pop(name)
        self._fulfilled_nodes[name] = node
        for i in node._required_by:
            i._fulfilled_dependencies += 1
            if len(i._depends_on) == i._fulfilled_dependencies:
                self._ready_nodes[i._name] = i

    @property
    def ready_nodes(self):
        return self._ready_nodes

class DependencyNode:
    def __init__(self, name, value):
        self._name = name
        self._values = [value]
        self._is_fulfilled = False
        self._depends_on = []
        self._required_by = []
        self._fulfilled_dependencies = 0

