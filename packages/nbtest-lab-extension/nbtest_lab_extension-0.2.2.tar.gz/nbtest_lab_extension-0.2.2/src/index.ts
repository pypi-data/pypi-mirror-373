import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import {
  ICommandPalette,
  ToolbarButton,
  ISessionContext,
  CommandToolbarButton,
  Dialog,
  showDialog,
  ISessionContextDialogs // Added for type compatibility
} from '@jupyterlab/apputils';
import {
  INotebookTracker,
  Notebook,
  NotebookActions,
  NotebookPanel
} from '@jupyterlab/notebook';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { ITranslator } from '@jupyterlab/translation'; // Added for type compatibility
import { Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import { CodeCell, CodeCellModel } from '@jupyterlab/cells';
import { EditorState } from '@codemirror/state';
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
import { python } from '@codemirror/lang-python';
import { jupyterTheme } from '@jupyterlab/codemirror';
import {
  EditorView,
  keymap,
  Decoration,
  ViewPlugin,
  ViewUpdate,
  DecorationSet
} from '@codemirror/view';
import { RangeSetBuilder } from '@codemirror/state';

// Signal for updating the status display of the ENV variable
class ToggleSignal {
  private _stateChanged = new Signal<this, string>(this);

  get stateChanged() {
    return this._stateChanged;
  }

  emitState(value: string) {
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
class EditableMergedSourceWidget extends Widget {
  private _model: CodeCellModel;
  private _editor: EditorView;

  constructor(
    model: CodeCellModel,
    assertions: { index: number; content: string }[]
  ) {
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
        } else {
          lines[assert.index] = assert.content;
        }
      }
    });

    const placeholderStyling = ViewPlugin.fromClass(
      class {
        decorations: DecorationSet;
        constructor(view: EditorView) {
          this.decorations = this.getDecorations(view);
        }
        update(update: ViewUpdate) {
          if (update.docChanged || update.viewportChanged) {
            this.decorations = this.getDecorations(update.view);
          }
        }
        getDecorations(view: EditorView): DecorationSet {
          const builder = new RangeSetBuilder<Decoration>();
          for (const { from, to } of view.visibleRanges) {
            for (let pos = from; pos <= to; ) {
              const line = view.state.doc.lineAt(pos);
              if (line.text === PLACEHOLDER) {
                builder.add(
                  line.from,
                  line.from,
                  Decoration.line({
                    attributes: {
                      style:
                        'color: var(--jp-ui-font-color2); opacity: 0.5; font-style: italic;'
                    }
                  })
                );
              }
              pos = line.to + 1;
            }
          }
          return builder.finish();
        }
      },
      {
        decorations: v => v.decorations
      }
    );

    const state = EditorState.create({
      doc: lines.join('\n'),
      extensions: [
        keymap.of([...defaultKeymap, ...historyKeymap]),
        history(),
        python(),
        EditorView.lineWrapping,
        EditorView.editable.of(true),
        jupyterTheme,
        placeholderStyling,
        EditorView.theme({
          '&': {
            backgroundColor: 'var(--jp-cell-editor-background)'
          }
        }),
        EditorView.updateListener.of(update => {
          if (update.focusChanged && !update.view.hasFocus) {
            this.saveAssertionsToMetadata();
          }
        })
      ]
    });

    this._editor = new EditorView({ state, parent: this.node });
  }

  public saveAssertionsToMetadata() {
    if (this.isDisposed) {
      return;
    }
    const newAsserts: { index: number; content: string }[] = [];
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

  dispose(): void {
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
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'nbtest_lab_extension:plugin',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker, IRenderMimeRegistry],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    tracker: INotebookTracker
  ) => {
    const { commands } = app;
    const toggleEnvCommand = 'nbtest:toggle-asserts-env';
    const toggleVisibilityCommand = 'nbtest:toggle-visibility';

    let isColumnarViewActive = false;
    const widgetMap = new WeakMap<CodeCell, EditableMergedSourceWidget>();

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
            const newStatusValue = (msg.content as any).text.trim();
            status = newStatusValue === '1' ? 1 : 0;
            toggleSignal.emitState(status === 1 ? 'ON' : 'OFF');
          }
        };
        await future.done;
      }
    });

    // Create a reusable function for your custom execution logic
    async function executeWithAssertions(
      cell: CodeCell,
      sessionContext: ISessionContext
    ): Promise<boolean> {
      if (status !== 1 || !sessionContext.session?.kernel) {
        return false; // We are not handling this execution
      }

      const cellModel = cell.model;
      const assertions = cellModel.getMetadata(METADATA_KEY) as
        | { index: number; content: string }[]
        | undefined;

      if (!Array.isArray(assertions) || assertions.length === 0) {
        return false; // No assertions, let the original function handle it
      }

      const sourceLines = cellModel.sharedModel.getSource().split('\n');
      const finalCodeLines: string[] = sourceLines;

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
          showDialog({
            title: 'Assertions Passed',
            body: 'All assertions in the cell executed successfully.',
            buttons: [Dialog.okButton({ label: 'OK' })]
          });
        }
        cell.model.executionCount = reply.content.execution_count;
        return true; // We handled the execution
      } catch (e) {
        console.error('Failed to execute cell with assertions:', e);
        cell.model.executionCount = reply.content.execution_count;
        return true; // We attempted to handle it, even if it failed.
      }
    }

    // 'run' for Ctrl+Enter
    const originalRun = NotebookActions.run;
    NotebookActions.run = async (
      notebook: Notebook,
      sessionContext?: ISessionContext,
      sessionDialogs?: ISessionContextDialogs,
      translator?: ITranslator
    ): Promise<boolean> => {
      const cell = notebook.activeCell;
      if (cell instanceof CodeCell && sessionContext) {
        const handled = await executeWithAssertions(cell, sessionContext);
        if (handled) {
          return true;
        }
      }
      return originalRun.call(
        NotebookActions,
        notebook,
        sessionContext,
        sessionDialogs,
        translator
      );
    };

    // 'runAndAdvance' (for Shift+Enter and Toolbar Run)
    const originalRunAndAdvance = NotebookActions.runAndAdvance;
    NotebookActions.runAndAdvance = async (
      notebook: Notebook,
      sessionContext?: ISessionContext,
      sessionDialogs?: ISessionContextDialogs,
      translator?: ITranslator
    ): Promise<boolean> => {
      const cell = notebook.activeCell;
      if (cell instanceof CodeCell && sessionContext) {
        const handled = await executeWithAssertions(cell, sessionContext);
        if (handled) {
          NotebookActions.selectBelow(notebook);
          return true;
        }
      }
      return originalRunAndAdvance.call(
        NotebookActions,
        notebook,
        sessionContext,
        sessionDialogs,
        translator
      );
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
          if (!(cell instanceof CodeCell)) {
            return;
          }
          const codeCell = cell;
          const cellModel = codeCell.model as CodeCellModel;
          const inputWrapper = codeCell.inputArea?.node.parentElement;

          if (isColumnarViewActive) {
            const assertions = cellModel.getMetadata(METADATA_KEY) as
              | { index: number; content: string }[]
              | undefined;
            if (
              !Array.isArray(assertions) ||
              assertions.length === 0 ||
              !inputWrapper
            ) {
              return;
            }
            const widget = new EditableMergedSourceWidget(
              cellModel,
              assertions
            );
            widgetMap.set(codeCell, widget);
            inputWrapper.style.display = 'flex';
            inputWrapper.style.alignItems = 'stretch';
            codeCell.inputArea.node.style.flex = '1';
            inputWrapper.appendChild(widget.node);
          } else {
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
      label: () =>
        isColumnarViewActive ? 'Hide Assertion Editor' : 'Show Assertion Editor'
    });

    palette.addItem({ command: toggleEnvCommand, category: 'NBTest' });
    palette.addItem({ command: toggleVisibilityCommand, category: 'NBTest' });

    tracker.widgetAdded.connect((sender, panel: NotebookPanel) => {
      const envButton = new ToolbarButton({
        label: 'Toggle Assertions',
        tooltip: 'Toggle NBTEST_RUN_ASSERTS Environment Variable',
        onClick: () => commands.execute(toggleEnvCommand)
      });

      const statusWidget = new Widget();
      const statusNode = document.createElement('span');
      statusWidget.node.appendChild(statusNode);
      statusWidget.node.title = 'NBTEST_RUN_ASSERTS Status';
      statusNode.style.cssText = `
        margin-left: 4px; padding: 2px 6px; border-radius: 3px;
        font-size: 12px; font-weight: 600; color: white;
      `;

      const updateStatusDisplay = (state: string) => {
        if (state === 'ON') {
          statusNode.textContent = 'NBTest Asserts: ON';
          statusNode.style.backgroundColor = 'var(--jp-success-color1)';
        } else {
          statusNode.textContent = 'NBTest Asserts: OFF';
          statusNode.style.backgroundColor = 'var(--jp-error-color2)';
        }
      };
      toggleSignal.stateChanged.connect((_, newStatus) => {
        updateStatusDisplay(newStatus);
      });
      updateStatusDisplay(status === 1 ? 'ON' : 'OFF');

      const visibilityButton = new CommandToolbarButton({
        commands: commands,
        id: toggleVisibilityCommand
      });

      panel.toolbar.addItem('toggleAssertsEnv', envButton);
      panel.toolbar.addItem('assertsStatus', statusWidget);
      panel.toolbar.addItem('toggleVisibility', visibilityButton);

      const highlightAssertCells = () => {
        panel.content.widgets.forEach(cell => {
          if (cell.model instanceof CodeCellModel) {
            const metadata = cell.model.getMetadata(METADATA_KEY) as any[];
            const hasAssertionsInMeta =
              Array.isArray(metadata) && metadata.length > 0;
            if (hasAssertionsInMeta) {
              cell.node.style.borderLeft = '4px solid #f39c12';
              cell.node.style.backgroundColor = 'rgba(243, 156, 18, 0.07)';
            } else {
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

export default plugin;
