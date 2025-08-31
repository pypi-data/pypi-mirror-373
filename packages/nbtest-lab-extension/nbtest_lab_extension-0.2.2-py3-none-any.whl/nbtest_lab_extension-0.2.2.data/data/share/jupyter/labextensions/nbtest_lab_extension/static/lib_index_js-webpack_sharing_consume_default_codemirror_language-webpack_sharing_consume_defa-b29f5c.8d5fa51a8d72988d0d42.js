"use strict";
(self["webpackChunknbtest_lab_extension"] = self["webpackChunknbtest_lab_extension"] || []).push([["lib_index_js-webpack_sharing_consume_default_codemirror_language-webpack_sharing_consume_defa-b29f5c"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/rendermime */ "webpack/sharing/consume/default/@jupyterlab/rendermime");
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/cells */ "webpack/sharing/consume/default/@jupyterlab/cells");
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _codemirror_state__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @codemirror/state */ "webpack/sharing/consume/default/@codemirror/state");
/* harmony import */ var _codemirror_state__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_codemirror_state__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _codemirror_commands__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @codemirror/commands */ "./node_modules/@codemirror/commands/dist/index.js");
/* harmony import */ var _codemirror_lang_python__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @codemirror/lang-python */ "./node_modules/@codemirror/lang-python/dist/index.js");
/* harmony import */ var _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @jupyterlab/codemirror */ "webpack/sharing/consume/default/@jupyterlab/codemirror");
/* harmony import */ var _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _codemirror_view__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @codemirror/view */ "webpack/sharing/consume/default/@codemirror/view");
/* harmony import */ var _codemirror_view__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(_codemirror_view__WEBPACK_IMPORTED_MODULE_8__);












// Signal for updating the status display of the ENV variable
class ToggleSignal {
    constructor() {
        this._stateChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__.Signal(this);
    }
    get stateChanged() {
        return this._stateChanged;
    }
    emitState(value) {
        this._stateChanged.emit(value);
    }
}
const toggleSignal = new ToggleSignal();
let status = 0; // Track status locally for the ENV variable
// Define constants for the metadata key and assertion prefix
const METADATA_KEY = 'nbtest_hidden_asserts';
const ASSERT_PREFIX = 'nbtest.assert_';
// A constant for our placeholder text. Using a valid comment is good practice.
const PLACEHOLDER = '# (This line is for spacing only)';
/**
 * An editable widget that uses a CodeMirror instance for syntax highlighting.
 */
class EditableMergedSourceWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Widget {
    constructor(model, assertions) {
        super();
        this._model = model;
        this.addClass('jp-Editor');
        this.addClass('jp-CodeMirrorEditor');
        this.addClass('nbtest-editable-merged-column');
        this.node.style.flex = '0 1 50%';
        this.node.style.maxWidth = '50%';
        this.node.style.paddingLeft = '10px';
        this.node.style.borderLeft = '1px solid var(--jp-border-color2)';
        // 1. Determine the total number of lines needed for the editor.
        const sourceLineCount = this._model.sharedModel
            .getSource()
            .split('\n').length;
        let highestAssertIndex = 0;
        assertions.forEach(a => {
            if (a.index > highestAssertIndex) {
                highestAssertIndex = a.index;
            }
        });
        const totalLines = Math.max(sourceLineCount, highestAssertIndex + 1);
        // 2. Create a sparse array representing the editor content.
        const lines = new Array(totalLines).fill(PLACEHOLDER);
        assertions.forEach(assert => {
            if (assert.index < totalLines) {
                // If an assertion already exists at this line, append the new one.
                if (lines[assert.index] !== PLACEHOLDER) {
                    lines[assert.index] += '\n' + assert.content;
                }
                else {
                    lines[assert.index] = assert.content;
                }
            }
        });
        const placeholderStyling = _codemirror_view__WEBPACK_IMPORTED_MODULE_8__.ViewPlugin.fromClass(class {
            constructor(view) {
                this.decorations = this.getDecorations(view);
            }
            update(update) {
                if (update.docChanged || update.viewportChanged) {
                    this.decorations = this.getDecorations(update.view);
                }
            }
            getDecorations(view) {
                const builder = new _codemirror_state__WEBPACK_IMPORTED_MODULE_6__.RangeSetBuilder();
                for (const { from, to } of view.visibleRanges) {
                    for (let pos = from; pos <= to;) {
                        const line = view.state.doc.lineAt(pos);
                        if (line.text === PLACEHOLDER) {
                            builder.add(line.from, line.from, _codemirror_view__WEBPACK_IMPORTED_MODULE_8__.Decoration.line({
                                attributes: {
                                    style: 'color: var(--jp-ui-font-color2); opacity: 0.5; font-style: italic;'
                                }
                            }));
                        }
                        pos = line.to + 1;
                    }
                }
                return builder.finish();
            }
        }, {
            decorations: v => v.decorations
        });
        const state = _codemirror_state__WEBPACK_IMPORTED_MODULE_6__.EditorState.create({
            doc: lines.join('\n'),
            extensions: [
                _codemirror_view__WEBPACK_IMPORTED_MODULE_8__.keymap.of([..._codemirror_commands__WEBPACK_IMPORTED_MODULE_9__.defaultKeymap, ..._codemirror_commands__WEBPACK_IMPORTED_MODULE_9__.historyKeymap]),
                (0,_codemirror_commands__WEBPACK_IMPORTED_MODULE_9__.history)(),
                (0,_codemirror_lang_python__WEBPACK_IMPORTED_MODULE_10__.python)(),
                _codemirror_view__WEBPACK_IMPORTED_MODULE_8__.EditorView.lineWrapping,
                _codemirror_view__WEBPACK_IMPORTED_MODULE_8__.EditorView.editable.of(true),
                _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_7__.jupyterTheme,
                placeholderStyling,
                _codemirror_view__WEBPACK_IMPORTED_MODULE_8__.EditorView.theme({
                    '&': {
                        backgroundColor: 'var(--jp-cell-editor-background)'
                    }
                }),
                _codemirror_view__WEBPACK_IMPORTED_MODULE_8__.EditorView.updateListener.of(update => {
                    if (update.focusChanged && !update.view.hasFocus) {
                        this.saveAssertionsToMetadata();
                    }
                })
            ]
        });
        this._editor = new _codemirror_view__WEBPACK_IMPORTED_MODULE_8__.EditorView({ state, parent: this.node });
    }
    saveAssertionsToMetadata() {
        if (this.isDisposed) {
            return;
        }
        const newAsserts = [];
        const editorLines = this._editor.state.doc.toString().split('\n');
        editorLines.forEach((lineContent, index) => {
            if (lineContent.trim() && lineContent.trim() !== PLACEHOLDER) {
                const singleAsserts = lineContent.split('\n');
                singleAsserts.forEach(assertText => {
                    if (assertText.trim().startsWith(ASSERT_PREFIX)) {
                        newAsserts.push({ index: index, content: assertText });
                    }
                });
            }
        });
        this._model.setMetadata(METADATA_KEY, newAsserts);
    }
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this.saveAssertionsToMetadata();
        this._editor.destroy();
        super.dispose();
    }
}
/**
 * The main extension plugin.
 */
const plugin = {
    id: 'nbtest_lab_extension:plugin',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.INotebookTracker, _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__.IRenderMimeRegistry],
    activate: (app, palette, tracker) => {
        const { commands } = app;
        const toggleEnvCommand = 'nbtest:toggle-asserts-env';
        const toggleVisibilityCommand = 'nbtest:toggle-visibility';
        let isColumnarViewActive = false;
        const widgetMap = new WeakMap();
        commands.addCommand(toggleEnvCommand, {
            label: 'Toggle NBTEST_RUN_ASSERTS Env Var',
            execute: async () => {
                const currentNotebook = tracker.currentWidget;
                if (!currentNotebook) {
                    return;
                }
                const session = currentNotebook.sessionContext.session;
                if (!session || !session.kernel) {
                    return;
                }
                const code = `
    import os
    os.environ["NBTEST_RUN_ASSERTS"] = "1" if os.environ.get("NBTEST_RUN_ASSERTS", "0") != "1" else "0"
    print(os.environ["NBTEST_RUN_ASSERTS"])
            `;
                const future = session.kernel.requestExecute({ code });
                future.onIOPub = msg => {
                    if (msg.header.msg_type === 'stream') {
                        const newStatusValue = msg.content.text.trim();
                        status = newStatusValue === '1' ? 1 : 0;
                        toggleSignal.emitState(status === 1 ? 'ON' : 'OFF');
                    }
                };
                await future.done;
            }
        });
        // Create a reusable function for your custom execution logic
        async function executeWithAssertions(cell, sessionContext) {
            var _a;
            if (status !== 1 || !((_a = sessionContext.session) === null || _a === void 0 ? void 0 : _a.kernel)) {
                return false; // We are not handling this execution
            }
            const cellModel = cell.model;
            const assertions = cellModel.getMetadata(METADATA_KEY);
            if (!Array.isArray(assertions) || assertions.length === 0) {
                return false; // No assertions, let the original function handle it
            }
            const sourceLines = cellModel.sharedModel.getSource().split('\n');
            const finalCodeLines = sourceLines;
            assertions.forEach(assert => {
                finalCodeLines.splice(assert.index, 0, assert.content);
            });
            const mergedCode = finalCodeLines.join('\n');
            const kernel = sessionContext.session.kernel;
            const future = kernel.requestExecute({ code: mergedCode });
            cell.outputArea.future = future;
            cell.model.executionState = 'running';
            cell.model.sharedModel.setMetadata('execution', {
                shell: {
                    reply: null
                }
            });
            const reply = await future.done;
            try {
                if (reply && reply.content.status === 'ok') {
                    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                        title: 'Assertions Passed',
                        body: 'All assertions in the cell executed successfully.',
                        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: 'OK' })]
                    });
                }
                cell.model.executionCount = reply.content.execution_count;
                return true; // We handled the execution
            }
            catch (e) {
                console.error('Failed to execute cell with assertions:', e);
                cell.model.executionCount = reply.content.execution_count;
                return true; // We attempted to handle it, even if it failed.
            }
        }
        // 'run' for Ctrl+Enter
        const originalRun = _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookActions.run;
        _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookActions.run = async (notebook, sessionContext, sessionDialogs, translator) => {
            const cell = notebook.activeCell;
            if (cell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5__.CodeCell && sessionContext) {
                const handled = await executeWithAssertions(cell, sessionContext);
                if (handled) {
                    return true;
                }
            }
            return originalRun.call(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookActions, notebook, sessionContext, sessionDialogs, translator);
        };
        // 'runAndAdvance' (for Shift+Enter and Toolbar Run)
        const originalRunAndAdvance = _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookActions.runAndAdvance;
        _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookActions.runAndAdvance = async (notebook, sessionContext, sessionDialogs, translator) => {
            const cell = notebook.activeCell;
            if (cell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5__.CodeCell && sessionContext) {
                const handled = await executeWithAssertions(cell, sessionContext);
                if (handled) {
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookActions.selectBelow(notebook);
                    return true;
                }
            }
            return originalRunAndAdvance.call(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookActions, notebook, sessionContext, sessionDialogs, translator);
        };
        commands.addCommand(toggleVisibilityCommand, {
            execute: () => {
                const panel = tracker.currentWidget;
                if (!panel) {
                    return;
                }
                isColumnarViewActive = !isColumnarViewActive;
                commands.notifyCommandChanged(toggleVisibilityCommand);
                panel.content.widgets.forEach(cell => {
                    var _a;
                    if (!(cell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5__.CodeCell)) {
                        return;
                    }
                    const codeCell = cell;
                    const cellModel = codeCell.model;
                    const inputWrapper = (_a = codeCell.inputArea) === null || _a === void 0 ? void 0 : _a.node.parentElement;
                    if (isColumnarViewActive) {
                        const assertions = cellModel.getMetadata(METADATA_KEY);
                        if (!Array.isArray(assertions) ||
                            assertions.length === 0 ||
                            !inputWrapper) {
                            return;
                        }
                        const widget = new EditableMergedSourceWidget(cellModel, assertions);
                        widgetMap.set(codeCell, widget);
                        inputWrapper.style.display = 'flex';
                        inputWrapper.style.alignItems = 'stretch';
                        codeCell.inputArea.node.style.flex = '1';
                        inputWrapper.appendChild(widget.node);
                    }
                    else {
                        if (widgetMap.has(codeCell) && inputWrapper) {
                            const widget = widgetMap.get(codeCell);
                            if (widget && !widget.isDisposed) {
                                if (inputWrapper.contains(widget.node)) {
                                    inputWrapper.removeChild(widget.node);
                                }
                                widget.dispose();
                            }
                            widgetMap.delete(codeCell);
                            inputWrapper.style.display = '';
                            inputWrapper.style.alignItems = '';
                        }
                    }
                });
            },
            isToggled: () => isColumnarViewActive,
            label: () => isColumnarViewActive ? 'Hide Assertion Editor' : 'Show Assertion Editor'
        });
        palette.addItem({ command: toggleEnvCommand, category: 'NBTest' });
        palette.addItem({ command: toggleVisibilityCommand, category: 'NBTest' });
        tracker.widgetAdded.connect((sender, panel) => {
            const envButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
                label: 'Toggle Assertions',
                tooltip: 'Toggle NBTEST_RUN_ASSERTS Environment Variable',
                onClick: () => commands.execute(toggleEnvCommand)
            });
            const statusWidget = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Widget();
            const statusNode = document.createElement('span');
            statusWidget.node.appendChild(statusNode);
            statusWidget.node.title = 'NBTEST_RUN_ASSERTS Status';
            statusNode.style.cssText = `
        margin-left: 4px; padding: 2px 6px; border-radius: 3px;
        font-size: 12px; font-weight: 600; color: white;
      `;
            const updateStatusDisplay = (state) => {
                if (state === 'ON') {
                    statusNode.textContent = 'NBTest Asserts: ON';
                    statusNode.style.backgroundColor = 'var(--jp-success-color1)';
                }
                else {
                    statusNode.textContent = 'NBTest Asserts: OFF';
                    statusNode.style.backgroundColor = 'var(--jp-error-color2)';
                }
            };
            toggleSignal.stateChanged.connect((_, newStatus) => {
                updateStatusDisplay(newStatus);
            });
            updateStatusDisplay(status === 1 ? 'ON' : 'OFF');
            const visibilityButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.CommandToolbarButton({
                commands: commands,
                id: toggleVisibilityCommand
            });
            panel.toolbar.addItem('toggleAssertsEnv', envButton);
            panel.toolbar.addItem('assertsStatus', statusWidget);
            panel.toolbar.addItem('toggleVisibility', visibilityButton);
            const highlightAssertCells = () => {
                panel.content.widgets.forEach(cell => {
                    if (cell.model instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5__.CodeCellModel) {
                        const metadata = cell.model.getMetadata(METADATA_KEY);
                        const hasAssertionsInMeta = Array.isArray(metadata) && metadata.length > 0;
                        if (hasAssertionsInMeta) {
                            cell.node.style.borderLeft = '4px solid #f39c12';
                            cell.node.style.backgroundColor = 'rgba(243, 156, 18, 0.07)';
                        }
                        else {
                            cell.node.style.borderLeft = '';
                            cell.node.style.backgroundColor = '';
                        }
                    }
                });
            };
            panel.revealed.then(highlightAssertCells);
            if (panel.content.model) {
                panel.content.model.contentChanged.connect(highlightAssertCells);
            }
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js-webpack_sharing_consume_default_codemirror_language-webpack_sharing_consume_defa-b29f5c.8d5fa51a8d72988d0d42.js.map