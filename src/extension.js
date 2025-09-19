const vscode = require('vscode');
const open = require('open');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    let disposable = vscode.commands.registerCommand('extension.googleSearch', async function () {
        const editor = vscode.window.activeTextEditor;
        let query = '';
        if (editor) {
            const selection = editor.selection;
            query = editor.document.getText(selection).trim();
        }

        if (!query) {
            const input = await vscode.window.showInputBox({ prompt: 'Texto para pesquisar no Google' });
            if (!input) {
                vscode.window.showInformationMessage('Nenhum texto fornecido.');
                return;
            }
            query = input;
        }

        const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
        try {
            // Tenta abrir no navegador padrão
            await open(url);
        } catch (err) {
            vscode.env.openExternal(vscode.Uri.parse(url));
        }
    });
    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
