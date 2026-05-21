"""
server.py — Tron Dashboard Server
Serve o dashboard com atualização automática de dados (Meta Ads + Nectar CRM).

Uso:    python server.py
Acesse: http://localhost:8080

Atualiza os dados automaticamente a cada 5 minutos.
"""

import sys, os, json, threading, time
from datetime import datetime, date

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from flask import Flask, jsonify, send_from_directory, Response
except ImportError:
    os.system(f"{sys.executable} -m pip install flask -q")
    from flask import Flask, jsonify, send_from_directory, Response

# Importa as funções de fetch do update_dashboard.py
DESKTOP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DESKTOP)
import update_dashboard as ud

# ─────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=DESKTOP, static_url_path="")

REFRESH_INTERVAL = 300  # segundos entre atualizações automáticas

# ─────────────────────────────────────────────────────────
# CACHE (thread-safe)
# ─────────────────────────────────────────────────────────
_cache = {
    "data":       None,
    "updated_at": None,
    "loading":    False,
    "error":      None,
    "next_at":    None,   # timestamp da próxima atualização
}
_lock = threading.Lock()


def _merge_campaigns(budgets):
    """Monta o objeto CAMPAIGNS com budgets reais incluídos."""
    result = {}
    for code, meta in ud.CAMPAIGN_META.items():
        result[code] = {
            "label":  meta["label"],
            "color":  meta["color"],
            "budget": budgets.get(code, 0),
        }
    return result


def do_refresh():
    """Busca todos os dados e atualiza o cache. Thread-safe."""
    with _lock:
        if _cache["loading"]:
            return
        _cache["loading"] = True
        _cache["error"]   = None

    try:
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{ts}] Iniciando atualização de dados...")

        all_dates, all_data = ud.fetch_daily_data()
        adsets              = ud.fetch_adsets()
        adset_metrics       = ud.fetch_adset_metrics()
        creatives           = ud.fetch_creatives()
        nectar              = ud.fetch_nectar_leadboard()
        budgets             = ud.calc_budgets(adsets)

        total_budget = ud.fetch_total_daily_budget()
        data = {
            "campaigns":          _merge_campaigns(budgets),
            "all_dates":          all_dates,
            "all_data":           all_data,
            "adsets_raw":         adsets,
            "adset_metrics":      adset_metrics,
            "creatives":          creatives,
            "nectar_leadboard":   nectar,
            "total_daily_budget": total_budget,
        }

        updated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

        with _lock:
            _cache["data"]                        = data
            _cache["updated_at"]                  = updated_at
            _cache["loading"]                     = False
            _cache["next_at"]                     = time.time() + REFRESH_INTERVAL
            if _cache["data"]:
                _cache["data"]["total_daily_budget"] = total_budget

        # Também atualiza o HTML estático para uso offline
        js_block = ud.build_js_block(
            all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar,
            total_budget=total_budget
        )
        ud.update_html(js_block)

        print(f"[{updated_at}] Dados atualizados com sucesso.")

    except Exception as e:
        with _lock:
            _cache["loading"] = False
            _cache["error"]   = str(e)
        print(f"ERRO ao atualizar: {e}")


def _background_loop():
    do_refresh()                        # primeira carga imediata
    while True:
        time.sleep(REFRESH_INTERVAL)
        do_refresh()


# ─────────────────────────────────────────────────────────
# ROTAS
# ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(DESKTOP, "dashboard.html")


@app.route("/api/data")
def api_data():
    with _lock:
        nxt  = _cache["next_at"]
        secs = max(0, int(nxt - time.time())) if nxt else 0
        return jsonify({
            "data":         _cache["data"],
            "updated_at":   _cache["updated_at"],
            "loading":      _cache["loading"],
            "error":        _cache["error"],
            "next_in_secs": secs,
        })


@app.route("/api/status")
def api_status():
    with _lock:
        nxt  = _cache["next_at"]
        secs = max(0, int(nxt - time.time())) if nxt else 0
        return jsonify({
            "loading":      _cache["loading"],
            "updated_at":   _cache["updated_at"],
            "error":        _cache["error"],
            "next_in_secs": secs,
        })


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    t = threading.Thread(target=do_refresh, daemon=True)
    t.start()
    return jsonify({"ok": True})


@app.route("/api/budget")
def api_budget():
    """Busca o total de verba diária direto da Meta API (sem cache)."""
    try:
        total = ud.fetch_total_daily_budget()
        # Atualiza o cache em tempo real
        with _lock:
            if _cache["data"]:
                _cache["data"]["total_daily_budget"] = total
        return jsonify({"total_daily_budget": total, "ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Tron — Dashboard Server")
    print("  http://localhost:8080")
    print(f"  Atualização automática a cada {REFRESH_INTERVAL // 60} minutos")
    print("=" * 60)

    t = threading.Thread(target=_background_loop, daemon=True)
    t.start()

    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)
