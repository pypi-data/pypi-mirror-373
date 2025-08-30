from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from BKTree import BKTree, BKTreeNode


def default_post_add_hook(tree: BKTree, _: BKTreeNode):
    tree.nb_elements += 1
