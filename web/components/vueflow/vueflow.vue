<!--web/components/vueflow/vueflow.vue-->
<template>
  <div ref="container" class="vue-flow-wrapper" :style="style"></div>
</template>

<script>
export default {
  props: {
    nodes: {
      type: Array,
      default: () => []
    },
    edges: {
      type: Array,
      default: () => []
    },
    options: {
      type: Object,
      default: () => ({'fit-view-on-init': true})
    }
  },
  mounted() {
    const VueFlowComponent = window.VueFlow.VueFlow;
    const {useVueFlow, Handle, Position, NodeResizer, Background} = window.VueFlow;
    const {ref, onMounted} = Vue;

    // SimpleNode component
    const SimpleNode = {
      props: ['id', 'data', 'selected'],
      components: { Handle, NodeResizer },
      setup(props, { emit }) {
        const vueFlow = useVueFlow();
        const label = ref(props.data?.label || '');

        onMounted(() => {
          if (props.data?.label) {
            label.value = props.data.label;
          }
        });

        const updateLabel = (newValue) => {
          label.value = newValue; // Update local state
          const nodeUpdate = {
            id: props.id,
            data: { ...props.data, label: newValue }
          };
          vueFlow.updateNode(props.id, nodeUpdate);
        };

        return {
          Position,
          label,
          updateLabel
        }
      },
      template: `
        <div class="simple-node">
          <NodeResizer
            :min-width="100"
            :min-height="60"
            :isVisible="selected"
          />
          <Handle type="target" :position="Position.Top" />
          <div class="node-content">
            <input
              class="nodrag node-input"
              :value="label"
              @input="updateLabel($event.target.value)"
              placeholder="Enter text"
            />
          </div>
          <Handle type="source" :position="Position.Bottom" />
        </div>
      `
    };

    // DetailNode component
    const DetailNode = {
      props: ['id', 'data', 'selected'],
      components: { Handle, NodeResizer },
      setup(props, { emit }) {
        const vueFlow = useVueFlow();
        const title = ref(props.data?.title || '');
        const description = ref(props.data?.description || '');

        onMounted(() => {
          if (props.data) {
            title.value = props.data.title || '';
            description.value = props.data.description || '';
          }
        });

        const updateNodeData = (updates) => {
          // Update local state
          if (updates.title !== undefined) {
            title.value = updates.title;
          }
          if (updates.description !== undefined) {
            description.value = updates.description;
          }

          const nodeUpdate = {
            id: props.id,
            data: { ...props.data, ...updates }
          };
          vueFlow.updateNode(props.id, nodeUpdate);
        };

        return {
          Position,
          title,
          description,
          updateNodeData
        }
      },
      template: `
        <div class="detail-node">
          <NodeResizer
            :min-width="200"
            :min-height="100"
            :isVisible="selected"
          />
          <Handle type="target" :position="Position.Top"/>
          <div class="node-content">
            <div class="node-header">
              <input
                class="nodrag node-input title-input"
                :value="title"
                @input="updateNodeData({ title: $event.target.value })"
                placeholder="Enter title"
              />
            </div>
            <div class="node-body">
              <textarea
                class="nodrag node-input description-input"
                :value="description"
                @input="updateNodeData({ description: $event.target.value })"
                placeholder="Enter description"
              ></textarea>
            </div>
          </div>
          <Handle type="source" :position="Position.Bottom"/>
        </div>
      `
    };

    const app = Vue.createApp({
      setup: () => {
        const vueFlow = useVueFlow();
        this.vueFlowInstance = vueFlow;

        const {onNodeClick, addEdges, onConnect} = vueFlow;

        onNodeClick(({node}) => this.$emit('node_clicked', node));
        onConnect(params => addEdges([params]));

        return {
          nodes: this.nodes,
          edges: this.edges,
          options: this.options
        };
      },
      render() {
        return Vue.h(VueFlowComponent, {
          nodes: this.nodes,
          edges: this.edges,
          options: this.options,
          class: 'vue-flow-instance'
        }, {
          'node-simple': (props) => Vue.h(SimpleNode, props),
          'node-detail': (props) => Vue.h(DetailNode, props),
          'default': () => [Vue.h(Background)]
        });
      }
    });

    window.VueFlow.install && app.use(window.VueFlow);
    this.child = app.mount(this.$refs.container);
  },
  methods: {
    getNodes() {
      if (!this.vueFlowInstance) return [];
      return this.vueFlowInstance.nodes.value;
    },

    getEdges() {
      if (!this.vueFlowInstance) return [];
      return this.vueFlowInstance.edges.value;
    },

    addNode(node) {
      if (!this.vueFlowInstance) return;
      this.vueFlowInstance.addNodes([node]);
    },

    updateNode(nodeId, updates) {
      if (!this.vueFlowInstance) return;
      if (updates.position) {
        this.vueFlowInstance.applyNodeChanges([{
          id: nodeId,
          type: 'position',
          position: updates.position
        }]);
      }
      if (updates.data) {
        this.vueFlowInstance.updateNodeData(nodeId, updates.data);
      }
      if (updates.style) {
        this.vueFlowInstance.updateNodeData(nodeId, updates.style);
      }
      this.$emit('node_updated', {id: nodeId, ...updates});
    },

    updateData(newNodes, newEdges) {
      if (!this.vueFlowInstance) return;
      this.vueFlowInstance.setNodes(newNodes);
      this.vueFlowInstance.setEdges(newEdges);
      this.$emit('data_updated', {nodes: newNodes, edges: newEdges});
    },

    getViewport() {
      if (!this.vueFlowInstance) return null;
      return this.vueFlowInstance.getViewport();
    },

    setViewport(viewport) {
      if (!this.vueFlowInstance) return;
      this.vueFlowInstance.setViewport(viewport);
    }
  }
}
</script>