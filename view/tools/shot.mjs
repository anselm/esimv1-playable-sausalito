// Headless screenshot of a WebGL page: node shot.mjs <url> <out.png> [width] [height]. WAIT_MS sets the wait (default 20000).
import { spawn } from 'node:child_process'
import { readdirSync, writeFileSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
const [url, out, w = '1500', h = '900'] = process.argv.slice(2)
const base = process.env.HOME + '/.cache/ms-playwright'
const dir = readdirSync(base).filter(d => d.startsWith('chromium-') && !d.includes('headless')).sort().pop()
const port = 9300 + Math.floor(Math.random() * 400)
const chrome = spawn(process.env.CHROME || `${base}/${dir}/chrome-linux64/chrome`, ['--headless=new', `--remote-debugging-port=${port}`, '--use-gl=angle', '--use-angle=vulkan', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', `--window-size=${w},${h}`, '--no-sandbox', '--no-first-run', `--user-data-dir=${mkdtempSync(tmpdir() + '/shot-')}`, 'about:blank'])
chrome.stderr.on('data', () => {})
const sleep = ms => new Promise(r => setTimeout(r, ms))
let page
for (let i = 0; i < 60 && !page; i++) { try { page = (await (await fetch(`http://localhost:${port}/json/list`)).json()).find(t => t.type === 'page') } catch {} if (!page) await sleep(250) }
const ws = new WebSocket(page.webSocketDebuggerUrl)
await new Promise(r => ws.addEventListener('open', r))
let id = 0; const pending = new Map(), logs = []
ws.addEventListener('message', e => { const m = JSON.parse(e.data)
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id) }
  if (m.method === 'Runtime.exceptionThrown') logs.push('EXC ' + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text || '').split('\n')[0])
  if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) logs.push(m.params.type + ' ' + m.params.args.map(a => a.value ?? a.description ?? '').join(' ').slice(0, 200)) })
const send = (method, params = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })) })
await send('Runtime.enable'); await send('Page.enable'); await send('Page.navigate', { url })
const t0 = Date.now(), limit = Number(process.env.WAIT_MS || 20000)
while (Date.now() - t0 < limit) { await sleep(500); const r = await send('Runtime.evaluate', { expression: 'document.title', returnByValue: true }); if (/\(drawn\)/.test(r.result?.value || '')) { await sleep(Number(process.env.SETTLE_MS || 1500)); break } }
const gl = await send('Runtime.evaluate', { expression: `(()=>{const c=document.createElement('canvas').getContext('webgl2');const e=c&&c.getExtension('WEBGL_debug_renderer_info');return e?c.getParameter(e.UNMASKED_RENDERER_WEBGL):'none'})()`, returnByValue: true })
const s = await send('Page.captureScreenshot', { format: 'png' })
writeFileSync(out, Buffer.from(s.data, 'base64'))
console.log(`${out}  ${((Date.now() - t0) / 1000).toFixed(1)} s  gl: ${gl.result?.value}  ${logs.length ? logs.slice(-6).join(' | ') : '(no page errors)'}`)
ws.close(); chrome.kill(); process.exit(0)
