import networkx as nx
import plotly.graph_objects as go
from networkx.drawing.nx_agraph import graphviz_layout


def reformat_graph_layout(G, layout):
    """
    this method provide positions based on layout algorithm
    :param G:
    :param layout:
    :return:
    """
    if layout == "graphviz":
        positions = graphviz_layout(G)
    elif layout == "spring":
        positions = nx.fruchterman_reingold_layout(G, k=0.5, iterations=1000)
    elif layout == "spectral":
        positions = nx.spectral_layout(G, scale=0.1)
    elif layout == "random":
        positions = nx.random_layout(G)
    else:
        raise Exception("please specify the layout from graphviz, spring, spectral or random")

    return positions


def networkx_graph_to_plotly(
    G: nx.Graph,
    labels: dict[str, str] | None = None,
    node_size: int = 10,
    edge_weight: int = 1,
    edge_color: str = "black",
    layout: str = "graphviz",
    title: str = "",
) -> go.Figure:
    """
    Visualize a NetworkX graph using Plotly.
    """
    positions = reformat_graph_layout(G, layout)
    if not labels:
        labels = {}
    # Initialize edge traces
    edge_traces = []
    for edge in G.edges():
        x0, y0 = positions[edge[0]]
        x1, y1 = positions[edge[1]]

        edge_trace = go.Scatter(
            x=[x0, x1], y=[y0, y1], line=dict(width=edge_weight, color=edge_color), hoverinfo="none", mode="lines"
        )
        edge_traces.append(edge_trace)

    # Initialize node trace
    node_x, node_y, node_colors, node_labels = [], [], [], []
    for node in G.nodes():
        x, y = positions[node]
        node_x.append(x)
        node_y.append(y)
        node_labels.append(labels.get(node, node))
        node_colors.append(len(list(G.neighbors(node))))  # Color based on degree

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        text=node_labels,
        mode="markers+text",
        textfont=dict(family="Calibri (Body)", size=15, color="grey"),
        marker=dict(
            size=node_size,
            color=node_colors,
        ),
    )

    # Assemble the figure
    fig = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.Layout(
            showlegend=False,
            template="plotly_white",
            margin=dict(l=50, r=50, t=0, b=40),
        ),
    )
    return fig
