"""A wrapper over matplotlib to easy plotting for research papers inspired by ggplot2.

TODO
"""

from ..infix_fn import infix


class Layer: ...


@infix
def on(top_layer: Layer, bottom_layer: Layer) -> Layer: ...
