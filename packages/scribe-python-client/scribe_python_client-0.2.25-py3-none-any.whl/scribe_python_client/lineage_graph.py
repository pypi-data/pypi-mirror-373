import json
import networkx as nx
# import plotly.graph_objects as go
from pyvis.network import Network
from pathlib import Path


def create_network(data, include_types, type_to_position):
    G = nx.DiGraph()
    for record in data:
        asset_type = record.get("asset_type")
        parent_type = record.get("parent_type")
        child = record.get("external_id")
        parent = record.get("parent_external_id")
        # Filter nodes based on allowed types.
        add_child = include_types is None or asset_type in include_types
        add_parent = include_types is None or parent_type in include_types

        if add_child and child:
            node_attrs = {"type": asset_type, "label": record.get("asset_name")}
            if record.get("uri"):
                node_attrs["uri"] = record.get("uri")
            G.add_node(child, **node_attrs)
        if parent and add_parent:
            node_attrs = {"type": parent_type, "label": record.get("parent_name")}
            if record.get("uri"):
                node_attrs["uri"] = record.get("uri")
            G.add_node(parent, **node_attrs)
        if child and parent and add_child and add_parent:
            G.add_edge(parent, child)

    # Assign 'layer' attribute for each node based on its type.
    for node in G.nodes():
        node_type = G.nodes[node].get('type')
        G.nodes[node]['layer'] = type_to_position.get(node_type, 1)
    return G

# def visualize_network_plotly(data, include_types, type_to_position):
#     """
#     Build and return a Plotly figure of a network graph.

#     Parameters:
#         data (list): JSON array of records.
#         include_types (set): Allowed asset types.
#         type_to_position (dict): Mapping of asset types to numeric layer positions.

#     Returns:
#         go.Figure: The Plotly figure with the network visualization.
#     """
#     # Create network graph

#     G = create_network(data, include_types, type_to_position)
#     # Compute positions using a multipartite layout (vertical alignment)
#     pos = nx.multipartite_layout(G, subset_key="layer", align="vertical")

#     # Build edge coordinates for Plotly
#     edge_x, edge_y = [], []
#     for source, target in G.edges():
#         x0, y0 = pos[source]
#         x1, y1 = pos[target]
#         edge_x.extend([x0, x1, None])
#         edge_y.extend([y0, y1, None])
#     edge_trace = go.Scatter(
#         x=edge_x, y=edge_y,
#         line=dict(width=1, color='#888'),
#         hoverinfo='none',
#         mode='lines'
#     )

#     # Build node coordinates and text lists.
#     node_x, node_y = [], []
#     node_text_trunc, node_text_hover, node_color = [], [], []
#     for node in G.nodes():
#         x, y = pos[node]
#         node_x.append(x)
#         node_y.append(y)
#         full_label = G.nodes[node].get('label', str(node))
#         truncated_label = full_label[0:30]  # truncated version for display
#         # Check for a "uri" attribute (lowercase) and create a clickable link if present.
#         uri = G.nodes[node].get('uri')
#         uri_link = f'<br><a href="{uri}" target="_blank">{uri}</a>' if uri else ""
#         node_text_trunc.append(f"{truncated_label}<br>Type: {G.nodes[node].get('type')}")
#         node_text_hover.append(f"{full_label}<br>Type: {G.nodes[node].get('type')}{uri_link}")
#         node_color.append(G.nodes[node]['layer'])

#     node_trace = go.Scatter(
#         x=node_x, y=node_y,
#         mode='markers+text',
#         textposition="bottom center",
#         hoverinfo='text',
#         marker=dict(
#             showscale=True,
#             colorscale='YlGnBu',
#             reversescale=True,
#             color=node_color,
#             size=15,
#             colorbar=dict(title='Layer')
#         ),
#         text=node_text_trunc,       # Display truncated text on the plot.
#         hovertext=node_text_hover   # Full text (with clickable URL if present) for hover.
#     )

#     # Create the Plotly figure.
#     fig = go.Figure(data=[edge_trace, node_trace],
#                     layout=go.Layout(
#                         title='<br>Integrated Network Graph Visualization',
#                         titlefont_size=16,
#                         dragmode='pan',
#                         showlegend=False,
#                         hovermode='closest',
#                         margin=dict(b=20, l=5, r=5, t=40),
#                         width=1000,
#                         height=800,
#                         xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#                         yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
#                     ))
#     return fig

def filter_network(data, include_types, include_fields):
    """
    Filter the data to only include records of the specified types
    and remove specified fields.

    Parameters:
        data (list): List of JSON records.
        include_types (set): Asset types to keep.
        include_fields (set): Fields to remove from records.

    Returns:
        list: Filtered data.
    """
    filtered_data = []
    
    for record in data:
        if record.get("asset_type") in include_types:
            # Create a copy to avoid modifying original data
            filtered_record = {key: value for key, value in record.items() if key in include_fields}
            filtered_data.append(filtered_record)
    
    return filtered_data

def visualize_network_pyvis(data, include_types, type_to_position, output_html = "graph.html"):

    width="100%" 
    height="1200px"
    layer_spacing=2.0
    node_spacing=2.0

    # import tempfile
    # output_html = tempfile.NamedTemporaryFile(delete=False)

    G = create_network(data, include_types, type_to_position)  # Create the network graph
    # 1. Assign hierarchy and determine types
    nx.set_node_attributes(
        G,
        {n: type_to_position.get(attrs["type"], 0) for n, attrs in G.nodes(data=True)},
        name="layer"
    )
    types = sorted({attrs["type"] for _, attrs in G.nodes(data=True)})

    # 2. Layout
    pos = nx.multipartite_layout(G, subset_key="layer", align="horizontal")
    pos = {n: (x * layer_spacing * 1000, y * node_spacing * 1000) for n, (x, y) in pos.items()}

    # 3. Assign colors
    base_colors = ["#e6194B", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
                   "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe"]
    color_map = {t: base_colors[i % len(base_colors)] for i, t in enumerate(types)}

    # 4. Build the graph
    net = Network(width=width, height=height, directed=True)
    net.toggle_physics(False)
    net.toggle_drag_nodes(True)
    net.show_buttons(filter_=["physics", "interaction", "clustering"])

    for node_id, attrs in G.nodes(data=True):
        x, y = pos[node_id]
        t = attrs["type"]
        c = color_map[t]
        net.add_node(node_id, label=attrs.get("label", str(node_id)), title=f"{attrs.get('label')}<br>Type: {t}<br>{attrs.get('uri','')}",
                     x=x, y=y, physics=False, group=t,
                     color={"background": c, "border": c, "highlight": {"background": c, "border": c}, "hover": {"background": c, "border": c}})
    for u, v in G.edges():
        net.add_edge(u, v)

    # 5. Inject clustering + double-click expand
    cluster_js = f"""
<script type="text/javascript">
window.addEventListener('load', () => {{
  const types = {types};
  const colors = {color_map};
  types.forEach(t => {{
    network.cluster({{
      joinCondition: opts => opts.group === t,
      clusterNodeProperties: {{
        id: 'cluster:' + t,
        label: 'Cluster: ' + t,
        shape: 'box',
        color: {{
          background: colors[t],
          border: colors[t],
          highlight: {{background: colors[t], border: colors[t]}},
          hover: {{background: colors[t], border: colors[t]}}
        }}
      }}
    }});
  }});
  network.on('doubleClick', params => {{
    if (params.nodes.length === 1) {{
      const id = params.nodes[0];
      if (network.isCluster(id)) {{
        network.openCluster(id);
      }}
    }}
  }});
}});
</script>
"""

    # 6. Inject a floating HTML legend panel
    legend_html = "<div id='legend' style='position:fixed; top:10px; right:10px; background:white; border:1px solid #ccc; padding:10px; font-family:Arial;'><strong>Legend</strong><br>"
    for t in types:
        c = color_map[t]
        legend_html += f"<div style='display:flex; align-items:center; margin-top:5px;'><span style='width:15px; height:15px; background:{c}; border:1px solid #000; display:inline-block; margin-right:5px;'></span>{t}</div>"
    legend_html += "</div>"
    
    # net.toggle_physics(True)


    # Combine HTML parts
    net.save_graph(output_html)
    with open(output_html, "r+", encoding="utf-8") as f:
        html = f.read().replace("</body>", cluster_js + legend_html + "\n</body>")
        f.seek(0); f.write(html); f.truncate()

    return output_html

def create_lineage_graph(lineage_data, type="pyvis", output_file="graph.html"):

    all_types = {record.get("asset_type") for record in lineage_data if record.get("asset_type")}
    # Exclude unwanted types.
    exclude_types = {"user", "secret", "org_secret", "commit", "actor", "build_machine"}
    types_to_position = {
            "organization": 1,
            "repo": 2,
            "branch": 3,
            "workflow": 4,
            "workflow_run": 5,
            "image": 6,
            "pod": 7,
            "namespace": 8

    }
    include_types = all_types - exclude_types
    # Generate and display the network visualization.
    if type == "plotly":
        # fig = visualize_network_plotly(lineage_data, include_types, types_to_position)
        return None
    else:
        output_file = Path(output_file)
        output_file.touch(exist_ok=True)
        output_file = output_file.resolve()
        output_file = str(output_file)
        file = visualize_network_pyvis(lineage_data, include_types, types_to_position, output_html=output_file)
        return file

if __name__ == "__main__":
    # Open the JSON file and load data.
    filepath = "demo-data/astro-lineage.json"
    with open(filepath, "r") as f:
        data = json.load(f)
    

    filename = create_lineage_graph(data, output_file="demo-data/lineage_graph.html")
    print(f"Network graph saved to {filename}")
    print(f"Open by browsing file:///{filename}")
