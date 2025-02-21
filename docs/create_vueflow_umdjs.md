# Compiling VueFlow UMD JS for NiceGUI

## 1. Create project structure:
```
vueflow_component/
├── src/
│   └── index.js    # Main source file
├── dist/           # Output directory
└── webpack.config.js
```

## 2. Initialize project and install dependencies:
```bash
npm init -y
npm install webpack webpack-cli vue-loader @babel/core @babel/preset-env babel-loader vue
npm install @vue-flow/core @vue-flow/background @vue-flow/node-resizer
```

## 3. Create src/index.js
```javascript
// src/index.js
import { VueFlow, Panel, useVueFlow, Handle, Position } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { NodeResizer } from '@vue-flow/node-resizer';

export default {
    install: (app) => {
        app.component('VueFlow', VueFlow);
        app.component('Panel', Panel);
        app.component('Background', Background);
        app.component('NodeResizer', NodeResizer);
    },
    VueFlow,
    Panel,
    Background,
    Handle,
    Position,
    NodeResizer,
    useVueFlow
};
```

## 4. Create webpack.config.umd.js
```javascript
// webpack.config.umd.js
const path = require('path');

module.exports = {
    mode: 'production',
    entry: './src/index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'vueflow-component.umd.js',
        library: {
            name: 'VueFlow',
            type: 'umd',
            export: 'default'
        },
        globalObject: 'this'
    },
    externals: {
       'vue': 'Vue'
    }
};
```

## 5. Create UMD bundle
```bash
npx webpack --config webpack.config.umd.js
```

The new file **vueflow-component.umd.js** will appear in **/dist** directory.

## 6. Include Required CSS Files
Add the following CSS files, or download and use locally:

```html
<!-- Base Vue Flow styles -->
<link href="https://unpkg.com/@vue-flow/core@latest/dist/style.css" rel="stylesheet" />
<link href="https://unpkg.com/@vue-flow/core@latest/dist/theme-default.css" rel="stylesheet" />

<!-- Node resizer extension styles -->
<link href="https://unpkg.com/@vue-flow/node-resizer@latest/dist/style.css" rel="stylesheet" />
