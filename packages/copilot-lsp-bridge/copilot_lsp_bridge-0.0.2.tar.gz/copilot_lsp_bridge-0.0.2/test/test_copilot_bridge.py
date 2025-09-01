import json
import subprocess
import tempfile
import time
import os


class LSPBridgeTester:
    """LSP Bridge Test Client"""
    
    def __init__(self):
        self.bridge_proc = None
        self.msg_id = 0
    
    def start_bridge(self):
        """Start bridge server"""
        self.bridge_proc = subprocess.Popen([
            'uv', 'run', 'python', '-m', 'src.copilot_lsp_bridge'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    def send_lsp_message(self, message):
        """Send LSP message to bridge"""
        payload = json.dumps(message)
        header = f"Content-Length: {len(payload)}\r\n\r\n"
        self.bridge_proc.stdin.write(header + payload)
        self.bridge_proc.stdin.flush()
    
    def read_lsp_response(self):
        """Read LSP response from bridge"""
        headers = {}
        while True:
            line = self.bridge_proc.stdout.readline().strip()
            if not line:
                break
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value
        
        length = int(headers.get("content-length", 0))
        if length > 0:
            content = self.bridge_proc.stdout.read(length)
            return json.loads(content)
        return None
    
    def request(self, method, params):
        """Send request and get response"""
        self.msg_id += 1
        self.send_lsp_message({
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": method,
            "params": params
        })
        return self.read_lsp_response()
    
    def notify(self, method, params):
        """Send notification"""
        self.send_lsp_message({
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        })
    
    def cleanup(self):
        """Cleanup bridge process"""
        if self.bridge_proc:
            self.bridge_proc.terminate()
            self.bridge_proc.wait()


def test_bridge_initialization():
    """
    Test LSP bridge server initialization and capability negotiation.
    
    This test verifies that the bridge can properly start and respond to LSP initialize requests.
    
    Input: LSP initialize request with client capabilities including textDocument/completion support
    Expected Output: Valid LSP initialize response with server capabilities including:
    - completionProvider: {} (indicates server supports textDocument/completion)
    - textDocumentSync: proper document synchronization settings
    - executeCommandProvider: for handling Copilot-specific commands
    - serverInfo: bridge server identification
    
    The test ensures the bridge acts as a proper LSP server that can be connected to by any LSP client.
    """
    tester = LSPBridgeTester()
    
    try:
        tester.start_bridge()
        
        response = tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {
                "textDocument": {
                    "completion": {"completionItem": {"snippetSupport": True}}
                }
            }
        })
        
        print(f"Initialize response: {json.dumps(response, indent=2)}")
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        caps = response["result"]["capabilities"]
        assert "completionProvider" in caps
        assert "textDocumentSync" in caps
        assert "executeCommandProvider" in caps
        
        print("✓ Bridge initialization successful")
        
    finally:
        tester.cleanup()


def test_completion_empty_file():
    """Test completion on empty file"""
    tester = LSPBridgeTester()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("")
        temp_file = f.name
    
    try:
        tester.start_bridge()
        
        # Initialize
        tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        })
        tester.notify("initialized", {})
        
        # Open empty file
        tester.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{temp_file}",
                "languageId": "python",
                "version": 1,
                "text": ""
            }
        })
        
        time.sleep(1)
        
        # Request completion at start
        response = tester.request("textDocument/completion", {
            "textDocument": {"uri": f"file://{temp_file}"},
            "position": {"line": 0, "character": 0}
        })
        
        print(f"Empty file completion: {json.dumps(response, indent=2)}")
        assert "result" in response, "Bridge must return LSP completion response with result field"
        assert "items" in response["result"], "Completion result must contain items array"
        assert isinstance(response["result"]["items"], list), "Completion items must be a list"
        
    finally:
        tester.cleanup()
        os.unlink(temp_file)


def test_completion_partial_function():
    """Test completion in partial function"""
    tester = LSPBridgeTester()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def process_data():\n    ")
        temp_file = f.name
    
    try:
        tester.start_bridge()
        
        # Initialize
        tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        })
        tester.notify("initialized", {})
        
        # Open file
        tester.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{temp_file}",
                "languageId": "python", 
                "version": 1,
                "text": "def process_data():\n    "
            }
        })
        
        time.sleep(2)
        
        # Request completion at function body
        response = tester.request("textDocument/completion", {
            "textDocument": {"uri": f"file://{temp_file}"},
            "position": {"line": 1, "character": 4}
        })
        
        print(f"Function completion: {json.dumps(response, indent=2)}")
        
        assert "result" in response, "Bridge must return LSP completion response with result field"
        assert "items" in response["result"], "Completion result must contain items array"
        
        items = response["result"]["items"]
        if items:
            print(f"✅ Got {len(items)} completion items")
            for i, item in enumerate(items):
                assert "label" in item, f"Completion item {i+1} must have label"
                assert "insertText" in item, f"Completion item {i+1} must have insertText"
                assert len(item["insertText"].strip()) > 0, f"Completion item {i+1} insertText cannot be empty"
                print(f"  {i+1}. {item.get('label', 'No label')}")
                if 'data' in item and 'copilot_uuid' in item['data']:
                    uuid = item['data']['copilot_uuid']
                    assert uuid and len(uuid) > 10, f"Completion item {i+1} must have valid Copilot UUID"
                    print(f"     UUID: {uuid[:8]}...")
        else:
            print("❌ No completions returned")
        
    finally:
        tester.cleanup()
        os.unlink(temp_file)


def test_completion_class_method():
    """Test completion in class method"""
    tester = LSPBridgeTester()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("class DataProcessor:\n    def __init__(self):\n        ")
        temp_file = f.name
    
    try:
        tester.start_bridge()
        
        # Initialize
        tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        })
        tester.notify("initialized", {})
        
        # Open file
        tester.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{temp_file}",
                "languageId": "python",
                "version": 1,
                "text": "class DataProcessor:\n    def __init__(self):\n        "
            }
        })
        
        time.sleep(2)
        
        # Request completion in constructor
        response = tester.request("textDocument/completion", {
            "textDocument": {"uri": f"file://{temp_file}"},
            "position": {"line": 2, "character": 8}
        })
        
        print(f"Class method completion: {json.dumps(response, indent=2)}")
        
        if "result" in response and response["result"].get("items"):
            items = response["result"]["items"]
            print(f"Got {len(items)} completion items")
            for i, item in enumerate(items):
                print(f"  {i+1}. {item.get('label', 'No label')[:80]}")
        
    finally:
        tester.cleanup()
        os.unlink(temp_file)


def test_document_changes():
    """Test document change notifications"""
    tester = LSPBridgeTester()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import os\n")
        temp_file = f.name
    
    try:
        tester.start_bridge()
        
        # Initialize
        tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        })
        tester.notify("initialized", {})
        
        # Open file
        tester.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{temp_file}",
                "languageId": "python",
                "version": 1,
                "text": "import os\n"
            }
        })
        
        # Change document - add new function
        new_text = "import os\n\ndef new_function():\n    "
        tester.notify("textDocument/didChange", {
            "textDocument": {"uri": f"file://{temp_file}", "version": 2},
            "contentChanges": [{"text": new_text}]
        })
        
        time.sleep(2)
        
        # Request completion at new position
        response = tester.request("textDocument/completion", {
            "textDocument": {"uri": f"file://{temp_file}"},
            "position": {"line": 3, "character": 4}
        })
        
        print(f"After change completion: {json.dumps(response, indent=2)}")
        
        if "result" in response and response["result"].get("items"):
            items = response["result"]["items"]
            print(f"Got {len(items)} completion items after change")
        
    finally:
        tester.cleanup()
        os.unlink(temp_file)


def test_multiple_completion_positions():
    """Test completions at different positions"""
    tester = LSPBridgeTester()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write("function calculateTotal(items) {\n    \n}")
        temp_file = f.name
    
    try:
        tester.start_bridge()
        
        # Initialize
        tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        })
        tester.notify("initialized", {})
        
        # Open JavaScript file
        tester.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{temp_file}",
                "languageId": "javascript",
                "version": 1,
                "text": "function calculateTotal(items) {\n    \n}"
            }
        })
        
        time.sleep(2)
        
        # Test different positions
        positions = [
            {"line": 0, "character": 0, "desc": "start of file"},
            {"line": 1, "character": 4, "desc": "function body"},
            {"line": 2, "character": 1, "desc": "end of function"}
        ]
        
        for pos in positions:
            response = tester.request("textDocument/completion", {
                "textDocument": {"uri": f"file://{temp_file}"},
                "position": {"line": pos["line"], "character": pos["character"]}
            })
            
            assert "result" in response, f"Bridge must return LSP completion response for {pos['desc']}"
            assert "items" in response["result"], f"Completion result must contain items array for {pos['desc']}"
            
            items = response["result"]["items"]
            print(f"Completion at {pos['desc']}: {len(items)} items")
            
            if items:
                for i, item in enumerate(items):
                    assert "label" in item, f"Item {i+1} at {pos['desc']} must have label"
                    assert "insertText" in item, f"Item {i+1} at {pos['desc']} must have insertText"
        
    finally:
        tester.cleanup()
        os.unlink(temp_file)


if __name__ == "__main__":
    print("=== Testing Bridge Initialization ===")
    test_bridge_initialization()
    
    print("\n=== Testing Empty File Completion ===")
    test_completion_empty_file()
    
    print("\n=== Testing Partial Function Completion ===")
    test_completion_partial_function()
    
    print("\n=== Testing Class Method Completion ===") 
    test_completion_class_method()
    
    print("\n=== Testing Document Changes ===")
    test_document_changes()
    
    print("\n=== Testing Multiple Positions ===")
    test_multiple_completion_positions()
    
    print("\n=== All Tests Complete ===")


def test_completion_empty_file():
    """
    Test completion requests on an empty Python file.
    
    This test verifies the bridge can handle completion requests on files with no content.
    It simulates a user opening a blank Python file and requesting completions at the very start.
    
    Input: 
    - Empty Python file (0 bytes)
    - Completion request at position (0, 0) - start of file
    
    Expected Output:
    - Valid LSP completion response (even if empty items list)
    - No errors or crashes from the bridge
    - Proper JSON-RPC 2.0 response format
    
    This tests the bridge's robustness when handling edge cases like empty files.
    """
    tester = LSPBridgeTester()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("")
        temp_file = f.name
    
    try:
        tester.start_bridge()
        
        # Initialize
        tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        })
        tester.notify("initialized", {})
        
        # Open empty file
        tester.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{temp_file}",
                "languageId": "python",
                "version": 1,
                "text": ""
            }
        })
        
        time.sleep(1)
        
        # Request completion at start
        response = tester.request("textDocument/completion", {
            "textDocument": {"uri": f"file://{temp_file}"},
            "position": {"line": 0, "character": 0}
        })
        
        print(f"Empty file completion: {json.dumps(response, indent=2)}")
        assert "result" in response, "Bridge must return LSP completion response with result field"
        assert "items" in response["result"], "Completion result must contain items array"
        assert isinstance(response["result"]["items"], list), "Completion items must be a list"
        
    finally:
        tester.cleanup()
        os.unlink(temp_file)


def test_completion_partial_function():
    """Test completion in partial function"""
    tester = LSPBridgeTester()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def process_data():\n    ")
        temp_file = f.name
    
    try:
        tester.start_bridge()
        
        # Initialize
        tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        })
        tester.notify("initialized", {})
        
        # Open file
        tester.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{temp_file}",
                "languageId": "python", 
                "version": 1,
                "text": "def process_data():\n    "
            }
        })
        
        time.sleep(2)
        
        # Request completion at function body
        response = tester.request("textDocument/completion", {
            "textDocument": {"uri": f"file://{temp_file}"},
            "position": {"line": 1, "character": 4}
        })
        
        print(f"Function completion: {json.dumps(response, indent=2)}")
        
        assert "result" in response, "Bridge must return LSP completion response with result field"
        assert "items" in response["result"], "Completion result must contain items array"
        
        items = response["result"]["items"]
        if items:
            print(f"✅ Got {len(items)} completion items")
            for i, item in enumerate(items):
                assert "label" in item, f"Completion item {i+1} must have label"
                assert "insertText" in item, f"Completion item {i+1} must have insertText"
                assert len(item["insertText"].strip()) > 0, f"Completion item {i+1} insertText cannot be empty"
                print(f"  {i+1}. {item.get('label', 'No label')}")
                if 'data' in item and 'copilot_uuid' in item['data']:
                    uuid = item['data']['copilot_uuid']
                    assert uuid and len(uuid) > 10, f"Completion item {i+1} must have valid Copilot UUID"
                    print(f"     UUID: {uuid[:8]}...")
        else:
            print("❌ No completions returned")
        
    finally:
        tester.cleanup()
        os.unlink(temp_file)


def test_document_changes():
    """Test document change notifications"""
    tester = LSPBridgeTester()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import os\n")
        temp_file = f.name
    
    try:
        tester.start_bridge()
        
        # Initialize
        tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        })
        tester.notify("initialized", {})
        
        # Open file
        tester.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{temp_file}",
                "languageId": "python",
                "version": 1,
                "text": "import os\n"
            }
        })
        
        # Change document - add new function
        new_text = "import os\n\ndef new_function():\n    "
        tester.notify("textDocument/didChange", {
            "textDocument": {"uri": f"file://{temp_file}", "version": 2},
            "contentChanges": [{"text": new_text}]
        })
        
        time.sleep(2)
        
        # Request completion at new position
        response = tester.request("textDocument/completion", {
            "textDocument": {"uri": f"file://{temp_file}"},
            "position": {"line": 3, "character": 4}
        })
        
        print(f"After change completion: {json.dumps(response, indent=2)}")
        
        if "result" in response and response["result"].get("items"):
            items = response["result"]["items"]
            print(f"Got {len(items)} completion items after change")
        
    finally:
        tester.cleanup()
        os.unlink(temp_file)


def test_multiple_completion_positions():
    """Test completions at different positions"""
    tester = LSPBridgeTester()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write("function calculateTotal(items) {\n    \n}")
        temp_file = f.name
    
    try:
        tester.start_bridge()
        
        # Initialize
        tester.request("initialize", {
            "processId": 12345,
            "rootUri": f"file://{os.getcwd()}",
            "capabilities": {"textDocument": {"completion": {}}}
        })
        tester.notify("initialized", {})
        
        # Open JavaScript file
        tester.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{temp_file}",
                "languageId": "javascript",
                "version": 1,
                "text": "function calculateTotal(items) {\n    \n}"
            }
        })
        
        time.sleep(2)
        
        # Test different positions
        positions = [
            {"line": 0, "character": 0, "desc": "start of file"},
            {"line": 1, "character": 4, "desc": "function body"},
            {"line": 2, "character": 1, "desc": "end of function"}
        ]
        
        for pos in positions:
            response = tester.request("textDocument/completion", {
                "textDocument": {"uri": f"file://{temp_file}"},
                "position": {"line": pos["line"], "character": pos["character"]}
            })
            
            assert "result" in response, f"Bridge must return LSP completion response for {pos['desc']}"
            assert "items" in response["result"], f"Completion result must contain items array for {pos['desc']}"
            
            items = response["result"]["items"]
            print(f"Completion at {pos['desc']}: {len(items)} items")
            
            if items:
                for i, item in enumerate(items):
                    assert "label" in item, f"Item {i+1} at {pos['desc']} must have label"
                    assert "insertText" in item, f"Item {i+1} at {pos['desc']} must have insertText"
        
    finally:
        tester.cleanup()
        os.unlink(temp_file)