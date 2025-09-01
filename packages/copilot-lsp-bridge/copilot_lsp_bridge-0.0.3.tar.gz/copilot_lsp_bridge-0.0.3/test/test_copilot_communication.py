#!/usr/bin/env python3

import subprocess
import json
import tempfile
import os
import time

def test_copilot_communication_works():
    """Test that bridge successfully communicates with Copilot"""
    
    # Start bridge 
    log_file = f"tmp/test-serialization-{int(time.time())}.log"
    os.makedirs("tmp", exist_ok=True)
    
    proc = subprocess.Popen([
        'uv', 'run', 'python', '-m', 'src.copilot_lsp_bridge', 
        '--log-level', 'DEBUG', '--log-file', log_file
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    def send_lsp(msg):
        payload = json.dumps(msg)
        header = f"Content-Length: {len(payload)}\r\n\r\n"
        proc.stdin.write(header + payload)
        proc.stdin.flush()
    
    def read_lsp():
        headers = {}
        while True:
            line = proc.stdout.readline().strip()
            if not line:
                break
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value
        
        length = int(headers.get("content-length", 0))
        if length > 0:
            content = proc.stdout.read(length)
            return json.loads(content)
        return None
    
    try:
        # Initialize exactly like the error log
        send_lsp({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "processId": 123,
                "rootUri": "file:///tmp", 
                "capabilities": {"textDocument": {"completion": {}}}
            }
        })
        
        init_resp = read_lsp()
        assert init_resp is not None, "Must get init response"
        
        # Send initialized 
        send_lsp({"jsonrpc": "2.0", "method": "initialized", "params": {}})
        
        # Open file exactly like error log
        send_lsp({
            "jsonrpc": "2.0", "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/test.py",
                    "languageId": "python",
                    "version": 1,
                    "text": "def test_func():\n    "
                }
            }
        })
        
        # Wait for Copilot to start
        time.sleep(5)
        
        # Request completion exactly like error log
        send_lsp({
            "jsonrpc": "2.0", "id": 2, "method": "textDocument/completion",
            "params": {
                "textDocument": {"uri": "file:///tmp/test.py"},
                "position": {"line": 1, "character": 4}
            }
        })
        
        comp_resp = read_lsp()
        print(f"Completion response: {json.dumps(comp_resp, indent=2)}")
        
        # Check if we got the serialization error
        with open(log_file, 'r') as f:
            log_content = f.read()
            
        assert "Agent service not initialized" in log_content, f"Expected Copilot communication not found in logs:\n{log_content}"
            
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_serialization_error()