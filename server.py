#!/usr/bin/env python3
import os
import socket
import threading
import mimetypes
from pathlib import Path

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8085))
WEBROOT = Path(os.environ.get("WEBROOT", "."))  # folder containing index.html

BUFFER_SIZE = 8192

def build_response(status_code: int, body: bytes, content_type="text/html; charset=utf-8"):
    reason = {
        200: "OK",
        404: "Not Found",
        500: "Internal Server Error"
    }.get(status_code, "OK")
    headers = [
        f"HTTP/1.1 {status_code} {reason}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "", ""
    ]
    return ("\r\n".join(headers)).encode("utf-8") + body

def handle_client(conn, addr):
    try:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            return
        text = data.decode(errors="ignore")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        print(f"[{addr}] {first_line}")

        # Very small HTTP request parse
        parts = first_line.split()
        if len(parts) < 2:
            resp = build_response(400, b"<h1>400 Bad Request</h1>")
            conn.sendall(resp)
            return

        method, path = parts[0], parts[1]
        if method != "GET":
            resp = build_response(405, b"<h1>405 Method Not Allowed</h1>")
            conn.sendall(resp)
            return

        # Normalize path
        if path == "/":
            path = "/index.html"

        # Prevent path traversal
        requested = (WEBROOT / path.lstrip("/")).resolve()
        if not str(requested).startswith(str(WEBROOT.resolve())):
            resp = build_response(403, b"<h1>403 Forbidden</h1>")
            conn.sendall(resp)
            return

        if requested.is_file():
            try:
                content = requested.read_bytes()
                ctype, _ = mimetypes.guess_type(str(requested))
                if ctype is None:
                    ctype = "application/octet-stream"
                resp = build_response(200, content, f"{ctype}; charset=utf-8" if ctype.startswith("text/") else ctype)
            except Exception as e:
                print("Error reading file:", e)
                resp = build_response(500, b"<h1>500 Internal Server Error</h1>")
        else:
            resp = build_response(404, b"<h1>404 Not Found</h1>")

        conn.sendall(resp)
    finally:
        try:
            conn.close()
        except Exception:
            pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"Serving {WEBROOT.resolve()} on http://{HOST}:{PORT}")

    try:
        while True:
            client, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    main()
