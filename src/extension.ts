import * as vscode from "vscode";
import { readFile } from "fs/promises";
const PATH = ["styling-hooks.json"];
const ENCODING = "utf-8";
export const SELECTOR = "css";
export const TRIGGER = "--slds";

export async function activate(context: vscode.ExtensionContext) {
  const json = await readFile(
    vscode.Uri.joinPath(context.extensionUri, ...PATH).fsPath,
    ENCODING
  ).catch((error) => vscode.window.showErrorMessage(error.message));
  if (!json) {
    return;
  }
  const STYLING_HOOKS: Record<string, string> = JSON.parse(json);
  const lwcStylingHooksProvider =
    vscode.languages.registerCompletionItemProvider(
      SELECTOR,
      {
        provideCompletionItems(
          document: vscode.TextDocument,
          position: vscode.Position
        ) {
          const word = document.getText(
            document.getWordRangeAtPosition(position)
          );
          const matchingHooks = Object.keys(STYLING_HOOKS).filter((hook) =>
            hook.startsWith(word)
          );
          return matchingHooks.map((hook) => {
            const completionItem = new vscode.CompletionItem(
              hook,
              vscode.CompletionItemKind.Unit
            );
            completionItem.detail = `${hook}: ${STYLING_HOOKS[hook]}`;
            return completionItem;
          });
        },
      },
      TRIGGER
    );
  context.subscriptions.push(lwcStylingHooksProvider);
}

export function deactivate() {}
