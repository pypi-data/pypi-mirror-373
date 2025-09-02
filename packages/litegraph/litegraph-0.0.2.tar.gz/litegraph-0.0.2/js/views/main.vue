
<script setup>
import { onMounted } from 'vue';
import { LiteGraph, LGraph, LGraphCanvas } from '@/litegraph'


//Constant
function ConstantNumber() {
    this.addOutput("value", "number");
    this.addProperty("value", 1.0);
    this.widget = this.addWidget("number","value",1,"value");
    this.widgets_up = true;
    this.size = [180, 30];
}

ConstantNumber.title = "Const Number";
ConstantNumber.desc = "Constant number";

ConstantNumber.prototype.onExecute = function() {
    this.setOutputData(0, parseFloat(this.properties["value"]));
};

ConstantNumber.prototype.getTitle = function() {
    if (this.flags.collapsed) {
        return this.properties.value;
    }
    return this.title;
};

ConstantNumber.prototype.setValue = function(v)
{
    this.setProperty("value",v);
}

ConstantNumber.prototype.onDrawBackground = function(ctx) {
    //show the current value
    this.outputs[0].label = this.properties["value"].toFixed(3);
};

LiteGraph.registerNodeType("basic/const", ConstantNumber);

//Watch a value in the editor
function Watch() {
    this.size = [60, 30];
    this.addInput("value", 0, { label: "" });
    this.value = 0;
}

Watch.title = "Watch";
Watch.desc = "Show value of input";

Watch.prototype.onExecute = function() {
    if (this.inputs[0]) {
        this.value = this.getInputData(0);
    }
};

Watch.prototype.getTitle = function() {
    if (this.flags.collapsed) {
        return this.inputs[0].label;
    }
    return this.title;
};

Watch.toString = function(o) {
    if (o == null) {
        return "null";
    } else if (o.constructor === Number) {
        return o.toFixed(3);
    } else if (o.constructor === Array) {
        var str = "[";
        for (var i = 0; i < o.length; ++i) {
            str += Watch.toString(o[i]) + (i + 1 != o.length ? "," : "");
        }
        str += "]";
        return str;
    } else {
        return String(o);
    }
};

Watch.prototype.onDrawBackground = function(ctx) {
    //show the current value
    this.inputs[0].label = Watch.toString(this.value);
};

LiteGraph.registerNodeType("basic/watch", Watch);

onMounted(() => {
var graph = new LGraph();
window.canvas_container = document.getElementById('canvas-container');
window.canvas = document.getElementById("mycanvas");
window.graphcanvas = new LGraphCanvas(window.canvas, graph, {autoresize: true});
window.canvas.width = window.canvas_container.clientWidth;
window.canvas.height = window.canvas_container.clientHeight;

var node_const = LiteGraph.createNode("basic/const");
node_const.pos = [200,200];
graph.add(node_const);
node_const.setValue(4.5);

var node_watch = LiteGraph.createNode("basic/watch");
node_watch.pos = [700,200];
graph.add(node_watch);

node_const.connect(0, node_watch, 0 );

graph.start()
});

window.addEventListener('resize', () => { window.graphcanvas.resize(); });
</script>

<template>
    <div id="canvas-container" class="w-full h-screen">
        <canvas id='mycanvas' width='100%' height='100%'></canvas>
    </div>
</template>
