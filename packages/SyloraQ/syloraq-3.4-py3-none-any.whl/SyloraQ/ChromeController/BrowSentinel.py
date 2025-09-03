import os
import sys
import time
import json
import socket
import struct
import base64
import threading
import subprocess
import http.client
import shutil
import hashlib
from SyloraQ import GlowShell

class WSC:
    def __init__(self, ws_url):
        _, rest = ws_url.split('://', 1)
        hostport, path = rest.split('/', 1)
        if ':' in hostport:
            self.host, port = hostport.split(':')
            self.port = int(port)
        else:
            self.host = hostport
            self.port = 80
        self.path = '/' + path
        self.sock = None
        self.connected = False
        self.running = False
        self.pending = {}
        self.next_id = 1
        self.lock = threading.Lock()
        self.on_event = None

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = sock.recv(4096)
            if not chunk: raise RuntimeError("Handshake failed: socket closed")
            buf += chunk
        self.sock = sock
        self.connected = True
        self.running = True
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk: raise RuntimeError("Socket closed during recv")
            buf += chunk
        return buf

    def _recv_frame(self):
        hdr = self._recv_exact(2)
        b1, b2 = hdr
        masked = b2 & 0x80
        length = b2 & 0x7F
        if length == 126:
            length = struct.unpack(">H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self._recv_exact(8))[0]
        mask = self._recv_exact(4) if masked else None
        payload = self._recv_exact(length)
        if mask:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        opcode = b1 & 0x0F
        if opcode == 0x8:
            self.close()
            return None
        if opcode == 0x9:
            self._send_frame(0x8A, payload) 
            return None
        if opcode != 0x1:
            return None
        return payload.decode('utf-8', errors='ignore')
    
    def add_event_handler(self, handler):
        self.event_handlers.append(handler)

    def _recv_loop(self):
        while self.running:
            try:
                msg = self._recv_frame()
                if msg is None:
                    break
                data = json.loads(msg)
                if "id" in data:
                    with self.lock:
                        slot = self.pending.get(data["id"])
                    if slot:
                        slot["resp"] = data
                        slot["event"].set()
                else:
                    if self.on_event:
                        self.on_event(data)
            except Exception:
                break
        self.running = False
        self.connected = False

    def _send_frame(self, first_byte, payload: bytes):
        header = bytes([first_byte])
        length = len(payload)
        if length < 126:
            header += bytes([0x80 | length])
        elif length < (1 << 16):
            header += bytes([0x80 | 126]) + struct.pack(">H", length)
        else:
            header += bytes([0x80 | 127]) + struct.pack(">Q", length)
        mask = os.urandom(4)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(header + masked)

    def send(self, method, params=None, timeout=5, retries=3, retry_delay=1):
        if not self.connected:
            raise RuntimeError("WebSocket not connected")

        attempt = 0
        while attempt < retries:
            with self.lock:
                msg_id = self.next_id
                self.next_id += 1
                ev = threading.Event()
                self.pending[msg_id] = {"event": ev, "resp": None}

            msg = {"id": msg_id, "method": method}
            if params is not None:
                msg["params"] = params
            text = json.dumps(msg).encode('utf-8')

            try:
                self._send_frame(0x81, text)
            except Exception as e:
                with self.lock:
                    self.pending.pop(msg_id, None)
                if attempt == retries - 1:
                    raise
                else:
                    attempt += 1
                    time.sleep(retry_delay)
                    continue

            if not ev.wait(timeout):
                with self.lock:
                    self.pending.pop(msg_id, None)
                if attempt == retries - 1:
                    raise TimeoutError(f"{method} timed out")
                else:
                    attempt += 1
                    time.sleep(retry_delay)
                    continue

            with self.lock:
                resp = self.pending[msg_id]["resp"]
                del self.pending[msg_id]

            if "error" in resp:
                if attempt == retries - 1:
                    raise RuntimeError(f"{method} error: {resp['error']}")
                else:
                    attempt += 1
                    time.sleep(retry_delay)
                    continue
            return resp
    def close(self):
        self.running = False
        self.connected = False
        try:
            if self.sock:
                self.sock.close()
                self.sock = None
        except Exception:pass


class BrowSentinel:
    def __init__(self, warn=False, headless=True, port=8381):
        self.headless = headless
        self.port = port
        self.proc = None
        self.ws = WSC
        self._started = False
        self._closed = False
        self._navigated = False
        self._warn = warn
    def _find_chrome(self):
        if sys.platform.startswith("win"):
            p = os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe")
            return p if os.path.exists(p) else None
        elif sys.platform == "darwin":
            p = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            return p if os.path.exists(p) else None
        else:return shutil.which("google-chrome")
    def start(self):
        chrome = self._find_chrome()
        if not chrome:raise RuntimeError("Chrome not found")
        args = [chrome, f"--remote-debugging-port={self.port}", "--disable-gpu"]
        if self.headless:args.append("--headless=new")
        args.append("about:blank")
        self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)
        conn = http.client.HTTPConnection("localhost", self.port)
        conn.request("GET", "/json")
        targets = json.loads(conn.getresponse().read())
        page = next(t for t in targets if t.get("type") == "page")
        ws_url = page["webSocketDebuggerUrl"]
        self.ws = WSC(ws_url)
        self.ws.connect()
        self.ws.send("Page.enable")
        self.ws.send("DOM.enable")
        self.ws.send("Network.enable")
        self._started = True
    def navigate(self, url):
        try:self._navigated = True;return self.ws.send("Page.navigate", {"url": url},timeout=10)
        except Exception as e:GlowShell.print(f"⚠️   Warning: Please enter a valid url.","red","Black")
    def reload(self):return self.ws.send("Page.reload")
    def back(self):
        history = self.ws.send("Page.getNavigationHistory")
        entries = history["result"]["entries"]
        idx = history["result"]["currentIndex"]
        if idx <= 0:raise RuntimeError("No back history entry")
        entry_id = entries[idx-1]["id"]
        return self.ws.send("Page.navigateToHistoryEntry", {"entryId": entry_id})
    def forward(self):
        history = self.ws.send("Page.getNavigationHistory")
        entries = history["result"]["entries"]
        idx = history["result"]["currentIndex"]
        if idx >= len(entries) - 1: raise RuntimeError("No forward history entry")
        entry_id = entries[idx+1]["id"]
        return self.ws.send("Page.navigateToHistoryEntry", {"entryId": entry_id})
    def set_viewport(self, width, height, deviceScaleFactor=1):return self.ws.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height,"deviceScaleFactor": deviceScaleFactor,"mobile": False})
    def evaluate(self, script):
        resp = self.ws.send("Runtime.evaluate", {"expression": script, "returnByValue": True})
        return resp.get("result", {}).get("result", {}).get("value")
    def get_html(self):
        resp = self.ws.send("DOM.getDocument")
        node_id = resp["result"]["root"]["nodeId"]
        outer = self.ws.send("DOM.getOuterHTML", {"nodeId": node_id})
        return outer["result"]["outerHTML"]
    def get_text(self):
        return self.evaluate("document.body.innerText")
    def click(self, selector):
        return self.evaluate(f"document.querySelector('{selector}').click()")
    def type(self, selector, text):
        js = (f"(el=document.querySelector('{selector}')).value='{text}';""el.dispatchEvent(new Event('input'));")
        return self.evaluate(js)
    def wait_for(self, selector, timeout=5):
        js = (
            "(sel,to)=>new Promise((res, rej)=>{"
            "let t=0; function check(){"
            "if(document.querySelector(sel)) return res(true);"
            "if(t>to*1000) return rej('timeout');""t+=100; setTimeout(check,100);} check();})")
        return self.evaluate(f"({js})('{selector}',{timeout})")
    def screenshot(self, path="page..png"):
        self.ws.send("Page.captureScreenshot")
        resp = self.ws.send("Page.captureScreenshot")
        data = resp["result"]["data"]
        with open(path, "wb") as f:f.write(base64.b64decode(data))
        return path
    def wait_until_loaded(self, timeout=10):
        js = (
            "(to)=>new Promise((res, rej)=>{"
            "let t=0; function check(){"
            "if(document.readyState==='complete') return res(true);"
            "if(t>to*1000) return rej('timeout');"
            "t+=100; setTimeout(check,100);} check();})")
        return self.evaluate(f"({js})({timeout})")
    def wait_for_selector_visible(self, selector, timeout=10):
        js = (
            "(sel,to)=>new Promise((res, rej)=>{"
            "let t=0; function check(){"
            "let el=document.querySelector(sel);"
            "if(el && el.offsetParent!==null) return res(true);"
            "if(t>to*1000) return rej('timeout');"
            "t+=100; setTimeout(check,100);} check();})")
        return self.evaluate(f"({js})({json.dumps(selector)},{timeout})")
    def wait_for_condition(self, condition_js, timeout=10):
        js = (
            "(cond,to)=>new Promise((res, rej)=>{"
            "let t=0; function check(){"
            "try{if(eval(cond)) return res(true);}catch(e){}"
            "if(t>to*1000) return rej('timeout');"
            "t+=100; setTimeout(check,100);} check();})")
        return self.evaluate(f"({js})({json.dumps(condition_js)},{timeout})")
    def highlight(self, selector):
        js = (
            f"let el = document.querySelector('{selector}');"
            "if(el) el.style.outline = '3px solid red';"
        )
        return self.evaluate(js)
    def wait_until_stable(self, timeout=10):
        js = (
            "(to)=>new Promise((res, rej)=>{"
            "let last = document.body.innerHTML, t=0;"
            "function check(){"
            "let now = document.body.innerHTML;"
            "if(now === last) return res(true);"
            "last = now; if(t>to*1000) return rej('timeout');"
            "t+=200; setTimeout(check, 200);}"
            "check();})"
        )
        return self.evaluate(f"({js})({timeout})")
    def clicktypeenter(self, selector, text, wait_selector=None, timeout=10):
        self.evaluate(f"document.querySelector({json.dumps(selector)}).click()")
        self.evaluate(f"(el => {{"f"el.focus(); el.value = {json.dumps(text)};"f"el.dispatchEvent(new Event('input'));"f"}})(document.querySelector({json.dumps(selector)}))")
        self.ws.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter"})
        if wait_selector:return self.wait_for_selector_visible(wait_selector, timeout)
    def wait_for_results_change(self, selector, timeout=10):
        initial = self.evaluate(f"document.querySelector({json.dumps(selector)}).innerText")
        js = (
            "(sel,init,to)=>new Promise((res, rej)=>{"
            "let t=0; function check(){"
            "let now = document.querySelector(sel)?.innerText || '';"
            "if(now !== init) return res(true);"
            "if(t>to*1000) return rej('timeout'); t+=200; setTimeout(check,200);} check();})"
        )
        return self.evaluate(f"({js})({json.dumps(selector)}, {json.dumps(initial)}, {timeout})")
    def wait_for_url_change(self, timeout=10):
        old_url = self.get_url()
        js = (
            "(old,to)=>new Promise((res, rej)=>{"
            "let t=0; function check(){"
            "let now = location.href;"
            "if(now !== old) return res(now);"
            "if(t > to * 1000) return rej('timeout');"
            "t += 200; setTimeout(check, 200); } check(); })"
        )
        return self.evaluate(f"({js})({json.dumps(old_url)}, {timeout})")
    def get_attribute(self, selector, attribute):
        js = f"document.querySelector({json.dumps(selector)})?.getAttribute({json.dumps(attribute)}) || null"
        return self.evaluate(js)
    def set_attribute(self, selector, attribute, value):
        js = (
            f"(el => {{ if(el) el.setAttribute({json.dumps(attribute)}, {json.dumps(value)}); }})"
            f"(document.querySelector({json.dumps(selector)}))"
        )
        return self.evaluate(js)
    def remove_element(self, selector):
        js = (
            f"(el => {{ if(el) el.remove(); }})"
            f"(document.querySelector({json.dumps(selector)}))"
        )
        return self.evaluate(js)
    def get_inner_html(self, selector):
        js = f"document.querySelector({json.dumps(selector)})?.innerHTML || null"
        return self.evaluate(js)
    def set_inner_html(self, selector, html):
        js = (
            f"(el => {{ if(el) el.innerHTML = {json.dumps(html)}; }})"
            f"(document.querySelector({json.dumps(selector)}))"
        )
        return self.evaluate(js)
    def is_checked(self, selector):
        js = f"document.querySelector({json.dumps(selector)})?.checked || false"
        return self.evaluate(js)
    def set_checked(self, selector, value=True):
        js = (
            f"(el => {{ if(el) {{ el.checked = {str(value).lower()}; el.dispatchEvent(new Event('change')); }} }})"
            f"(document.querySelector({json.dumps(selector)}))"
        )
        return self.evaluate(js)
    def save_to_local_storage(self, key, value):
        js = (
            f"localStorage.setItem({json.dumps(key)}, JSON.stringify({json.dumps(value)}));"
        )
        return self.evaluate(js)
    def load_from_local_storage(self, key):
        js = (
            f"(() => {{"
            f"try {{ return JSON.parse(localStorage.getItem({json.dumps(key)})); }}"
            f"catch(e) {{ return null; }}"
            f"}})()"
        )
        return self.evaluate(js)
    def save_to_session_storage(self, key, value):
        js = (
            f"sessionStorage.setItem({json.dumps(key)}, JSON.stringify({json.dumps(value)}));"
        )
        return self.evaluate(js)
    def load_from_session_storage(self, key):
        js = (
            f"(() => {{"
            f"try {{ return JSON.parse(sessionStorage.getItem({json.dumps(key)})); }}"
            f"catch(e) {{ return null; }}"
            f"}})()"
        )
        return self.evaluate(js)
    def download_data_as_file(self, data, filename="data.json"):
        data_json = json.dumps(data)
        js = (
            f"(() => {{"
            f"const blob = new Blob([{json.dumps(data_json)}], {{type: 'application/json'}});"
            f"const url = URL.createObjectURL(blob);"
            f"const a = document.createElement('a');"
            f"a.href = url;"
            f"a.download = {json.dumps(filename)};"
            f"document.body.appendChild(a);"
            f"a.click();"
            f"setTimeout(() => {{ document.body.removeChild(a); URL.revokeObjectURL(url); }}, 100);"
            f"}})()"
        )
        return self.evaluate(js)
    def load_with(self, url, headers=None, body=None, method="GET"):
        self.ws.send("Fetch.enable", {"patterns": [{"urlPattern": "*"}]})
        self._last_request_id = None
        def request_handler(event):
            if event.get("method") == "Fetch.requestPaused":
                request_id = event["params"]["requestId"]
                request = event["params"]["request"]
                overrides = {"headers": [{"name": k, "value": v} for k, v in (headers or {}).items()],"method": method,}
                if body:
                    overrides["postData"] = body
                    if not any(h["name"].lower() == "content-type" for h in overrides["headers"]):overrides["headers"].append({"name": "Content-Type", "value": "application/x-www-form-urlencoded"})
                self.ws.send("Fetch.continueRequest", {"requestId": request_id, **overrides})
        self.ws.on_event = request_handler
        self.ws.send("Page.navigate", {"url": url})
        time.sleep(5)
        self.ws.send("Fetch.disable")
        self.ws.on_event = None
    def get_cookies(self):
        resp = self.ws.send("Network.getAllCookies")
        return resp.get("result", {}).get("cookies", [])
    def set_cookie(self, name, value, domain=None, path='/', secure=False, httpOnly=False, sameSite=None, expires=None):
        params = {"name": name,"value": value,"path": path,"secure": secure,"httpOnly": httpOnly}
        if domain:params["domain"] = domain
        if sameSite:params["sameSite"] = sameSite
        if expires:params["expires"] = expires
        return self.ws.send("Network.setCookie", params)
    def delete_cookie(self, name, domain=None, path='/'):
        cookies = self.get_cookies()
        target = next((c for c in cookies if c["name"] == name and (domain is None or c.get("domain") == domain)), None)
        if not target:raise RuntimeError("Cookie not found")
        params = {"name": name,"domain": target.get("domain"),"path": path}
        return self.ws.send("Network.deleteCookies", params)
    def wait_for_load(self, timeout=10):
        ev = threading.Event()
        def on_event(event):
            if event.get("method") == "Page.loadEventFired":ev.set()
        self.ws.on_event = on_event
        try:
            if not ev.wait(timeout):raise TimeoutError("Page load timed out")
        finally:self.ws.on_event = None
    def click_by_name(self, name, index=0):
        js = (
            f"(els => {{"
            f"  if (!els || els.length <= {index}) return false;"
            f"  els[{index}].click();"
            f"  return true;"
            f"}})(document.querySelectorAll('[name=\"{name}\"]'))"
        )
        return self.evaluate(js)
    def type_by_name(self, name, text, index=0):
        js = (
            f"(els => {{"
            f"  if (!els || els.length <= {index}) return false;"
            f"  const el = els[{index}];"
            f"  el.value = {json.dumps(text)};"
            f"  el.dispatchEvent(new Event('input'));"
            f"  return true;"
            f"}})(document.querySelectorAll('[name=\"{name}\"]'))"
        )
        return self.evaluate(js)
    def click_by_id(self, id_, index=0):
        js = (
            f"(els => {{"
            f"  if (!els || els.length <= {index}) return false;"
            f"  els[{index}].click();"
            f"  return true;"
            f"}})(document.querySelectorAll('#{id_}'))"
        )
        return self.evaluate(js)
    def type_by_id(self, id_, text, index=0):
        js = (
            f"(els => {{"
            f"  if (!els || els.length <= {index}) return false;"
            f"  const el = els[{index}];"
            f"  el.value = {json.dumps(text)};"
            f"  el.dispatchEvent(new Event('input'));"
            f"  return true;"
            f"}})(document.querySelectorAll('#{id_}'))"
        )
        return self.evaluate(js)
    def press_enter(self, selector, index=0):
        js = (
            f"(els => {{"
            f"  if (!els || els.length <= {index}) return false;"
            f"  const el = els[{index}];"
            f"  const event = new KeyboardEvent('keydown', {{key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}});"
            f"  el.dispatchEvent(event);"
            f"  return true;"
            f"}})(document.querySelectorAll({json.dumps(selector)}))"
        )
        return self.evaluate(js)
    def press_enter_by_name(self, name, index=0):
        js = (
            f"(els => {{"
            f"  if (!els || els.length <= {index}) return false;"
            f"  const el = els[{index}];"
            f"  const event = new KeyboardEvent('keydown', {{key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}});"
            f"  el.dispatchEvent(event);"
            f"  return true;"
            f"}})(document.querySelectorAll('[name=\"{name}\"]'))"
        )
        return self.evaluate(js)
    def close(self):
        if self.ws:self.ws.close()
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self._closed = True
    def __del__(self):
        try:
            if not getattr(self, "_started", False):
                if self._warn:GlowShell.print("⚠️   Warning: BrowSentinel was used without calling .start(), attempting to start automatically...", "red", "black")
                try:
                    self.start()
                    if self._warn:GlowShell.print("✅ Auto-start succeeded in destructor.", "green", "black")
                except Exception as e:
                    if self._warn:GlowShell.print(f"❌ Auto-start failed in destructor: {e}", "red", "black")
            elif not getattr(self, "_closed", False):
                if self._warn:GlowShell.print("⚠️   Warning: BrowSentinel was not closed properly. Automatically closing.", "red", "black")
                try:self.close()
                except Exception:pass
            elif not getattr(self, "_navigated", False):
                if self._warn:GlowShell.print("⚠️   Warning: BrowSentinel was used without calling .navigate()", "red", "black")
        except Exception:pass
