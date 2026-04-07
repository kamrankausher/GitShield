const vscode = require('vscode');
const { exec } = require('child_process');
const path = require('path');

/**
 * DevFlow AI++ VS Code Extension
 * ================================
 * Integrates the DevFlow CLI into VS Code with:
 * - Status bar indicators
 * - Problem panel integration
 * - Command palette commands
 * - Auto-scan on save
 * - Notification popups
 */

let statusBarItem;
let diagnosticCollection;
let outputChannel;

function activate(context) {
    outputChannel = vscode.window.createOutputChannel('DevFlow AI++');
    diagnosticCollection = vscode.languages.createDiagnosticCollection('devflow');
    
    // Status bar
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarItem.text = '$(shield) DevFlow';
    statusBarItem.tooltip = 'DevFlow AI++ — Click to scan';
    statusBarItem.command = 'devflow.scan';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Register commands
    const commands = [
        { id: 'devflow.scan', handler: runScan },
        { id: 'devflow.check', handler: runCheck },
        { id: 'devflow.health', handler: runHealth },
        { id: 'devflow.fix', handler: runFix },
        { id: 'devflow.init', handler: runInit },
        { id: 'devflow.stats', handler: runStats },
        { id: 'devflow.doctor', handler: runDoctor },
        { id: 'devflow.panel', handler: openPanel },
    ];

    commands.forEach(({ id, handler }) => {
        context.subscriptions.push(
            vscode.commands.registerCommand(id, handler)
        );
    });

    // Auto-scan on save
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument((doc) => {
            const config = vscode.workspace.getConfiguration('devflow');
            if (config.get('autoScan')) {
                runQuickScan(doc.uri.fsPath);
            }
        })
    );

    // Initial scan
    runQuickScan();
    
    outputChannel.appendLine('DevFlow AI++ activated');
}

function runDevflow(args, cwd) {
    return new Promise((resolve, reject) => {
        const workspaceFolder = cwd || 
            (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0]?.uri.fsPath) || 
            '.';
        
        exec(`python -m devflow.cli ${args}`, { cwd: workspaceFolder, encoding: 'utf-8' }, (err, stdout, stderr) => {
            if (err && !stdout) {
                reject(err);
            } else {
                resolve(stdout || stderr);
            }
        });
    });
}

// ═══════════════════════════════════════════════════════════════
// COMMAND HANDLERS
// ═══════════════════════════════════════════════════════════════

async function runScan() {
    statusBarItem.text = '$(loading~spin) Scanning...';
    try {
        const result = await runDevflow('scan .');
        outputChannel.clear();
        outputChannel.appendLine(result);
        outputChannel.show();
        
        if (result.includes('No security issues')) {
            statusBarItem.text = '$(shield) DevFlow ✓';
            statusBarItem.backgroundColor = undefined;
            vscode.window.showInformationMessage('DevFlow: No security issues found! ✅');
        } else {
            statusBarItem.text = '$(warning) DevFlow ⚠';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            vscode.window.showWarningMessage('DevFlow: Security issues detected! Check output panel.');
        }
    } catch (e) {
        statusBarItem.text = '$(error) DevFlow';
        vscode.window.showErrorMessage(`DevFlow scan failed: ${e.message}`);
    }
}

async function runCheck() {
    try {
        const result = await runDevflow('check');
        outputChannel.clear();
        outputChannel.appendLine(result);
        outputChannel.show();
        vscode.window.showInformationMessage('DevFlow: Pre-commit check complete');
    } catch (e) {
        outputChannel.appendLine(e.message);
        outputChannel.show();
    }
}

async function runHealth() {
    try {
        const result = await runDevflow('health .');
        outputChannel.clear();
        outputChannel.appendLine(result);
        outputChannel.show();
    } catch (e) {
        vscode.window.showErrorMessage(`DevFlow health check failed: ${e.message}`);
    }
}

async function runFix() {
    const options = [
        { label: '$(history) Undo last commit (keep staged)', id: 'undo_soft' },
        { label: '$(history) Undo last commit (unstage)', id: 'undo_mixed' },
        { label: '$(trash) Undo last commit (DELETE)', id: 'undo_hard' },
        { label: '$(edit) Amend last commit', id: 'amend' },
        { label: '$(git-pull-request) Revert pushed commit', id: 'revert' },
        { label: '$(file-symlink-directory) Unstage all files', id: 'unstage' },
        { label: '$(discard) Discard all changes', id: 'discard' },
        { label: '$(alert) EMERGENCY: Secret leaked!', id: 'secret' },
    ];

    const selected = await vscode.window.showQuickPick(options, {
        placeHolder: 'Select a recovery action...',
        title: 'DevFlow Recovery Wizard'
    });

    if (selected) {
        const result = await runDevflow(`fix`);
        outputChannel.clear();
        outputChannel.appendLine(result);
        outputChannel.show();
    }
}

async function runInit() {
    try {
        const result = await runDevflow('init');
        outputChannel.clear();
        outputChannel.appendLine(result);
        outputChannel.show();
        vscode.window.showInformationMessage('DevFlow: Hooks installed successfully! ✅');
    } catch (e) {
        vscode.window.showErrorMessage(`DevFlow init failed: ${e.message}`);
    }
}

async function runStats() {
    try {
        const result = await runDevflow('stats');
        outputChannel.clear();
        outputChannel.appendLine(result);
        outputChannel.show();
    } catch (e) {
        vscode.window.showErrorMessage(`DevFlow stats failed: ${e.message}`);
    }
}

async function runDoctor() {
    try {
        const result = await runDevflow('doctor');
        outputChannel.clear();
        outputChannel.appendLine(result);
        outputChannel.show();
    } catch (e) {
        vscode.window.showErrorMessage(`DevFlow doctor failed: ${e.message}`);
    }
}

async function runQuickScan(filePath) {
    try {
        const result = await runDevflow('scan . --staged');
        if (result.includes('CRITICAL') || result.includes('SECRET')) {
            statusBarItem.text = '$(warning) DevFlow ⚠';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            
            const config = vscode.workspace.getConfiguration('devflow');
            if (config.get('showNotifications')) {
                vscode.window.showWarningMessage('DevFlow: Potential security issue detected!', 'Show Details').then(action => {
                    if (action === 'Show Details') {
                        outputChannel.clear();
                        outputChannel.appendLine(result);
                        outputChannel.show();
                    }
                });
            }
        } else {
            statusBarItem.text = '$(shield) DevFlow ✓';
            statusBarItem.backgroundColor = undefined;
        }
    } catch (e) {
        // Silent fail for background scans
    }
}

function openPanel() {
    runHealth();
}

function deactivate() {
    if (statusBarItem) statusBarItem.dispose();
    if (diagnosticCollection) diagnosticCollection.dispose();
    if (outputChannel) outputChannel.dispose();
}

module.exports = { activate, deactivate };
