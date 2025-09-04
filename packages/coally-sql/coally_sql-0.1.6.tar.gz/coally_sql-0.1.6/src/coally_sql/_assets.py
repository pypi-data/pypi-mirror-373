from __future__ import annotations

def shared_css(opts) -> str:
    return f"""
    <style>
      .drop-wrap {{ width:100%; }}
      #drop-area {{
        border: 2px dashed #bbb; padding: 20px; text-align: center;
        border-radius: 12px; background:#fafafa; transition:.2s;
        height: 26vh; min-height: {opts.drop_zone_min_h}px; max-height: {opts.drop_zone_max_h}px;
        display:flex; align-items:center; justify-content:center;
        font:600 15px ui-sans-serif;
      }}
      #drop-area.dragover {{ border-color:#4285F4; background:#f3f8ff; color:#2b5ebc; }}
      #drop-area.disabled {{ opacity:.55; filter:grayscale(0.15); pointer-events:none; user-select:none; }}

      #loading-block {{ display:none; text-align:center; }}
      #loading-text {{ font:600 13px ui-sans-serif; margin:6px 0 4px; }}
      .bar {{ width:100%; max-width:{opts.progress_bar_max_w}px; height:10px; background:#eee; border-radius:6px; overflow:hidden; margin:0 auto; }}
      .bar > div {{ height:100%; width:0%; background:linear-gradient(90deg,#1a73e8,#4e9af9); }}
      #file-meta {{ margin-top:10px; font:13px ui-sans-serif; }}

      #upload-fallback {{ display:none; margin-top:10px; }}
      #upload-fallback .msg {{ font:600 13px ui-sans-serif; color:#b00020; margin-bottom:8px; }}
      #upload-fallback .row {{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; }}
      #file-input {{ font:600 12px ui-sans-serif; }}
      .btn {{ display:inline-flex; align-items:center; gap:8px; background:#1a73e8; color:#fff; border:none; border-radius:10px; padding:9px 14px; font:600 13px ui-sans-serif; cursor:pointer }}
      .btn:disabled{{ opacity:.5; cursor:not-allowed }}

      .card {{ border:1px solid #e8e8e8; border-radius:12px; padding:12px; box-shadow:0 1px 2px rgba(0,0,0,.02); background:#fff; }}
      .row {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
      .muted {{ color:#777 }}

      #sql-box {{ display:none; margin-top:14px; position:relative; }}
      #result-title {{ margin-top:10px; font:600 13px ui-sans-serif; }}
      #result {{ overflow:auto; border:1px solid #eee; border-radius:10px; padding:8px; max-height:40vh; background:#fff; }}

      #editor-host {{ margin-top: 12px; }}
      .CodeMirror {{
        background:#fff;
        border:1px solid #e8e8e8;
        border-radius:10px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
        font-size: {opts.editor_font_size_px}px;
        line-height: {opts.editor_line_height};
        padding: 8px 12px;
        margin-top: 6px;
      }}
      .CodeMirror pre {{ padding-left: 4px; }}
      .CodeMirror-gutters {{ background:#fff; border-right: 1px solid #eee; }}
    </style>
    """

def cm_includes() -> str:
    return """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/codemirror.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/mode/sql/sql.min.js"></script>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/dialog/dialog.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/hint/show-hint.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/comment/comment.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/edit/matchbrackets.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/search/search.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/search/searchcursor.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/dialog/dialog.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/selection/active-line.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/hint/show-hint.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/hint/sql-hint.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/keymap/sublime.min.js"></script>
    """

def editor_boot_js() -> str:
    return """
    <script>
    (function(){
      function ensureEditor(){
        if(!window.sqlEditor){
          var ta = document.getElementById('sql-editor');
          if (ta) {
            window.sqlEditor = CodeMirror.fromTextArea(ta, {
              mode: "text/x-sql",
              theme: "default",
              lineNumbers: true,
              indentWithTabs: false,
              indentUnit: 2,
              smartIndent: true,
              lineWrapping: true,
              autofocus: false,
              viewportMargin: Infinity,
              keyMap: "sublime",
              styleActiveLine: true,
              matchBrackets: true,
              extraKeys: {
                "Ctrl-Enter": function(){ triggerRun(); },
                "Cmd-Enter":  function(){ triggerRun(); },
                "Ctrl-/":     "toggleComment",
                "Cmd-/":      "toggleComment",
                "Shift-Ctrl-/": "blockComment",
                "Shift-Cmd-/":  "blockComment",
                "Tab":        "indentMore",
                "Shift-Tab":  "indentLess",
                "Ctrl-Space": "autocomplete",
                "Cmd-Space":  "autocomplete"
              }
            });
          }
        }
      }

      function triggerRun(){
        google.colab.kernel.invokeFunction('ally.run_sql', [], {})
          .catch(function(err){ console.error(err); });
      }

      Array.from(document.querySelectorAll('.run-btn, #run-btn')).forEach(function(btn){
        btn.addEventListener('click', triggerRun);
      });

      function parsePythonReprToJSON(txt){
        if (typeof txt !== 'string') return null;
        const jsonish = txt
          .trim()
          .replace(/^['"]|['"]$/g, '')
          .replace(/\bNone\b/g, 'null')
          .replace(/\bTrue\b/g, 'true')
          .replace(/\bFalse\b/g, 'false')
          .replace(/'/g, '"');
        try { return JSON.parse(jsonish); } catch(e){ return null; }
      }

      function extractPayload(res){
        if (res && res.data && Array.isArray(res.data) && res.data.length && typeof res.data[0] === 'object'){
          return res.data[0];
        }
        if (res && res.data && typeof res.data["text/plain"] === 'string'){
          const parsed = parsePythonReprToJSON(res.data["text/plain"]);
          if (parsed) return parsed;
        }
        if (res && res.data && typeof res.data["application/json"] === 'string'){
          try { return JSON.parse(res.data["application/json"]); } catch(e){}
        }
        console.error('Unexpected Colab response shape:', res);
        return null;
      }

      // Download button behavior
      Array.from(document.querySelectorAll('.dl-csv-btn')).forEach(function(btn){
        btn.addEventListener('click', async function(){
          try{
            if (window.__ally_last_csv){
              const a = document.createElement('a');
              a.href = 'data:text/csv;base64,' + window.__ally_last_csv;
              a.download = window.__ally_last_csv_name || 'query_result.csv';
              document.body.appendChild(a);
              a.click();
              setTimeout(()=>{ document.body.removeChild(a); }, 0);
              return;
            }
            const res = await google.colab.kernel.invokeFunction('ally.get_last_csv', [], {});
            const payload = extractPayload(res);
            if(!payload || !payload.ok){
              const err = (payload && payload.error) ? payload.error : 'unknown';
              alert(err === 'no_csv' ? 'No CSV available. Run a query first.' : ('Download failed: ' + err));
              return;
            }
            const a = document.createElement('a');
            a.href = 'data:text/csv;base64,' + payload.b64;
            a.download = payload.filename || 'query_result.csv';
            document.body.appendChild(a);
            a.click();
            setTimeout(()=>{ document.body.removeChild(a); }, 0);
          }catch(e){
            console.error(e);
            alert('Download failed: ' + e.message);
          }
        });
      });

      ensureEditor();
    })();
    </script>
    """

def full_js() -> str:
    return """
    <script>
    (function(){
      var SIZE_LIMIT = 50 * 1024 * 1024; // 50 MB
      var CHUNK_SIZE = 2 * 1024 * 1024;  // 2 MB

      var dropArea = document.getElementById('drop-area');
      var loadingBlock = document.getElementById('loading-block');
      var loadingText = document.getElementById('loading-text');
      var barFill = document.getElementById('bar-fill');

      var uploadFallback = document.getElementById('upload-fallback');
      var fileInput = document.getElementById('file-input');
      var uploadBtn = document.getElementById('upload-btn');

      function stop(e){ e.preventDefault(); e.stopPropagation(); }
      ['dragenter','dragover','dragleave','drop'].forEach(function(ev){
        dropArea.addEventListener(ev, stop, false);
      });
      dropArea.addEventListener('dragover', function(){ dropArea.classList.add('dragover'); });
      dropArea.addEventListener('dragleave', function(){ dropArea.classList.remove('dragover'); });

      function toBase64FromArrayBuffer(buf){
        var bytes = new Uint8Array(buf);
        var binary = '';
        for (var i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
        return btoa(binary);
      }

      async function chunkedUpload(file){
        dropArea.classList.remove('dragover');
        dropArea.style.display = 'none';
        loadingBlock.style.display = 'block';
        loadingText.textContent = 'Uploading… 0%';
        barFill.style.width = '0%';

        var sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2);
        await google.colab.kernel.invokeFunction('ally.begin_upload_session',
          [sessionId, file.name, file.size, file.lastModified], {});

        var offset = 0;
        while (offset < file.size){
          var slice = file.slice(offset, Math.min(offset + CHUNK_SIZE, file.size));
          var buf = await slice.arrayBuffer();
          var b64 = toBase64FromArrayBuffer(buf);
          await google.colab.kernel.invokeFunction('ally.upload_chunk', [sessionId, b64], {});
          offset += slice.size;

          var pct = Math.round(offset * 100 / file.size);
          loadingText.textContent = 'Uploading… ' + pct + '%';
          barFill.style.width = pct + '%';
        }

        await google.colab.kernel.invokeFunction('ally.finish_upload', [sessionId], {});
        loadingText.textContent = 'Processing file…';
        await google.colab.kernel.invokeFunction('ally.read_uploaded', [sessionId], {});
        loadingBlock.style.display = 'none';
      }

      function handleFileProcess(file){
        return chunkedUpload(file);
      }

      dropArea.addEventListener('drop', function(event) {
        var file = event.dataTransfer.files[0];
        dropArea.classList.remove('dragover');
        if (!file) return;
        if (file.size > SIZE_LIMIT) {
          dropArea.classList.add('disabled');
          uploadFallback.style.display = 'block';
          return;
        }
        handleFileProcess(file).catch(function(e){
          console.error(e);
          loadingBlock.style.display = 'none';
          alert('Upload failed: ' + e.message);
        });
      });

      if (uploadBtn){
        uploadBtn.addEventListener('click', function(){
          var file = fileInput && fileInput.files && fileInput.files[0];
          if (!file) { alert('Please choose a file first.'); return; }
          uploadBtn.disabled = true;
          uploadBtn.textContent = 'Uploading…';
          fileInput.disabled = true;

          chunkedUpload(file).catch(function(e){
            console.error(e);
            alert('Upload failed: ' + e.message);
          }).finally(function(){
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload';
            fileInput.disabled = false;
          });
        });
      }
    })();
    </script>
    """
