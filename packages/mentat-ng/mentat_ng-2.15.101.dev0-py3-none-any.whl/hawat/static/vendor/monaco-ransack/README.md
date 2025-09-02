# monaco-ransack

**Monaco language support for [ransack](https://ransack-125e0a.gitlab-pages.cesnet.cz/)** – a modern, extensible language for manipulating structured data.

This package provides a syntax highlighter and language configuration for the [Monaco Editor](https://github.com/microsoft/monaco-editor) to support the `ransack` language.

##  Installation

```bash
npm install monaco-ransack
````

This package requires `monaco-editor` as a peer dependency:

```bash
npm install monaco-editor
```

## Usage

1. Include the module in your Monaco setup:

```js
import * as monaco from 'monaco-editor';
import 'monaco-ransack';

window.registerRansack(monaco);
```

2. Set language and theme (optional):

```js
monaco.editor.create(document.getElementById('editor'), {
  value: 'source_ip = 192.168.1.1 and status == "ok"',
  language: 'ransack',
});
```

## About ransack

**[ransack](https://ransack-125e0a.gitlab-pages.cesnet.cz/)** is a modern language designed for querying and filtering structured data formats like JSON, YAML, or domain-specific formats such as [IDEA](https://idea.cesnet.cz).
