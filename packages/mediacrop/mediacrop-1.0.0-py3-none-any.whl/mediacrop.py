#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, webbrowser, json, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

media_file = None
verbose = False

class CropHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if verbose:
            super().log_message(format, *args)

    def do_GET(self):
        path = urlparse(self.path).path
        ext = os.path.splitext(media_file)[1].lower()

        # Formats that are natively supported by most modern web browsers
        supported_image_exts = [
            ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg", ".ico", ".avif"
        ]
        
        supported_video_exts = [
            ".mp4", ".webm", ".ogv", ".mov" # MOV support can depend on the codec
        ]
        
        supported_audio_exts = [
            ".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".opus"
        ]

        if path == "/":
            # Add a cache buster to the media URL to prevent browser caching issues
            cache_buster = int(time.time())
            
            # Determine media type and create appropriate tag
            if ext in supported_image_exts:
                media_tag = f'<img id="media" src="/file?v={cache_buster}" onload="initializeCrop()" draggable="false" alt="Media file" />'
                media_type = "image"
            elif ext in supported_video_exts:
                media_tag = f'<video id="media" controls preload="metadata" src="/file?v={cache_buster}" onloadeddata="initializeCrop()" draggable="false"></video>'
                media_type = "video"
            elif ext in supported_audio_exts:
                media_tag = f'<audio id="media" controls preload="metadata" src="/file?v={cache_buster}" onloadeddata="initializeCrop()"></audio>'
                media_type = "audio"
            else:
                # Fallback for formats not previewable in the browser
                media_tag = '<div id="unsupported"><div class="unsupported-content"><div class="unsupported-icon">📁</div><div class="unsupported-text">Format not supported for preview</div><div class="unsupported-subtext">You can still set crop coordinates</div></div></div>'
                media_type = "unsupported"

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MediaCrop - Visual FFmpeg Crop Tool</title>
  <style>
    * {{ 
      box-sizing: border-box; 
      margin: 0; 
      padding: 0;
    }}
    
    :root {{
      --primary: #00ff41;
      --primary-hover: #00cc33;
      --primary-dark: #00aa2a;
      --bg-main: #0f0f0f;
      --bg-panel: #1a1a1a;
      --bg-control: #252525;
      --border: #333;
      --border-light: #444;
      --text-main: #ffffff;
      --text-muted: #aaa;
      --text-dim: #666;
      --shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
      --shadow-heavy: 0 8px 32px rgba(0, 0, 0, 0.6);
      --radius: 8px;
      --radius-large: 12px;
    }}
    
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: var(--bg-main);
      color: var(--text-main);
      user-select: none;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* Header Bar */
    .header-bar {{
      background: var(--bg-panel);
      border-bottom: 1px solid var(--border);
      padding: 12px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
      height: 60px;
    }}

    .app-title {{
      font-size: 18px;
      font-weight: 600;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .app-title::before {{
      content: '✂️';
      font-size: 20px;
    }}

    .file-info {{
      display: flex;
      align-items: center;
      gap: 15px;
      font-size: 13px;
      color: var(--text-muted);
    }}

    .file-detail {{
      display: flex;
      align-items: center;
      gap: 5px;
    }}

    .file-detail-label {{
      color: var(--text-dim);
    }}

    .file-detail-value {{
      color: var(--text-main);
      font-weight: 500;
    }}

    /* Main Content Area */
    .main-content {{
      display: flex;
      flex: 1;
      min-height: 0;
    }}

    /* Left Sidebar */
    .sidebar {{
      width: 280px;
      background: var(--bg-panel);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }}

    .sidebar-section {{
      border-bottom: 1px solid var(--border);
      padding: 20px;
    }}

    .sidebar-section:last-child {{
      border-bottom: none;
      flex: 1;
    }}

    .section-title {{
      font-size: 14px;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .section-title::before {{
      font-size: 16px;
    }}

    .section-title.aspect::before {{ content: '📐'; }}
    .section-title.tools::before {{ content: '🔧'; }}
    .section-title.info::before {{ content: '📊'; }}

    /* Form Controls */
    .form-group {{
      margin-bottom: 15px;
    }}

    .form-group:last-child {{
      margin-bottom: 0;
    }}

    .form-label {{
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-muted);
      margin-bottom: 6px;
    }}

    .form-select, .form-input, .form-button {{
      width: 100%;
      padding: 10px 12px;
      background: var(--bg-control);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      color: var(--text-main);
      font-size: 13px;
      transition: all 0.2s ease;
    }}

    .form-select:focus, .form-input:focus {{
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(0, 255, 65, 0.1);
    }}

    .form-input {{
      text-align: center;
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
    }}

    .custom-ratio {{
      display: none;
      grid-template-columns: 1fr auto 1fr;
      gap: 8px;
      align-items: center;
      margin-top: 8px;
    }}

    .custom-ratio.visible {{
      display: grid;
    }}

    .ratio-separator {{
      color: var(--text-muted);
      font-weight: 500;
    }}

    .form-button {{
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: #000;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: all 0.2s ease;
    }}

    .form-button:hover {{
      background: linear-gradient(135deg, var(--primary-hover), var(--primary));
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0, 255, 65, 0.3);
    }}

    .form-button:active {{
      transform: translateY(0);
    }}

    .button-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .button-grid .form-button {{
      font-size: 12px;
      padding: 8px 10px;
    }}

    /* Info Stats */
    .info-stats {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .info-stat {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
    }}

    .info-stat-label {{
      color: var(--text-muted);
    }}

    .info-stat-value {{
      color: var(--primary);
      font-weight: 600;
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
    }}

    /* Media Viewer */
    .media-viewer {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      position: relative;
      background: radial-gradient(circle at center, #1a1a1a 0%, var(--bg-main) 100%);
      min-height: 0;
    }}

    #container {{
      position: relative;
      border: 2px solid var(--border-light);
      border-radius: var(--radius-large);
      overflow: hidden;
      background: #000;
      box-shadow: var(--shadow-heavy);
      max-width: 100%;
      max-height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    img, video, audio {{
      max-width: 100%;
      max-height: 100%;
      display: block;
      user-select: none;
      -webkit-user-drag: none;
      -moz-user-drag: none;
      -o-user-drag: none;
      user-drag: none;
    }}

    #unsupported {{
      width: 500px;
      height: 300px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .unsupported-content {{
      text-align: center;
      padding: 40px;
    }}

    .unsupported-icon {{
      font-size: 48px;
      margin-bottom: 16px;
    }}

    .unsupported-text {{
      font-size: 18px;
      color: var(--text-main);
      margin-bottom: 8px;
      font-weight: 500;
    }}

    .unsupported-subtext {{
      font-size: 14px;
      color: var(--text-muted);
    }}

    /* Crop Box */
    .crop-box {{
      border: 2px dashed var(--primary);
      position: absolute;
      z-index: 50;
      box-sizing: border-box;
      min-width: 30px;
      min-height: 30px;
      cursor: grab;
      background: rgba(0, 255, 65, 0.08);
      box-shadow: 
        0 0 0 9999px rgba(0, 0, 0, 0.7),
        inset 0 0 0 1px rgba(0, 255, 65, 0.3);
      transition: box-shadow 0.2s ease;
    }}

    .crop-box:hover {{
      box-shadow: 
        0 0 0 9999px rgba(0, 0, 0, 0.75),
        inset 0 0 0 1px rgba(0, 255, 65, 0.5),
        0 0 20px rgba(0, 255, 65, 0.4);
    }}

    .crop-box.dragging {{
      cursor: grabbing;
      box-shadow: 
        0 0 0 9999px rgba(0, 0, 0, 0.8),
        inset 0 0 0 1px rgba(0, 255, 65, 0.7),
        0 0 25px rgba(0, 255, 65, 0.6);
    }}

    .crop-box.show-grid::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-image: 
        linear-gradient(to right, rgba(0, 255, 65, 0.3) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 255, 65, 0.3) 1px, transparent 1px);
      background-size: 33.33% 33.33%;
      pointer-events: none;
    }}

    /* Resize Handles */
    .resize-handle {{
      position: absolute;
      background: var(--primary);
      width: 12px;
      height: 12px;
      border: 2px solid #000;
      border-radius: 50%;
      z-index: 51;
      transition: all 0.2s ease;
      transform: translate(-50%, -50%);
    }}

    .resize-handle:hover {{
      background: #fff;
      transform: translate(-50%, -50%) scale(1.2);
      box-shadow: 0 0 8px rgba(0, 255, 65, 0.5);
    }}

    .resize-handle.nw {{ top: 0; left: 0; cursor: nw-resize; }}
    .resize-handle.ne {{ top: 0; right: 0; cursor: ne-resize; transform: translate(50%, -50%); }}
    .resize-handle.sw {{ bottom: 0; left: 0; cursor: sw-resize; transform: translate(-50%, 50%); }}
    .resize-handle.se {{ bottom: 0; right: 0; cursor: se-resize; transform: translate(50%, 50%); }}
    .resize-handle.n {{ top: 0; left: 50%; cursor: n-resize; }}
    .resize-handle.s {{ bottom: 0; left: 50%; cursor: s-resize; transform: translate(-50%, 50%); }}
    .resize-handle.w {{ left: 0; top: 50%; cursor: w-resize; }}
    .resize-handle.e {{ right: 0; top: 50%; cursor: e-resize; transform: translate(50%, -50%); }}

    /* Loading Indicator */
    .loading {{
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: var(--bg-panel);
      padding: 30px 40px;
      border-radius: var(--radius-large);
      box-shadow: var(--shadow-heavy);
      z-index: 1000;
      text-align: center;
    }}

    .spinner {{
      width: 32px;
      height: 32px;
      border: 3px solid var(--border);
      border-top: 3px solid var(--primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 15px;
    }}

    @keyframes spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}

    .loading-text {{
      font-size: 16px;
      font-weight: 500;
      color: var(--text-main);
    }}

    /* Help Modal */
    .help-modal {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      backdrop-filter: blur(4px);
    }}

    .help-content {{
      background: var(--bg-panel);
      border-radius: var(--radius-large);
      padding: 30px;
      max-width: 400px;
      box-shadow: var(--shadow-heavy);
      border: 1px solid var(--border);
    }}

    .help-title {{
      font-size: 20px;
      font-weight: 600;
      color: var(--primary);
      margin-bottom: 20px;
      text-align: center;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}

    .help-title::before {{
      content: '⌨️';
      font-size: 24px;
    }}

    .help-shortcuts {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 25px;
    }}

    .help-shortcut {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 14px;
    }}

    .help-shortcut-desc {{
      color: var(--text-muted);
    }}

    .help-shortcut-key {{
      background: var(--bg-control);
      color: var(--primary);
      padding: 4px 8px;
      border-radius: 4px;
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
      font-size: 12px;
      font-weight: 600;
    }}

    .help-close {{
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: #000;
      border: none;
      padding: 12px 24px;
      border-radius: var(--radius);
      font-weight: 600;
      cursor: pointer;
      width: 100%;
      transition: all 0.2s ease;
    }}

    .help-close:hover {{
      background: linear-gradient(135deg, var(--primary-hover), var(--primary));
      transform: translateY(-1px);
    }}

    /* Context Menu */
    .context-menu {{
      position: fixed;
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 8px 0;
      z-index: 300;
      display: none;
      box-shadow: var(--shadow);
      min-width: 180px;
    }}

    .context-item {{
      padding: 12px 16px;
      cursor: pointer;
      font-size: 14px;
      transition: background 0.2s ease;
      color: var(--text-main);
    }}

    .context-item:hover {{
      background: var(--bg-control);
      color: var(--primary);
    }}

    /* Notification */
    .notification {{
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: var(--bg-panel);
      color: var(--text-main);
      padding: 25px 35px;
      border-radius: var(--radius-large);
      z-index: 1000;
      box-shadow: var(--shadow-heavy);
      border: 1px solid var(--primary);
      text-align: center;
      max-width: 400px;
    }}

    .notification-title {{
      font-size: 18px;
      font-weight: 600;
      color: var(--primary);
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}

    .notification-title::before {{
      content: '✅';
      font-size: 20px;
    }}

    .notification-code {{
      background: var(--bg-control);
      padding: 12px 16px;
      border-radius: var(--radius);
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
      font-size: 14px;
      color: var(--primary);
      margin: 15px 0;
      border: 1px solid var(--border);
    }}

    .notification-subtitle {{
      font-size: 13px;
      color: var(--text-muted);
    }}

    /* Responsive Design */
    @media (max-width: 1024px) {{
      .sidebar {{
        width: 250px;
      }}
      
      #container {{
        max-width: calc(100vw - 270px);
      }}
    }}

    @media (max-width: 768px) {{
      .header-bar {{
        flex-direction: column;
        height: auto;
        padding: 12px 15px;
        gap: 10px;
        flex-shrink: 0;
      }}
      
      .file-info {{
        gap: 10px;
        font-size: 12px;
      }}
      
      .main-content {{
        flex-direction: column;
      }}
      
      .sidebar {{
        width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--border);
        flex-direction: row;
        overflow-x: auto;
        padding: 0;
        flex-shrink: 0;
        scrollbar-width: thin;
        scrollbar-color: var(--primary) var(--bg-control);
      }}

      .sidebar::-webkit-scrollbar {{
        height: 6px;
      }}
      .sidebar::-webkit-scrollbar-track {{
        background: var(--bg-control);
      }}
      .sidebar::-webkit-scrollbar-thumb {{
        background-color: var(--primary);
        border-radius: 6px;
      }}
      
      .sidebar-section {{
        min-width: 220px;
        border-right: 1px solid var(--border);
        border-bottom: none;
        flex-shrink: 0;
      }}
      
      .sidebar-section:last-child {{
        border-right: none;
      }}

      .media-viewer {{
        flex: 1;
        min-height: 0;
      }}
      
      #container {{
        max-width: 100%;
        max-height: 100%;
      }}
    }}

    /* Utilities */
    .smooth-transition {{
      transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .visually-hidden {{
      position: absolute;
      width: 1px;
      height: 1px;
      margin: -1px;
      padding: 0;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }}
  </style>
</head>
<body>
  <div class="loading" id="loadingIndicator">
    <div class="spinner"></div>
    <div class="loading-text">Loading media...</div>
  </div>

  <div class="header-bar">
    <div class="app-title">MediaCrop - Visual FFmpeg Crop Tool</div>
    <div class="file-info">
      <div class="file-detail">
        <span class="file-detail-label">Format:</span>
        <span class="file-detail-value">{ext.upper().replace('.', '')}</span>
      </div>
      <div class="file-detail">
        <span class="file-detail-label">Type:</span>
        <span class="file-detail-value">{media_type.title()}</span>
      </div>
      <div class="file-detail">
        <span class="file-detail-label">Size:</span>
        <span class="file-detail-value" id="fileSizeInfo">Loading...</span>
      </div>
    </div>
  </div>

  <div class="main-content">
    <div class="sidebar">
      <div class="sidebar-section">
        <div class="section-title aspect">Aspect Ratio</div>
        
        <div class="form-group">
          <label class="form-label" for="aspect">Preset</label>
          <select id="aspect" class="form-select">
            <option value="free">Free Form</option>
            <option value="1:1">1:1 (Square)</option>
            <option value="4:3">4:3 (Standard)</option>
            <option value="16:9">16:9 (Widescreen)</option>
            <option value="9:16">9:16 (Portrait)</option>
            <option value="3:2">3:2 (Photo)</option>
            <option value="5:4">5:4 (Large Format)</option>
            <option value="21:9">21:9 (Ultrawide)</option>
            <option value="2.35:1">2.35:1 (Cinemascope)</option>
            <option value="2.39:1">2.39:1 (Anamorphic)</option>
            <option value="custom">Custom Ratio</option>
          </select>
        </div>
        
        <div class="custom-ratio" id="customRatio">
          <input type="text" id="customW" class="form-input" value="16" placeholder="W">
          <div class="ratio-separator">:</div>
          <input type="text" id="customH" class="form-input" value="9" placeholder="H">
        </div>
      </div>

      <div class="sidebar-section">
        <div class="section-title tools">Quick Tools</div>
        
        <div class="form-group">
          <div class="button-grid">
            <button class="form-button" onclick="toggleGrid()">📐 Grid</button>
            <button class="form-button" onclick="centerCrop()">🎯 Center</button>
            <button class="form-button" onclick="resetCropSize()">🔄 Reset</button>
            <button class="form-button" onclick="toggleHelp()">❓ Help</button>
          </div>
        </div>
        
        <div class="form-group">
          <button class="form-button" onclick="saveCrop()" style="background: linear-gradient(135deg, #4CAF50, #45a049); font-size: 14px; padding: 12px;">
            💾 Save Coordinates
          </button>
        </div>
      </div>

      <div class="sidebar-section">
        <div class="section-title info">Crop Info</div>
        
        <div class="info-stats">
          <div class="info-stat">
            <span class="info-stat-label">Position:</span>
            <span class="info-stat-value" id="positionInfo">(0, 0)</span>
          </div>
          <div class="info-stat">
            <span class="info-stat-label">Size:</span>
            <span class="info-stat-value" id="sizeInfo">200×150</span>
          </div>
          <div class="info-stat">
            <span class="info-stat-label">Ratio:</span>
            <span class="info-stat-value" id="ratioInfo">4:3</span>
          </div>
        </div>
      </div>
    </div>

    <div class="media-viewer">
      <div id="container">
        {media_tag}
        <div id="crop" class="crop-box" style="left:50px;top:50px;width:200px;height:150px;" tabindex="0" role="img" aria-label="Crop selection area">
          <div class="resize-handle nw"></div>
          <div class="resize-handle ne"></div>
          <div class="resize-handle sw"></div>
          <div class="resize-handle se"></div>
          <div class="resize-handle n"></div>
          <div class="resize-handle s"></div>
          <div class="resize-handle w"></div>
          <div class="resize-handle e"></div>
        </div>
      </div>
    </div>
  </div>

  <div class="help-modal" id="helpModal">
    <div class="help-content">
      <div class="help-title">Keyboard Shortcuts</div>
      <div class="help-shortcuts">
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Move crop box</span>
          <span class="help-shortcut-key">Arrow Keys</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Fine adjustment</span>
          <span class="help-shortcut-key">Shift + Arrows</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Center crop box</span>
          <span class="help-shortcut-key">C</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Toggle grid</span>
          <span class="help-shortcut-key">G</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Save coordinates</span>
          <span class="help-shortcut-key">Enter</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Close help</span>
          <span class="help-shortcut-key">Esc</span>
        </div>
      </div>
      <button class="help-close" onclick="toggleHelp()">Got it!</button>
    </div>
  </div>

  <div class="context-menu" id="contextMenu">
    <div class="context-item" onclick="centerCrop()">🎯 Center Crop Box</div>
    <div class="context-item" onclick="toggleGrid()">📐 Toggle Grid</div>
    <div class="context-item" onclick="resetCropSize()">🔄 Reset Size</div>
    <div class="context-item" onclick="saveCrop()">💾 Save Coordinates</div>
  </div>

  <script>
    // Enhanced global state management
    const elements = {{
      media: document.getElementById("media"),
      container: document.getElementById("container"),
      crop: document.getElementById("crop"),
      aspectSelect: document.getElementById("aspect"),
      customRatio: document.getElementById("customRatio"),
      customW: document.getElementById("customW"),
      customH: document.getElementById("customH"),
      positionInfo: document.getElementById("positionInfo"),
      sizeInfo: document.getElementById("sizeInfo"),
      ratioInfo: document.getElementById("ratioInfo"),
      fileSizeInfo: document.getElementById("fileSizeInfo"),
      loadingIndicator: document.getElementById("loadingIndicator"),
      helpModal: document.getElementById("helpModal"),
      contextMenu: document.getElementById("contextMenu")
    }};

    // Enhanced state management
    const state = {{
      // Movement state
      isDragging: false,
      isResizing: false,
      resizeDirection: '',
      
      // Position tracking
      startMouseX: 0,
      startMouseY: 0,
      startCropLeft: 0,
      startCropTop: 0,
      startCropWidth: 0,
      startCropHeight: 0,
      
      // Dimensions
      mediaWidth: 0,
      mediaHeight: 0,
      naturalWidth: 0,
      naturalHeight: 0,
      
      // Aspect ratio
      aspectMode: "free",
      aspectRatio: null,
      
      // UI state
      isInitialized: false,
      showGrid: false,
      isHelpVisible: false,
      
      // Performance
      lastUpdate: 0,
      animationFrame: null,
      
      // File info
      mediaType: "{media_type}",
      fileExtension: "{ext}"
    }};

    // Utility functions
    const utils = {{
      // Debounce function for performance
      debounce(func, wait) {{
        let timeout;
        return function executedFunction(...args) {{
          const later = () => {{
            clearTimeout(timeout);
            func(...args);
          }};
          clearTimeout(timeout);
          timeout = setTimeout(later, wait);
        }};
      }},
      
      // Throttle function for smooth animations
      throttle(func, limit) {{
        let inThrottle;
        return function(...args) {{
          if (!inThrottle) {{
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
          }}
        }};
      }},
      
      // Get event coordinates (mouse/touch)
      getEventCoords(e) {{
        if (e.type.startsWith('touch')) {{
          return {{
            x: e.touches[0].clientX,
            y: e.touches[0].clientY
          }};
        }}
        return {{
          x: e.clientX,
          y: e.clientY
        }};
      }},
      
      // Calculate greatest common divisor for aspect ratio
      gcd(a, b) {{
        return b === 0 ? a : this.gcd(b, a % b);
      }},
      
      // Format file size
      formatFileSize(bytes) {{
        const sizes = ['B', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
      }},
      
      // Smooth interpolation
      lerp(start, end, factor) {{
        return start + (end - start) * factor;
      }}
    }};

    // Enhanced initialization
    function initializeCrop() {{
      setTimeout(() => {{
        updateMediaDimensions();
        updateFileInfo();
        positionCropBox();
        updateCropInfo();
        state.isInitialized = true;
        hideLoading();
        
        // Initial focus for accessibility
        elements.crop.focus();
      }}, 150);
    }}

    function hideLoading() {{
      elements.loadingIndicator.style.display = 'none';
    }}

    // Enhanced media dimensions tracking
    function updateMediaDimensions() {{
      if (!elements.media) {{
        // For unsupported formats
        if (state.mediaType === 'unsupported') {{
          state.mediaWidth = 500;
          state.mediaHeight = 300;
          state.naturalWidth = 500;
          state.naturalHeight = 300;
        }}
        return;
      }}
      
      const mediaRect = elements.media.getBoundingClientRect();
      state.mediaWidth = mediaRect.width;
      state.mediaHeight = mediaRect.height;
      
      // Get natural dimensions for scaling calculations
      if (elements.media.tagName === 'IMG') {{
        state.naturalWidth = elements.media.naturalWidth || state.mediaWidth;
        state.naturalHeight = elements.media.naturalHeight || state.mediaHeight;
      }} else if (elements.media.tagName === 'VIDEO') {{
        state.naturalWidth = elements.media.videoWidth || state.mediaWidth;
        state.naturalHeight = elements.media.videoHeight || state.mediaHeight;
      }} else {{
        // For audio or unsupported, use container dimensions
        state.naturalWidth = state.mediaWidth;
        state.naturalHeight = state.mediaHeight;
      }}
    }}

    // File information display
    function updateFileInfo() {{
      // Get file size via HTTP HEAD request
      fetch('/file', {{ method: 'HEAD' }})
        .then(response => {{
          const contentLength = response.headers.get('content-length');
          if (contentLength) {{
            elements.fileSizeInfo.textContent = utils.formatFileSize(parseInt(contentLength));
          }}
        }})
        .catch(() => {{
          elements.fileSizeInfo.textContent = 'Unknown';
        }});
    }}

    // Enhanced crop box positioning
    function positionCropBox() {{
      if (state.mediaWidth === 0 || state.mediaHeight === 0) return;
      
      const cropWidth = Math.min(200, state.mediaWidth * 0.4);
      const cropHeight = Math.min(150, state.mediaHeight * 0.3);
      const centerX = Math.max(0, (state.mediaWidth - cropWidth) / 2);
      const centerY = Math.max(0, (state.mediaHeight - cropHeight) / 2);
      
      setCropDimensions(centerX, centerY, cropWidth, cropHeight);
    }}

    // Enhanced dimension setting with smooth transitions - FIXED: No padding for edge access
    function setCropDimensions(left, top, width, height, smooth = false) {{
      // Ensure minimum dimensions
      width = Math.max(30, width);
      height = Math.max(30, height);
      
      // Constrain to media bounds without padding - crop box can reach exact edges
      left = Math.max(0, Math.min(left, state.mediaWidth - width));
      top = Math.max(0, Math.min(top, state.mediaHeight - height));
      width = Math.min(width, state.mediaWidth - left);
      height = Math.min(height, state.mediaHeight - top);
      
      // Apply dimensions with optional smooth transition
      const cropStyle = elements.crop.style;
      
      if (smooth && state.animationFrame) {{
        cancelAnimationFrame(state.animationFrame);
      }}
      
      if (smooth) {{
        elements.crop.classList.add('smooth-transition');
        setTimeout(() => elements.crop.classList.remove('smooth-transition'), 200);
      }}
      
      cropStyle.left = Math.round(left) + 'px';
      cropStyle.top = Math.round(top) + 'px';
      cropStyle.width = Math.round(width) + 'px';
      cropStyle.height = Math.round(height) + 'px';
    }}

    // Enhanced aspect ratio handling
    function applyAspectRatio(width, height, maintainWidth = true) {{
      if (state.aspectMode === "free" || !state.aspectRatio) {{
        return {{ width, height }};
      }}
      
      if (maintainWidth) {{
        height = Math.round(width / state.aspectRatio);
      }} else {{
        width = Math.round(height * state.aspectRatio);
      }}
      
      return {{ width, height }};
    }}

    // Enhanced info display with animations
    function updateCropInfo() {{
      const left = parseInt(elements.crop.style.left) || 0;
      const top = parseInt(elements.crop.style.top) || 0;
      const width = parseInt(elements.crop.style.width) || 0;
      const height = parseInt(elements.crop.style.height) || 0;
      
      // Update position and size
      elements.positionInfo.textContent = `(${{left}}, ${{top}})`;
      elements.sizeInfo.textContent = `${{width}}×${{height}}`;
      
      // Calculate and display aspect ratio
      if (width && height) {{
        const gcd = utils.gcd(width, height);
        const ratioW = width / gcd;
        const ratioH = height / gcd;
        
        // Simplify common ratios
        let ratioText = `${{ratioW}}:${{ratioH}}`;
        if (ratioW === ratioH) ratioText = "1:1";
        else if (Math.abs(ratioW/ratioH - 16/9) < 0.1) ratioText = "16:9";
        else if (Math.abs(ratioW/ratioH - 4/3) < 0.1) ratioText = "4:3";
        else if (Math.abs(ratioW/ratioH - 3/2) < 0.1) ratioText = "3:2";
        
        elements.ratioInfo.textContent = ratioText;
      }}
    }}

    // Enhanced dragging with smooth movement
    const dragHandlers = {{
      start(e) {{
        if (e.target.classList.contains('resize-handle')) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        const coords = utils.getEventCoords(e);
        state.isDragging = true;
        state.startMouseX = coords.x;
        state.startMouseY = coords.y;
        state.startCropLeft = parseInt(elements.crop.style.left) || 0;
        state.startCropTop = parseInt(elements.crop.style.top) || 0;
        
        elements.crop.classList.add('dragging');
        
        // Add event listeners
        document.addEventListener('mousemove', dragHandlers.move, {{ passive: false }});
        document.addEventListener('mouseup', dragHandlers.stop);
        document.addEventListener('touchmove', dragHandlers.move, {{ passive: false }});
        document.addEventListener('touchend', dragHandlers.stop);
      }},
      
      move: utils.throttle((e) => {{
        if (!state.isDragging) return;
        
        e.preventDefault();
        const coords = utils.getEventCoords(e);
        const deltaX = coords.x - state.startMouseX;
        const deltaY = coords.y - state.startMouseY;
        
        let newLeft = state.startCropLeft + deltaX;
        let newTop = state.startCropTop + deltaY;
        
        const currentWidth = parseInt(elements.crop.style.width) || 0;
        const currentHeight = parseInt(elements.crop.style.height) || 0;
        
        setCropDimensions(newLeft, newTop, currentWidth, currentHeight);
        updateCropInfo();
      }}, 16), // 60fps throttling
      
      stop() {{
        state.isDragging = false;
        elements.crop.classList.remove('dragging');
        
        // Remove event listeners
        document.removeEventListener('mousemove', dragHandlers.move);
        document.removeEventListener('mouseup', dragHandlers.stop);
        document.removeEventListener('touchmove', dragHandlers.move);
        document.removeEventListener('touchend', dragHandlers.stop);
      }}
    }};

    // Enhanced resizing with smooth aspect ratio handling
    const resizeHandlers = {{
      start(e) {{
        e.preventDefault();
        e.stopPropagation();
        
        const coords = utils.getEventCoords(e);
        state.isResizing = true;
        state.resizeDirection = Array.from(e.target.classList).find(cls => cls !== 'resize-handle');
        state.startMouseX = coords.x;
        state.startMouseY = coords.y;
        state.startCropLeft = parseInt(elements.crop.style.left) || 0;
        state.startCropTop = parseInt(elements.crop.style.top) || 0;
        state.startCropWidth = parseInt(elements.crop.style.width) || 0;
        state.startCropHeight = parseInt(elements.crop.style.height) || 0;
        
        document.addEventListener('mousemove', resizeHandlers.move, {{ passive: false }});
        document.addEventListener('mouseup', resizeHandlers.stop);
        document.addEventListener('touchmove', resizeHandlers.move, {{ passive: false }});
        document.addEventListener('touchend', resizeHandlers.stop);
      }},
      
      move: utils.throttle((e) => {{
        if (!state.isResizing) return;
        
        e.preventDefault();
        const coords = utils.getEventCoords(e);
        const deltaX = coords.x - state.startMouseX;
        const deltaY = coords.y - state.startMouseY;
        
        let left = state.startCropLeft;
        let top = state.startCropTop;
        let width = state.startCropWidth;
        let height = state.startCropHeight;
        
        // Apply resize based on direction
        switch (state.resizeDirection) {{
          case 'se': width += deltaX; height += deltaY; break;
          case 'sw': left += deltaX; width -= deltaX; height += deltaY; break;
          case 'ne': width += deltaX; top += deltaY; height -= deltaY; break;
          case 'nw': left += deltaX; top += deltaY; width -= deltaX; height -= deltaY; break;
          case 'e': width += deltaX; break;
          case 'w': left += deltaX; width -= deltaX; break;
          case 's': height += deltaY; break;
          case 'n': top += deltaY; height -= deltaY; break;
        }}
        
        // Apply aspect ratio constraints
        if (state.aspectRatio && state.aspectMode !== "free") {{
          const isWidthPrimary = ['e', 'w', 'ne', 'nw', 'se', 'sw'].includes(state.resizeDirection);
          const adjusted = applyAspectRatio(width, height, isWidthPrimary);
          width = adjusted.width;
          height = adjusted.height;
        }}
        
        setCropDimensions(left, top, width, height);
        updateCropInfo();
      }}, 16),
      
      stop() {{
        state.isResizing = false;
        
        document.removeEventListener('mousemove', resizeHandlers.move);
        document.removeEventListener('mouseup', resizeHandlers.stop);
        document.removeEventListener('touchmove', resizeHandlers.move);
        document.removeEventListener('touchend', resizeHandlers.stop);
      }}
    }};

    // Keyboard navigation support
    function handleKeyboard(e) {{
      if (state.isHelpVisible && e.key === 'Escape') {{
        toggleHelp();
        return;
      }}
      
      if (state.isHelpVisible) return;
      
      const step = e.shiftKey ? 1 : 10; // Fine adjustment with Shift
      const currentLeft = parseInt(elements.crop.style.left) || 0;
      const currentTop = parseInt(elements.crop.style.top) || 0;
      const currentWidth = parseInt(elements.crop.style.width) || 0;
      const currentHeight = parseInt(elements.crop.style.height) || 0;
      
      let newLeft = currentLeft;
      let newTop = currentTop;
      
      switch (e.key) {{
        case 'ArrowLeft':
          e.preventDefault();
          newLeft = Math.max(0, currentLeft - step);
          break;
        case 'ArrowRight':
          e.preventDefault();
          newLeft = Math.min(state.mediaWidth - currentWidth, currentLeft + step);
          break;
        case 'ArrowUp':
          e.preventDefault();
          newTop = Math.max(0, currentTop - step);
          break;
        case 'ArrowDown':
          e.preventDefault();
          newTop = Math.min(state.mediaHeight - currentHeight, currentTop + step);
          break;
        case 'c':
        case 'C':
          e.preventDefault();
          centerCrop();
          break;
        case 'g':
        case 'G':
          e.preventDefault();
          toggleGrid();
          break;
        case 'Enter':
          e.preventDefault();
          saveCrop();
          break;
        default:
          return;
      }}
      
      if (newLeft !== currentLeft || newTop !== currentTop) {{
        setCropDimensions(newLeft, newTop, currentWidth, currentHeight, true);
        updateCropInfo();
      }}
    }}

    // UI Enhancement functions
    function toggleGrid() {{
      state.showGrid = !state.showGrid;
      elements.crop.classList.toggle('show-grid', state.showGrid);
    }}

    function centerCrop() {{
      const currentWidth = parseInt(elements.crop.style.width) || 0;
      const currentHeight = parseInt(elements.crop.style.height) || 0;
      const centerX = (state.mediaWidth - currentWidth) / 2;
      const centerY = (state.mediaHeight - currentHeight) / 2;
      
      setCropDimensions(centerX, centerY, currentWidth, currentHeight, true);
      updateCropInfo();
    }}

    function resetCropSize() {{
      positionCropBox();
      updateCropInfo();
    }}

    function toggleHelp() {{
      state.isHelpVisible = !state.isHelpVisible;
      elements.helpModal.style.display = state.isHelpVisible ? 'flex' : 'none';
    }}

    // Context menu handling
    function showContextMenu(e) {{
      e.preventDefault();
      const menu = elements.contextMenu;
      menu.style.display = 'block';
      menu.style.left = e.clientX + 'px';
      menu.style.top = e.clientY + 'px';
      
      // Hide menu when clicking elsewhere
      document.addEventListener('click', hideContextMenu, {{ once: true }});
    }}

    function hideContextMenu() {{
      if (elements.contextMenu) {{
        elements.contextMenu.style.display = 'none';
      }}
    }}

    // Enhanced aspect ratio handling
    function handleAspectRatioChange(e) {{
      state.aspectMode = e.target.value;
      
      if (state.aspectMode === "custom") {{
        elements.customRatio.classList.add('visible');
        updateCustomAspectRatio();
      }} else {{
        elements.customRatio.classList.remove('visible');
        
        if (state.aspectMode === "free") {{
          state.aspectRatio = null;
        }} else {{
          const parts = state.aspectMode.split(":");
          state.aspectRatio = parseFloat(parts[0]) / parseFloat(parts[1]);
          applyCurrentAspectRatio();
        }}
      }}
    }}

    function updateCustomAspectRatio() {{
      const w = parseFloat(elements.customW.value) || 1;
      const h = parseFloat(elements.customH.value) || 1;
      state.aspectRatio = w / h;
      if (state.aspectMode === "custom") {{
        applyCurrentAspectRatio();
      }}
    }}

    function applyCurrentAspectRatio() {{
      if (!state.aspectRatio || !state.isInitialized) return;
      
      const currentLeft = parseInt(elements.crop.style.left) || 0;
      const currentTop = parseInt(elements.crop.style.top) || 0;
      const currentWidth = parseInt(elements.crop.style.width) || 0;
      const newHeight = Math.round(currentWidth / state.aspectRatio);
      
      setCropDimensions(currentLeft, currentTop, currentWidth, newHeight, true);
      updateCropInfo();
    }}

    // Enhanced save function with better scaling
    function saveCrop() {{
      updateMediaDimensions();
      
      const left = parseInt(elements.crop.style.left) || 0;
      const top = parseInt(elements.crop.style.top) || 0;
      const width = parseInt(elements.crop.style.width) || 0;
      const height = parseInt(elements.crop.style.height) || 0;
      
      // Calculate precise scaling factors
      let scaleX = 1, scaleY = 1;
      
      if (state.naturalWidth && state.naturalHeight && state.mediaWidth && state.mediaHeight) {{
        scaleX = state.naturalWidth / state.mediaWidth;
        scaleY = state.naturalHeight / state.mediaHeight;
      }}
      
      const finalX = Math.round(left * scaleX);
      const finalY = Math.round(top * scaleY);
      const finalW = Math.round(width * scaleX);
      const finalH = Math.round(height * scaleY);
      
      // Enhanced feedback
      fetch("/save", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ 
          x: finalX, 
          y: finalY, 
          w: finalW, 
          h: finalH,
          scaleX: scaleX,
          scaleY: scaleY,
          mediaType: state.mediaType
        }})
      }})
      .then(response => {{
        if (response.ok) {{
          // Create a more informative notification
          const notification = document.createElement('div');
          notification.className = 'notification';
          notification.innerHTML = `
            <div class="notification-title">Crop Saved Successfully!</div>
            <div class="notification-code">crop=${{finalW}}:${{finalH}}:${{finalX}}:${{finalY}}</div>
            <div class="notification-subtitle">Check your terminal for the output</div>
          `;
          
          document.body.appendChild(notification);
          setTimeout(() => document.body.removeChild(notification), 3000);
        }} else {{
          alert("Error: Could not save crop parameters");
        }}
      }})
      .catch(error => {{
        alert("Network Error: " + error.message);
      }});
    }}

    // Window resize handler with debouncing
    const handleWindowResize = utils.debounce(() => {{
      updateMediaDimensions();
      updateCropInfo();
      
      // Adjust crop box if it's outside bounds
      const left = parseInt(elements.crop.style.left) || 0;
      const top = parseInt(elements.crop.style.top) || 0;
      const width = parseInt(elements.crop.style.width) || 0;
      const height = parseInt(elements.crop.style.height) || 0;
      
      if (left + width > state.mediaWidth || top + height > state.mediaHeight) {{
        setCropDimensions(left, top, width, height, true);
      }}
    }}, 300);

    // Event listener setup
    function setupEventListeners() {{
      // Crop box interactions
      elements.crop.addEventListener("mousedown", dragHandlers.start);
      elements.crop.addEventListener("touchstart", dragHandlers.start, {{ passive: false }});
      elements.crop.addEventListener("contextmenu", showContextMenu);
      elements.crop.addEventListener("dblclick", centerCrop);
      
      // Resize handles
      document.querySelectorAll('.resize-handle').forEach(handle => {{
        handle.addEventListener("mousedown", resizeHandlers.start);
        handle.addEventListener("touchstart", resizeHandlers.start, {{ passive: false }});
      }});
      
      // Aspect ratio controls
      elements.aspectSelect.addEventListener("change", handleAspectRatioChange);
      elements.customW.addEventListener("input", utils.debounce(updateCustomAspectRatio, 300));
      elements.customH.addEventListener("input", utils.debounce(updateCustomAspectRatio, 300));
      
      // Keyboard navigation
      document.addEventListener("keydown", handleKeyboard);
      
      // Window resize
      window.addEventListener("resize", handleWindowResize);
      
      // Prevent unwanted selections and context menus
      document.addEventListener("selectstart", e => {{
        if (state.isDragging || state.isResizing) e.preventDefault();
      }});
      
      // Click outside to hide context menu
      document.addEventListener("click", (e) => {{
        if (elements.contextMenu && !elements.contextMenu.contains(e.target)) {{
          hideContextMenu();
        }}
      }});

      // Close help modal when clicking outside
      elements.helpModal.addEventListener('click', (e) => {{
        if (e.target === elements.helpModal) {{
          toggleHelp();
        }}
      }});
    }}

    // Initialize everything when DOM is ready
    document.addEventListener("DOMContentLoaded", function() {{
      setupEventListeners();
      
      // Initialize when media is ready
      if (elements.media) {{
        if (elements.media.complete || elements.media.readyState >= 2) {{
          initializeCrop();
        }} else {{
          // For video/audio that need time to load
          elements.media.addEventListener('loadedmetadata', initializeCrop);
          elements.media.addEventListener('canplay', initializeCrop);
        }}
      }} else {{
        // For unsupported formats, still initialize UI
        setTimeout(() => {{
          initializeCrop();
        }}, 100);
      }}
    }});
  </script>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        elif path == "/file":
            try:
                with open(media_file, "rb") as f:
                    data = f.read()
                self.send_response(200)
                
                # Comprehensive MIME type mapping
                mime_types = {
                    # Images - Common
                    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                    '.png': 'image/png', '.webp': 'image/webp',
                    '.gif': 'image/gif', '.bmp': 'image/bmp',
                    '.tiff': 'image/tiff', '.tif': 'image/tiff',
                    
                    # Images - Modern
                    '.avif': 'image/avif', '.heic': 'image/heic', 
                    '.heif': 'image/heif', '.jxl': 'image/jxl',
                    
                    # Images - Vector/Other
                    '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
                    
                    # Videos - Common
                    '.mp4': 'video/mp4', '.webm': 'video/webm',
                    '.mov': 'video/quicktime', '.ogv': 'video/ogg',
                    
                    # Audio - Common
                    '.mp3': 'audio/mpeg', '.wav': 'audio/wav',
                    '.ogg': 'audio/ogg', '.m4a': 'audio/mp4',
                    '.flac': 'audio/flac', '.aac': 'audio/aac',
                    '.opus': 'audio/opus'
                }
                
                mime_type = mime_types.get(ext, 'application/octet-stream')
                
                # Enhanced headers
                self.send_header("Content-type", mime_type)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Cache-Control", "public, max-age=3600")
                self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(media_file)))
                
                # CORS for cross-origin requests
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Range")
                
                self.end_headers()
                self.wfile.write(data)
                
            except FileNotFoundError:
                self.send_error(404, f"File not found: {media_file}")
            except PermissionError:
                self.send_error(403, f"Permission denied: {media_file}")
            except Exception as e:
                self.send_error(500, f"File error: {str(e)}")
                
        else:
            self.send_error(404, "Not Found")

    def do_HEAD(self):
        """Handle HEAD requests for file size information"""
        if urlparse(self.path).path == "/file":
            try:
                file_size = os.path.getsize(media_file)
                self.send_response(200)
                self.send_header("Content-Length", str(file_size))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
            except Exception as e:
                self.send_error(404, str(e))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/save":
            try:
                length = int(self.headers.get("Content-Length", 0))
                if length > 10000:  # Prevent large payloads
                    self.send_error(413, "Payload too large")
                    return
                    
                body = self.rfile.read(length)
                data = json.loads(body.decode("utf-8"))
                
                # Validate crop parameters
                required_fields = ['w', 'h', 'x', 'y']
                for field in required_fields:
                    if field not in data or not isinstance(data[field], (int, float)) or data[field] < 0:
                        self.send_error(400, f"Invalid {field} parameter")
                        return
                
                # Clean terminal output
                print(f'crop={int(data["w"])}:{int(data["h"])}:{int(data["x"])}:{int(data["y"])}')
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "Crop parameters saved successfully",
                    "crop_filter": f"crop={int(data['w'])}:{int(data['h'])}:{int(data['x'])}:{int(data['y'])}",
                    "timestamp": self.date_time_string()
                }).encode("utf-8"))
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON data")
            except KeyError as e:
                self.send_error(400, f"Missing required field: {e}")
            except Exception as e:
                self.send_error(500, f"Server error: {str(e)}")
        else:
            self.send_error(404, "Not Found")

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Range")
        self.end_headers()


def get_file_info(filepath):
    """Get comprehensive file information"""
    try:
        stat = os.stat(filepath)
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'name': os.path.basename(filepath),
            'extension': os.path.splitext(filepath)[1].lower(),
            'absolute_path': os.path.abspath(filepath)
        }
    except Exception:
        return None

def print_help():
    """Prints the detailed help message for the script."""
    print("\nMediaCrop - FFmpeg Crop Tool")
    print("=" * 50)
    print("A web-based visual tool to get FFmpeg crop coordinates for media files.")
    print("\nUsage:")
    print("""  mediacrop <media_file>
                        Path to the video or image.""")
    print("\nOptions:")
    print("  -h, --help            Show this help message and exit.")
    print("  -v, --verbose         Show detailed server logs.")
    print("  -p N, --port N        Use a specific port for the server (default: 8000).")
    print("\nSupported Preview Formats:")
    print("  Images : JPG, PNG, WEBP, AVIF, GIF, BMP, SVG, ICO")
    print("  Videos : MP4, WEBM, MOV, OGV")
    print("  Audio  : MP3, WAV, FLAC, OGG, M4A, AAC, OPUS")
    print(f"\nAuthor Info:")
    print(f"  Name   : Mallik Mohammad Musaddiq")
    print(f"  GitHub : https://github.com/mallikmusaddiq1/MediaCrop")
    print(f"  Email  : mallikmusaddiq1@gmail.com")


def main():
    # Check for help flag first
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        sys.exit(0)

    # Enhanced command line handling
    if len(sys.argv) < 2 or sys.argv[1].startswith('-'):
        print("Error: No media file specified.")
        print("Usage: python cropper.py <media_file> [options]")
        print("Use 'python cropper.py --help' for more information.")
        sys.exit(1)

    global media_file, verbose
    media_file = os.path.abspath(sys.argv[1])
    if not os.path.exists(media_file):
        print(f"Error: File not found - {media_file}")
        sys.exit(1)

    if not os.access(media_file, os.R_OK):
        print(f"Error: Permission denied - {media_file}")
        sys.exit(1)

    # Parse arguments
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    port = 8000
    
    port_arg = None
    if "--port" in sys.argv:
        port_arg = "--port"
    elif "-p" in sys.argv:
        port_arg = "-p"

    if port_arg:
        try:
            port_index = sys.argv.index(port_arg) + 1
            if port_index < len(sys.argv):
                port = int(sys.argv[port_index])
                if not (1024 <= port <= 65535):
                    raise ValueError("Port must be between 1024 and 65535")
        except (ValueError, IndexError):
            print("Error: Invalid port number provided.")
            sys.exit(1)

    # Get file information
    file_info = get_file_info(media_file)
    if file_info:
        file_size_mb = file_info['size'] / (1024 * 1024)
        print(f"File   : {file_info['name']}")
        print(f"Size   : {file_size_mb:.2f} MB")
        print(f"Format : {file_info['extension'].upper().replace('.', '')}")
    
    # Find available port
    original_port = port
    for attempt in range(10):
        try:
            server = HTTPServer(("127.0.0.1", port), CropHandler)
            break
        except OSError as e:
            if attempt == 0 and port != original_port:
                print(f"Port {original_port} busy, trying {port}")
            port += 1
    else:
        print("Error: Could not find available port")
        sys.exit(1)
    
    url = f"http://127.0.0.1:{port}"
    
    try:
        if not verbose:
            print(f"Server : {url}")
            print(f"Open {url} in browser...")
            print()
            print("Tips:")
            print("   • Drag crop box to move anywhere")
            print("   • Use arrow keys for precision") 
            print("   • Press 'G' for grid overlay")
            print("   • Press 'C' to center crop")
            print("   • Right-click for more options")
            print()
            print("Click 'Save Coordinates' when ready")
            print("Press Ctrl+C to stop server")
            print("-" * 50)
        
        # Open browser
        webbrowser.open(url)
        
        # Start server
        print(f"Server running on port {port}")
        print(f"Open http://127.0.0.1:{port} in browser")
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.server_close()
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        server.server_close()
        sys.exit(1)


if __name__ == "__main__":
    main()
