import { App } from '@modelcontextprotocol/ext-apps';

const app = new App({ name: 'Big Research', version: '2.1.1' }, {});
app.ontoolresult = result => {
  if (result.structuredContent?.project) window.researchWorkspace.update(result.structuredContent);
};
app.onerror = error => { document.getElementById('notice').textContent = error.message; };
try {
  await app.connect();
  window.researchWorkspace.connect({
    send: text => app.sendMessage({ role: 'user', content: [{ type: 'text', text }] }),
    refresh: async () => {
      const project = window.researchWorkspace.current().workspace;
      if (!project) throw new Error('Open the project from the conversation first.');
      const result = await app.callServerTool({ name: 'workspace_status', arguments: { project } });
      if (result.isError) throw new Error('Refresh failed; inspect the tool response in the conversation.');
      return result.structuredContent;
    },
  });
} catch (error) {
  document.getElementById('notice').textContent = 'Read-only view / 只读视图: ' + error.message;
}
