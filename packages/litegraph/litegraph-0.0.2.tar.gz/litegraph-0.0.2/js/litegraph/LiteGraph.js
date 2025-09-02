import { LiteGraphBase as LiteGraph } from "./LiteGraphBase";
import LGraphNode from "./LGraphNode";

/**
 * Register a node class so it can be listed when the user wants to create a new one
 * @method registerNodeType
 * @param {String} type name of the node and path
 * @param {Class} base_class class containing the structure of a node
 */
LiteGraph.registerNodeType = function(type, base_class) {
    if (!base_class.prototype) {
        throw "Cannot register a simple object, it must be a class with a prototype";
    }
    base_class.type = type;

    if (LiteGraph.debug) {
        console.log("Node registered: " + type);
    }

    const classname = base_class.name;

    const pos = type.lastIndexOf("/");
    base_class.category = type.substring(0, pos);

    if (!base_class.title) {
        base_class.title = classname;
    }

    //extend class
    for (var i in LGraphNode.prototype) {
        if (!base_class.prototype[i]) {
            base_class.prototype[i] = LGraphNode.prototype[i];
        }
    }

    const prev = this.registered_node_types[type];
    if(prev) {
        console.log("replacing node type: " + type);
    }
    if( !Object.prototype.hasOwnProperty.call( base_class.prototype, "shape") ) {
        Object.defineProperty(base_class.prototype, "shape", {
            set: function(v) {
                switch (v) {
                    case "default":
                        delete this._shape;
                        break;
                    case "box":
                        this._shape = LiteGraph.BOX_SHAPE;
                        break;
                    case "round":
                        this._shape = LiteGraph.ROUND_SHAPE;
                        break;
                    case "circle":
                        this._shape = LiteGraph.CIRCLE_SHAPE;
                        break;
                    case "card":
                        this._shape = LiteGraph.CARD_SHAPE;
                        break;
                    default:
                        this._shape = v;
                }
            },
            get: function() {
                return this._shape;
            },
            enumerable: true,
            configurable: true
        });
        

        //used to know which nodes to create when dragging files to the canvas
        if (base_class.supported_extensions) {
            for (let i in base_class.supported_extensions) {
                const ext = base_class.supported_extensions[i];
                if(ext && ext.constructor === String) {
                    this.node_types_by_file_extension[ ext.toLowerCase() ] = base_class;
                }
            }
        }
    }

    this.registered_node_types[type] = base_class;
    if (base_class.constructor.name) {
        this.Nodes[classname] = base_class;
    }
    if (LiteGraph.onNodeTypeRegistered) {
        LiteGraph.onNodeTypeRegistered(type, base_class);
    }
    if (prev && LiteGraph.onNodeTypeReplaced) {
        LiteGraph.onNodeTypeReplaced(type, base_class, prev);
    }

    //warnings
    if (base_class.prototype.onPropertyChange) {
        console.warn(
            "LiteGraph node class " +
                type +
                " has onPropertyChange method, it must be called onPropertyChanged with d at the end"
        );
    }
    
    // TODO one would want to know input and ouput :: this would allow through registerNodeAndSlotType to get all the slots types
    if (this.auto_load_slot_types) {
        new base_class(base_class.title || "tmpnode");
    }
}

/**
 * removes a node type from the system
 * @method unregisterNodeType
 * @param {String|Object} type name of the node or the node constructor itself
 */
LiteGraph.unregisterNodeType = function(type) {
    const base_class =
        type.constructor === String
            ? this.registered_node_types[type]
            : type;
    if (!base_class) {
        throw "node type not found: " + type;
    }
    delete this.registered_node_types[base_class.type];
    if (base_class.constructor.name) {
        delete this.Nodes[base_class.constructor.name];
    }
}


/**
 * Adds this method to all nodetypes, existing and to be created
 * (You can add it to LGraphNode.prototype but then existing node types wont have it)
 * @method addNodeMethod
 * @param {Function} func
 */
LiteGraph.addNodeMethod = function(name, func) {
    LGraphNode.prototype[name] = func;
    for (var i in this.registered_node_types) {
        var type = this.registered_node_types[i];
        if (type.prototype[name]) {
            type.prototype["_" + name] = type.prototype[name];
        } //keep old in case of replacing
        type.prototype[name] = func;
    }
}

export { LiteGraph };
