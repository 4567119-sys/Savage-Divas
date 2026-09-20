// Small dependency-free server for the static demo portals.
const http = require('http');
const fs = require('fs');
const path = require('path');

const root = __dirname;
const port = Number(process.env.PORT || 5173);
const mime = { '.css': 'text/css', '.html': 'text/html', '.jpg': 'image/jpeg', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.webmanifest': 'application/manifest+json' };

http.createServer((request, response) => {
  const requestPath = decodeURIComponent((request.url || '/').split('?')[0]);
  const relativePath = requestPath === '/' ? 'index.html' : requestPath.replace(/^[/\\]+/, '');
  const filePath = path.resolve(root, relativePath);
  if (!filePath.startsWith(root + path.sep)) {
    response.writeHead(403); response.end('Forbidden'); return;
  }
  fs.readFile(filePath, (error, data) => {
    if (error) { response.writeHead(error.code === 'ENOENT' ? 404 : 500); response.end(error.code === 'ENOENT' ? 'Not found' : 'Server error'); return; }
    response.writeHead(200, { 'Content-Type': `${mime[path.extname(filePath).toLowerCase()] || 'application/octet-stream'}; charset=utf-8` });
    response.end(data);
  });
}).listen(port, '127.0.0.1', () => console.log(`Royal Square demo is running at http://localhost:${port}`));
