import copy
import json
import logging
import os
import re
from typing import Self, Callable, Sequence, Hashable, Any

logger = logging.getLogger(__name__)


class BKTreeNode[ValueT]:
    def __init__(self, value: ValueT, value_type: type[ValueT] = str):
        self.value: ValueT = value
        self.children: dict[int, Self] = {}
        self.value_type: type[ValueT] = value_type

    def __eq__(self, other):
        """Check the equality between two BKTree nodes.

        Two nodes are equals when their value is the same and their children are equals (at the same distance).

        Args:
            other (BKTreeNode[ValueT]): The second node.

        Returns:
            True if the two nodes are equals.
        """
        if not isinstance(other, BKTreeNode):
            return NotImplemented

        if self.value != other.value:
            return False

        if len(self.children.items()) != len(other.children.items()):
            return False

        for (distance_1, child_1), (distance_2, child_2) in zip(
            self.children.items(), other.children.items()
        ):
            if distance_1 != distance_2 or child_1 != child_2:
                return False

        return True

    @classmethod
    def from_dict(
        cls,
        node_input,
        value_type: type[ValueT] = str,
    ):
        if value_type is str:
            new_node = cls(value=node_input["value"], value_type=value_type)
        else:
            new_node = cls(
                value=value_type(**node_input["value"]), value_type=value_type
            )
        for key, value in node_input["children"].items():
            new_node.children[int(key)] = cls.from_dict(value)
        return new_node

    def __len__(self):
        return 1 + sum(len(child) for child in self.children.values())

    def __str__(self, level: int = 0, distance: int = 0):
        ret = "\t" * level + repr(distance) + " " + repr(self.value) + "\n"
        for distance, child in self.children.items():
            ret += child.__str__(level + 1, distance)
        return ret

    def copy(self):
        return copy.deepcopy(self)

    def to_dict(self):
        return {
            "value": self.value,
            "children": {
                str(distance): child_node.to_dict()
                for distance, child_node in self.children.items()
            },
        }


class BKTree[ValueT, NodeT: BKTreeNode]:
    def __init__(
        self,
        distance_function: Callable[[Sequence[Hashable], Sequence[Hashable]], int],
        max_distance: int = 0,
        key: Callable[[ValueT], str] | None = None,
        value_type: type[ValueT] = str,
        node_type: type[NodeT] = BKTreeNode,
        *,
        post_add_hook: Callable[[Self, NodeT], None] = lambda tree, node: None,
        post_already_added_hook: Callable[[Self, NodeT], None] = lambda tree,
        node: None,
        post_filter_add_hook: Callable[[Self, NodeT, NodeT], None] = lambda tree,
        node,
        filtered_node: None,
        post_insert_subtree_hook: Callable[[Self, NodeT, NodeT], None] = lambda tree,
        node,
        subtree_root: None,
        post_combine_hook: Callable[[Self, NodeT, NodeT], None] = lambda tree,
        node,
        combined_node: None,
    ):
        self.root: NodeT | None = None
        self.distance_function = distance_function
        self.max_distance = max_distance
        self.nb_elements = 0
        self.key = key if key else lambda x: x
        self.value_type = value_type
        self.node_type = node_type
        self.post_add_hook = post_add_hook
        self.post_already_added_hook = post_already_added_hook
        self.post_filter_add_hook = post_filter_add_hook
        self.post_insert_subtree_hook = post_insert_subtree_hook
        self.post_combine_hook = post_combine_hook

    @classmethod
    def from_json(
        cls,
        filepath: os.PathLike | str,
        distance_function: Callable[[Sequence[Hashable], Sequence[Hashable]], int],
        key: Callable[[ValueT], str] | None = None,
        value_type: type[ValueT] = str,
        node_type: type[NodeT] = BKTreeNode,
        *,
        post_add_hook: Callable[[Self, NodeT], None] = lambda tree, node: None,
        post_already_added_hook: Callable[[Self, NodeT], None] = lambda tree,
        node: None,
        post_filter_add_hook: Callable[[Self, NodeT, NodeT], None] = lambda tree,
        node,
        filtered_node: None,
        post_insert_subtree_hook: Callable[[Self, NodeT, NodeT], None] = lambda tree,
        node,
        subtree_root: None,
        post_combine_hook: Callable[[Self, NodeT, NodeT], None] = lambda tree,
        node,
        combined_node: None,
    ) -> Self:
        """Create a BK-Tree from a JSON file.

        Args:
            filepath (os.PathLike): The path to the JSON file.
            distance_function (Callable): A function that calculates the distance between two song identifiers
            key (Callable[[ValueT], str] | None): A callable that return the string to be compared.
            value_type (type[ValueT]): The type of the value to store in the tree.
            node_type (type[NodeT]): The type of the node to use in the tree.
            post_add_hook (Callable[[Self, NodeT], None]): A callable that is called after adding a new node to the tree.
            post_already_added_hook (Callable[[Self, NodeT], None]): A callable that is called when trying to add a node that is
                already in the tree.
            post_filter_add_hook (Callable[[Self, NodeT, NodeT], None]): A callable that is called after adding a node to the tree
            post_insert_subtree_hook (Callable[[Self, NodeT, NodeT], None]): A callable that is called after
                inserting a subtree to the tree.
            post_combine_hook (Callable[[Self, NodeT, NodeT], None]): A callable that is called after combining two trees.

        Returns:
            CustomBKTree: The BK-Tree.
        """
        with open(filepath, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)

        return cls.create_tree(
            json_data,
            distance_function,
            key,
            value_type=value_type,
            node_type=node_type,
            post_add_hook=post_add_hook,
            post_already_added_hook=post_already_added_hook,
            post_filter_add_hook=post_filter_add_hook,
            post_insert_subtree_hook=post_insert_subtree_hook,
            post_combine_hook=post_combine_hook,
        )

    @classmethod
    def create_tree(
        cls,
        json_data: Any,
        distance_function: Callable[[Sequence[Hashable], Sequence[Hashable]], int],
        key: Callable[[ValueT], str] | None = None,
        value_type: type[ValueT] = str,
        node_type: type[NodeT] = BKTreeNode,
        *,
        post_add_hook: Callable[[Self, NodeT], None] = lambda tree, node: None,
        post_already_added_hook: Callable[[Self, NodeT], None] = lambda tree,
        node: None,
        post_filter_add_hook: Callable[[Self, NodeT, NodeT], None] = lambda tree,
        node,
        filtered_node: None,
        post_insert_subtree_hook: Callable[[Self, NodeT, NodeT], None] = lambda tree,
        node,
        subtree_root: None,
        post_combine_hook: Callable[[Self, NodeT, NodeT], None] = lambda tree,
        node,
        combined_node: None,
    ) -> Self:
        tree = cls(
            distance_function,
            json_data["max_distance"],
            key=key,
            value_type=value_type,
            node_type=node_type,
            post_add_hook=post_add_hook,
            post_already_added_hook=post_already_added_hook,
            post_filter_add_hook=post_filter_add_hook,
            post_insert_subtree_hook=post_insert_subtree_hook,
            post_combine_hook=post_combine_hook,
        )
        tree.nb_elements = json_data["nb_elements"]
        tree.root = node_type.from_dict(json_data["nodes"], value_type=value_type)

        return tree

    def __eq__(self, other):
        if not isinstance(other, BKTree):
            return NotImplemented

        if self.nb_elements != other.nb_elements:
            logger.debug(
                f"The number of elements is not the same: {self.nb_elements} - {other.nb_elements}"
            )
            return False

        return self.root == other.root

    def __len__(self):
        if self.root:
            return len(self.root)
        else:
            return 0

    def __contains__(self, item: ValueT):
        if self.root is None:
            return False

        for element in self:
            if element == item:
                return True

        return False

    def __iter__(self):
        return self.depth_search(self.root)

    def depth_search(self, node: NodeT):
        if node:
            yield node.value
            for child in node.children.values():
                yield from self.depth_search(child)

    def __str__(self, level: int = 0):
        return self.root.__str__()

    def contains_node(self, node: NodeT):
        if self.root is None:
            return False

        if self.root is node:
            return True

        return self._contains_node(node, self.root)

    def _contains_node(self, node: NodeT, comparison_node: NodeT):
        for child_node in comparison_node.children.values():
            if child_node is node:
                return True
            elif self._contains_node(node, child_node):
                return True

        return False

    def search(
        self,
        key_value: str,
        max_distance: int | None = None,
        start_node: NodeT | None = None,
    ) -> list[NodeT]:
        """Searches in the BK-Tree nodes that are within a specified distance from another node.

        Args:
            key_value (str): The string value to search for.
            max_distance (int): The maximum allowable distance from the node value.
            start_node (NodeT | None): The node from which to start searching

        Returns:
            list[NodeT]: A list of nodes that are within the max_distance from the given value.
        """
        if self.root is None:
            return []

        if start_node is None:
            start_node = self.root

        if max_distance is None:
            max_distance = self.max_distance

        return self._search(start_node, key_value, max_distance)

    def _search(self, node: NodeT, key_value: str, max_distance: int) -> list[NodeT]:
        """Recursively search in the BK-Tree for nodes that are within a specified distance from another node.

        Args:
            node (NodeT): The current node being compared.
            key_value (str): The string value to search for.
            max_distance (int): The maximum allowable distance from the value.

        Returns:
            list[NodeT]: A list of nodes that are within the max_distance from the given value.
        """
        distance = self.distance_function(key_value, self.key(node.value))
        results: list[NodeT] = []
        if distance <= max_distance:
            results.append(node)

        # Check subtrees within distance range
        for dist in range(distance - max_distance, distance + max_distance + 1):
            child = node.children.get(dist)
            if child is not None:
                results.extend(self._search(child, key_value, max_distance))

        return results

    def add(self, value: ValueT) -> tuple[NodeT | None, bool]:
        """Add a value to the BK-Tree. If the tree is empty, the value becomes the root.

        Args:
            value: The value to add.

        Returns:
            NodeT: The node where the value is stored.
            bool: Whether it's a new Node or not.
        """
        string_value = self.key(value)
        logger.debug(f"Adding {string_value} to the tree.")

        if self.root is None:
            logger.debug(f"Setting the root of the tree to {string_value}")
            self.root = self.node_type(value, self.value_type)
            self.nb_elements = 1
            return self.root, True
        else:
            # Search if the identifier or a similar identifier is already in the tree.
            search_result = self.search(string_value, self.max_distance)

            # If there is still no similar identifier, we add the song to the tree.
            if not search_result:
                return self._add(self.root, value), True
            else:
                if len(search_result) > 1:
                    logger.warning(
                        f"Several results for the identifier {string_value}: {[self.key(node.value) for node in search_result]}"
                    )
                    return search_result[0], False
                else:
                    logger.debug(
                        f"{self.key(search_result[0].value)} is similar to {self.key(value)} and is already in the tree."
                    )
                    self.post_already_added_hook(self, search_result[0])
                    return search_result[0], False

    def _add(self, node: NodeT, value: ValueT) -> NodeT:
        """Recursively adds the song to the correct position in the BK-Tree.

        Args:
            node (NodeT): The current node being compared to the song identifier.
            value (T): The value to add to the tree.

        Returns:
            NodeT: The newly created node.
        """
        comparison_distance = self.distance_function(
            self.key(node.value), self.key(value)
        )

        if comparison_distance in node.children:
            return self._add(node.children[comparison_distance], value)
        else:
            new_node = self.node_type(value, self.value_type)
            node.children[comparison_distance] = new_node
            self.nb_elements += 1
            self.post_add_hook(self, new_node)
            logger.debug(
                f"New song: {self.key(value)} as a children of {self.key(node.value)} (dist: {comparison_distance})"
            )
            return new_node

    def filter(self, filter_fn: Callable[[NodeT], bool]) -> "BKTree":
        filtered_tree = BKTree(self.distance_function, self.max_distance, key=self.key)

        if not self.root:
            return filtered_tree

        def _filter_recursive(node: NodeT):
            if filter_fn(node):
                if filtered_tree.root is None:
                    filtered_tree.root = self.node_type(node.value, self.value_type)
                    filtered_tree.nb_elements = 1
                    added_node = filtered_tree.root
                else:
                    added_node = filtered_tree._add(filtered_tree.root, node.value)
                self.post_filter_add_hook(filtered_tree, added_node, node)

            for _, child in node.children.items():
                _filter_recursive(child)

        _filter_recursive(self.root)

        return filtered_tree

    def insert(self, value: ValueT, start_node: NodeT) -> NodeT | None:
        """Insert a value in a subtree.

        Args:
            value (T): The value to insert
            start_node (NodeT): The start node of the subtree

        Returns:
            NodeT: The newly created node.
        """
        if not isinstance(start_node, self.node_type):
            raise TypeError(
                f"The start_node must be of type BKTreeNode, not of type {type(start_node)}"
            )

        if not self.contains_node(start_node):
            raise ValueError("The start_node must already be in the BKTree.")

        logger.debug(
            f"Inserting {value} to the subtree from {self.key(start_node.value)}."
        )

        # Search if the identifier or a similar identifier is already in the tree.
        search_result = self.search(
            self.key(value), self.max_distance, start_node=start_node
        )

        if not search_result:
            # Remove ending content between parentheses or brackets from the identifier.
            cleaned_identifier = re.sub(
                r"((\(.+\))|(\[.+]))$", "", self.key(value)
            ).rstrip()
            if cleaned_identifier != self.key(value):
                # Search if the cleaned_identifier is already in the tree
                search_result = self.search(
                    cleaned_identifier,
                    max_distance=self.max_distance,
                    start_node=start_node,
                )

        # If there is still no similar identifier, we add the song to the tree.
        if not search_result:
            comparison_node = start_node
            new_node = self._add(comparison_node, value)
            return new_node
        else:
            if len(search_result) > 1:
                logger.warning(
                    f"Several results for the identifier {self.key(value)}: {[self.key(node.value) for node in search_result]}"
                )
                return None
            else:
                logger.debug(
                    f"{self.key(search_result[0].value)} is similar to {self.key(value)} and is already in the tree."
                )
                return search_result[0]

    def search_node_and_parent(
        self, value: ValueT
    ) -> tuple[NodeT | None, NodeT | None, int | None]:
        """Get the node containing the value and his parent node.

        Args:
            value:
                The value of the node to retrieve.

        Returns:
            A tuple with the node containing the value, his parent_node and the distance between them. If the node containing the value is
            the root node, then the parent_node and the distance is equal to None. If the value isn't in the tree, the function return a
            tuple containing None for the 3 values.
        """
        return self._search_node_and_parent(value, self.root)

    def _search_node_and_parent(
        self,
        value: ValueT,
        node: NodeT,
        parent: NodeT | None = None,
        distance_parent: int | None = None,
    ) -> tuple[NodeT | None, NodeT | None, int | None]:
        """Get the node containing the value and his parent node.

        Args:
            value:
                The value of the node to retrieve.
            node:
                The node from which we search the value.
            parent:
                The parent of the node parameter. Useful only for the function to be called recursively, do not use when calling the
                function. None by default.
            distance_parent:
                The distance between the node and the parent. Useful only for the function to be called recursively, do not use when
                calling the function. None by default.

        Returns:
            A tuple with the node containing the value, his parent_node and the distance between them. If the node containing the value is
            the root node, then the parent_node and the distance is equal to None. If the value isn't in the tree, the function return a
            tuple containing None for the 3 values.
        """
        if node.value == value:
            return node, parent, distance_parent

        for dist, child in node.children.items():
            found_node, found_parent, distance = self._search_node_and_parent(
                value, child, node, dist
            )
            if found_node:
                return found_node, found_parent, distance

        # If the song isn't found, return None and None.
        return None, None, None

    def get_node_largest_subtree(self, node: NodeT) -> tuple[NodeT | None, int | None]:
        """Getting the node child with the largest size and the distance from the node.

        Args:
            node:
                The input node.

        Returns:
            A tuple that contains the node and the distance from the parent.
            If the node hasn't child, returns a tuple with None
        """
        if not self.contains_node(node):
            raise ValueError("The node passed in parameter must be in the BKTree.")

        if not node.children:
            return None, None

        largest_subtree_value = 0
        distance_from_parent = 0
        best_node: NodeT | None = None

        for distance, child in node.children.items():
            if (child_length := len(child)) > largest_subtree_value:
                largest_subtree_value = child_length
                best_node = child
                distance_from_parent = distance

        logger.debug(f"Largest subtree value: {largest_subtree_value}")
        return best_node, distance_from_parent

    def insert_subtree(self, node: NodeT, parent_node: NodeT) -> None:
        """Insert a subtree in the tree from the parent node passed in parameter.

        Args:
            node:
                The root of the subtree to insert.
            parent_node:
                The parent node of the root of the subtree.
        """
        new_node = self.insert(node.value, parent_node)
        if new_node:
            self.post_insert_subtree_hook(self, new_node, node)

        for _, child in node.children.items():
            self.insert_subtree(child, parent_node)

    def remove(self, value: ValueT) -> None:
        if not self.root:
            return

        if self.root.value == value:
            logger.debug("The song to remove is the root node.")
            if self.root.children:
                root_children = self.root.children.copy()
                initial_root_size = len(self.root)
                new_root, distance_from_root = self.get_node_largest_subtree(self.root)
                root_children.pop(distance_from_root)
                # Substract the number of children, because we will reinsert it after and it will re-increment the counter.
                self.nb_elements -= initial_root_size - len(new_root)
                self.root = new_root

                for _, child in root_children.items():
                    self.insert_subtree(child, self.root)
            else:
                self.root = None
                self.nb_elements = 0

            return

        node, parent, distance_from_parent = self.search_node_and_parent(value)

        if node is None:
            raise

        logger.debug(f"The node identifier is {self.key(node.value)}.")
        logger.debug(f"The parent identifier is {self.key(parent.value)}.")

        if node:
            if node.children:
                # There is always a parent ? Otherwise, it is the root but the case is already treated above.
                if parent:
                    original_children = node.children.copy()
                    new_node, distance_from_node = self.get_node_largest_subtree(node)
                    original_children.pop(distance_from_node)
                    parent.children[distance_from_parent] = new_node
                    # Substract the number of children, because we will reinsert it after and it will re-increment the counter.
                    self.nb_elements -= len(node) - len(new_node)
                    for _, child in original_children.items():
                        self.insert_subtree(child, parent)
            else:
                parent.children.pop(distance_from_parent)
                self.nb_elements -= 1

    def remove_key(self, key_value: str):
        node_to_delete = self.search(key_value, max_distance=0)
        if node_to_delete:
            if len(node_to_delete) == 1:
                self.remove(node_to_delete[0].value)
            else:
                for element in node_to_delete:
                    self.remove(element.value)
        else:
            logger.error("No nodes with this identifier.")

    def clear(self):
        self.root = None
        self.nb_elements = 0

    def copy(self) -> "BKTree":
        tree_copy = BKTree(self.distance_function, self.max_distance, key=self.key)
        if self.root:
            tree_copy.root = self.root.copy()
            tree_copy.nb_elements = self.nb_elements
        return tree_copy

    def collect_values(self) -> list[ValueT]:
        """Collect all the values in the BK-Tree.

        Returns:
            list[Song]: The list of the songs.
        """
        values: list[ValueT] = []
        if self.root:
            self._collect_values(self.root, values)

        return values

    def _collect_values(self, node: NodeT, values: list[ValueT]):
        values.append(node.value)

        for child in node.children.values():
            self._collect_values(child, values)

    def combine(self, other_tree: Self):
        """Combine the data of two CustomBKTree.

        Args:
            other_tree: The other CustomBKTree
        """
        if other_tree.root:
            self._combine(other_tree.root)

    def _combine(self, other_tree_node: NodeT):
        new_node, _ = self.add(other_tree_node.value)

        if new_node:
            self.post_combine_hook(self, new_node, other_tree_node)

        for node in other_tree_node.children.values():
            self._combine(node)

    def find_best_root_node(self) -> ValueT | None:
        """Find the root node with the best efficiency (which has the lowest average distance from other nodes)

        Returns:
            NodeT | Node: The node with the best efficiency or None if the tree is empty.
        """
        min_avg_distance = float("inf")
        best_node = None

        data = self.collect_values()

        for candidate in data:
            total_distance = sum(
                self.distance_function(self.key(candidate), self.key(other))
                for other in data
                if other != candidate
            )
            avg_distance = total_distance / len(data)

            if avg_distance < min_avg_distance:
                min_avg_distance = avg_distance
                best_node = candidate

        return best_node

    def balance(self):
        best_song_node = self.find_best_root_node()
        tree_copy = self.copy()
        self.clear()
        self.add(best_song_node)
        tree_copy.remove(best_song_node)
        self.combine(tree_copy)

    def to_json(self, filepath, balance_tree: bool = False) -> dict[str, Any]:
        if balance_tree:
            self.balance()

        json_data = {
            "nb_elements": self.nb_elements,
            "max_distance": self.max_distance,
            "nodes": self.root.to_dict() if self.root else {},
        }

        with open(filepath, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)

        return json_data
