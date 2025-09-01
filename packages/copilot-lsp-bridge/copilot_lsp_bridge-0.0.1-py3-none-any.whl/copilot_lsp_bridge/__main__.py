#!/usr/bin/env python3
"""
Copilot LSP Bridge
Translates standard LSP completion requests to Copilot's inlineCompletion protocol.
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional

from pygls.server import LanguageServer
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    ExecuteCommandParams,
    InitializeParams,
    InsertTextFormat,
    MessageType,
    Position,
    Range,
    TextDocumentIdentifier,
    TextDocumentItem,
    VersionedTextDocumentIdentifier,
)


class CopilotClient:
    """Async Copilot LSP client"""
    
    def __init__(self, server_path: str = "copilot-language-server"):
        self.server_path = server_path
        self.proc = None
        self.msg_id = 0
        self.lock = threading.Lock()
        self.notifications = []
        self.responses = {}
        self.authenticated = False
        self.logger = logging.getLogger("copilot-client")
        
    async def start(self):
        """Start Copilot subprocess"""
        self.logger.info(f"Starting Copilot server: {self.server_path}")
        try:
            self.proc = subprocess.Popen(
                [self.server_path, "--stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.logger.info(f"Copilot subprocess started with PID: {self.proc.pid}")
        except Exception as e:
            self.logger.error(f"Failed to start Copilot subprocess: {e}")
            raise
        
        # Start reader thread
        threading.Thread(target=self._reader_thread, daemon=True).start()
        
        # Initialize Copilot
        await self._initialize()
        
    def _reader_thread(self):
        """Read responses from Copilot server"""
        while self.proc and self.proc.poll() is None:
            try:
                headers = {}
                while True:
                    line = self.proc.stdout.readline().decode("utf-8")
                    if not line.strip():
                        break
                    if ": " in line:
                        key, value = line.strip().split(": ", 1)
                        headers[key.lower()] = value
                
                length = int(headers.get("content-length", 0))
                if length == 0:
                    continue
                    
                content = self.proc.stdout.read(length)
                resp = json.loads(content.decode("utf-8"))
                
                self.logger.debug(f"Received from Copilot: {json.dumps(resp, indent=2)}")
                
                if "method" in resp and "params" in resp:
                    with self.lock:
                        self.notifications.append(resp)
                        self.logger.debug(f"Added notification: {resp['method']}")
                else:
                    with self.lock:
                        self.responses[resp.get("id")] = resp
                        self.logger.debug(f"Added response for ID {resp.get('id')}")
                        
            except Exception as e:
                self.logger.error(f"Reader thread error: {e}")
                break
    
    def _send(self, msg: Dict[str, Any]):
        """Send message to Copilot server"""
        if not self.proc:
            self.logger.error("Cannot send message - no process")
            return
            
        self.logger.debug(f"Sending to Copilot: {json.dumps(msg, indent=2)}")
        payload = json.dumps(msg, separators=(",", ":")).encode("utf-8")
        header = f"Content-Length: {len(payload)}\r\n\r\n".encode("utf-8")
        self.proc.stdin.write(header)
        self.proc.stdin.write(payload)
        self.proc.stdin.flush()
    
    async def request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send request and wait for response"""
        self.msg_id += 1
        msg = {"jsonrpc": "2.0", "id": self.msg_id, "method": method, "params": params or {}}
        self.logger.debug(f"Sending request {self.msg_id}: {method}")
        self._send(msg)
        
        # Wait for response
        timeout = 30
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                if self.msg_id in self.responses:
                    resp = self.responses.pop(self.msg_id)
                    self.logger.debug(f"Got response for {self.msg_id}: {json.dumps(resp, indent=2)}")
                    return resp
            await asyncio.sleep(0.01)
        
        self.logger.error(f"Request {method} timed out after {timeout}s")
        raise TimeoutError(f"Request {method} timed out")
    
    def notify(self, method: str, params: Optional[Dict[str, Any]] = None):
        """Send notification"""
        msg = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        self._send(msg)
    
    async def _initialize(self):
        """Initialize Copilot and handle authentication"""
        self.logger.info("Initializing Copilot LSP client")
        
        init_params = {
            "processId": os.getpid(),
            "workspaceFolders": [{"uri": f"file://{os.getcwd()}"}],
            "capabilities": {
                "workspace": {"workspaceFolders": True},
                "textDocument": {
                    "completion": {
                        "completionItem": {
                            "snippetSupport": True,
                            "commitCharactersSupport": True,
                            "documentationFormat": ["markdown", "plaintext"],
                            "deprecatedSupport": True,
                            "preselectSupport": True
                        },
                        "completionItemKind": {
                            "valueSet": list(range(1, 26))
                        },
                        "contextSupport": True,
                        "insertTextMode": 1
                    },
                    "inlineCompletion": {
                        "dynamicRegistration": False
                    }
                }
            },
            "initializationOptions": {
                "editorInfo": {"name": "copilot-bridge", "version": "1.0"},
                "editorPluginInfo": {"name": "blink-cmp-bridge", "version": "1.0"}
            }
        }
        
        resp = await self.request("initialize", init_params)
        self.logger.info(f"Copilot initialize response: {json.dumps(resp, indent=2)}")
        
        self.notify("initialized")
        self.logger.info("Sent initialized notification to Copilot")
        
        # Wait for status notification like t.py does
        self.logger.info("Waiting for Copilot authentication status...")
        status = await self._wait_for_status(timeout=5)
        
        if status:
            status_kind = status["params"].get("kind")
            self.logger.info(f"Copilot status: {status_kind}")
            
            if status_kind == "Error":
                self.logger.warning("Copilot not authenticated, starting device flow...")
                auth_resp = await self.request("workspace/executeCommand", 
                                 {"command": "github.copilot.finishDeviceFlow"})
                self.logger.info(f"Device flow response: {auth_resp}")
                
                # Wait for Normal status
                status_ok = await self._wait_for_status(kind="Normal", timeout=60)
                if status_ok:
                    self.logger.info("Authentication completed successfully")
                    self.authenticated = True
                else:
                    self.logger.error("Authentication timed out!")
                    
            elif status_kind == "Normal":
                self.logger.info("Copilot already authenticated")
                self.authenticated = True
        else:
            self.logger.warning("No status notification received, assuming authenticated")
            self.authenticated = True
    
    async def _wait_for_status(self, kind=None, timeout=30):
        """Wait for status notification like t.py"""
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                for notification in self.notifications:
                    if notification.get("method") == "didChangeStatus":
                        status_kind = notification["params"].get("kind")
                        if kind is None or status_kind == kind:
                            return notification
            await asyncio.sleep(0.05)
        return None
    
    async def get_inline_completion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get inline completion from Copilot"""
        copilot_params = {
            "textDocument": params["textDocument"],
            "position": params["position"],
            "context": {"triggerKind": 1},
            "formattingOptions": {"tabSize": 4, "insertSpaces": True}
        }
        
        self.logger.info(f"Requesting inline completion: {json.dumps(copilot_params, indent=2)}")
        result = await self.request("textDocument/inlineCompletion", copilot_params)
        self.logger.info(f"Copilot inline completion response: {json.dumps(result, indent=2)}")
        return result


class CopilotBridge(LanguageServer):
    """LSP Bridge Server"""
    
    def __init__(self):
        super().__init__("copilot-bridge", "1.0.0")
        self.copilot_client = None
        self.logger = logging.getLogger("bridge")
    
    async def start_copilot(self):
        """Start Copilot client"""
        self.logger.info("Starting Copilot client...")
        try:
            self.copilot_client = CopilotClient()
            await self.copilot_client.start()
            self.logger.info("Copilot client started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start Copilot client: {e}")
            raise


# Create server instance
server = CopilotBridge()


@server.feature("initialize")
async def initialize(params: InitializeParams):
    """Initialize the bridge server"""
    await server.start_copilot()
    
    return {
        "capabilities": {
            "textDocumentSync": {"openClose": True, "change": 2},
            "completionProvider": {
                "triggerCharacters": [],
                "resolveProvider": False
            },
            "executeCommandProvider": {
                "commands": ["copilot.acceptCompletion"]
            }
        },
        "serverInfo": {"name": "Copilot Bridge", "version": "1.0.0"}
    }


@server.feature("textDocument/didOpen")
async def did_open(params):
    """Forward didOpen to Copilot"""
    if server.copilot_client:
        server.logger.info(f"Forwarding didOpen for {params.text_document.uri}")
        # Convert params object to dict for Copilot
        copilot_params = {
            "textDocument": {
                "uri": params.text_document.uri,
                "languageId": params.text_document.language_id,
                "version": params.text_document.version,
                "text": params.text_document.text
            }
        }
        server.copilot_client.notify("textDocument/didOpen", copilot_params)


@server.feature("textDocument/didChange") 
async def did_change(params):
    """Forward didChange to Copilot"""
    if server.copilot_client:
        server.logger.info(f"Forwarding didChange for {params.text_document.uri}")
        # Convert params object to dict for Copilot
        copilot_params = {
            "textDocument": {
                "uri": params.text_document.uri,
                "version": params.text_document.version
            },
            "contentChanges": [
                {"text": change.text} for change in params.content_changes
            ]
        }
        server.copilot_client.notify("textDocument/didChange", copilot_params)


@server.feature("textDocument/didClose")
async def did_close(params):
    """Forward didClose to Copilot"""
    if server.copilot_client:
        server.logger.info(f"Forwarding didClose for {params.text_document.uri}")
        # Convert params object to dict for Copilot
        copilot_params = {
            "textDocument": {
                "uri": params.text_document.uri
            }
        }
        server.copilot_client.notify("textDocument/didClose", copilot_params)


@server.feature("textDocument/completion")
async def completion(params: CompletionParams) -> CompletionList:
    """Convert completion request to inlineCompletion"""
    if not server.copilot_client:
        server.logger.warning("No Copilot client available")
        return CompletionList(is_incomplete=False, items=[])
    
    try:
        server.logger.info(f"Completion request for {params.text_document.uri} at {params.position.line}:{params.position.character}")
        
        # Convert to inlineCompletion request
        inline_params = {
            "textDocument": {"uri": params.text_document.uri},
            "position": {"line": params.position.line, "character": params.position.character},
            "context": {"triggerKind": 1},
            "formattingOptions": {"tabSize": 4, "insertSpaces": True}
        }
        
        copilot_resp = await server.copilot_client.get_inline_completion(inline_params)
        
        if "error" in copilot_resp:
            server.logger.warning(f"Copilot error: {copilot_resp['error']}")
            return CompletionList(is_incomplete=False, items=[])
        
        # Convert Copilot inline items to LSP completion items
        copilot_items = copilot_resp.get("result", {}).get("items", [])
        server.logger.info(f"Got {len(copilot_items)} completion items from Copilot")
        lsp_items = []
        
        for item in copilot_items:
            insert_text = item.get("insertText", "")
            completion_item = CompletionItem(
                label=insert_text[:50] + ("..." if len(insert_text) > 50 else ""),
                kind=CompletionItemKind.Text,
                insert_text=insert_text,
                insert_text_format=InsertTextFormat.PlainText,
                detail="Copilot suggestion",
                data={
                    "copilot_uuid": item.get("command", {}).get("arguments", [None])[0],
                    "copilot_range": item.get("range")
                }
            )
            
            # Handle textEdit if range provided
            if "range" in item:
                completion_item.text_edit = {
                    "range": item["range"],
                    "newText": insert_text
                }
            
            lsp_items.append(completion_item)
        
        return CompletionList(is_incomplete=False, items=lsp_items)
        
    except Exception as e:
        logging.error(f"Completion error: {e}")
        return CompletionList(is_incomplete=False, items=[])


@server.feature("workspace/executeCommand")
async def execute_command(params: ExecuteCommandParams):
    """Handle command execution"""
    if params.command == "copilot.acceptCompletion" and params.arguments:
        completion_data = params.arguments[0]
        copilot_uuid = completion_data.get("copilot_uuid")
        
        if copilot_uuid and server.copilot_client:
            try:
                await server.copilot_client.request("workspace/executeCommand", {
                    "command": "github.copilot.didAcceptCompletionItem",
                    "arguments": [copilot_uuid]
                })
                return True
            except Exception as e:
                logging.error(f"Accept completion error: {e}")
    
    return False


def main():
    from .__version__ import __version__
    
    parser = argparse.ArgumentParser(description="Copilot LSP Bridge")
    parser.add_argument("--version", action="version", version=f"copilot-lsp-bridge {__version__}")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Set logging level")
    parser.add_argument("--log-file", help="Log to file instead of stderr")
    args = parser.parse_args()
    
    # Setup logging
    log_config = {
        "level": getattr(logging, args.log_level),
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S"
    }
    
    if args.log_file:
        log_config["filename"] = args.log_file
    else:
        log_config["stream"] = sys.stderr
    
    logging.basicConfig(**log_config)
    
    logger = logging.getLogger("copilot-bridge")
    logger.info("Starting Copilot LSP Bridge")
    logger.info(f"Log level: {args.log_level}")
    if args.log_file:
        logger.info(f"Logging to file: {args.log_file}")
    
    server.start_io()


if __name__ == "__main__":
    main()