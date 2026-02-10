#!/usr/bin/env python3
"""
RAG Document Chat web interface - pibiCo guidelines compliant
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.config import settings

router = APIRouter()


@router.get("/", response_class=HTMLResponse, tags=["Web Interface"])
async def web_interface(request: Request):
    """
    Serve RAG Document Chat interface with pibico-guidelines styling.
    """
    base_path = settings.ROOT_PATH if settings.ROOT_PATH else ''
    api_endpoint = f"{base_path}/api/v1"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#4682B4">
    <title>RAG Document Chat - pibiCo AI Services</title>
    <link rel="icon" href="{base_path}/static/pibico_icon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="{base_path}/static/css/pibico.css">
    <link rel="stylesheet" href="{base_path}/static/css/bootstrap-icons.min.css">
    <style>
        /* Navbar Card */
        .navbar {{
            position: fixed;
            top: 8px;
            left: 12px;
            right: 12px;
            z-index: 900;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.6rem 1.5rem;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            background: rgba(255, 255, 255, 0.85);
            border-radius: 12px;
            box-shadow: 0 0 12px rgba(70, 130, 180, 0.15),
                        0 0 4px rgba(70, 130, 180, 0.08);
            line-height: 1.1;
        }}

        .navbar-title {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', Arial, sans-serif;
            font-size: 1.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #4682B4 0%, #B33A2B 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .navbar-nav {{
            display: flex;
            flex-direction: row;
            gap: 0.5rem;
            align-items: center;
            list-style: none;
            margin: 0;
            padding: 0;
        }}

        .navbar-nav li {{
            display: inline-block;
            margin: 0;
            padding: 0;
        }}

        .nav-link {{
            color: #4682B4;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.8rem;
            padding: 0.35rem 0.75rem;
            border-radius: 8px;
            transition: all 0.2s ease;
        }}

        .nav-link:hover {{
            background: #D6E8F5;
            color: #365F8A;
        }}

        .btn-icon {{
            width: 34px;
            height: 34px;
            border: none;
            border-radius: 8px;
            background: #E8E8EA;
            color: #4682B4;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }}

        .btn-icon:hover {{
            background: #D6E8F5;
            color: #365F8A;
        }}

        /* Footer Card */
        .app-footer {{
            position: fixed;
            bottom: 8px;
            left: 12px;
            right: 12px;
            z-index: 900;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.4rem 1.5rem;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            background: rgba(255, 255, 255, 0.85);
            border-radius: 12px;
            box-shadow: 0 0 12px rgba(70, 130, 180, 0.15),
                        0 0 4px rgba(70, 130, 180, 0.08);
            font-size: 0.75rem;
            color: #6E6E76;
            line-height: 1.1;
        }}

        .footer-separator {{
            color: #C8C8CC;
        }}

        .footer-link {{
            color: #4682B4;
            text-decoration: none;
        }}

        .footer-link:hover {{
            text-decoration: underline;
        }}

        /* Main content area */
        .app-main {{
            margin-top: 60px;
            margin-bottom: 44px;
            min-height: calc(100vh - 104px);
            padding: 12px;
            background: linear-gradient(135deg, #2c5171 0%, #4682B4 50%, #6a9bc3 100%);
        }}

        /* Layout grid */
        .rag-container {{
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
            height: calc(100vh - 116px);
        }}

        /* Document sidebar */
        .documents-sidebar {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .document-item {{
            background: var(--pibico-white);
            border-radius: var(--pibico-radius);
            padding: 12px;
            line-height: 1.1;
            box-shadow: var(--pibico-card-shadow);
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }}

        .document-item:hover {{
            box-shadow: var(--pibico-card-shadow-hover);
            transform: translateY(-2px);
        }}

        .document-item.active {{
            box-shadow: 0 0 0 2px var(--pibico-steel-blue), var(--pibico-card-shadow-hover);
        }}

        .document-title {{
            font-weight: 600;
            color: var(--pibico-near-black);
            margin-bottom: 4px;
            padding-right: 32px;
        }}

        .document-meta {{
            font-size: 0.75rem;
            color: var(--pibico-grey-dark);
        }}

        .document-delete {{
            position: absolute;
            top: 8px;
            right: 8px;
            width: 28px;
            height: 28px;
            border: none;
            border-radius: 6px;
            background: transparent;
            color: #B33A2B;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: all 0.2s ease;
            font-size: 16px;
        }}

        .document-item:hover .document-delete {{
            opacity: 1;
        }}

        .document-delete:hover {{
            background: rgba(179, 58, 43, 0.1);
            transform: scale(1.1);
        }}

        /* Chat area */
        .chat-area {{
            background: var(--pibico-white);
            border-radius: var(--pibico-radius);
            box-shadow: var(--pibico-card-shadow);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .chat-header {{
            padding: 12px 16px;
            background: var(--pibico-grad-primary);
            color: var(--pibico-white);
            font-weight: 600;
            line-height: 1.1;
        }}

        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .chat-input-area {{
            padding: 12px 16px;
            border-top: 1px solid var(--pibico-light-grey);
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .chat-input {{
            flex: 1;
            font-family: var(--pibico-font-body);
            font-size: 0.9rem;
            padding: 8px 12px;
            border: none;
            border-radius: var(--pibico-radius-sm);
            background: var(--pibico-light-grey);
            color: var(--pibico-near-black);
            line-height: 1.1;
            outline: none;
        }}

        .chat-input:focus {{
            box-shadow: 0 0 0 2px var(--pibico-steel-blue);
            background: var(--pibico-white);
        }}

        /* Message bubbles */
        .message {{
            display: flex;
            gap: 10px;
            max-width: 75%;
            animation: fadeIn 0.3s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .message.user {{
            align-self: flex-end;
            flex-direction: row-reverse;
        }}

        .message.assistant {{
            align-self: flex-start;
        }}

        .message-avatar {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.9rem;
            flex-shrink: 0;
        }}

        .message.user .message-avatar {{
            background: var(--pibico-steel-blue);
            color: var(--pibico-white);
        }}

        .message.assistant .message-avatar {{
            background: var(--pibico-light-grey);
            color: var(--pibico-steel-blue);
        }}

        .message-bubble {{
            padding: 10px 14px;
            border-radius: var(--pibico-radius);
            line-height: 1.2;
            word-wrap: break-word;
        }}

        .message.user .message-bubble {{
            background: var(--pibico-steel-blue);
            color: var(--pibico-white);
            border-bottom-right-radius: 4px;
        }}

        .message.assistant .message-bubble {{
            background: var(--pibico-light-grey);
            color: var(--pibico-near-black);
            border-bottom-left-radius: 4px;
        }}

        .message-time {{
            font-size: 0.7rem;
            opacity: 0.7;
            margin-top: 4px;
        }}

        /* Welcome state */
        .welcome-state {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            color: var(--pibico-grey-dark);
        }}

        .welcome-state i {{
            font-size: 4rem;
            color: var(--pibico-steel-light);
            margin-bottom: 16px;
        }}

        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 60px;
            right: 20px;
            background: var(--pibico-white);
            border-radius: var(--pibico-radius);
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
            padding: 12px 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1100;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s ease;
            line-height: 1.1;
        }}

        .toast.show {{
            transform: translateY(0);
            opacity: 1;
        }}

        .toast.success {{ border-left: 4px solid #10b981; }}
        .toast.error {{ border-left: 4px solid var(--pibico-red-brick); }}

        /* Loading spinner */
        .spinner {{
            border: 2px solid var(--pibico-light-grey);
            border-top-color: var(--pibico-steel-blue);
            border-radius: 50%;
            width: 16px;
            height: 16px;
            animation: spin 0.8s linear infinite;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        /* Confirmation Dialog */
        .confirm-dialog {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.9);
            background: var(--pibico-white);
            border-radius: var(--pibico-radius);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            padding: 24px;
            z-index: 1100;
            min-width: 320px;
            max-width: 400px;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
        }}

        .confirm-dialog.active {{
            opacity: 1;
            visibility: visible;
            transform: translate(-50%, -50%) scale(1);
        }}

        .confirm-backdrop {{
            position: fixed;
            inset: 0;
            background: rgba(26, 26, 46, 0.5);
            z-index: 1050;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
        }}

        .confirm-backdrop.active {{
            opacity: 1;
            visibility: visible;
        }}

        .confirm-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--pibico-near-black);
            margin-bottom: 12px;
        }}

        .confirm-message {{
            color: var(--pibico-grey-dark);
            margin-bottom: 20px;
            line-height: 1.4;
        }}

        .confirm-buttons {{
            display: flex;
            gap: 8px;
            justify-content: flex-end;
        }}

        /* Auth notice */
        .auth-notice {{
            background: var(--pibico-steel-pale);
            padding: 12px;
            border-radius: var(--pibico-radius);
            text-align: center;
            line-height: 1.2;
            margin-bottom: 12px;
        }}

        /* Drag and drop upload zone */
        .upload-dropzone {{
            border: 2px dashed var(--pibico-steel-light);
            border-radius: var(--pibico-radius);
            padding: 32px;
            text-align: center;
            background: var(--pibico-steel-pale);
            cursor: pointer;
            transition: all 0.2s ease;
            margin-bottom: 16px;
        }}

        .upload-dropzone:hover {{
            border-color: var(--pibico-steel-blue);
            background: rgba(70, 130, 180, 0.05);
        }}

        .upload-dropzone.dragover {{
            border-color: var(--pibico-steel-blue);
            background: rgba(70, 130, 180, 0.1);
            transform: scale(1.02);
        }}

        .upload-dropzone-icon {{
            font-size: 3rem;
            color: var(--pibico-steel-blue);
            margin-bottom: 12px;
        }}

        .upload-dropzone-text {{
            color: var(--pibico-grey-dark);
            margin-bottom: 8px;
            font-weight: 500;
        }}

        .upload-dropzone-hint {{
            font-size: 0.85rem;
            color: var(--pibico-grey-dark);
            opacity: 0.8;
        }}

        .upload-file-list {{
            margin-top: 12px;
            padding: 12px;
            background: var(--pibico-light-grey);
            border-radius: var(--pibico-radius-sm);
            max-height: 150px;
            overflow-y: auto;
        }}

        .upload-file-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 8px;
            margin-bottom: 4px;
            background: var(--pibico-white);
            border-radius: var(--pibico-radius-sm);
            font-size: 0.85rem;
        }}

        .upload-file-item:last-child {{
            margin-bottom: 0;
        }}

        .upload-file-remove {{
            background: none;
            border: none;
            color: var(--pibico-red-brick);
            cursor: pointer;
            padding: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }}

        .upload-file-remove:hover {{
            transform: scale(1.2);
        }}

        /* Preset management */
        .preset-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: 200px;
            overflow-y: auto;
            margin-bottom: 12px;
        }}

        .preset-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            background: var(--pibico-steel-pale);
            border-radius: var(--pibico-radius-sm);
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .preset-item:hover {{
            background: rgba(70, 130, 180, 0.15);
        }}

        .preset-item.active {{
            background: var(--pibico-steel-blue);
            color: var(--pibico-white);
        }}

        .preset-name {{
            font-weight: 500;
            flex: 1;
        }}

        .preset-actions {{
            display: flex;
            gap: 4px;
        }}

        .preset-action-btn {{
            background: none;
            border: none;
            color: var(--pibico-grey-dark);
            cursor: pointer;
            padding: 4px;
            display: flex;
            align-items: center;
            transition: all 0.2s ease;
        }}

        .preset-action-btn:hover {{
            color: var(--pibico-steel-blue);
            transform: scale(1.2);
        }}

        .preset-item.active .preset-action-btn {{
            color: rgba(255, 255, 255, 0.8);
        }}

        .preset-item.active .preset-action-btn:hover {{
            color: var(--pibico-white);
        }}

        .preset-form {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .preset-selector {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: var(--pibico-steel-pale);
            border-radius: var(--pibico-radius-sm);
            margin-bottom: 8px;
        }}

        .preset-selector select {{
            flex: 1;
            border: 1px solid var(--pibico-light-grey);
            border-radius: var(--pibico-radius-sm);
            padding: 6px 10px;
            background: var(--pibico-white);
            font-size: 0.85rem;
        }}

        .preset-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 0.75rem;
            color: var(--pibico-steel-blue);
            font-weight: 500;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .rag-container {{
                grid-template-columns: 1fr;
            }}
            .documents-sidebar {{
                max-height: 200px;
                overflow-y: auto;
            }}
            .message {{
                max-width: 85%;
            }}
            .pibico-panel {{
                width: 100%;
            }}
            .navbar {{
                left: 6px;
                right: 6px;
                top: 6px;
                padding: 3px 12px;
            }}
            .navbar-title {{
                font-size: 1.2rem;
            }}
            .app-footer {{
                left: 6px;
                right: 6px;
                bottom: 6px;
                padding: 3px 12px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="navbar-title">RAG Document Chat</span>
        </div>
        <ul class="navbar-nav">
            <li><button class="btn-icon" onclick="openSettingsPanel()" title="Settings"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></button></li>
            <li><a href="{api_endpoint}/docs" class="nav-link" target="_blank" title="API Docs"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg> API</a></li>
            <li><button class="pibico-btn pibico-btn-outline" onclick="openUploadPanel()">
                <i class="bi bi-cloud-upload"></i> Upload
            </button></li>
        </ul>
    </nav>

    <!-- Main content -->
    <main class="app-main">
        <div class="rag-container">
            <!-- Documents sidebar -->
            <div class="documents-sidebar">
                <h4 style="color: rgba(255,255,255,0.9); margin-bottom: 12px; font-size: 0.9rem; font-weight: 600; padding-left: 4px;">Your Documents</h4>
                <div id="documentsList" style="flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px;">
                    <div style="text-align: center; padding: 20px; color: rgba(255,255,255,0.7);">
                        No documents yet
                    </div>
                </div>
            </div>

            <!-- Chat area -->
            <div class="chat-area">
                <div class="chat-header" id="chatHeader">
                    Select a document to start chatting
                </div>
                <div class="chat-messages" id="chatMessages">
                    <div class="welcome-state">
                        <i class="bi bi-chat-text"></i>
                        <h3>Welcome to RAG Document Chat</h3>
                        <p>Upload a document and start asking questions</p>
                    </div>
                </div>
                <div class="chat-input-area" id="chatInputArea" style="display: none;">
                    <div style="width: 100%; display: flex; flex-direction: column; gap: 8px;">
                        <div class="preset-selector">
                            <label style="font-size: 0.85rem; color: var(--pibico-grey-dark); white-space: nowrap;">
                                <i class="bi bi-code-square"></i> Preset:
                            </label>
                            <select id="presetSelector" onchange="updatePresetIndicator()">
                                <option value="">Default (General Q&A)</option>
                            </select>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <input type="text" class="chat-input" id="chatInput" placeholder="Ask a question..."
                                   onkeypress="if(event.key==='Enter') sendMessage()" style="margin: 0;">
                            <button class="pibico-btn pibico-btn-primary" onclick="sendMessage()">
                                <i class="bi bi-send"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
        <span><svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M15 9.354a4 4 0 1 0 0 5.292" stroke-linecap="round"/></svg> pibiCo 2026</span>
        <span class="footer-separator">|</span>
        <a href="{api_endpoint}/redoc" target="_blank" style="color: #4682B4; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;"><svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg> ReDoc</a>
        <span class="footer-separator">|</span>
        <span><svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg> v1.0.0</span>
    </footer>

    <!-- Upload Panel -->
    <div class="pibico-panel-backdrop" id="uploadPanel-backdrop" onclick="closeUploadPanel()"></div>
    <div class="pibico-panel" id="uploadPanel">
        <div class="pibico-panel-header">
            <span>Upload Document</span>
            <button class="pibico-panel-close" onclick="closeUploadPanel()">&times;</button>
        </div>
        <div class="pibico-panel-body">
            <div class="upload-dropzone" id="uploadDropzone" onclick="document.getElementById('uploadFileInput').click()">
                <div class="upload-dropzone-icon">
                    <i class="bi bi-cloud-upload"></i>
                </div>
                <div class="upload-dropzone-text">
                    Drag & drop files here
                </div>
                <div class="upload-dropzone-hint">
                    or click to browse (PDF, TXT, MD)
                </div>
            </div>
            <input type="file" id="uploadFileInput" accept=".pdf,.txt,.md,.markdown" multiple style="display: none;">
            <div id="uploadFileList" style="display: none;" class="upload-file-list"></div>
            <button class="pibico-btn pibico-btn-primary" onclick="uploadDocuments()" id="uploadBtn" style="width: 100%; display: none;">
                <i class="bi bi-cloud-upload"></i> Upload <span id="uploadCount"></span>
            </button>
        </div>
    </div>

    <!-- Settings Panel -->
    <div class="pibico-panel-backdrop" id="settingsPanel-backdrop" onclick="closeSettingsPanel()"></div>
    <div class="pibico-panel" id="settingsPanel">
        <div class="pibico-panel-header">
            <span>Settings</span>
            <button class="pibico-panel-close" onclick="closeSettingsPanel()">&times;</button>
        </div>
        <div class="pibico-panel-body">
            <!-- Model selection -->
            <div class="pibico-card" style="padding: 12px; margin-bottom: 16px;">
                <h4 style="margin-bottom: 12px;">LLM Model</h4>
                <label class="pibico-label">Ollama Model</label>
                <select class="pibico-input" id="ollamaModel" onchange="saveModel()">
                    <option value="qwen2.5:7b-instruct">qwen2.5:7b-instruct</option>
                    <option value="mistral:7b">mistral:7b</option>
                    <option value="llama3.2:3b">llama3.2:3b</option>
                </select>
            </div>

            <!-- API Key -->
            <div class="pibico-card" style="padding: 12px; margin-bottom: 16px;">
                <h4 style="margin-bottom: 12px;">API Configuration</h4>
                <label class="pibico-label">API Key (optional)</label>
                <input type="password" class="pibico-input" id="apiKey" placeholder="Optional API key">
                <button class="pibico-btn pibico-btn-primary" onclick="saveApiKey()" style="margin-top: 12px; width: 100%;">
                    <i class="bi bi-check-circle"></i> Save
                </button>
            </div>

            <!-- System Instruction Presets -->
            <div class="pibico-card" style="padding: 12px;">
                <h4 style="margin-bottom: 12px;"><i class="bi bi-code-square"></i> System Instruction Presets</h4>
                <div id="presetsList" class="preset-list"></div>
                <button class="pibico-btn pibico-btn-outline" onclick="showPresetForm()" style="width: 100%; margin-bottom: 12px;">
                    <i class="bi bi-plus-circle"></i> New Preset
                </button>
                <div id="presetForm" class="preset-form" style="display: none;">
                    <input type="hidden" id="editPresetId">
                    <label class="pibico-label">Preset Name</label>
                    <input type="text" class="pibico-input" id="presetName" placeholder="e.g., Invoice Extractor">
                    <label class="pibico-label">System Instruction</label>
                    <textarea class="pibico-input" id="presetInstruction" rows="6" placeholder="Enter the system instruction that will guide the AI..."></textarea>
                    <div style="display: flex; gap: 8px;">
                        <button class="pibico-btn pibico-btn-primary" onclick="savePreset()" style="flex: 1;">
                            <i class="bi bi-check-circle"></i> Save
                        </button>
                        <button class="pibico-btn pibico-btn-outline" onclick="cancelPresetForm()" style="flex: 1;">
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast -->
    <div class="toast" id="toast">
        <i class="bi bi-check-circle" id="toastIcon"></i>
        <span id="toastMessage"></span>
    </div>

    <!-- Confirmation Dialog -->
    <div class="confirm-backdrop" id="confirmBackdrop"></div>
    <div class="confirm-dialog" id="confirmDialog">
        <div class="confirm-title" id="confirmTitle">Confirm Action</div>
        <div class="confirm-message" id="confirmMessage">Are you sure?</div>
        <div class="confirm-buttons">
            <button class="pibico-btn pibico-btn-outline" onclick="closeConfirm()">Cancel</button>
            <button class="pibico-btn pibico-btn-danger" id="confirmBtn">Delete</button>
        </div>
    </div>

    <script>
        // API configuration
        const API_ENDPOINT = '{api_endpoint}';
        const BASE_PATH = '{base_path}';

        // State
        let currentDocument = null;
        let currentSession = null;
        let documents = [];
        let chatMessages = [];
        let confirmCallback = null;
        let uploadFiles = [];

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('RAG Chat UI initializing...');

            // Set up drag and drop
            setupDragAndDrop();

            // Load saved model selection
            const savedModel = localStorage.getItem('rag_model');
            if (savedModel) {{
                document.getElementById('ollamaModel').value = savedModel;
            }}

            // Load saved API key
            const savedApiKey = sessionStorage.getItem('rag_api_key');
            if (savedApiKey) {{
                document.getElementById('apiKey').value = savedApiKey;
            }}

            // Load documents on init
            loadDocuments();

            // Load presets
            loadPresets();

            console.log('RAG Chat UI initialized');
        }});

        // Panel management
        function openUploadPanel() {{
            // Reset upload state
            uploadFiles = [];
            document.getElementById('uploadFileInput').value = '';
            document.getElementById('uploadFileList').style.display = 'none';
            document.getElementById('uploadBtn').style.display = 'none';

            document.getElementById('uploadPanel').classList.add('active');
            document.getElementById('uploadPanel-backdrop').classList.add('active');
        }}

        function closeUploadPanel() {{
            document.getElementById('uploadPanel').classList.remove('active');
            document.getElementById('uploadPanel-backdrop').classList.remove('active');
        }}

        function openSettingsPanel() {{
            document.getElementById('settingsPanel').classList.add('active');
            document.getElementById('settingsPanel-backdrop').classList.add('active');
        }}

        function closeSettingsPanel() {{
            document.getElementById('settingsPanel').classList.remove('active');
            document.getElementById('settingsPanel-backdrop').classList.remove('active');
        }}

        // Toast notifications
        function showToast(message, type = 'success') {{
            const toast = document.getElementById('toast');
            const icon = document.getElementById('toastIcon');
            const msg = document.getElementById('toastMessage');

            toast.className = 'toast ' + type;
            icon.className = type === 'error' ? 'bi bi-x-circle' : 'bi bi-check-circle';
            msg.textContent = message;

            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }}

        // Confirmation dialog
        function showConfirm(title, message, onConfirm) {{
            document.getElementById('confirmTitle').textContent = title;
            document.getElementById('confirmMessage').textContent = message;
            document.getElementById('confirmBackdrop').classList.add('active');
            document.getElementById('confirmDialog').classList.add('active');

            confirmCallback = onConfirm;

            // Set up confirm button click
            const confirmBtn = document.getElementById('confirmBtn');
            confirmBtn.onclick = () => {{
                if (confirmCallback) {{
                    confirmCallback();
                }}
                closeConfirm();
            }};
        }}

        function closeConfirm() {{
            document.getElementById('confirmBackdrop').classList.remove('active');
            document.getElementById('confirmDialog').classList.remove('active');
            confirmCallback = null;
        }}

        // Close on backdrop click
        document.addEventListener('DOMContentLoaded', function() {{
            document.getElementById('confirmBackdrop').onclick = closeConfirm;
        }});

        // Drag and drop setup
        function setupDragAndDrop() {{
            const dropzone = document.getElementById('uploadDropzone');
            const fileInput = document.getElementById('uploadFileInput');

            // Prevent default drag behaviors
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {{
                dropzone.addEventListener(eventName, preventDefaults, false);
                document.body.addEventListener(eventName, preventDefaults, false);
            }});

            // Highlight drop zone when item is dragged over it
            ['dragenter', 'dragover'].forEach(eventName => {{
                dropzone.addEventListener(eventName, () => {{
                    dropzone.classList.add('dragover');
                }}, false);
            }});

            ['dragleave', 'drop'].forEach(eventName => {{
                dropzone.addEventListener(eventName, () => {{
                    dropzone.classList.remove('dragover');
                }}, false);
            }});

            // Handle dropped files
            dropzone.addEventListener('drop', handleDrop, false);

            // Handle file input change
            fileInput.addEventListener('change', function() {{
                handleFiles(this.files);
            }});
        }}

        function preventDefaults(e) {{
            e.preventDefault();
            e.stopPropagation();
        }}

        function handleDrop(e) {{
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }}

        function handleFiles(files) {{
            uploadFiles = Array.from(files).filter(file => {{
                const ext = file.name.split('.').pop().toLowerCase();
                return ['pdf', 'txt', 'md', 'markdown'].includes(ext);
            }});

            if (uploadFiles.length === 0) {{
                showToast('Please select valid files (PDF, TXT, MD)', 'error');
                return;
            }}

            renderFileList();
        }}

        function renderFileList() {{
            const fileList = document.getElementById('uploadFileList');
            const uploadBtn = document.getElementById('uploadBtn');
            const uploadCount = document.getElementById('uploadCount');

            if (uploadFiles.length === 0) {{
                fileList.style.display = 'none';
                uploadBtn.style.display = 'none';
                return;
            }}

            fileList.style.display = 'block';
            uploadBtn.style.display = 'block';
            uploadCount.textContent = uploadFiles.length === 1 ? '' : `(${{uploadFiles.length}} files)`;

            fileList.innerHTML = uploadFiles.map((file, index) => `
                <div class="upload-file-item">
                    <span><i class="bi bi-file-earmark-text"></i> ${{file.name}}</span>
                    <button class="upload-file-remove" onclick="removeUploadFile(${{index}})" title="Remove">
                        <i class="bi bi-x-circle"></i>
                    </button>
                </div>
            `).join('');
        }}

        function removeUploadFile(index) {{
            uploadFiles.splice(index, 1);
            renderFileList();
        }}

        // Document management
        async function uploadDocuments() {{
            if (uploadFiles.length === 0) {{
                showToast('Please select files to upload', 'error');
                return;
            }}

            const uploadBtn = document.getElementById('uploadBtn');
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<div class="spinner"></div> Uploading...';

            let successCount = 0;
            let failCount = 0;

            for (let i = 0; i < uploadFiles.length; i++) {{
                const file = uploadFiles[i];
                const formData = new FormData();
                formData.append('file', file);

                try {{
                    const res = await fetch(`${{API_ENDPOINT}}/documents/upload`, {{
                        method: 'POST',
                        body: formData
                    }});

                    if (res.ok) {{
                        successCount++;
                    }} else {{
                        failCount++;
                        console.error(`Failed to upload ${{file.name}}`);
                    }}
                }} catch (err) {{
                    failCount++;
                    console.error(`Error uploading ${{file.name}}:`, err);
                }}
            }}

            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="bi bi-cloud-upload"></i> Upload <span id="uploadCount"></span>';

            if (successCount > 0) {{
                showToast(`${{successCount}} document(s) uploaded! Indexing...`);
                closeUploadPanel();
                setTimeout(loadDocuments, 1000);
            }}

            if (failCount > 0) {{
                showToast(`${{failCount}} upload(s) failed`, 'error');
            }}
        }}

        async function loadDocuments() {{
            try {{
                const res = await fetch(`${{API_ENDPOINT}}/documents/`);

                if (res.ok) {{
                    documents = await res.json();
                    renderDocuments();
                }}
            }} catch (err) {{
                console.error('Error loading documents:', err);
            }}
        }}

        async function deleteDocument(docId) {{
            const doc = documents.find(d => d.id === docId);
            const docTitle = doc ? doc.title : 'this document';

            showConfirm(
                'Delete Document',
                `Are you sure you want to delete "${{docTitle}}"? This action cannot be undone.`,
                async () => {{
                    try {{
                        const res = await fetch(`${{API_ENDPOINT}}/documents/${{docId}}`, {{
                            method: 'DELETE'
                        }});

                        if (res.ok) {{
                            // Try to parse JSON, but don't fail if it's not JSON
                            try {{
                                await res.json();
                            }} catch (e) {{
                                // Response might not be JSON, that's okay
                            }}

                            showToast('Document deleted successfully');

                            // If deleted document was active, reset chat
                            if (currentDocument?.id === docId) {{
                                currentDocument = null;
                                currentSession = null;
                                resetChat();
                                document.getElementById('chatHeader').textContent = 'Select a document to start chatting';
                                document.getElementById('chatInputArea').style.display = 'none';
                            }}

                            // Reload documents list
                            loadDocuments();
                        }} else {{
                            let errorMessage = 'Delete failed';
                            try {{
                                const error = await res.json();
                                errorMessage = error.detail || errorMessage;
                            }} catch (e) {{
                                errorMessage = `Delete failed with status: ${{res.status}}`;
                            }}
                            showToast(errorMessage, 'error');
                        }}
                    }} catch (err) {{
                        showToast('Error: ' + err.message, 'error');
                    }}
                }}
            );
        }}

        function renderDocuments() {{
            const list = document.getElementById('documentsList');

            if (documents.length === 0) {{
                list.innerHTML = '<div style="text-align: center; padding: 20px; color: rgba(255,255,255,0.7);">No documents yet</div>';
                return;
            }}

            list.innerHTML = documents.map(doc => {{
                const isActive = currentDocument?.id === doc.id;
                const statusColors = {{
                    'pending': 'grey',
                    'indexing': 'blue',
                    'ready': 'blue',
                    'error': 'red'
                }};
                const statusColor = statusColors[doc.status] || 'grey';

                return `
                    <div class="document-item ${{isActive ? 'active' : ''}}" onclick="selectDocument(${{doc.id}})">
                        <button class="document-delete" onclick="event.stopPropagation(); deleteDocument(${{doc.id}})" title="Delete document">
                            <i class="bi bi-trash"></i>
                        </button>
                        <div class="document-title">${{doc.title}}</div>
                        <div class="document-meta">
                            <span class="pibico-badge pibico-badge-${{statusColor}}">${{doc.status}}</span>
                            <span style="margin-left: 8px;">${{doc.filename}}</span>
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        async function selectDocument(docId) {{
            const doc = documents.find(d => d.id === docId);
            if (!doc) return;

            if (doc.status !== 'ready') {{
                showToast('Document is still ' + doc.status, 'error');
                return;
            }}

            currentDocument = doc;
            chatMessages = [];
            renderDocuments();

            // Create chat session
            try {{
                const res = await fetch(`${{API_ENDPOINT}}/chat/sessions`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ document_id: docId }})
                }});

                if (res.ok) {{
                    currentSession = await res.json();
                    document.getElementById('chatHeader').textContent = doc.title;
                    document.getElementById('chatInputArea').style.display = 'flex';
                    resetChat();
                    showToast('Chat session started!');
                }} else {{
                    const error = await res.json();
                    showToast(error.detail || 'Failed to create session', 'error');
                }}
            }} catch (err) {{
                showToast('Error: ' + err.message, 'error');
            }}
        }}

        // Chat functions
        function resetChat() {{
            const messagesDiv = document.getElementById('chatMessages');
            messagesDiv.innerHTML = '';
            chatMessages = [];
        }}

        async function sendMessage() {{
            const input = document.getElementById('chatInput');
            const query = input.value.trim();

            if (!query || !currentSession) return;

            const startTime = Date.now();
            addMessage(query, 'user');
            input.value = '';

            // Get selected preset
            const presetId = document.getElementById('presetSelector').value;
            let systemInstruction = null;
            if (presetId) {{
                const preset = systemPresets.find(p => p.id === presetId);
                if (preset) {{
                    systemInstruction = preset.instruction;
                }}
            }}

            // Show typing indicator
            const typingId = 'typing-' + Date.now();
            addTypingIndicator(typingId);

            try {{
                const requestBody = {{
                    session_id: currentSession.id,
                    query: query,
                    top_k: 5
                }};

                // Add system_instruction if a preset is selected
                if (systemInstruction) {{
                    requestBody.system_instruction = systemInstruction;
                }}

                const res = await fetch(`${{API_ENDPOINT}}/chat/query`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(requestBody)
                }});

                removeTypingIndicator(typingId);

                if (res.ok) {{
                    const data = await res.json();
                    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
                    addMessage(data.answer, 'assistant', elapsedTime);
                }} else {{
                    const error = await res.json();
                    showToast(error.detail || 'Query failed', 'error');
                }}
            }} catch (err) {{
                removeTypingIndicator(typingId);
                showToast('Error: ' + err.message, 'error');
            }}
        }}

        function addMessage(text, role, elapsedTime = null) {{
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + role;

            const timestamp = new Date();
            const timeString = timestamp.toLocaleTimeString('en-US', {{
                hour: '2-digit',
                minute: '2-digit'
            }});

            const avatar = role === 'user' ? 'U' : 'AI';
            let timeDisplay = timeString;
            if (elapsedTime) {{
                timeDisplay += ` • ${{elapsedTime}}s`;
            }}

            messageDiv.innerHTML = `
                <div class="message-avatar">${{avatar}}</div>
                <div>
                    <div class="message-bubble">${{text}}</div>
                    <div class="message-time">${{timeDisplay}}</div>
                </div>
            `;

            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            chatMessages.push({{ text, role, timestamp }});
        }}

        function addTypingIndicator(id) {{
            const messagesDiv = document.getElementById('chatMessages');
            const typingDiv = document.createElement('div');
            typingDiv.id = id;
            typingDiv.className = 'message assistant';
            typingDiv.innerHTML = `
                <div class="message-avatar">AI</div>
                <div>
                    <div class="message-bubble">
                        <div class="spinner"></div>
                    </div>
                </div>
            `;
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}

        function removeTypingIndicator(id) {{
            const el = document.getElementById(id);
            if (el) el.remove();
        }}

        // Settings
        function saveModel() {{
            const model = document.getElementById('ollamaModel').value;
            localStorage.setItem('rag_model', model);
            showToast('Model saved: ' + model);
        }}

        function saveApiKey() {{
            const apiKey = document.getElementById('apiKey').value;
            sessionStorage.setItem('rag_api_key', apiKey);
            showToast('API key saved');
        }}

        // System Instruction Presets Management
        let systemPresets = [];
        let currentPresetId = null;

        function loadPresets() {{
            const stored = localStorage.getItem('rag_system_presets');
            if (stored) {{
                try {{
                    systemPresets = JSON.parse(stored);
                }} catch (e) {{
                    systemPresets = [];
                }}
            }} else {{
                // Add default Invoice Extractor preset
                systemPresets = [{{
                    id: 'invoice-extractor',
                    name: 'Invoice Extractor',
                    instruction: `You are a specialized AI assistant for extracting purchase invoice information from OCR text.

Your task is to analyze the provided text and extract the following information into a JSON object:

{{
  "supplier": "Company name of the supplier/vendor",
  "tax_id": "Tax ID / CIF / NIF of the supplier",
  "is_paid": false,
  "set_posting_time": 1,
  "posting_date": "YYYY-MM-DD format",
  "bill_no": "Invoice number",
  "bill_date": "YYYY-MM-DD format",
  "currency": "EUR or other currency code",
  "items": [
    {{
      "description": "Item description",
      "qty": 1,
      "rate": 0.00
    }}
  ],
  "tax_amount": 0.00
}}

Rules:
1. Return ONLY the JSON object, no additional text or explanations
2. Dates must be in YYYY-MM-DD format
3. All monetary values must be numbers (not strings)
4. If a field cannot be determined, use reasonable defaults
5. tax_amount should be the total VAT/IVA amount
6. is_paid should always be false (boolean)
7. set_posting_time should always be 1 (integer)
8. Extract all line items from the invoice into the items array`
                }}];
                localStorage.setItem('rag_system_presets', JSON.stringify(systemPresets));
            }}
            renderPresets();
            updatePresetSelector();
        }}

        function renderPresets() {{
            const list = document.getElementById('presetsList');
            if (systemPresets.length === 0) {{
                list.innerHTML = '<p style="text-align: center; color: var(--pibico-grey-dark); font-size: 0.85rem; margin: 12px 0;">No presets yet</p>';
                return;
            }}

            list.innerHTML = systemPresets.map(preset => `
                <div class="preset-item" onclick="viewPreset('${{preset.id}}')">
                    <span class="preset-name">${{preset.name}}</span>
                    <div class="preset-actions">
                        <button class="preset-action-btn" onclick="event.stopPropagation(); editPreset('${{preset.id}}')" title="Edit">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="preset-action-btn" onclick="event.stopPropagation(); deletePreset('${{preset.id}}')" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }}

        function updatePresetSelector() {{
            const selector = document.getElementById('presetSelector');
            const currentValue = selector.value;

            selector.innerHTML = '<option value="">Default (General Q&A)</option>' +
                systemPresets.map(preset =>
                    `<option value="${{preset.id}}">${{preset.name}}</option>`
                ).join('');

            // Restore selection if it still exists
            if (currentValue && systemPresets.find(p => p.id === currentValue)) {{
                selector.value = currentValue;
            }}
        }}

        function showPresetForm() {{
            document.getElementById('editPresetId').value = '';
            document.getElementById('presetName').value = '';
            document.getElementById('presetInstruction').value = '';
            document.getElementById('presetForm').style.display = 'flex';
        }}

        function cancelPresetForm() {{
            document.getElementById('presetForm').style.display = 'none';
        }}

        function viewPreset(id) {{
            const preset = systemPresets.find(p => p.id === id);
            if (!preset) return;

            document.getElementById('editPresetId').value = id;
            document.getElementById('presetName').value = preset.name;
            document.getElementById('presetInstruction').value = preset.instruction;
            document.getElementById('presetForm').style.display = 'flex';
        }}

        function editPreset(id) {{
            viewPreset(id);
        }}

        function savePreset() {{
            const id = document.getElementById('editPresetId').value;
            const name = document.getElementById('presetName').value.trim();
            const instruction = document.getElementById('presetInstruction').value.trim();

            if (!name || !instruction) {{
                showToast('Please fill in all fields', 'error');
                return;
            }}

            if (id) {{
                // Update existing
                const preset = systemPresets.find(p => p.id === id);
                if (preset) {{
                    preset.name = name;
                    preset.instruction = instruction;
                }}
            }} else {{
                // Create new
                const newPreset = {{
                    id: 'preset-' + Date.now(),
                    name: name,
                    instruction: instruction
                }};
                systemPresets.push(newPreset);
            }}

            localStorage.setItem('rag_system_presets', JSON.stringify(systemPresets));
            renderPresets();
            updatePresetSelector();
            cancelPresetForm();
            showToast('Preset saved successfully');
        }}

        function deletePreset(id) {{
            showConfirm(
                'Delete Preset',
                'Are you sure you want to delete this preset?',
                () => {{
                    systemPresets = systemPresets.filter(p => p.id !== id);
                    localStorage.setItem('rag_system_presets', JSON.stringify(systemPresets));
                    renderPresets();
                    updatePresetSelector();
                    showToast('Preset deleted');
                }}
            );
        }}

        function updatePresetIndicator() {{
            // Can be used to show visual indicator when preset is selected
        }}

        // Auto-refresh documents
        setInterval(loadDocuments, 10000);
    </script>
</body>
</html>
    """

    return HTMLResponse(content=html_content)
