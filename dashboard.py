#!/usr/bin/env python3
"""
Trading Bot Web Dashboard — runs the bot in demo mode
and displays live results in a beautiful browser UI.
"""
import http.server
import json
import random
import time
import uuid
import threading
import webbrowser
from urllib.parse import parse_qs, urlparse

# ── Simulated market prices ──────────────────────────────────────────
MOCK_PRICES = {
    "BTCUSDT": 67432.50, "ETHUSDT": 3215.80, "SOLUSDT": 148.65,
    "BNBUSDT": 598.20, "XRPUSDT": 0.5234, "DOGEUSDT": 0.1567,
    "ADAUSDT": 0.4521, "AVAXUSDT": 35.72, "DOTUSDT": 7.15,
    "MATICUSDT": 0.7823, "LINKUSDT": 14.56, "LTCUSDT": 84.30,
}

order_history = []

# ── Price ticker simulation ─────────────────────────────────────────
live_prices = {k: v for k, v in MOCK_PRICES.items()}

def tick_prices():
    """Drift prices randomly every second."""
    while True:
        for sym in live_prices:
            drift = random.uniform(-0.002, 0.002)
            live_prices[sym] = round(live_prices[sym] * (1 + drift), 4)
        time.sleep(1)

threading.Thread(target=tick_prices, daemon=True).start()

# ── Order logic ──────────────────────────────────────────────────────
def simulate_order(symbol, side, order_type, quantity, price=None):
    symbol = symbol.upper().strip()
    side = side.upper()
    order_type = order_type.upper()

    base = live_prices.get(symbol, 100.0)
    slip = random.uniform(-0.0005, 0.0005)
    fill_price = round(base * (1 + slip), 4)
    if order_type == "LIMIT" and price:
        fill_price = float(price)

    order = {
        "order_id": random.randint(1_000_000_000, 9_999_999_999),
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": float(quantity),
        "price": fill_price,
        "status": "FILLED" if order_type == "MARKET" else "NEW",
        "client_id": f"x-demo-{uuid.uuid4().hex[:12]}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pnl": round(random.uniform(-50, 120), 2),
    }
    order_history.insert(0, order)
    return order

# ── HTML dashboard ───────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Trading Bot — Live Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0e1a;--surface:#111827;--card:#1a2236;--border:#1e293b;
  --accent:#6366f1;--accent2:#818cf8;--green:#22c55e;--red:#ef4444;
  --yellow:#eab308;--cyan:#06b6d4;--text:#e2e8f0;--muted:#64748b;
  --glass:rgba(99,102,241,.08);
}
html{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);overflow-x:hidden}
body{min-height:100vh}

/* ── HEADER ─────────────────── */
.header{
  background:linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#0f172a 100%);
  border-bottom:1px solid var(--border);
  padding:1.25rem 2rem;display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:50;backdrop-filter:blur(20px);
}
.header h1{font-size:1.35rem;font-weight:700;display:flex;align-items:center;gap:.6rem}
.header h1 span{background:linear-gradient(135deg,var(--accent),var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.badge{font-size:.65rem;background:var(--green);color:#000;padding:.2rem .55rem;border-radius:50px;font-weight:700;letter-spacing:.5px;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
.clock{font-family:'JetBrains Mono',monospace;color:var(--muted);font-size:.85rem}

/* ── LAYOUT ─────────────────── */
.container{max-width:1440px;margin:0 auto;padding:1.5rem 2rem 3rem}
.grid-top{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem}
.grid-main{display:grid;grid-template-columns:1fr 380px;gap:1.5rem}
@media(max-width:1024px){.grid-top{grid-template-columns:repeat(2,1fr)}.grid-main{grid-template-columns:1fr}}
@media(max-width:600px){.grid-top{grid-template-columns:1fr}}

/* ── STAT CARDS ─────────────── */
.stat-card{
  background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.15rem 1.3rem;
  position:relative;overflow:hidden;transition:transform .2s,box-shadow .2s;
}
.stat-card:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(99,102,241,.12)}
.stat-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--accent),var(--cyan));opacity:.7;
}
.stat-label{font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:.45rem}
.stat-value{font-size:1.55rem;font-weight:800;font-family:'JetBrains Mono',monospace}
.stat-sub{font-size:.7rem;color:var(--muted);margin-top:.3rem;display:flex;align-items:center;gap:.35rem}
.stat-sub .up{color:var(--green)}
.stat-sub .down{color:var(--red)}

/* ── PANELS ─────────────────── */
.panel{
  background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;
}
.panel-header{
  padding:1rem 1.3rem;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;
  background:linear-gradient(135deg,var(--glass),transparent);
}
.panel-header h2{font-size:.95rem;font-weight:700;display:flex;align-items:center;gap:.5rem}
.panel-body{padding:0}

/* ── TICKER STRIP ───────────── */
.ticker-wrap{overflow:hidden;background:var(--surface);border-bottom:1px solid var(--border);padding:.6rem 0}
.ticker{display:flex;gap:2rem;animation:scroll 30s linear infinite;white-space:nowrap;padding:0 1rem}
.ticker-item{font-family:'JetBrains Mono',monospace;font-size:.78rem;display:flex;gap:.5rem;align-items:center}
.ticker-sym{color:var(--accent2);font-weight:600}
@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}

/* ── TABLE ──────────────────── */
table{width:100%;border-collapse:collapse}
th{text-align:left;font-size:.7rem;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);padding:.75rem 1rem;font-weight:600;border-bottom:1px solid var(--border);background:var(--glass)}
td{padding:.7rem 1rem;font-size:.82rem;border-bottom:1px solid rgba(30,41,59,.5);font-family:'JetBrains Mono',monospace}
tr{transition:background .15s}
tr:hover{background:var(--glass)}
.buy{color:var(--green);font-weight:600}
.sell{color:var(--red);font-weight:600}
.filled{color:var(--green);background:rgba(34,197,94,.1);padding:.15rem .5rem;border-radius:6px;font-size:.7rem;font-weight:600}
.new-status{color:var(--yellow);background:rgba(234,179,8,.1);padding:.15rem .5rem;border-radius:6px;font-size:.7rem;font-weight:600}
.empty-state{padding:3rem;text-align:center;color:var(--muted);font-size:.9rem}

/* ── ORDER FORM ─────────────── */
.form-section{padding:1.3rem}
.form-group{margin-bottom:1rem}
.form-group label{display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:.4rem;font-weight:600}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}
input,select{
  width:100%;background:var(--surface);border:1px solid var(--border);border-radius:10px;
  padding:.65rem .85rem;color:var(--text);font-family:'JetBrains Mono',monospace;font-size:.82rem;
  outline:none;transition:border-color .2s,box-shadow .2s;
}
input:focus,select:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(99,102,241,.15)}
select option{background:var(--surface)}
.btn{
  width:100%;padding:.8rem;border:none;border-radius:10px;font-family:'Inter',sans-serif;
  font-weight:700;font-size:.85rem;cursor:pointer;transition:all .2s;text-transform:uppercase;letter-spacing:1px;
  position:relative;overflow:hidden;
}
.btn-buy{background:linear-gradient(135deg,#16a34a,#22c55e);color:#fff}
.btn-buy:hover{box-shadow:0 0 25px rgba(34,197,94,.35);transform:translateY(-1px)}
.btn-sell{background:linear-gradient(135deg,#dc2626,#ef4444);color:#fff}
.btn-sell:hover{box-shadow:0 0 25px rgba(239,68,68,.35);transform:translateY(-1px)}
.btn:active{transform:scale(.98)}
.btn-row{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-top:1.2rem}
.btn .ripple{position:absolute;border-radius:50%;background:rgba(255,255,255,.25);transform:scale(0);animation:rippleAnim .6s ease-out}
@keyframes rippleAnim{to{transform:scale(4);opacity:0}}

/* ── PRICE CARDS ────────────── */
.price-grid{display:grid;grid-template-columns:1fr 1fr;gap:.5rem;padding:1rem 1.3rem}
.price-card{
  background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:.7rem .85rem;
  transition:all .2s;cursor:default;
}
.price-card:hover{border-color:var(--accent);background:var(--glass)}
.price-card .sym{font-size:.72rem;color:var(--accent2);font-weight:700;letter-spacing:.5px}
.price-card .val{font-size:1rem;font-weight:700;font-family:'JetBrains Mono',monospace;margin-top:.15rem}
.price-card .chg{font-size:.65rem;margin-top:.1rem;font-weight:600}

/* ── TOAST ──────────────────── */
.toast-container{position:fixed;top:5rem;right:1.5rem;z-index:999;display:flex;flex-direction:column;gap:.5rem}
.toast{
  background:var(--card);border:1px solid var(--border);border-left:4px solid var(--green);
  border-radius:10px;padding:.85rem 1.2rem;min-width:300px;
  animation:slideIn .4s cubic-bezier(.16,1,.3,1);
  box-shadow:0 10px 40px rgba(0,0,0,.4);
}
.toast.sell-toast{border-left-color:var(--red)}
.toast-title{font-size:.78rem;font-weight:700;margin-bottom:.2rem}
.toast-msg{font-size:.72rem;color:var(--muted);font-family:'JetBrains Mono',monospace}
@keyframes slideIn{from{transform:translateX(120%);opacity:0}to{transform:translateX(0);opacity:1}}
@keyframes slideOut{from{transform:translateX(0);opacity:1}to{transform:translateX(120%);opacity:0}}

/* ── CHART (CSS-only sparkline) */
.mini-chart{display:flex;align-items:flex-end;gap:2px;height:48px;padding:1rem 1.3rem}
.mini-chart .bar{flex:1;background:linear-gradient(to top,var(--accent),var(--cyan));border-radius:3px 3px 0 0;min-width:3px;transition:height .5s cubic-bezier(.16,1,.3,1);opacity:.7}
.mini-chart .bar:hover{opacity:1}
</style>
</head>
<body>

<!-- TICKER STRIP -->
<div class="ticker-wrap">
  <div class="ticker" id="ticker"></div>
</div>

<!-- HEADER -->
<div class="header">
  <h1>⚡ <span>Trading Bot</span> <span class="badge">DEMO LIVE</span></h1>
  <div class="clock" id="clock"></div>
</div>

<div class="container">

  <!-- STAT CARDS -->
  <div class="grid-top">
    <div class="stat-card">
      <div class="stat-label">Total Orders</div>
      <div class="stat-value" id="s-total">0</div>
      <div class="stat-sub">Session trades</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Volume (USDT)</div>
      <div class="stat-value" id="s-volume">$0.00</div>
      <div class="stat-sub"><span class="up">▲</span> Simulated volume</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Win Rate</div>
      <div class="stat-value" id="s-winrate">—</div>
      <div class="stat-sub">Positive P&L trades</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Net P&L</div>
      <div class="stat-value" id="s-pnl">$0.00</div>
      <div class="stat-sub" id="s-pnl-sub">Unrealized</div>
    </div>
  </div>

  <!-- MAIN -->
  <div class="grid-main">
    <!-- LEFT: Orders table -->
    <div class="panel">
      <div class="panel-header">
        <h2>📋 Order History</h2>
        <span style="font-size:.72rem;color:var(--muted)" id="order-count">0 orders</span>
      </div>
      <!-- Mini chart -->
      <div class="mini-chart" id="mini-chart"></div>
      <div class="panel-body">
        <table>
          <thead><tr><th>Time</th><th>Symbol</th><th>Side</th><th>Type</th><th>Qty</th><th>Price</th><th>Status</th><th>P&L</th></tr></thead>
          <tbody id="order-tbody"><tr><td colspan="8" class="empty-state">No orders yet — place your first trade →</td></tr></tbody>
        </table>
      </div>
    </div>

    <!-- RIGHT: Form + Prices -->
    <div style="display:flex;flex-direction:column;gap:1.5rem">
      <!-- Order form -->
      <div class="panel">
        <div class="panel-header"><h2>🚀 New Order</h2></div>
        <div class="form-section">
          <div class="form-group">
            <label>Symbol</label>
            <select id="f-symbol">
              <option>BTCUSDT</option><option>ETHUSDT</option><option>SOLUSDT</option>
              <option>BNBUSDT</option><option>XRPUSDT</option><option>DOGEUSDT</option>
              <option>ADAUSDT</option><option>AVAXUSDT</option><option>DOTUSDT</option>
              <option>LINKUSDT</option><option>LTCUSDT</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Order Type</label>
              <select id="f-type"><option value="MARKET">Market</option><option value="LIMIT">Limit</option></select>
            </div>
            <div class="form-group">
              <label>Quantity</label>
              <input type="number" id="f-qty" value="0.01" step="0.001" min="0.001"/>
            </div>
          </div>
          <div class="form-group" id="price-group" style="display:none">
            <label>Limit Price (USDT)</label>
            <input type="number" id="f-price" placeholder="0.00" step="0.01"/>
          </div>
          <div class="btn-row">
            <button class="btn btn-buy" onclick="placeOrder('BUY')">Buy / Long</button>
            <button class="btn btn-sell" onclick="placeOrder('SELL')">Sell / Short</button>
          </div>
        </div>
      </div>

      <!-- Live prices -->
      <div class="panel">
        <div class="panel-header"><h2>📊 Live Prices</h2></div>
        <div class="price-grid" id="price-grid"></div>
      </div>
    </div>
  </div>
</div>

<!-- Toasts -->
<div class="toast-container" id="toasts"></div>

<script>
// ── Clock ───────────────────────────────────────────────────────────
function updateClock(){document.getElementById('clock').textContent=new Date().toLocaleString('en-US',{weekday:'short',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false})}
setInterval(updateClock,1000);updateClock();

// ── Prices ──────────────────────────────────────────────────────────
let prices={};
let prevPrices={};
async function fetchPrices(){
  try{const r=await fetch('/api/prices');prices=await r.json();renderPrices();renderTicker();prevPrices={...prices}}catch(e){}
}
function renderPrices(){
  const g=document.getElementById('price-grid');
  g.innerHTML=Object.entries(prices).map(([s,p])=>{
    const prev=prevPrices[s]||p;const pct=((p-prev)/prev*100).toFixed(2);
    const cls=pct>=0?'up':'down';const arrow=pct>=0?'▲':'▼';
    return `<div class="price-card"><div class="sym">${s}</div><div class="val">$${p.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:4})}</div><div class="chg ${cls}">${arrow} ${Math.abs(pct)}%</div></div>`
  }).join('');
}
function renderTicker(){
  const items=Object.entries(prices).map(([s,p])=>{
    const prev=prevPrices[s]||p;const cls=p>=prev?'up':'down';
    return `<span class="ticker-item"><span class="ticker-sym">${s}</span><span class="${cls}">$${p.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:4})}</span></span>`
  }).join('');
  document.getElementById('ticker').innerHTML=items+items;
}
setInterval(fetchPrices,1500);fetchPrices();

// ── Show/hide limit price ───────────────────────────────────────────
document.getElementById('f-type').addEventListener('change',e=>{
  document.getElementById('price-group').style.display=e.target.value==='LIMIT'?'block':'none';
});

// ── Place order ─────────────────────────────────────────────────────
let orders=[];
async function placeOrder(side){
  const symbol=document.getElementById('f-symbol').value;
  const type=document.getElementById('f-type').value;
  const qty=document.getElementById('f-qty').value;
  const price=document.getElementById('f-price').value;
  const body=JSON.stringify({symbol,side,type,quantity:qty,price:price||null});
  try{
    const r=await fetch('/api/order',{method:'POST',headers:{'Content-Type':'application/json'},body});
    const order=await r.json();
    orders.unshift(order);
    renderOrders();updateStats();showToast(order);
  }catch(e){console.error(e)}
}
function renderOrders(){
  const tb=document.getElementById('order-tbody');
  if(!orders.length){tb.innerHTML='<tr><td colspan="8" class="empty-state">No orders yet</td></tr>';return}
  tb.innerHTML=orders.map(o=>`<tr>
    <td>${o.timestamp}</td>
    <td>${o.symbol}</td>
    <td class="${o.side.toLowerCase()}">${o.side}</td>
    <td>${o.type}</td>
    <td>${o.quantity}</td>
    <td>$${Number(o.price).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:4})}</td>
    <td><span class="${o.status==='FILLED'?'filled':'new-status'}">${o.status}</span></td>
    <td class="${o.pnl>=0?'buy':'sell'}">$${o.pnl.toFixed(2)}</td>
  </tr>`).join('');
  document.getElementById('order-count').textContent=`${orders.length} orders`;
  // chart
  const chart=document.getElementById('mini-chart');
  chart.innerHTML=orders.slice(0,40).reverse().map(o=>{const h=Math.max(4,Math.min(48,Math.abs(o.pnl)/2));return `<div class="bar" style="height:${h}px;background:${o.pnl>=0?'linear-gradient(to top,#16a34a,#22c55e)':'linear-gradient(to top,#dc2626,#ef4444)'}"></div>`}).join('');
}
function updateStats(){
  const total=orders.length;
  const vol=orders.reduce((s,o)=>s+o.price*o.quantity,0);
  const pnl=orders.reduce((s,o)=>s+o.pnl,0);
  const wins=orders.filter(o=>o.pnl>0).length;
  document.getElementById('s-total').textContent=total;
  document.getElementById('s-volume').textContent='$'+vol.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
  document.getElementById('s-winrate').textContent=total?((wins/total*100).toFixed(1)+'%'):'—';
  const pnlEl=document.getElementById('s-pnl');
  pnlEl.textContent=(pnl>=0?'+':'')+pnl.toFixed(2);
  pnlEl.style.color=pnl>=0?'var(--green)':'var(--red)';
  document.getElementById('s-pnl-sub').innerHTML=`<span class="${pnl>=0?'up':'down'}">${pnl>=0?'▲':'▼'}</span> Simulated P&L`;
}
function showToast(o){
  const c=document.getElementById('toasts');
  const t=document.createElement('div');
  t.className=`toast ${o.side==='SELL'?'sell-toast':''}`;
  t.innerHTML=`<div class="toast-title">✓ ${o.side} ${o.symbol}</div><div class="toast-msg">${o.quantity} @ $${Number(o.price).toLocaleString('en-US',{minimumFractionDigits:2})} — ${o.status}</div>`;
  c.appendChild(t);
  setTimeout(()=>{t.style.animation='slideOut .4s forwards';setTimeout(()=>t.remove(),400)},3500);
}
</script>
</body>
</html>"""


# ── HTTP SERVER ──────────────────────────────────────────────────────
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_): pass  # silence logs

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/prices":
            self._json(live_prices)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode())

    def do_POST(self):
        if urlparse(self.path).path == "/api/order":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            order = simulate_order(
                body["symbol"], body["side"], body["type"],
                body["quantity"], body.get("price")
            )
            self._json(order)
        else:
            self.send_response(404); self.end_headers()

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def main():
    PORT = 8888
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"\n  ⚡ Trading Bot Dashboard running at  http://localhost:{PORT}")
    print(f"  📊 Demo mode — no API keys required")
    print(f"  🛑 Press Ctrl+C to stop\n")
    webbrowser.open(f"http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
