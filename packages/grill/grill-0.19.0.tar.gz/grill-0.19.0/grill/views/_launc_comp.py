from ._qt import QtCore, QtWidgets
from pxr import Usd, Pcp, UsdGeom

def crash_edit_target(stage):
    "This crashes in usdview"
    prim = stage.GetPrimAtPath("/root/stoat/body_M_hrc/GEO/nose_M_geo")
    # index = prim.GetPrimIndex()
    index = prim.ComputeExpandedPrimIndex()
    root = index.rootNode

    def walk_composition(node):
        yield node
        for child in node.children:
            yield from walk_composition(child)

    target_node = next(
        (
            (index, node) for index, node in enumerate(walk_composition(root))
            if "mk020_0281_shotrange_edit_shot.usda" in node.layerStack.layerTree.layer.identifier
               and node.path == prim.GetPath()
               and node.arcType == Pcp.ArcTypeReference
        ),
        None
    )
    # first_inherits = next((child for child in root.children if child.arcType == Pcp.ArcTypeInherit), None)
    # assert first_inherits
    assert target_node
    target_node_index, target_node = target_node
    print(f"{target_node_index=}")
    edit_target = Usd.EditTarget(target_node.layerStack.layerTree.layer, target_node)
    with Usd.EditContext(stage, edit_target):
        UsdGeom.Gprim(prim).MakeInvisible()

    print(edit_target.GetLayer().ExportToString())


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    # python -m grill.views._graph
    app = QtWidgets.QApplication([])

    from . import description



    stage = Usd.Stage.Open(r"R:\dpel\ALab\ALab\entry.usda")
    crash_edit_target(stage)
    stage = Usd.Stage.Open(r"R:\dpel\ALab\ALab\entity\stoat01\stoat01.usda")
    # stage = Usd.Stage.Open(r"A:\write\code\git\easy-edgedb\chapter10\assets\dracula-3d-Model-Country-rnd-main-Romania-lead-base-whole.1.usda")
    prim = stage.GetPrimAtPath("/root/body_M_hrc/GEO/nose_M_geo")
    # prim = stage.GetPrimAtPath("/Origin/Buildings/GoldenKroneHotel/Geom/Basis_L/Basis_L_0")

    # index = prim.GetPrimIndex()
    # pattern = description._PCP_DUMP_PATTERN


    widget = QtWidgets.QFrame()
    splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
    child = description.PrimComposition(parent=widget)
    child.setPrim(prim)
    splitter.addWidget(child)
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(splitter)

    widget.setLayout(layout)
    widget.show()

    app.exec_()
