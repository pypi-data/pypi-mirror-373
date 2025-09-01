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
import time
from typing import Any, Dict, List, Optional

from pygls.lsp.client import BaseLanguageClient as LanguageClient
from pygls.server import LanguageServer
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    ExecuteCommandParams,
    InitializeParams,
    InlineCompletionContext,
    InlineCompletionParams,
    InlineCompletionTriggerKind,
    InsertTextFormat,
    MessageType,
    Position,
    Range,
    TextDocumentIdentifier,
    TextDocumentItem,
    VersionedTextDocumentIdentifier,
)


class CopilotBridge(LanguageServer):
    """LSP Bridge Server"""

    def __init__(self):
        super().__init__("copilot-bridge", "1.0.0")
        self.copilot_client = None
        self.logger = logging.getLogger("bridge")
        self.authenticated = False


server = CopilotBridge()

@server.feature("initialize")
async def initialize(params: InitializeParams):
    """Initialize the bridge server"""
    
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


@server.feature("initialized")
async def initialized(params):
    """Start Copilot client after LSP initialization"""
    server.logger.info("Starting Copilot client after LSP initialization")
    try:
        client = LanguageClient("copilot-client", "1.0.0")
        await client.start_io("copilot-language-server", "--stdio")
        server.copilot_client = client
        server.logger.info("Copilot client started successfully")
    except Exception as e:
        server.logger.error(f"Failed to start Copilot client: {e}")
        server.copilot_client = None


@server.feature("textDocument/didOpen")
async def did_open(params):
    """Forward didOpen to Copilot"""
    if server.copilot_client:
        server.logger.info(f"Forwarding didOpen for {params.text_document.uri}")
        server.copilot_client.text_document_did_open(params)


@server.feature("textDocument/didChange") 
async def did_change(params):
    """Forward didChange to Copilot"""
    if server.copilot_client:
        server.logger.info(f"Forwarding didChange for {params.text_document.uri}")
        server.copilot_client.text_document_did_change(params)


@server.feature("textDocument/didClose")
async def did_close(params):
    """Forward didClose to Copilot"""
    if server.copilot_client:
        server.logger.info(f"Forwarding didClose for {params.text_document.uri}")
        server.copilot_client.text_document_did_close(params)


@server.feature("textDocument/completion")
async def completion(params: CompletionParams) -> CompletionList:
    """Convert completion request to inlineCompletion"""
    if not server.copilot_client:
        server.logger.warning("No Copilot client available")
        return CompletionList(is_incomplete=False, items=[])
    
    try:
        server.logger.info(f"Completion request for {params.text_document.uri} at {params.position.line}:{params.position.character}")
        
        # Convert to inlineCompletion request
        
        inline_params = InlineCompletionParams(
            text_document=TextDocumentIdentifier(uri=params.text_document.uri),
            position=Position(line=params.position.line, character=params.position.character),
            context=InlineCompletionContext(trigger_kind=InlineCompletionTriggerKind.Invoked)
        )
        
        copilot_resp = await server.copilot_client.text_document_inline_completion_async(inline_params)
        
        # Convert Copilot inline items to LSP completion items
        copilot_items = copilot_resp.items
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
                await server.copilot_client.workspace_execute_command_async({
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


    
# Create server instance

    # Start bridge server - Copilot will start on "initialized"
    server.start_io()


if __name__ == "__main__":
    main()
