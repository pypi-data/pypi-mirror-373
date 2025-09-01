from ._qt import QtCore, QtWidgets
from . import _graph

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    # python -m grill.views._graph
    app = QtWidgets.QApplication([])
    # TODO: create "plugs" from parsing label?
    nodes_info = {
        1: dict(
            label="{<one>x:y:z|<two>z}",
            style="rounded",  # these can be set at the graph level
            shape="record",
        ),
        2: dict(
            label="{<three>a|<four>b}",
            style='rounded',
            shape="record",
        ),
        3: dict(
            label="{<five>c|<six>d}",
            style='rounded',
            shape="record",
        ),
        "parent": dict(
            shape="box", fillcolor="#afd7ff", color="#1E90FF", style="filled,rounded"
        ),
        "child1": dict(
            shape="box", fillcolor="#afd7ff", color="#1E90FF", style="filled,rounded"
        ),
        "child2": dict(
            shape="box", fillcolor="#afd7ff", color="#1E90FF", style="invis"
        ),
    }
    edges_info = (
        (1, 1, dict(color='sienna:crimson:orange')),
        (1, 2, dict(color='crimson')),
        (2, 1, dict(color='seagreen')),
        (3, 2, dict(color='steelblue', tailport='five')),
        (3, 1, dict(color='hotpink', tailport='five')),
        ("parent", "child1"),
        ("parent", "child2", dict(label='invis')),
    )

    graph = _graph.nx.MultiDiGraph()
    graph.add_nodes_from(nodes_info.items())
    graph.add_edges_from(edges_info)
    graph.graph['graph'] = {'rankdir': 'LR'}
    graph.graph['edge'] = {"color": 'crimson'}
    outline_color = "#4682B4"  # 'steelblue'
    background_color = "#F0FFFF"  # 'azure'
    # graph.graph['node'] = {'shape': 'none', 'color': outline_color, 'fillcolor': background_color}
    table_row = '<tr><td port="{port}" border="0" bgcolor="{color}" style="ROUNDED">{text}</td></tr>'

    connection_nodes = dict(
        ancestor=dict(
            # fields=('ancestor', 'cycle_in', 'roughness', 'cycle_out', 'surface'),
            plugs={
                '': 0,
                'cycle_in': 1,
                'roughness': 2,
                'cycle_out': 3,
                'surface': 4
            },
            shape='none',
            connections=dict(
                surface=[('successor', 'surface')],
                cycle_out=[('ancestor', 'cycle_in')],
            ),
        ),
        successor=dict(
            plugs={'': 0, 'surface': 1},
            shape='none',
            connections=dict(),
        )
    )
    connection_edges = []

# A:\write\code\git\easy-edgedb\chapter10\assets\dracula-3d-Model-Place-rnd-main-GoldenKroneHotel-lead-base-whole.1.usda
    def _add_edges(src_node, src_name, tgt_node, tgt_name):
        tooltip = f"{src_node}.{src_name} -> {tgt_node}.{tgt_name}"
        print(tooltip)
        connection_edges.append(
            (src_node, tgt_node, {"tailport": src_name, "headport": tgt_name, "tooltip": tooltip}))


    for node, data in connection_nodes.items():
        label = f'<<table border="1" cellspacing="2" style="ROUNDED" bgcolor="{background_color}" color="{outline_color}">'
        label += table_row.format(port="", color="white",
                                  text=f'<font color="{outline_color}"><b>{node}</b></font>')
        # for index, plug in enumerate(data['plugs'], start=1):  # we start at 1 because index 0 is the node itself
        for plug, index in data['plugs'].items():  # we start at 1 because index 0 is the node itself
            if not plug:
                continue
            plug_name = plug
            sources = data['connections'].get(plug, [])  # (valid, invalid): we care only about valid sources (index 0)
            print(f"{node=}, {plug=}")
            print(sources)
            color = r"#F08080" if sources else background_color
            # color = plug_colors[type(plug)] if isinstance(plug, UsdShade.Output) or sources else background_color
            label += table_row.format(port=plug_name, color=color, text=f'<font color="#242828">{plug_name}</font>')
            for source_node, source_plug in sources:
                # node_id='ancestor', plug_name='cycle_out', ancestor, source.sourceName='cycle_in'
                # tooltip='/TexModel/boardMat/PBRShader.cycle_in -> /TexModel/boardMat/PBRShader.cycle_out'
                _add_edges(node, plug_name, source_node, source_plug)

        label += '</table>>'
        data['label'] = label
        data.pop('connections', None)

    graph.add_nodes_from(connection_nodes.items())
    graph.add_edges_from(connection_edges)

    widget = QtWidgets.QFrame()
    splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
    # return
    cached = {}
    from networkx import nx_pydot

    original = nx_pydot.write_dot


    # def _cached_dot(subgraph, fp):
    #     if not cached:
    #         print("WRITIGGGNNNNG")
    #         original(subgraph, fp)
    #         cached[True] = fp


    # cached_svg = {}
    # original_dot2svg = _graph._dot_2_svg


    # def _cached_dot2svg(fp):
    #     if not cached_svg:
    #         print(f"~~~~~~~~~~~~~~~~~~~ ~~~~~~~~~~~~~~~~~~~~ WITIHGN AND SAVING SVG: {fp}")
    #         result = original_dot2svg(fp)
    #         cached_svg[True] = result
    #         return result
    #     return cached_svg[True]


    from unittest import mock

    def _redirect_svg(self, filepath):
        return self._on_dot_result(r"A:\write\code\git\grill\tests\test_data\_mini_graph.svg")
        # return

    # with (
    #     # mock.patch(f"grill.views._graph.nx.nx_pydot.write_dot", new=_cached_dot),
    #     # mock.patch(f"grill.views._graph._dot_2_svg", new=_cached_dot2svg),
    #     mock.patch(f"grill.views._graph._DotViewer.setDotPath", new=_redirect_svg),
    #     # ...
    # ):
    from pxr import Usd, UsdShade, Sdf
    from . import description
    stage = Usd.Stage.CreateInMemory()
    material = UsdShade.Material.Define(stage, '/TexModel/boardMat')
    pbrShader = UsdShade.Shader.Define(stage, '/TexModel/boardMat/PBRShader')
    pbrShader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
    material.CreateSurfaceOutput().ConnectToSource(pbrShader.ConnectableAPI(), "surface")
    # Ensure cycles don't cause recursion
    cycle_input = pbrShader.CreateInput("cycle_in", Sdf.ValueTypeNames.Float)
    cycle_output = pbrShader.CreateOutput("cycle_out", Sdf.ValueTypeNames.Float)
    cycle_input.ConnectToSource(cycle_output)

    stage = Usd.Stage.Open(r"A:\write\code\git\easy-edgedb\chapter10\assets\dracula-3d-Model-Place-rnd-main-GoldenKroneHotel-lead-base-whole.1.usda")
    stage.GetPrimAtPath("/Origin").GetVariantSet("color").SetVariantSelection("random_uniform")

    for cls in _graph.GraphView, _graph._GraphSVGViewer:
            for pixmap_enabled in ((True, False) if cls == _graph._GraphSVGViewer else (False,)):
                _graph._GraphViewer = cls
                _graph._USE_SVG_VIEWPORT = pixmap_enabled

                child = description.LayerStackComposition(parent=widget)
                child.setStage(stage)
                # stack.show()

                # child = cls(parent=widget)
                # child._graph = graph
                # child.view(graph.nodes)
                # child.setMinimumWidth(150)
                splitter.addWidget(child)
                # viewer = description._ConnectableAPIViewer()
                # viewer.setPrim(material)
                # splitter.addWidget(viewer)

    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(splitter)

    widget.setLayout(layout)
    widget.show()

    app.exec_()
