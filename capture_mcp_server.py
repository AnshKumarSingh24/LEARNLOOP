#!/usr/bin/env python3
"""
CAPTURE — Model Context Protocol (MCP) Server
Thin, robust JSON-RPC 2.0 wrapper around the Agentic Context Orchestrator.
Directly executes orchestrator.orchestrate(...) with full agent tracing,
authority gating, entity coreference, and token reduction metrics.
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any, Optional, List

# Add capture_api directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.join(SCRIPT_DIR, "capture_api") if not os.path.basename(SCRIPT_DIR) == "capture_api" else SCRIPT_DIR
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    from capture_api.services.orchestrator import orchestrate, OrchestratorResult
    from capture_api.services.db import get_db
    from capture_api.dependencies import get_supabase_client
except ImportError:
    from services.orchestrator import orchestrate, OrchestratorResult  # type: ignore
    from services.db import get_db  # type: ignore
    from dependencies import get_supabase_client  # type: ignore

TOOLS_SPEC = [
    {
        "name": "get_context_pack",
        "description": "Calls the Master Context Orchestrator to assemble the Minimum Sufficient Context Pack for a goal, including authority gating, entity coreference, contradiction detection, and reduction metrics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "User goal, question, or task specification"
                },
                "space_id": {
                    "type": "string",
                    "description": "Optional space UUID to scope the context assembly"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum token budget for assembled pack (default: 4000)",
                    "default": 4000
                }
            },
            "required": ["goal"]
        }
    },
    {
        "name": "resolve_entity",
        "description": "Resolves a raw mention to its canonical entity record and aliases across live database captures.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mention": {
                    "type": "string",
                    "description": "Entity mention or alias to look up or resolve"
                }
            },
            "required": ["mention"]
        }
    },
    {
        "name": "report_contradiction",
        "description": "Records a newly discovered cross-source conflict into the live contradiction review ledger.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_a": {"type": "string", "description": "First conflicting source name or ID"},
                "source_b": {"type": "string", "description": "Second conflicting source name or ID"},
                "conflicting_field": {"type": "string", "description": "Field or statement in conflict (e.g. 'Deadline')"},
                "explanation": {"type": "string", "description": "Detailed explanation of the disagreement"}
            },
            "required": ["source_a", "source_b", "conflicting_field", "explanation"]
        }
    },
    {
        "name": "capture_add_memory",
        "description": "Ingests a new raw memory, document snippet, or decision into the live database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Raw text content"},
                "title": {"type": "string", "description": "Optional title for capture"},
                "space_id": {"type": "string", "description": "Optional target space ID"}
            },
            "required": ["content"]
        }
    }
]

async def handle_rpc_request(req: Dict[str, Any]) -> Dict[str, Any]:
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": "capture-orchestrator-mcp-server",
                    "version": "4.0.0",
                    "description": "Thin MCP wrapper around Master Context Orchestrator"
                }
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_SPEC}
        }

    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})

        if name == "get_context_pack":
            goal = args.get("goal", "")
            space_id = args.get("space_id")
            max_tokens = args.get("max_tokens", 4000)
            
            supabase = get_supabase_client()
            user_id = "00000000-0000-0000-0000-000000000000"

            # Execute Master Orchestrator
            orch_result: OrchestratorResult = await orchestrate(
                supabase=supabase,
                user_id=user_id,
                goal_text=goal,
                space_id=space_id,
                max_tokens=max_tokens
            )

            # Return serialized ContextPack + Agent Trace
            output_payload = {
                "status": "SUCCESS",
                "goal": goal,
                "context_pack": orch_result.context_pack.dict() if hasattr(orch_result.context_pack, "dict") else orch_result.context_pack,
                "pipeline_log": orch_result.pipeline_log,
                "agent_trace": orch_result.agent_trace
            }

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(output_payload, indent=2, default=str)}]
                }
            }

        elif name == "resolve_entity":
            mention = args.get("mention", "")
            db = get_db()
            all_entities = list(db.resolved_entities.values())
            matches = [e for e in all_entities if mention.lower() in e.get("canonical_name", "").lower() or any(mention.lower() in a.lower() for a in e.get("aliases", []))]
            
            res_obj = matches[0] if matches else {
                "canonical_name": mention,
                "aliases": [mention],
                "status": "live_unresolved_mention"
            }
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res_obj, indent=2, default=str)}]
                }
            }

        elif name == "report_contradiction":
            db = get_db()
            created = db.create_contradiction(
                space_id=args.get("space_id", "default"),
                capture_a_id=args.get("source_a"),
                capture_b_id=args.get("source_b"),
                conflicting_field=args.get("conflicting_field"),
                description=args.get("explanation"),
                contradiction_type="conflicting_requirement",
                severity="high"
            )
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": f"Logged live contradiction ID {created['id']} for review."}]
                }
            }

        elif name == "capture_add_memory":
            db = get_db()
            demo_user = "00000000-0000-0000-0000-000000000000"
            content = args.get("content", "")
            title = args.get("title", content[:30] + "...")
            space_id = args.get("space_id")
            
            cap = db.create_capture(
                user_id=demo_user,
                original_content=content,
                capture_type="text",
                title=title,
                source_type="mcp_agent",
                space_ids=[space_id] if space_id else []
            )
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": f"Successfully persisted capture '{title}' (ID: {cap['id']}) into live store."}]
                }
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Tool '{name}' not found"}
            }

    return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

async def async_main():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        try:
            line = await reader.readline()
            if not line:
                break
            line_str = line.decode("utf-8").strip()
            if not line_str:
                continue
            req = json.loads(line_str)
            res = await handle_rpc_request(req)
            sys.stdout.write(json.dumps(res, default=str) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_res = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
