/* eslint-disable @typescript-eslint/no-var-requires */
const vscode = require('vscode');
const cp = require('child_process');
const fs = require('fs');
const path = require('path');

function findPythonExecutable() {
  const wsFolders = vscode.workspace.workspaceFolders || [];
  for (const f of wsFolders) {
    const venvPy = path.join(f.uri.fsPath, '.venv', 'Scripts', 'python.exe');
    if (fs.existsSync(venvPy)) return venvPy;
  }
  return process.platform === 'win32' ? 'python' : 'python3';
}

function runPythonEval(pyExe, code, inputText) {
  return new Promise((resolve, reject) => {
    const p = cp.spawn(pyExe, ['-u', '-c', code], { stdio: ['pipe', 'pipe', 'pipe'] });
    let out = '';
    let err = '';
    p.stdout.on('data', (d) => (out += d.toString()));
    p.stderr.on('data', (d) => (err += d.toString()));
    p.on('error', reject);
    p.on('close', (code) => {
      if (code === 0) resolve(out);
      else reject(new Error(err || `python exited with ${code}`));
    });
    if (inputText) p.stdin.write(inputText);
    p.stdin.end();
  });
}

async function formatSup(pyExe, text) {
  const code = "import sys, json; from sup.supfmt import format_text; sys.stdout.write(format_text(sys.stdin.read()))";
  return await runPythonEval(pyExe, code, text);
}

async function lintSup(pyExe, text, pathUri) {
  const code = [
    'import sys, json',
    'from sup.suplint import lint_text',
    'src=sys.stdin.read()',
    'diags=[{"path": d.path, "line": d.line, "column": d.column, "code": d.code, "message": d.message} for d in lint_text("", src)]',
    'sys.stdout.write(json.dumps(diags))',
  ].join('; ');
  const raw = await runPythonEval(pyExe, code, text);
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function activate(context) {
  const pyExe = findPythonExecutable();
  const serverModuleCode = `from sup.lsp_server import main; import sys; sys.exit(main())`;
  const serverOptions = () => {
    const proc = cp.spawn(pyExe, ['-u', '-c', serverModuleCode], { stdio: 'pipe' });
    return { reader: proc.stdout, writer: proc.stdin, process: proc };
  };

  // Minimal client: forward open/change/formatting requests and show diagnostics
  const diagCollection = vscode.languages.createDiagnosticCollection('suplsp');
  context.subscriptions.push(diagCollection);

  function send(msg) {
    const proc = lsp.process;
    if (!proc || proc.killed) return;
    const data = Buffer.from(JSON.stringify(msg), 'utf8');
    lsp.writer.write(`Content-Length: ${data.length}\r\n\r\n`);
    lsp.writer.write(data);
  }

  function readLoop() {
    const stream = lsp.reader;
    let buffer = '';
    stream.on('data', (chunk) => {
      buffer += chunk.toString();
      while (true) {
        const headerEnd = buffer.indexOf('\r\n\r\n');
        if (headerEnd === -1) break;
        const header = buffer.slice(0, headerEnd);
        const m = /Content-Length:\s*(\d+)/i.exec(header);
        if (!m) {
          buffer = buffer.slice(headerEnd + 4);
          continue;
        }
        const len = parseInt(m[1], 10);
        const bodyStart = headerEnd + 4;
        if (buffer.length < bodyStart + len) break;
        const body = buffer.slice(bodyStart, bodyStart + len);
        buffer = buffer.slice(bodyStart + len);
        const msg = JSON.parse(body);
        if (msg.method === 'textDocument/publishDiagnostics') {
          const { uri, diagnostics } = msg.params || {};
          const vscDiags = (diagnostics || []).map((d) => {
            const range = new vscode.Range(
              d.range.start.line,
              d.range.start.character,
              d.range.end.line,
              d.range.end.character
            );
            const diag = new vscode.Diagnostic(range, d.message, vscode.DiagnosticSeverity.Warning);
            diag.source = 'suplsp';
            diag.code = d.code;
            return diag;
          });
          diagCollection.set(vscode.Uri.parse(uri), vscDiags);
        }
      }
    });
  }

  const lsp = serverOptions();
  readLoop();

  // Initialize
  send({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { capabilities: {} } });
  // Apply workspace configuration to diagnostics backend
  const cfg = vscode.workspace.getConfiguration('sup');
  const backend = cfg.get('diagnosticsBackend') || 'interp';
  send({ jsonrpc: '2.0', id: 2, method: 'workspace/didChangeConfiguration', params: { settings: { sup: { diagnosticsBackend: backend } } } });

  // Wire document events
  function openDoc(doc) {
    if (doc.languageId !== 'sup') return;
    send({ jsonrpc: '2.0', method: 'textDocument/didOpen', params: { textDocument: { uri: doc.uri.toString(), text: doc.getText() } } });
  }
  function changeDoc(e) {
    const doc = e.document;
    if (doc.languageId !== 'sup') return;
    send({ jsonrpc: '2.0', method: 'textDocument/didChange', params: { textDocument: { uri: doc.uri.toString() }, contentChanges: [{ text: doc.getText() }] } });
  }

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(openDoc),
    vscode.workspace.onDidChangeTextDocument(changeDoc)
  );
  if (vscode.window.activeTextEditor) openDoc(vscode.window.activeTextEditor.document);

  // Register formatting provider that asks the server
  context.subscriptions.push(vscode.languages.registerDocumentFormattingEditProvider('sup', {
    provideDocumentFormattingEdits(document) {
      const id = Math.floor(Math.random() * 1e9);
      return new Promise((resolve) => {
        const onData = (chunk) => {
          buffer += chunk.toString();
          while (true) {
            const headerEnd = buffer.indexOf('\r\n\r\n');
            if (headerEnd === -1) break;
            const header = buffer.slice(0, headerEnd);
            const m = /Content-Length:\s*(\d+)/i.exec(header);
            if (!m) { buffer = buffer.slice(headerEnd + 4); continue; }
            const len = parseInt(m[1], 10);
            const bodyStart = headerEnd + 4;
            if (buffer.length < bodyStart + len) break;
            const body = buffer.slice(bodyStart, bodyStart + len);
            buffer = buffer.slice(bodyStart + len);
            const msg = JSON.parse(body);
            if (msg.id === id) {
              lsp.reader.removeListener('data', onData);
              const edits = (msg.result || []).map((e) => new vscode.TextEdit(
                new vscode.Range(
                  e.range.start.line, e.range.start.character,
                  e.range.end.line, e.range.end.character
                ), e.newText
              ));
              resolve(edits);
            }
          }
        };
        let buffer = '';
        lsp.reader.on('data', onData);
        send({ jsonrpc: '2.0', id, method: 'textDocument/formatting', params: { textDocument: { uri: document.uri.toString() } } });
      });
    }
  }));
}

function deactivate() {}

module.exports = { activate, deactivate };


