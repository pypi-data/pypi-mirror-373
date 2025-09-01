from __future__ import annotations

import base64
import io
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import pandasql as psql
from IPython.display import HTML, Javascript, display

# Optional import so package can be imported outside Colab
try:
    from google.colab import output  # type: ignore
except Exception:
    output = None  # type: ignore

from .csv_utils import smart_read_csv
from . import _assets


@dataclass
class UIOptions:
    title: str = "SQL Query"
    default_query: str = "SELECT * FROM data LIMIT 10;"
    auto_quote_default: bool = True
    allow_excel: bool = True
    editor_theme: str = "default"
    editor_font_size_px: int = 13
    editor_line_height: float = 1.4
    drop_zone_min_h: int = 150
    drop_zone_max_h: int = 320
    progress_bar_max_w: int = 520


class AllySequelUI:
    _STATE: Dict[str, Any] = {
        "df": None, "name": None, "size": None, "when": None,
        "_uploads": {},
        "last_sql_df": None,
        "last_sql_csv_name": None
    }

    @classmethod
    def show(cls, options: Optional[UIOptions] = None) -> None:
        if output is None:
            raise RuntimeError("AllySequelUI runs only inside Google Colab.")
        opts = options or UIOptions()
        cls._register_callbacks(opts)
        cls._render_full(opts)

    @classmethod
    def show_sql_only(cls, options: Optional[UIOptions] = None) -> None:
        if output is None:
            raise RuntimeError("AllySequelUI runs only inside Google Colab.")
        opts = options or UIOptions()
        cls._register_callbacks(opts)
        cls._render_sql_only(opts)

    @staticmethod
    def _human_size(n: Any) -> str:
        try:
            n = float(n)
        except Exception:
            return "n/a"
        units = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while n >= 1024 and i < len(units) - 1:
            n /= 1024; i += 1
        return f"{n:.1f} {units[i]}"

    @staticmethod
    def _set_html(el_id: str, html: str) -> None:
        display(HTML(
            f"<script>var el=document.getElementById('{el_id}');"
            f"if(el){{el.innerHTML = `{html}`;}}</script>"
        ))

    @classmethod
    def _register_callbacks(cls, opts: UIOptions) -> None:
        if output is None:
            raise RuntimeError("AllySequelUI runs only inside Google Colab.")

        def begin_upload_session(session_id: str, filename: str, size: int, mtime: int) -> Dict[str, Any]:
            fd, path = tempfile.mkstemp(prefix="ally_", suffix=os.path.splitext(filename)[1])
            os.close(fd)
            cls._STATE["_uploads"][session_id] = {
                "path": path, "size": int(size), "written": 0,
                "name": filename, "mtime": int(mtime)
            }
            return {"ok": True, "path": path}

        def upload_chunk(session_id: str, b64data: str) -> Dict[str, Any]:
            u = cls._STATE["_uploads"].get(session_id)
            if not u:
                return {"ok": False, "error": "bad_session"}
            try:
                chunk = base64.b64decode(b64data)
                with open(u["path"], "ab") as f:
                    f.write(chunk)
                u["written"] += len(chunk)
                return {"ok": True, "written": u["written"], "total": u["size"]}
            except Exception as e:
                return {"ok": False, "error": str(e)}

        def finish_upload(session_id: str) -> Dict[str, Any]:
            u = cls._STATE["_uploads"].get(session_id)
            if not u:
                return {"ok": False, "error": "bad_session"}
            ok = u["written"] > 0
            return {"ok": ok, **u}

        def _finalize_df_from_path(file_path: str, filename: str, size: int, mtime: int) -> Dict[str, Any]:
            df = None
            last_err = None
            try:
                lower = (filename or file_path).lower()
                if opts.allow_excel and lower.endswith(".xlsx"):
                    df = pd.read_excel(file_path)
                else:
                    try:
                        df = smart_read_csv(file_path)
                    except Exception as e:
                        last_err = e
            except Exception as e:
                last_err = e

            if df is None:
                cls._set_html("file-meta",
                              f"<div style='color:#b00020;font:600 13px ui-sans-serif'>Parse error: {last_err}</div>")
                return {"ok": False, "error": str(last_err)}

            cls._STATE["df"] = df
            cls._STATE["name"] = filename or os.path.basename(file_path)
            cls._STATE["size"] = size
            cls._STATE["when"] = datetime.fromtimestamp(mtime/1000.0) if isinstance(mtime, (int, float)) else datetime.now()

            rows, cols = df.shape
            meta_html = (
                f"✅ File: <b>{cls._STATE['name']}</b> "
                f"(<span class='muted'>{cls._human_size(cls._STATE['size'])}</span>, "
                f"{cls._STATE['when'].strftime('%Y-%m-%d %H:%M')})<br>"
                f"Rows: <b>{rows}</b> &nbsp;|&nbsp; Columns: <b>{cols}</b>"
            )
            cls._set_html("file-meta", meta_html)

            cols_json = json.dumps(list(df.columns))
            display(Javascript(f"""
              (function(){{
                window.sqlTables = {{ data: {cols_json} }};
                if (window.sqlEditor) {{
                  window.sqlEditor.setOption('hintOptions', {{ tables: window.sqlTables }});
                }}
              }})();
            """))

            display(HTML("<script>var box=document.getElementById('sql-box'); if(box) box.style.display='block';</script>"))
            display(Javascript("setTimeout(function(){ if (window.sqlEditor) { window.sqlEditor.refresh(); } }, 0);"))

            return {"ok": True, "rows": int(rows), "cols": int(cols)}

        def read_uploaded(session_id: str) -> Dict[str, Any]:
            u = cls._STATE["_uploads"].get(session_id)
            if not u:
                cls._set_html("file-meta",
                              "<div style='color:#b00020;font:600 13px ui-sans-serif'>Session not found.</div>")
                return {"ok": False, "error": "bad_session"}
            return _finalize_df_from_path(u["path"], u["name"], u["size"], u["mtime"])

        def read_csv_callback(file_text: Optional[str] = None,
                              filename: Optional[str] = None,
                              size: Optional[int] = None,
                              mtime: Optional[int] = None,
                              file_path: Optional[str] = None) -> Dict[str, Any]:
            if file_path:
                return _finalize_df_from_path(file_path, filename or file_path, size or 0, mtime or 0)

            df = None
            last_err = None
            try:
                lower = (filename or "uploaded").lower()
                if UIOptions().allow_excel and lower.endswith(".xlsx"):
                    data_bytes = file_text.encode() if isinstance(file_text, str) else (file_text or b"")
                    df = pd.read_excel(io.BytesIO(data_bytes))
                else:
                    fd, tmp = tempfile.mkstemp(prefix="ally_mem_", suffix=".csv")
                    os.close(fd)
                    with open(tmp, "wb") as f:
                        f.write(file_text.encode() if isinstance(file_text, str) else (file_text or b""))
                    try:
                        df = smart_read_csv(tmp)
                    except Exception as e:
                        last_err = e
                    finally:
                        try: os.remove(tmp)
                        except Exception: pass
            except Exception as e:
                last_err = e

            if df is None:
                cls._set_html("file-meta",
                              f"<div style='color:#b00020;font:600 13px ui-sans-serif'>Parse error: {last_err}</div>")
                return {"ok": False, "error": str(last_err)}

            cls._STATE["df"] = df
            cls._STATE["name"] = filename or "uploaded.csv"
            cls._STATE["size"] = size
            cls._STATE["when"] = (datetime.fromtimestamp(mtime/1000.0)
                                  if isinstance(mtime, (int, float)) else datetime.now())

            rows, cols = df.shape
            meta_html = (
                f"✅ File: <b>{cls._STATE['name']}</b> "
                f"(<span class='muted'>{cls._human_size(cls._STATE['size'])}</span>, "
                f"{cls._STATE['when'].strftime('%Y-%m-%d %H:%M')})<br>"
                f"Rows: <b>{rows}</b> &nbsp;|&nbsp; Columns: <b>{cols}</b>"
            )
            cls._set_html("file-meta", meta_html)

            cols_json = json.dumps(list(df.columns))

            display(HTML("<script>var box=document.getElementById('sql-box'); if(box) box.style.display='block';</script>"))
            display(Javascript("setTimeout(function(){ if (window.sqlEditor) { window.sqlEditor.refresh(); } }, 0);"))

            return {"ok": True, "rows": int(rows), "cols": int(cols)}

        def run_sql() -> Dict[str, Any]:
            if cls._STATE["df"] is None:
                cls._set_html("result-title",
                              "<span style='color:#b00020;font:600 13px ui-sans-serif'>Please upload a CSV/XLSX first, or set AllySequelUI._STATE['df'].</span>")
                cls._set_html("result", "")
                return {"ok": False, "reason": "no_data"}

            raw_q = output.eval_js("window.sqlEditor ? window.sqlEditor.getValue() : ''") or ""  # type: ignore
            if not raw_q.strip():
                raw_q = UIOptions().default_query

            quote_on = bool(output.eval_js(  # type: ignore
                "!!document.getElementById('quote-cols') && document.getElementById('quote-cols').checked"
            ))
            if quote_on:
                raw_q = cls._auto_quote_dotted(raw_q, list(cls._STATE["df"].columns))

            try:
                out = psql.sqldf(raw_q, {"data": cls._STATE["df"]})
                cls._STATE["last_sql_df"] = out

                base = (cls._STATE.get("name") or "data").split("/")[-1].rsplit(".", 1)[0]
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                fname = f"{base}__query_{stamp}.csv"
                cls._STATE["last_sql_csv_name"] = fname

                csv_text = out.to_csv(index=False)
                b64 = base64.b64encode(csv_text.encode("utf-8")).decode("ascii")

                b64_js = json.dumps(b64)
                fname_js = json.dumps(fname)
                display(Javascript(f"""
                  (function(){{
                    window.__ally_last_csv = {b64_js};
                    window.__ally_last_csv_name = {fname_js};
                    document.querySelectorAll('.dl-csv-btn').forEach(b=>b.disabled=false);
                  }})();
                """))

                cls._set_html("result-title", f"Result: {len(out)} rows × {out.shape[1]}")
                cls._set_html("result", out.to_html(index=False))
                return {"ok": True, "rows": int(len(out)), "cols": int(out.shape[1])}
            except Exception as e:
                cls._set_html("result-title",
                              f"<span style='color:#b00020;font:600 13px ui-sans-serif'>SQL error: {e}</span>")
                cls._set_html("result", "")
                display(Javascript("document.querySelectorAll('.dl-csv-btn').forEach(b=>b.disabled=true);"))
                return {"ok": False, "error": str(e)}

        def get_last_csv() -> Dict[str, Any]:
            df = cls._STATE.get("last_sql_df")
            if df is None or (getattr(df, "empty", False) and df.shape[1] == 0):
                return {"ok": False, "error": "no_csv"}
            try:
                csv_text = df.to_csv(index=False)
                b64 = base64.b64encode(csv_text.encode("utf-8")).decode("ascii")
                fname = cls._STATE.get("last_sql_csv_name") or "query_result.csv"
                return {"ok": True, "b64": b64, "filename": fname}
            except Exception as e:
                return {"ok": False, "error": str(e)}

        # Register callbacks (Colab)
        output.register_callback('ally.begin_upload_session', begin_upload_session)  # type: ignore
        output.register_callback('ally.upload_chunk', upload_chunk)                  # type: ignore
        output.register_callback('ally.finish_upload', finish_upload)                # type: ignore
        output.register_callback('ally.read_csv', read_csv_callback)                 # type: ignore
        output.register_callback('ally.read_uploaded', read_uploaded)                # type: ignore
        output.register_callback('ally.run_sql', run_sql)                            # type: ignore
        output.register_callback('ally.get_last_csv', get_last_csv)                  # type: ignore

    @staticmethod
    def _auto_quote_dotted(sql: str, columns: list[str]) -> str:
        if not sql or not columns:
            return sql
        cols = [c for c in columns if isinstance(c, str) and "." in c]
        cols.sort(key=len, reverse=True)
        for col in cols:
            if f"\"{col}\"" in sql:
                continue
            for left, right in [
                (" ", " "), (" ", ","), (",", " "), ("(", ")"), (" ", ")"),
                ("(", " "), ("\n", " "), (" ", "\n"), ("\t", " "), (" ", "\t")
            ]:
                sql = sql.replace(f"{left}{col}{right}", f'{left}"{col}"{right}')
            if sql.startswith(col + " "):
                sql = sql.replace(col + " ", f'"{col}" ')
            if sql.endswith(" " + col):
                sql = sql[:-len(col)] + f'"{col}"'
        return sql

    @classmethod
    def _render_full(cls, opts: UIOptions) -> None:
        css = _assets.shared_css(opts)
        html = f"""
        <div class="drop-wrap">
          <div id="drop-area"><p>📂 <b>Drop your CSV/XLSX</b> <span class="muted">&nbsp;(drag & drop)</span></p></div>
          <div id="loading-block">
            <div id="loading-text">Loading… 0%</div>
            <div class="bar"><div id="bar-fill"></div></div>
          </div>
          <div id="file-meta"></div>
          <div id="upload-fallback" class="card">
            <div class="msg">File is too large for drag-and-drop (over 50&nbsp;MB). Please use the <b>Upload</b> button below.</div>
            <div class="row">
              <input id="file-input" type="file" accept=".csv,.xlsx" />
              <button id="upload-btn" class="btn">Upload</button>
            </div>
          </div>
          <div id="sql-box" class="card">
            <div class="row" style="justify-content:space-between;">
              <div style="font:600 13px ui-sans-serif">{opts.title} <span class="muted">(Ctrl/Cmd + Enter = Run)</span></div>
              <div class="row">
                <label style="font:600 12px ui-sans-serif">
                  <input type="checkbox" id="quote-cols" {'checked' if opts.auto_quote_default else ''}/> Auto-quote dotted columns
                </label>
                <button id="run-btn" class="btn run-btn">Run query</button>
                <button class="btn dl-csv-btn" style="background:#0b7e37" disabled>Download CSV</button>
              </div>
            </div>
            <div id="editor-host">
              <textarea id="sql-editor">{opts.default_query}</textarea>
            </div>
            <div id="result-title"></div>
            <div id="result"></div>
          </div>
        </div>
        """
        cm = _assets.cm_includes()
        js_upload = _assets.full_js()
        js_editor = _assets.editor_boot_js()
        display(HTML(css + html + cm + js_upload + js_editor))

    @classmethod
    def _render_sql_only(cls, opts: UIOptions) -> None:
        css = _assets.shared_css(opts)
        html = f"""
        <div id="sql-box" class="card" style="display:block">
          <div class="row" style="justify-content:space-between;">
            <div style="font:600 13px ui-sans-serif">{opts.title} <span class="muted">(Ctrl/Cmd + Enter = Run)</span></div>
            <div class="row">
              <label style="font:600 12px ui-sans-serif">
                <input type="checkbox" id="quote-cols" {'checked' if opts.auto_quote_default else ''}/> Auto-quote dotted columns
              </label>
              <button id="run-btn" class="btn">Run query</button>
              <button class="btn dl-csv-btn" style="background:#0b7e37" disabled>Download CSV</button>
            </div>
          </div>
          <div id="editor-host">
            <textarea id="sql-editor">{opts.default_query}</textarea>
          </div>
          <div id="result-title"></div>
          <div id="result"></div>
        </div>
        """
        cm = _assets.cm_includes()
        js_editor = _assets.editor_boot_js()
        display(HTML(css + html + cm + js_editor))
