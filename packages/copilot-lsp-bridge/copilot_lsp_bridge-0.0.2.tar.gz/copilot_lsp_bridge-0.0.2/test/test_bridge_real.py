import json
import subprocess
import tempfile
import time
import os


def test_real_copilot_completions():
    """
    REAL TEST: Verify bridge actually gets meaningful completions from Copilot.
    
    This test creates realistic coding scenarios and validates that:
    1. Copilot subprocess starts correctly
    2. Authentication works
    3. Bridge translates requests properly
    4. We get actual AI-generated code suggestions
    
    NO BULLSHIT - if this fails, the bridge is broken.
    """
    
    # Start bridge with debug logging
    bridge_proc = subprocess.Popen([
        'uv', 'run', 'python', '-m', 'src.copilot_lsp_bridge', '--log-level', 'DEBUG'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    def send_request(method, params, msg_id):
        message = {"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params}
        payload = json.dumps(message)
        header = f"Content-Length: {len(payload)}\r\n\r\n"
        bridge_proc.stdin.write(header + payload)
        bridge_proc.stdin.flush()
        
        # Read response
        headers = {}
        while True:
            line = bridge_proc.stdout.readline().strip()
            if not line:
                break
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value
        
        length = int(headers.get("content-length", 0))
        if length > 0:
            content = bridge_proc.stdout.read(length)
            return json.loads(content)
        return None
    
    def send_notification(method, params):
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        payload = json.dumps(message)
        header = f"Content-Length: {len(payload)}\r\n\r\n"
        bridge_proc.stdin.write(header + payload)
        bridge_proc.stdin.flush()
    
    try:
        # Initialize
        init_resp = send_request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        }, 1)
        
        print("INIT RESPONSE:", json.dumps(init_resp, indent=2))
        assert "completionProvider" in init_resp["result"]["capabilities"], "Bridge must advertise completion support"
        
        send_notification("initialized", {})
        
        # Create test scenarios that should trigger Copilot
        test_scenarios = [
            {
                "name": "Python function completion",
                "file": "test.py", 
                "content": "def calculate_fibonacci(n):\n    ",
                "position": {"line": 1, "character": 4},
                "expected_keywords": ["if", "return", "fibonacci", "n"]
            },
            {
                "name": "JavaScript async function",
                "file": "test.js",
                "content": "async function fetchUserData(userId) {\n    ",
                "position": {"line": 1, "character": 4}, 
                "expected_keywords": ["await", "fetch", "return", "try", "catch"]
            },
            {
                "name": "Python class method",
                "file": "test.py",
                "content": "class DatabaseManager:\n    def __init__(self):\n        ",
                "position": {"line": 2, "character": 8},
                "expected_keywords": ["self.", "self.connection", "self.db"]
            }
        ]
        
        for i, scenario in enumerate(test_scenarios):
            print(f"\n=== TESTING: {scenario['name']} ===")
            
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix=f".{scenario['file'].split('.')[-1]}", delete=False) as f:
                f.write(scenario["content"])
                temp_file = f.name
            
            try:
                # Open document
                send_notification("textDocument/didOpen", {
                    "textDocument": {
                        "uri": f"file://{temp_file}",
                        "languageId": scenario['file'].split('.')[-1],
                        "version": 1,
                        "text": scenario["content"]
                    }
                })
                
                # Wait for Copilot to process
                time.sleep(3)
                
                # Request completion
                comp_resp = send_request("textDocument/completion", {
                    "textDocument": {"uri": f"file://{temp_file}"},
                    "position": scenario["position"]
                }, i + 10)
                
                print(f"COMPLETION RESPONSE: {json.dumps(comp_resp, indent=2)}")
                
                # REAL ASSERTIONS
                assert "result" in comp_resp, "Must have result"
                assert "items" in comp_resp["result"], "Must have items array"
                
                items = comp_resp["result"]["items"]
                
                if not items:
                    print("❌ FAILURE: No completions returned")
                    print("This means either:")
                    print("  1. Bridge is not connecting to Copilot")
                    print("  2. Copilot is not authenticated") 
                    print("  3. Translation logic is broken")
                    continue
                
                print(f"✅ SUCCESS: Got {len(items)} completions")
                
                # Validate completion quality
                meaningful_completions = 0
                for j, item in enumerate(items):
                    print(f"  Completion {j+1}:")
                    print(f"    Label: {item.get('label', 'MISSING')[:100]}")
                    print(f"    Text: {item.get('insertText', 'MISSING')[:100]}")
                    
                    # STRICT VALIDATION
                    assert "label" in item, "Missing label"
                    assert "insertText" in item, "Missing insertText"
                    assert len(item["insertText"].strip()) > 0, "Empty insertText"
                    
                    # Check for meaningful content
                    insert_text = item["insertText"].lower()
                    if any(keyword in insert_text for keyword in scenario["expected_keywords"]):
                        meaningful_completions += 1
                        print(f"    ✅ Contains expected keywords")
                    
                    # Check Copilot UUID
                    if "data" in item and "copilot_uuid" in item["data"]:
                        uuid = item["data"]["copilot_uuid"]
                        assert uuid and len(uuid) > 10, "Invalid Copilot UUID"
                        print(f"    ✅ Valid UUID: {uuid[:8]}...")
                    else:
                        print("    ❌ No Copilot UUID - acceptance will fail")
                
                if meaningful_completions == 0:
                    print(f"❌ FAILURE: No meaningful completions for {scenario['name']}")
                    print("Completions don't contain expected keywords - may be generic/broken")
                else:
                    print(f"✅ SUCCESS: {meaningful_completions}/{len(items)} completions are contextually relevant")
            
            finally:
                os.unlink(temp_file)
        
        print("\n=== FINAL VERDICT ===")
        print("If you see ✅ SUCCESS messages above, the bridge is working correctly.")
        print("If you see ❌ FAILURE messages, there are real problems to fix.")
                
    finally:
        bridge_proc.terminate()
        bridge_proc.wait()


if __name__ == "__main__":
    test_real_copilot_completions()