"""Browser verification of static snapshots and the real bundled MCP Apps bridge."""

from __future__ import annotations

import functools
import http.server
import json
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

from big_research.core import Project
from big_research.views import render

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / ".cache/ui-check"
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="research-ui-") as tmp:
        directory = Path(tmp)
        project = Project.create(
            directory / "study",
            "A study <script>window.injected=true</script>",
            field="history",
            paradigm="interpretive",
            method_ids=["interpretive"],
        )
        (project.root / "artifacts/source.md").write_text("An inspected primary passage.", encoding="utf-8")
        project.record_evidence(
            {
                "id": "S1",
                "title": "Primary source",
                "kind": "source",
                "status": "verified",
                "path": "artifacts/source.md",
                "accessed": "2026-10-17",
                "locator": "paragraph 1",
            }
        )
        project.record_claim(
            {"id": "C1", "text": "A bounded reading", "status": "supported", "supports": ["S1"], "contradicts": []}
        )
        project.record_decision(
            {
                "id": "D1",
                "question": "Which direction?",
                "status": "pending",
                "options": ["Read context", "Compare readings"],
            }
        )
        project.record_candidate(
            {
                "id": "A",
                "title": "Contextual reading",
                "value": "Clarify context",
                "evidence": "S1",
                "cost": "One hour",
                "feasibility": "Available material",
            }
        )
        data = {**project.status(), "workspace": "study"}
        (directory / "static.html").write_text(render(data), encoding="utf-8")
        (directory / "interactive.html").write_text(render(interactive=True), encoding="utf-8")
        fixture = json.dumps(data).replace("<", "\\u003c")
        host = """<!doctype html><html><head><meta charset="utf-8"></head><body><iframe title="Research workspace" src="interactive.html" style="width:100%;height:1100px;border:0"></iframe><script>
const fixture=__FIXTURE__;window.messages=[];window.refreshes=0;
window.addEventListener('message',event=>{const frame=document.querySelector('iframe');if(event.source!==frame.contentWindow)return;const m=event.data;if(!m||m.jsonrpc!=='2.0')return;
const reply=result=>event.source.postMessage({jsonrpc:'2.0',id:m.id,result},event.origin);
if(m.method==='ui/initialize')reply({protocolVersion:m.params.protocolVersion,hostInfo:{name:'Big Research protocol test',version:'1'},hostCapabilities:{serverTools:{},message:{text:{}}},hostContext:{theme:'light',displayMode:'inline',availableDisplayModes:['inline'],locale:'zh-CN'}});
else if(m.method==='ui/notifications/initialized')event.source.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:{content:[],structuredContent:fixture}},event.origin);
else if(m.method==='tools/call'){window.refreshes++;fixture.project.title='Refreshed workspace';reply({content:[],structuredContent:fixture,isError:false});}
else if(m.method==='ui/message'){window.messages.push(m.params);reply({});}
else if(m.id!==undefined)reply({});});
</script></body></html>""".replace("__FIXTURE__", fixture)
        (directory / "host.html").write_text(host, encoding="utf-8")
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1280, "height": 900})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                base = f"http://127.0.0.1:{server.server_port}"
                page.goto(base + "/static.html")
                page.get_by_role("tab", name="论据 / Evidence").click()
                page.get_by_text("S1 · Primary source", exact=True).first.click()
                assert page.locator("details[open]").count() == 1
                assert page.evaluate("window.injected") is None
                page.evaluate(
                    "const data=window.researchWorkspace.current();data.project.title='制度文本如何分配权力？ / Reading institutional authority';window.researchWorkspace.update(data)"
                )
                page.get_by_role("tab", name="方案 / Compare").click()
                assert page.get_by_role("heading", name="A · Contextual reading").is_visible()
                page.locator("#filter").fill("no matching material")
                assert page.get_by_text("暂无匹配记录 / No matching records.").is_visible()
                page.locator("#filter").fill("")
                page.get_by_role("tab", name="决定与修订 / Decisions").click()
                assert page.get_by_role("heading", name="D1 · Which direction?").is_visible()
                assert page.get_by_role("button", name="刷新 / Refresh").is_disabled()
                page.get_by_role("tab", name="研究地图 / Map").click()
                page.screenshot(path=str(output / "workspace-desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                page.screenshot(path=str(output / "workspace-mobile.png"), full_page=True)
                page.set_viewport_size({"width": 1280, "height": 1000})
                page.goto(base + "/host.html")
                frame = page.frame_locator('iframe[title="Research workspace"]')
                frame.get_by_role("button", name="刷新 / Refresh").wait_for()
                page.wait_for_function(
                    "document.querySelector('iframe').contentWindow.document.getElementById('refresh').disabled === false"
                )
                frame.get_by_role("button", name="继续此任务 / Continue").first.click()
                page.wait_for_function("window.messages.length === 1")
                assert "frame" in page.evaluate("window.messages[0].content[0].text")
                frame.get_by_role("tab", name="决定与修订 / Decisions").click()
                frame.get_by_role("button", name="选择 / Choose: Read context").click()
                page.wait_for_function("window.messages.length === 2")
                assert "D1" in page.evaluate("window.messages[1].content[0].text")
                frame.get_by_role("button", name="刷新 / Refresh").click()
                frame.get_by_role("heading", name="Refreshed workspace", exact=True).wait_for()
                assert page.evaluate("window.refreshes") == 1
                assert not errors, errors
                page.screenshot(path=str(output / "workspace-interactive.png"), full_page=True)
                browser.close()
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
    print("Static views, text safety, mobile layout and real SDK bridge interactions passed.")


if __name__ == "__main__":
    main()
