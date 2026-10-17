import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPTests(unittest.TestCase):
    def test_real_stdio_workspace_and_resource(self):
        async def exercise(home):
            params = StdioServerParameters(
                command=sys.executable,
                args=["-m", "big_research.server"],
                env={**os.environ, "BIG_RESEARCH_HOME": home},
            )
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    names = {t.name: t for t in (await session.list_tools()).tools}
                    self.assertIn("workspace_record", names)
                    self.assertTrue(names["workspace_status"].annotations.readOnlyHint)
                    result = await session.call_tool(
                        "workspace_create",
                        {"project": "study", "title": "A human-led study", "method_ids": ["interpretive"]},
                    )
                    self.assertFalse(result.isError)
                    self.assertEqual(result.structuredContent["project"]["schema_version"], 2)
                    view = await session.read_resource("ui://big-research/workspace.html")
                    self.assertEqual(view.contents[0].mimeType, "text/html;profile=mcp-app")
                    self.assertIn("Big Research", view.contents[0].text)
                    blocked = await session.call_tool("workspace_open", {"project": "../outside"})
                    self.assertTrue(blocked.isError)
                    result = await session.call_tool(
                        "workspace_update", {"project": "study", "action": "configure", "payload": {"field": "history"}}
                    )
                    self.assertFalse(result.isError)
                    result = await session.call_tool(
                        "workspace_record",
                        {
                            "project": "study",
                            "kind": "decision",
                            "record": {"id": "D1", "question": "Which?", "status": "pending", "options": ["A", "B"]},
                        },
                    )
                    self.assertFalse(result.isError)
                    result = await session.call_tool("workspace_assess", {"project": "study"})
                    self.assertFalse(result.structuredContent["scientific_validity_certified"])
                    result = await session.call_tool("workspace_export", {"project": "study"})
                    self.assertTrue(Path(result.structuredContent["path"]).is_file())

        with tempfile.TemporaryDirectory() as temp:
            asyncio.run(exercise(temp))
