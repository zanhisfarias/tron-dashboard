"""
update_dashboard.py — Tron Meta Ads Dashboard
Puxa dados reais da API do Meta e atualiza o dashboard.html automaticamente.

Uso manual:    python update_dashboard.py
Agendado:      Tarefa do Windows Scheduler — toda segunda-feira às 08h
"""

import os
import sys
import json
import re
import time
import warnings
import calendar
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Força UTF-8 no terminal do Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")

try:
    import requests
except ImportError:
    print("Instalando requests...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

# ─────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────

ENV_FILE = r"C:\Users\Marketing\.claude\meta_ads_config.env"
DASHBOARD_HTML = r"C:\Users\Marketing\Desktop\Dashboard\dashboard.html"
API_BASE = "https://graph.facebook.com/v21.0"

# Carrega variáveis do .env
def load_env(path):
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

ENV = load_env(ENV_FILE)
TOKEN         = ENV["META_ACCESS_TOKEN"]
ACCOUNT       = ENV["META_AD_ACCOUNT_TRON"]
ACCOUNT_RV    = ENV.get("META_AD_ACCOUNT_TRON_RV", "act_250138776254796")
NECTAR_TOKEN  = ENV.get("NECTAR_API_TOKEN", "")
NECTAR_BASE   = "https://app.nectarcrm.com.br/crm/api/1"

LEADBOARD_STAGES = ["Contatos", "Qualificação", "Agendamento", "Qualificada", "Vendida"]

# Mapeamento campanha → código do dashboard
CAMPAIGN_IDS = {
    "MR":   "120241773113870686",
    "EMP":  "120240938082390686",
    "C01":  "120240938079060686",
    "C00":  "120238524414810686",
    "INST": "120242553041390686",
}

CAMPAIGN_META = {
    "MR":   {"label": "MR Contábil",     "color": "#6366F1"},
    "EMP":  {"label": "Empresarial",     "color": "#F59E0B"},
    "C01":  {"label": "Contábil 01",     "color": "#10B981"},
    "C00":  {"label": "Contábil 00",     "color": "#8B5CF6"},
    "INST": {"label": "Institucional",   "color": "#64748B"},
}

# Campanhas da conta Rio Verde
RV_CAMPAIGN_IDS = {
    "CONT_RV": "120247073560660700",
    "EMP_RV":  "120247073793960700",
}

RV_CAMPAIGN_META = {
    "CONT_RV": {"label": "Contábil RV",    "color": "#06B6D4"},
    "EMP_RV":  {"label": "Empresarial RV", "color": "#F97316"},
}

# ─────────────────────────────────────────────────────────
# HELPERS DE API
# ─────────────────────────────────────────────────────────

def api_get(path, params=None):
    """GET na Graph API com token automático."""
    p = {"access_token": TOKEN, **(params or {})}
    r = requests.get(f"{API_BASE}/{path}", params=p, timeout=30)
    r.raise_for_status()
    return r.json()

def get_leads(actions):
    """Extrai total de leads do array de actions."""
    for a in (actions or []):
        if a.get("action_type") == "lead":
            return int(a.get("value", 0))
    return 0

# ─────────────────────────────────────────────────────────
# 1. DADOS DIÁRIOS POR CAMPANHA (desde 01/01/2026)
# ─────────────────────────────────────────────────────────

def fetch_daily_data():
    """Retorna ALL_DATES e ALL_DATA desde 01/01/2026 até hoje."""
    today = date.today()
    since = date(2026, 1, 1)
    days_total = (today - since).days + 1
    date_range = {"since": since.isoformat(), "until": today.isoformat()}

    all_dates = [(since + timedelta(days=i)).isoformat() for i in range(days_total)]
    all_data  = {d: {} for d in all_dates}

    for code, camp_id in CAMPAIGN_IDS.items():
        print(f"  → Insights diários: {code} ({camp_id})...")
        cursor = None
        while True:
            params = {
                "fields": "date_start,impressions,clicks,spend,actions",
                "time_increment": "1",
                "time_range": json.dumps(date_range),
                "limit": "100",
            }
            if cursor:
                params["after"] = cursor
            try:
                resp = api_get(f"{camp_id}/insights", params)
            except Exception as e:
                print(f"    ERRO: {e}")
                break

            for row in resp.get("data", []):
                d     = row["date_start"]
                impr  = int(row.get("impressions", 0))
                click = int(row.get("clicks", 0))
                spend = float(row.get("spend", 0))
                leads = get_leads(row.get("actions"))
                ctr   = click / impr * 100 if impr else 0
                cpc   = spend / click if click else 0
                cpm   = spend / impr * 1000 if impr else 0
                cpl   = spend / leads if leads else 0

                if d not in all_data:
                    all_data[d] = {}
                all_data[d][code] = {
                    "leads": leads, "impr": impr, "clicks": click,
                    "spend": spend, "ctr": ctr, "cpc": cpc, "cpm": cpm, "cpl": cpl,
                }

            paging = resp.get("paging", {})
            cursor = paging.get("cursors", {}).get("after")
            if not paging.get("next"):
                break

    return all_dates, all_data

# ─────────────────────────────────────────────────────────
# 2. ADSETS DE TODAS AS CAMPANHAS
# ─────────────────────────────────────────────────────────

def fetch_adsets():
    """Retorna lista de adsets com id, name, budget, status, camp."""
    adsets = []
    for code, camp_id in CAMPAIGN_IDS.items():
        print(f"  → Adsets: {code}...")
        cursor = None
        while True:
            params = {
                "fields": "id,name,daily_budget,status",
                "limit": "50",
            }
            if cursor:
                params["after"] = cursor
            try:
                resp = api_get(f"{camp_id}/adsets", params)
            except Exception as e:
                print(f"    ERRO: {e}")
                break

            for a in resp.get("data", []):
                budget = int(a.get("daily_budget", 0)) // 100  # centavos → BRL
                adsets.append({
                    "id":     a["id"],
                    "camp":   code,
                    "name":   a["name"],
                    "budget": budget,
                    "status": "active" if a.get("status") == "ACTIVE" else "paused",
                })

            paging = resp.get("paging", {})
            cursor = paging.get("cursors", {}).get("after")
            if not paging.get("next"):
                break

    return adsets

# ─────────────────────────────────────────────────────────
# 3. MÉTRICAS POR ADSET (3 janelas de tempo)
# ─────────────────────────────────────────────────────────

def _fetch_adset_metrics_range(metrics, key, since_date, until_date, label):
    """Busca métricas de adset para um intervalo e armazena em metrics[aid][key]."""
    date_range = {"since": since_date.isoformat(), "until": until_date.isoformat()}
    print(f"  → Métricas por adset: {label}...")
    cursor = None
    while True:
        params = {
            "level":   "adset",
            "fields":  "adset_id,impressions,clicks,spend,actions",
            "time_range": json.dumps(date_range),
            "limit":   "100",
        }
        if cursor:
            params["after"] = cursor
        try:
            resp = api_get(f"{ACCOUNT}/insights", params)
        except Exception as e:
            print(f"    ERRO: {e}")
            break

        for row in resp.get("data", []):
            aid   = row["adset_id"]
            impr  = int(row.get("impressions", 0))
            click = int(row.get("clicks", 0))
            spend = float(row.get("spend", 0))
            leads = get_leads(row.get("actions"))
            ctr   = click / impr * 100 if impr else 0
            cpc   = spend / click if click else 0
            cpm   = spend / impr * 1000 if impr else 0
            cpl   = spend / leads if leads else None

            if aid not in metrics:
                metrics[aid] = {}
            metrics[aid][key] = {
                "spend": spend, "impressions": impr, "clicks": click,
                "leads": leads, "ctr": ctr, "cpc": cpc, "cpm": cpm, "cpl": cpl,
            }

        paging = resp.get("paging", {})
        cursor = paging.get("cursors", {}).get("after")
        if not paging.get("next"):
            break


def fetch_adset_metrics(windows=(7, 14, 30)):
    """
    Retorna dict:  adset_id → { 7: {...}, 14: {...}, 30: {...}, '2026-01': {...}, ... }
    Busca janelas de dias + meses de Jan/2026 até o mês corrente.
    """
    today = date.today()
    metrics = {}

    # Janelas de dias
    for days in windows:
        since = today - timedelta(days=days - 1)
        _fetch_adset_metrics_range(metrics, days, since, today, f"últimos {days} dias")

    # Meses de Jan/2026 até o mês corrente
    year = 2026
    for month in range(1, today.month + 1):
        month_key = f"{year}-{month:02d}"
        since = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        until = today if month == today.month else date(year, month, last_day)
        mes_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
        _fetch_adset_metrics_range(metrics, month_key, since, until, f"{mes_nomes[month-1]}/{year}")

    return metrics

# ─────────────────────────────────────────────────────────
# 4. ORÇAMENTO DIÁRIO DAS CAMPANHAS (soma dos adsets ativos)
# ─────────────────────────────────────────────────────────

def fetch_campaign_budgets():
    """Busca daily_budget no nível de campanha (para campanhas CBO)."""
    camp_budgets = {}
    for code, camp_id in CAMPAIGN_IDS.items():
        try:
            resp = api_get(camp_id, {"fields": "daily_budget,lifetime_budget,status"})
            b = int(resp.get("daily_budget", 0)) // 100
            camp_budgets[code] = b
            if b:
                print(f"  → Budget CBO {code}: R${b}/dia")
        except Exception as e:
            print(f"    AVISO: erro ao buscar budget campanha {code}: {e}")
            camp_budgets[code] = 0
    return camp_budgets


def calc_budgets(adsets, camp_budgets=None):
    """Soma budgets dos adsets ativos. Para campanhas CBO (adsets sem budget), usa o budget da campanha."""
    budgets = {code: 0 for code in CAMPAIGN_IDS}
    for a in adsets:
        if a["status"] == "active":
            budgets[a["camp"]] += a["budget"]
    # Fallback: campanha CBO tem budget=0 nos adsets — usa budget da campanha
    if camp_budgets:
        for code in CAMPAIGN_IDS:
            if budgets[code] == 0 and camp_budgets.get(code, 0) > 0:
                budgets[code] = camp_budgets[code]
                print(f"  → {code} usa CBO: R${budgets[code]}/dia (budget da campanha)")
    return budgets


def fetch_total_daily_budget(adsets=None):
    """Calcula verba diária total a partir dos adsets já buscados (sem chamada extra à API)."""
    if adsets is None:
        adsets = []
    total = sum(a["budget"] for a in adsets if a["status"] == "active")
    print(f"  → Verba diária total (conta): R${total}/dia")
    return total

# ─────────────────────────────────────────────────────────
# 5. CRIATIVOS (anúncios com thumbnail + leads 2026)
# ─────────────────────────────────────────────────────────

def fetch_creatives():
    """Busca anúncios com thumbnail e leads gerados em 2026."""
    today = date.today()
    date_range = {"since": "2026-01-01", "until": today.isoformat()}

    # Insights por anúncio (nível ad) para todo o ano
    print("  → Insights por anúncio (2026 YTD)...")
    ad_insights = {}
    cursor = None
    while True:
        params = {
            "level":  "ad",
            "fields": "ad_id,ad_name,impressions,clicks,spend,actions",
            "time_range": json.dumps(date_range),
            "limit": "100",
        }
        if cursor:
            params["after"] = cursor
        try:
            resp = api_get(f"{ACCOUNT}/insights", params)
        except Exception as e:
            print(f"    ERRO insights: {e}")
            break
        for row in resp.get("data", []):
            aid   = row["ad_id"]
            spend = float(row.get("spend", 0))
            leads = get_leads(row.get("actions"))
            impr  = int(row.get("impressions", 0))
            click = int(row.get("clicks", 0))
            cpl   = spend / leads if leads else None
            ad_insights[aid] = {
                "spend": spend, "leads": leads,
                "impressions": impr, "clicks": click, "cpl": cpl,
            }
        paging = resp.get("paging", {})
        cursor = paging.get("cursors", {}).get("after")
        if not paging.get("next"):
            break

    # Busca anúncios com thumbnail por campanha
    creatives = []
    for code, camp_id in CAMPAIGN_IDS.items():
        print(f"  → Anúncios/thumbnails: {code}...")
        cursor = None
        while True:
            params = {
                "fields": "id,name,status,creative{thumbnail_url}",
                "limit": "50",
            }
            if cursor:
                params["after"] = cursor
            try:
                resp = api_get(f"{camp_id}/ads", params)
            except Exception as e:
                print(f"    ERRO ads: {e}")
                break
            for ad in resp.get("data", []):
                aid = ad["id"]
                ins = ad_insights.get(aid, {})
                if not ins.get("spend", 0):
                    continue  # ignora anúncios sem gasto em 2026
                thumbnail = (
                    ad.get("creative", {}).get("thumbnail_url") or ""
                )
                creatives.append({
                    "id":        aid,
                    "name":      ad.get("name", ""),
                    "camp":      code,
                    "status":    "active" if ad.get("status") == "ACTIVE" else "paused",
                    "thumbnail": thumbnail,
                    "spend":     ins.get("spend", 0),
                    "leads":     ins.get("leads", 0),
                    "cpl":       ins.get("cpl"),
                    "impressions": ins.get("impressions", 0),
                    "clicks":    ins.get("clicks", 0),
                })
            paging = resp.get("paging", {})
            cursor = paging.get("cursors", {}).get("after")
            if not paging.get("next"):
                break

    # Ordena por leads desc, depois por spend desc
    creatives.sort(key=lambda x: (-x["leads"], -x["spend"]))
    print(f"      {len(creatives)} criativos com gasto em 2026.")
    return creatives

# ─────────────────────────────────────────────────────────
# 5b. LEADBOARD — NECTAR CRM
# ─────────────────────────────────────────────────────────

def fetch_nectar_leadboard():
    """
    Busca qualificacoes (Leadboard) do Nectar CRM.
    Retorna:
      - pipeline: contagem atual por etapa (status=1, abertos)
      - vendidas_mes: total vendidas no mês corrente (status=2)
      - perdidas_mes: total perdidas no mês corrente (status=3)
      - historico_mes: dict {mes_iso: {"vendidas": N, "perdidas": N}}
    """
    empty = {
        "pipeline": {s: 0 for s in LEADBOARD_STAGES},
        "vendidas_mes": 0,
        "perdidas_mes": 0,
        "historico_mes": {},
    }

    if not NECTAR_TOKEN:
        print("  AVISO: NECTAR_API_TOKEN não configurado — pulando Leadboard.")
        return empty

    today   = date.today()
    mes_ini = date(today.year, today.month, 1).isoformat()
    mes_fim = today.isoformat()

    pipeline      = {s: 0 for s in LEADBOARD_STAGES}
    vendidas_mes  = 0
    perdidas_mes  = 0
    historico_mes = {}
    receita_avulso_mes   = 0.0
    mrr_mes              = 0.0
    receita_avulso_total = 0.0   # acumulado geral (todos os meses)
    mrr_total            = 0.0
    receita_historico    = {}

    # Origens consideradas como "ads" para filtro do dashboard
    ADS_ORIGENS = {"Meta Ads", "Google Ads"}

    # A API do Nectar retorna no máx. 15 registros por página.
    # A paginação correta é pelo parâmetro page=N (não displayStart).
    PAGE_SIZE = 15
    MAX_PAGES = 300  # ~4500 registros por status
    PAGE_DELAY = 0.15  # delay entre páginas para evitar rate-limit

    # Session reutiliza conexão TCP e reduz drops
    nectar_session = requests.Session()

    for status in [1, 2, 3]:
        label = {1: "abertas", 2: "vendidas", 3: "perdidas"}[status]
        print(f"  → Leadboard {label}...")
        seen_ids = set()
        ads_count = 0

        for pg in range(1, MAX_PAGES + 1):
            data = None
            for attempt in range(4):
                try:
                    resp = nectar_session.get(
                        f"{NECTAR_BASE}/qualificacoes/",
                        params={"api_token": NECTAR_TOKEN, "displayLength": PAGE_SIZE,
                                "page": pg, "status": status},
                        timeout=60,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    break
                except Exception as e:
                    if attempt == 3:
                        print(f"    ERRO Nectar ({label}) pg={pg}: {e}")
                    else:
                        wait = (attempt + 1) * 3
                        time.sleep(wait)
            if data is None:
                break

            time.sleep(PAGE_DELAY)

            items = data if isinstance(data, list) else data.get("data", [])
            if not items:
                break

            # Detecta loop (API repetindo a mesma página)
            page_ids = [o.get("id") for o in items]
            if all(i in seen_ids for i in page_ids):
                break
            seen_ids.update(page_ids)

            for o in items:
                # Filtra apenas leads com origem em Meta Ads ou Google Ads
                cli    = o.get("cliente") or {}
                origem = cli.get("origem") or ""
                if origem not in ADS_ORIGENS:
                    continue
                ads_count += 1

                ea       = o.get("etapaAtual") or {}
                stage_nm = ea.get("nome", "")

                if status == 1:
                    # Pipeline atual: mapeia pelo nome real da etapa
                    nm = stage_nm.lower()
                    if "agendamento" in nm:
                        pipeline["Agendamento"] += 1
                    elif "qualificada" in nm:
                        pipeline["Qualificada"] += 1
                    elif "qualifica" in nm:
                        pipeline["Qualificação"] += 1
                    elif "contato" in nm:
                        pipeline["Contatos"] += 1
                    else:
                        pipeline["Contatos"] += 1

                else:
                    # Ganha (2) ou Perdida (3): usa dataConclusao para filtrar mês
                    data_conclu = (
                        o.get("dataConclusao") or
                        o.get("dataConversao") or
                        o.get("dataAtualizacao") or ""
                    )
                    mes_iso = data_conclu[:7] if data_conclu else ""

                    if mes_iso:
                        if mes_iso not in historico_mes:
                            historico_mes[mes_iso] = {"vendidas": 0, "perdidas": 0}

                    if status == 2:
                        if mes_iso:
                            historico_mes[mes_iso]["vendidas"] += 1
                        if mes_ini <= data_conclu[:10] <= mes_fim:
                            vendidas_mes += 1
                    else:
                        if mes_iso:
                            historico_mes[mes_iso]["perdidas"] += 1
                        if mes_ini <= data_conclu[:10] <= mes_fim:
                            perdidas_mes += 1

                # Extrai receita de camposListagem para TODOS os status
                campos = o.get("camposListagem") or []
                data_ref = (
                    o.get("dataConclusao") or
                    o.get("dataConversao") or
                    o.get("dataAtualizacao") or ""
                )
                mes_ref = data_ref[:7] if data_ref else ""
                for campo in (campos if isinstance(campos, list) else []):
                    if not campo or not isinstance(campo, dict):
                        continue
                    lbl = (campo.get("label") or "").strip().lower()
                    try:
                        val = float(campo.get("value") or 0)
                    except (TypeError, ValueError):
                        val = 0.0
                    if not val:
                        continue
                    if lbl in ("valor único", "valor avulso", "valor unico"):
                        if mes_ref:
                            if mes_ref not in receita_historico:
                                receita_historico[mes_ref] = {"avulso": 0.0, "mrr": 0.0}
                            receita_historico[mes_ref]["avulso"] += val
                        receita_avulso_total += val
                        if mes_ini <= data_ref[:10] <= mes_fim:
                            receita_avulso_mes += val
                    elif "mrr" in lbl or ("mensal" in lbl and "valor" in lbl):
                        if mes_ref:
                            if mes_ref not in receita_historico:
                                receita_historico[mes_ref] = {"avulso": 0.0, "mrr": 0.0}
                            receita_historico[mes_ref]["mrr"] += val
                        mrr_total += val
                        if mes_ini <= data_ref[:10] <= mes_fim:
                            mrr_mes += val

            if len(items) < PAGE_SIZE:
                break

        print(f"    {label}: {len(seen_ids)} total | {ads_count} de ads (Meta+Google)")

    pipeline["Vendida"] = vendidas_mes  # Vendida = fechadas no mês

    print(f"      Pipeline: {pipeline}")
    print(f"      Vendidas no mês: {vendidas_mes} | Perdidas no mês: {perdidas_mes}")
    print(f"      Receita mês: avulso=R${receita_avulso_mes:.2f} | MRR=R${mrr_mes:.2f}")
    print(f"      Receita total CRM: avulso=R${receita_avulso_total:.2f} | MRR=R${mrr_total:.2f}")

    return {
        "pipeline":             pipeline,
        "vendidas_mes":         vendidas_mes,
        "perdidas_mes":         perdidas_mes,
        "historico_mes":        historico_mes,
        "receita_avulso_mes":   receita_avulso_mes,
        "mrr_mes":              mrr_mes,
        "receita_avulso_total": receita_avulso_total,
        "mrr_total":            mrr_total,
        "receita_historico":    receita_historico,
    }


# ─────────────────────────────────────────────────────────
# 6. DADOS DA CONTA TRON RIO VERDE
# ─────────────────────────────────────────────────────────

def fetch_rv_data():
    """Busca dados da conta Tron Rio Verde: campanhas, adsets e métricas."""
    today = date.today()
    date_range_ytd = {"since": "2026-01-01", "until": today.isoformat()}
    mes_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

    rv_campaigns = {}

    # 1. Insights por campanha (YTD)
    for code, camp_id in RV_CAMPAIGN_IDS.items():
        meta = RV_CAMPAIGN_META[code]
        print(f"  → RV insights: {code} ({camp_id})...")
        try:
            resp = api_get(f"{camp_id}/insights", {
                "fields": "spend,impressions,clicks,actions",
                "time_range": json.dumps(date_range_ytd),
                "limit": "1",
            })
            rows = resp.get("data", [])
            if rows:
                row   = rows[0]
                spend = float(row.get("spend", 0))
                leads = get_leads(row.get("actions"))
                impr  = int(row.get("impressions", 0))
                click = int(row.get("clicks", 0))
                cpl   = spend / leads if leads else None
                ctr   = click / impr * 100 if impr else 0
            else:
                spend, leads, impr, click, cpl, ctr = 0, 0, 0, 0, None, 0
        except Exception as e:
            print(f"    ERRO: {e}")
            spend, leads, impr, click, cpl, ctr = 0, 0, 0, 0, None, 0
        rv_campaigns[code] = {
            "label": meta["label"], "color": meta["color"],
            "spend": spend, "leads": leads, "cpl": cpl,
            "impressions": impr, "clicks": click, "ctr": ctr,
            "budget": 0,
        }

    # 2. Adsets com budget/status
    rv_adsets = []
    for code, camp_id in RV_CAMPAIGN_IDS.items():
        print(f"  → RV adsets: {code}...")
        cursor = None
        while True:
            params = {"fields": "id,name,daily_budget,status", "limit": "50"}
            if cursor:
                params["after"] = cursor
            try:
                resp = api_get(f"{camp_id}/adsets", params)
            except Exception as e:
                print(f"    ERRO: {e}")
                break
            for a in resp.get("data", []):
                budget = int(a.get("daily_budget", 0)) // 100
                rv_adsets.append({
                    "id":     a["id"],
                    "camp":   code,
                    "name":   a["name"],
                    "budget": budget,
                    "status": "active" if a.get("status") == "ACTIVE" else "paused",
                })
                if a.get("status") == "ACTIVE":
                    rv_campaigns[code]["budget"] += budget
            paging = resp.get("paging", {})
            cursor = paging.get("cursors", {}).get("after")
            if not paging.get("next"):
                break

    print(f"      {len(rv_adsets)} adsets RV encontrados.")

    # 3. Métricas por adset — janelas temporais (conta RV)
    rv_adset_metrics = {}
    windows_def = []
    for days in [7, 14, 30]:
        since_w = today - timedelta(days=days - 1)
        windows_def.append((days, since_w, today, f"últimos {days} dias"))
    for month in range(1, today.month + 1):
        month_key = f"2026-{month:02d}"
        since_m = date(2026, month, 1)
        last_day = calendar.monthrange(2026, month)[1]
        until_m = today if month == today.month else date(2026, month, last_day)
        windows_def.append((month_key, since_m, until_m, f"{mes_nomes[month-1]}/2026"))

    for key, since_date, until_date, label in windows_def:
        print(f"  → RV métricas adset: {label}...")
        date_range = {"since": since_date.isoformat(), "until": until_date.isoformat()}
        cursor = None
        while True:
            params = {
                "level":  "adset",
                "fields": "adset_id,impressions,clicks,spend,actions",
                "time_range": json.dumps(date_range),
                "limit": "100",
            }
            if cursor:
                params["after"] = cursor
            try:
                resp = api_get(f"{ACCOUNT_RV}/insights", params)
            except Exception as e:
                print(f"    ERRO: {e}")
                break
            for row in resp.get("data", []):
                aid   = row["adset_id"]
                impr  = int(row.get("impressions", 0))
                click = int(row.get("clicks", 0))
                spend = float(row.get("spend", 0))
                leads = get_leads(row.get("actions"))
                ctr   = click / impr * 100 if impr else 0
                cpc   = spend / click if click else 0
                cpm   = spend / impr * 1000 if impr else 0
                cpl   = spend / leads if leads else None
                if aid not in rv_adset_metrics:
                    rv_adset_metrics[aid] = {}
                rv_adset_metrics[aid][str(key)] = {
                    "spend": spend, "impressions": impr, "clicks": click,
                    "leads": leads, "ctr": ctr, "cpc": cpc, "cpm": cpm, "cpl": cpl,
                }
            paging = resp.get("paging", {})
            cursor = paging.get("cursors", {}).get("after")
            if not paging.get("next"):
                break

    # Injeta métricas em cada adset
    for a in rv_adsets:
        a["metrics"] = rv_adset_metrics.get(a["id"], {})

    # Totais consolidados
    total_spend  = sum(c["spend"] for c in rv_campaigns.values())
    total_leads  = sum(c["leads"] for c in rv_campaigns.values())
    total_budget = sum(c["budget"] for c in rv_campaigns.values())
    total_cpl    = total_spend / total_leads if total_leads else None

    print(f"      RV total: R${total_spend:.2f} gasto | {total_leads} leads"
          f" | CPL R${total_cpl:.2f}" if total_cpl else
          f"      RV total: R${total_spend:.2f} gasto | {total_leads} leads | CPL —")

    return {
        "campaigns":     rv_campaigns,
        "adsets":        rv_adsets,
        "adset_metrics": rv_adset_metrics,
        "totals": {
            "spend":  total_spend,
            "leads":  total_leads,
            "cpl":    total_cpl,
            "budget": total_budget,
        },
    }


# ─────────────────────────────────────────────────────────
# 7. GERAÇÃO DO BLOCO JS
# ─────────────────────────────────────────────────────────

def build_js_block(all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar=None, total_budget=0, rv_data=None):
    """Gera o bloco de dados JS para injetar no HTML."""

    # CAMPAIGNS com orçamentos reais
    camp_lines = []
    for code, meta in CAMPAIGN_META.items():
        b = budgets.get(code, 0)
        camp_lines.append(
            f"  {code}: {{ label: {json.dumps(meta['label'])}, "
            f"color: {json.dumps(meta['color'])}, budget: {b} }},"
        )
    campaigns_js = "var CAMPAIGNS = {\n" + "\n".join(camp_lines) + "\n};"

    # ALL_DATES
    dates_js = "var ALL_DATES = " + json.dumps(all_dates, ensure_ascii=False) + ";"

    # ALL_DATA
    all_data_js = "var ALL_DATA = " + json.dumps(all_data, ensure_ascii=False, separators=(',', ':')) + ";"

    # ADSETS_RAW
    adset_lines = []
    for a in adsets:
        adset_lines.append(
            f"  {{ id: {json.dumps(a['id'])}, camp: {json.dumps(a['camp'])}, "
            f"name: {json.dumps(a['name'])}, budget: {a['budget']}, "
            f"status: {json.dumps(a['status'])} }},"
        )
    adsets_js = "var ADSETS_RAW = [\n" + "\n".join(adset_lines) + "\n];"

    # ADSET_METRICS
    metrics_js = "var ADSET_METRICS = " + json.dumps(adset_metrics, ensure_ascii=False, separators=(',', ':')) + ";"

    # CREATIVES
    creatives_js = "var CREATIVES = " + json.dumps(creatives, ensure_ascii=False, separators=(',', ':')) + ";"

    # NECTAR LEADBOARD
    if not nectar:
        nectar = {"pipeline": {s: 0 for s in LEADBOARD_STAGES}, "vendidas_mes": 0, "perdidas_mes": 0, "historico_mes": {}}
    nectar_js = "var NECTAR_LEADBOARD = " + json.dumps(nectar, ensure_ascii=False, separators=(',', ':')) + ";"

    updated_at = date.today().strftime("%d/%m/%Y")

    total_budget_js = f"var TOTAL_DAILY_BUDGET = {total_budget};"

    # RIO VERDE
    rv_data_js = "var RV_DATA = " + json.dumps(rv_data or {}, ensure_ascii=False, separators=(',', ':')) + ";"

    block = f"""// ─────────────────────────────────────────────────────────
// 1. DADOS — atualizado automaticamente pelo update_dashboard.py
// DATA:START
// Última atualização: {updated_at}
// ─────────────────────────────────────────────────────────

{campaigns_js}

{dates_js}
{all_data_js}

{adsets_js}

{metrics_js}

{creatives_js}

{nectar_js}

{total_budget_js}

{rv_data_js}

// DATA:END"""

    return block

# ─────────────────────────────────────────────────────────
# 6. ATUALIZA O HTML
# ─────────────────────────────────────────────────────────

DATA_START = "// DATA:START"
DATA_END   = "// DATA:END"

def update_html(js_block):
    with open(DASHBOARD_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    start_idx = html.find(DATA_START)
    end_idx   = html.find(DATA_END)

    if start_idx == -1 or end_idx == -1:
        print("ERRO: Marcadores DATA:START / DATA:END não encontrados no HTML.")
        sys.exit(1)

    end_idx += len(DATA_END)

    # Substitui apenas o bloco de dados — o restante do HTML (funções, render, etc.) é preservado
    new_html = html[:start_idx] + js_block + html[end_idx:]

    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"  ✓ {DASHBOARD_HTML} atualizado com sucesso.")

# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Tron — Atualização do Dashboard Meta Ads")
    print(f"Data: {date.today().strftime('%d/%m/%Y')}")
    print("=" * 60)

    print("\n[1/7] Buscando dados diários por campanha (30d)...")
    all_dates, all_data = fetch_daily_data()

    print("\n[2/7] Buscando adsets...")
    adsets = fetch_adsets()
    print(f"      {len(adsets)} adsets encontrados.")

    print("\n[3/7] Buscando métricas por adset (7d / 14d / 30d)...")
    adset_metrics = fetch_adset_metrics()
    print(f"      {len(adset_metrics)} adsets com métricas.")

    print("\n[4/7] Buscando criativos e thumbnails...")
    creatives = fetch_creatives()

    print("\n[5/6] Buscando Leadboard do Nectar CRM...")
    nectar = fetch_nectar_leadboard()

    print("\n[6/7] Buscando dados da Tron Rio Verde...")
    rv_data = fetch_rv_data()

    print("\n[7/7] Calculando orçamentos e atualizando HTML...")
    camp_budgets = fetch_campaign_budgets()
    budgets = calc_budgets(adsets, camp_budgets)
    total_budget = fetch_total_daily_budget(adsets)
    js_block = build_js_block(all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar,
                               total_budget=total_budget, rv_data=rv_data)
    update_html(js_block)

    print("\n" + "=" * 60)
    print("Dashboard atualizado! Abra o arquivo no navegador.")
    print("=" * 60)

if __name__ == "__main__":
    main()
