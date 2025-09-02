import { LiteGraph } from "./LiteGraph";
import LGraphCanvas from "./LGraphCanvas";
import LGraph from "./LGraph";
import LLink from "./LLink";
import LGraphNode from "./LGraphNode";
import LGraphGroup from "./LgraphGroup";
import DragAndScale from "./DragAndScale";
import ContextMenu from "./ContextMenu";
import CurveEditor from "./CurveEditor";

LiteGraph.LGraphCanvas = LGraphCanvas;
LiteGraph.LGraphGroup = LGraphGroup;
LiteGraph.LGraphNode = LGraphNode;
LiteGraph.LGraph = LGraph;
LiteGraph.LLink = LLink;
LiteGraph.DragAndScale = DragAndScale;
LiteGraph.CurveEditor = CurveEditor;
LiteGraph.ContextMenu = ContextMenu;

LGraphGroup.prototype.isPointInside = LGraphNode.prototype.isPointInside;
LGraphGroup.prototype.setDirtyCanvas = LGraphNode.prototype.setDirtyCanvas;

/**
 * Attach Canvas to this graph
 * @method attachCanvas
 * @param {GraphCanvas} graph_canvas
 */

LGraph.prototype.attachCanvas = function(graphcanvas) {
    if (graphcanvas.constructor != LGraphCanvas) {
        throw "attachCanvas expects a LGraphCanvas instance";
    }
    if (graphcanvas.graph && graphcanvas.graph != this) {
        graphcanvas.graph.detachCanvas(graphcanvas);
    }

    graphcanvas.graph = this;

    if (!this.list_of_graphcanvas) {
        this.list_of_graphcanvas = [];
    }
    this.list_of_graphcanvas.push(graphcanvas);
};

export { LGraph, LLink, LGraphNode, LGraphGroup, DragAndScale, ContextMenu, CurveEditor, LiteGraph, LGraphCanvas };
