import { Widget } from '@lumino/widgets';
import { CodeEditor } from '@jupyterlab/codeeditor';
import { Decoration, DecorationSet, EditorView, WidgetType } from '@codemirror/view';
import { Compartment, Extension, StateEffect, StateField } from '@codemirror/state';

export class InlineCompletionWidget {
  private completionText: string = '';
  private editor: CodeEditor.IEditor | null = null;
  private onAccept: (() => void) | null = null;
  private onReject: (() => void) | null = null;
  private originalCursor: CodeEditor.IPosition | null = null;
  private replacementEndPos: CodeEditor.IPosition | null = null;

  // CM6 ghost decoration plumbing
  private ghostAppendConfig = StateEffect.appendConfig.of([] as unknown as Extension);
  private setGhostEffect = StateEffect.define<DecorationSet>();
  private clearGhostEffect = StateEffect.define<null>();
  private ghostField = StateField.define<DecorationSet>({
    create: () => Decoration.none,
    update: (deco, tr) => {
      for (const e of tr.effects) {
        if (e.is(this.setGhostEffect)) return e.value;
        if (e.is(this.clearGhostEffect)) return Decoration.none;
      }
      if (tr.docChanged) return Decoration.none;
      return deco.map(tr.changes);
    },
    provide: field => EditorView.decorations.from(field)
  });
  private ghostCompartment = new Compartment();
  private ghostExtension: Extension | null = null;
  private isGhostVisible = false;

  // Queue to serialize clear/show operations and avoid CM update re-entrancy
  private clearQueue: Promise<void> = Promise.resolve();

  public showCompletion(
    editor: CodeEditor.IEditor,
    completionText: string,
    onAccept: () => void,
    onReject: () => void,
    replacementEndPos?: CodeEditor.IPosition
  ): void {
    // Always hide previous first and then schedule show after clear completes
    this.hideCompletion();

    this.editor = editor;
    this.completionText = completionText;
    this.onAccept = onAccept;
    this.onReject = onReject;
    this.replacementEndPos = replacementEndPos || null;

    const cursor = editor.getCursorPosition();
    this.originalCursor = { line: cursor.line, column: cursor.column };

    const view: EditorView | null = this.getEditorView();
    if (!view) {
      console.error('[InlineCompletionWidget] CodeMirror view not found');
      return;
    }

    // Ensure extension is present once
    this.ensureGhostExtension(view);

    // After any pending clears complete, render the ghost
            this.clearQueue = this.clearQueue.then(
          () =>
            new Promise<void>(resolve => {
              requestAnimationFrame(() => {
                const pos = this.computeOffsetFromPosition(editor, cursor);
                let decorations = [
                  Decoration.widget({
                    widget: new GhostTextWidget(completionText),
                    side: 1
                  }).range(pos)
                ];

                // If we have a replacement range, add a strikethrough decoration for the text being replaced
                if (this.replacementEndPos) {
                  const replaceEndPos = this.computeOffsetFromPosition(editor, this.replacementEndPos);
                  if (replaceEndPos > pos) {
                    decorations.push(
                      Decoration.mark({
                        class: 'sage-completion-replacement',
                        attributes: { style: 'opacity: 0.3; text-decoration: line-through;' }
                      }).range(pos, replaceEndPos)
                    );
                  }
                }

                const deco = Decoration.set(decorations);
                view.dispatch({ effects: this.setGhostEffect.of(deco) });
                this.isGhostVisible = true;
                console.log(
                  '[InlineCompletionWidget] Showing inline completion (ghost) with replacement:',
                  completionText
                );
                resolve();
              });
            })
        );
  }

  private getEditorView(): EditorView | null {
    const ed: any = this.editor as any;
    if (!ed) return null;
    const view = ed.editor ?? ed._editor ?? ed.cm ?? null;
    return (view as EditorView) ?? null;
  }

  private ensureGhostExtension(view: EditorView): void {
    if (this.ghostExtension) return;
    this.ghostExtension = this.ghostCompartment.of([this.ghostField]);
    view.dispatch({ effects: StateEffect.appendConfig.of(this.ghostExtension) });
  }

  private computeOffsetFromPosition(editor: CodeEditor.IEditor, pos: CodeEditor.IPosition): number {
    const model = editor.model;
    const text = model.sharedModel.getSource();
    const lines = text.split('\n');

    let offset = 0;
    for (let i = 0; i < pos.line; i++) {
      if (lines[i] !== undefined) {
        offset += lines[i].length + 1; // +1 for newline character
      }
    }
    offset += pos.column;
    return offset;
  }

  public hideCompletion(): void {
    const view = this.getEditorView();
    if (view) {
      // Queue clear into the next frame to avoid CM re-entrancy errors
      this.clearQueue = this.clearQueue.then(
        () =>
          new Promise<void>(resolve => {
            requestAnimationFrame(() => {
              view.dispatch({ effects: this.clearGhostEffect.of(null) });
              resolve();
            });
          })
      );
    }
    this.isGhostVisible = false;

    console.log('[InlineCompletionWidget] Cleared ghost overlay');

    this.completionText = '';
    this.onAccept = null;
    this.onReject = null;
    this.replacementEndPos = null;
  }

  public acceptCompletion(): void {
    if (this.editor && this.originalCursor && this.completionText) {
      try {
        const insertOffset = this.computeOffsetFromPosition(this.editor, this.originalCursor);
        const view = this.getEditorView();
        
        // Determine replacement range
        let replaceToOffset = insertOffset;
        if (this.replacementEndPos) {
          replaceToOffset = this.computeOffsetFromPosition(this.editor, this.replacementEndPos);
        }

        if (view) {
          // Replace via CodeMirror so selection can be set atomically
          const end = insertOffset + this.completionText.length;
          view.dispatch({
            changes: { from: insertOffset, to: replaceToOffset, insert: this.completionText },
            selection: { anchor: end }
          });
        } else {
          // Fallback to model mutation and then set cursor on next frame
          const model = this.editor.model;
          const currentText = model.sharedModel.getSource();
          const newText = currentText.slice(0, insertOffset) + this.completionText + currentText.slice(replaceToOffset);
          model.sharedModel.setSource(newText);
          const insertedLines = this.completionText.split('\n');
          let newCursor: CodeEditor.IPosition;
          if (insertedLines.length === 1) {
            newCursor = {
              line: this.originalCursor.line,
              column: this.originalCursor.column + this.completionText.length
            };
          } else {
            const lastLineLength = insertedLines[insertedLines.length - 1].length;
            newCursor = {
              line: this.originalCursor.line + insertedLines.length - 1,
              column: lastLineLength
            };
          }
          requestAnimationFrame(() => {
            this.editor!.setCursorPosition(newCursor);
          });
        }

        console.log('[InlineCompletionWidget] Completion accepted, text replaced from', insertOffset, 'to', replaceToOffset);
      } catch (error) {
        console.error('[InlineCompletionWidget] Error accepting completion:', error);
      }
    }

    if (this.onAccept) {
      this.onAccept();
    }

    this.hideCompletion();
    this.originalCursor = null;
    this.replacementEndPos = null;
  }

  public rejectCompletion(): void {
    if (this.onReject) {
      this.onReject();
    }
    this.hideCompletion();
    this.originalCursor = null;
    this.replacementEndPos = null;
  }

  public isCompletionShowing(): boolean {
    return this.isGhostVisible;
  }

  public getCompletionMark(): any {
    return null;
  }

  public clearCompletionMark(): void {
    this.isGhostVisible = false;
  }
}

class GhostTextWidget extends WidgetType {
  constructor(private readonly text: string) {
    super();
  }
  toDOM(): HTMLElement {
    const span = document.createElement('span');
    span.textContent = this.text;
    // Inherit everything from editor theme; only make it translucent
    span.style.opacity = '0.45';
    span.style.whiteSpace = 'pre';
    return span;
  }
}