try:
    import matplotlib.pyplot as plt
    import networkx as nx
except ImportError as exc:
    raise ImportError("Install regscale[viz] to visualize regscale.") from exc
