// The site's server: the files of view/ over HTTP, compressed, and nothing else yet. No
// dependencies. It is the place a conversational interface and a request for a run would be added.
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import zlib from 'node:zlib'
const ROOT = path.resolve(process.env.SITE_ROOT || path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'view')), PORT = Number(process.env.PORT || 8000)
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json', '.bin': 'application/octet-stream', '.css': 'text/css; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml' }
const SQUEEZE = new Set(['.html', '.js', '.mjs', '.json', '.bin', '.css', '.svg'])
http.createServer((req, res) => {
  let rel = decodeURIComponent((req.url || '/').split('?')[0]); if (rel.endsWith('/')) rel += 'index.html'
  const file = path.resolve(ROOT, '.' + rel)
  if (!file.startsWith(ROOT + path.sep) || /\/(tools|prepare\.py|window\.json)/.test(rel)) { res.statusCode = 404; return res.end('not found') }
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) { res.statusCode = 404; return res.end('not found') }
    const ext = path.extname(file); res.setHeader('Content-Type', TYPES[ext] || 'application/octet-stream'); res.setHeader('Cache-Control', 'no-cache'); res.setHeader('Vary', 'Accept-Encoding')
    res.setHeader('ETag', `"${st.size}-${Math.floor(st.mtimeMs)}"`)
    if (req.headers['if-none-match'] === res.getHeader('ETag')) { res.statusCode = 304; return res.end() }
    if (SQUEEZE.has(ext) && /\bgzip\b/.test(req.headers['accept-encoding'] || '')) { res.setHeader('Content-Encoding', 'gzip'); fs.createReadStream(file).pipe(zlib.createGzip({ level: 6 })).pipe(res) }
    else { res.setHeader('Content-Length', st.size); fs.createReadStream(file).pipe(res) }
  })
}).listen(PORT, '0.0.0.0', () => console.log(`sausalito view on :${PORT}, serving ${ROOT}`))
