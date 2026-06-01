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
from datetime import date, datetime, timedelta
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
DASHBOARD_HTML = r"C:\Users\Marketing\Desktop\Dashboard\index.html"
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
NECTAR_TOKEN          = ENV.get("NECTAR_API_TOKEN", "")
NECTAR_BIG_DATA_TOKEN = ENV.get("NECTAR_BIG_DATA_TOKEN", "")
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
                "fields": "id,name,daily_budget,status,destination_type",
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
                    "id":          a["id"],
                    "camp":        code,
                    "name":        a["name"],
                    "budget":      budget,
                    "status":      "active" if a.get("status") == "ACTIVE" else "paused",
                    "destination": a.get("destination_type", "UNDEFINED"),
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
                "fields": "id,name,status,effective_status,creative{thumbnail_url}",
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
                    "status":    "active" if ad.get("effective_status") == "ACTIVE" else "paused",
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
    Busca dados do Nectar CRM via /big-data/qualification.
    Uma única chamada retorna todos os registros do ano com fases, datas e receita.
    Filtra por origem: Meta Ads, Google Ads, Site.
    """
    today   = date.today()
    ano_ini = f"{today.year}-01-01"
    mes_ini_iso = f"{today.year}-{today.month:02d}-01"
    mes_fim_iso = today.isoformat()
    mes_atual   = f"{today.year}-{today.month:02d}"

    ORIGENS_TRACK = ["Meta Ads", "Google Ads", "Site"]
    ADS_ORIGENS   = set(ORIGENS_TRACK)

    FASES_ATIVAS  = {"Em Andamento", "Agendada", "Qualificada"}
    FASES_VENDIDA = {"Vendida"}
    FASES_PERDIDA = {"Descartada", "Não Vendida"}

    empty = {
        "pipeline":             {s: 0 for s in LEADBOARD_STAGES},
        "pipeline_by_origem":   {o: {s: 0 for s in LEADBOARD_STAGES} for o in ORIGENS_TRACK},
        "vendidas_mes":         0,
        "vendidas_by_origem":   {o: 0 for o in ORIGENS_TRACK},
        "perdidas_mes":         0,
        "perdidas_by_origem":   {o: 0 for o in ORIGENS_TRACK},
        "historico_mes":        {},
        "receita_avulso_mes":   0.0,
        "mrr_mes":              0.0,
        "receita_avulso_total": 0.0,
        "mrr_total":            0.0,
        "receita_historico":    {},
        "receita_by_origem":    {o: {"avulso": 0.0, "mrr": 0.0} for o in ORIGENS_TRACK},
        "leads_by_origem_mes":     {o: 0 for o in ORIGENS_TRACK},
        "leads_by_origem_ano":     {o: 0 for o in ORIGENS_TRACK},
        "leads_historico":         {},
        "vendidas_historico":      {},
        "perdidas_historico":      {},
        "receita_hist_by_origem":  {},
        "ticket_por_produto":      {},
    }

    token = NECTAR_BIG_DATA_TOKEN or NECTAR_TOKEN
    if not token:
        print("  AVISO: token Nectar não configurado — pulando Leadboard.")
        return empty

    print(f"  → big-data/qualification ({ano_ini} → {mes_fim_iso})...")
    try:
        resp = requests.get(
            f"{NECTAR_BASE}/big-data/qualification",
            params={"api_token": token, "aggregator": 0,
                    "initialDate": ano_ini, "endDate": mes_fim_iso},
            timeout=120,
        )
        resp.raise_for_status()
        rows = resp.json()
    except Exception as e:
        print(f"    ERRO big-data: {e}")
        return empty

    print(f"    {len(rows)} registros recebidos.")

    def parse_br(s):
        """DD/MM/YYYY [HH:MM] → YYYY-MM-DD"""
        if not s or "/" not in str(s): return ""
        try:
            p = str(s)[:10].split("/")
            return f"{p[2]}-{p[1]}-{p[0]}"
        except: return ""

    def mes_de(date_br):
        iso = parse_br(date_br)
        return iso[:7] if iso else ""

    def no_mes_atual(date_br):
        return mes_de(date_br) == mes_atual

    def detect_produto(tags, funil):
        t = (tags or "").lower()
        f = (funil or "").lower()
        if "ordix"   in t: return "Ordix"
        if "tron dp" in t or ("dp" in t and "tron" in t): return "DP"
        if "tgc"     in t or "contab" in f: return "TGC"
        if "box"     in t: return "Box"
        if "sittax"  in t: return "Sittax"
        if "empresarial" in f: return "DP"
        return "Outros"

    pipeline             = {s: 0 for s in LEADBOARD_STAGES}
    pipeline_by_origem   = {o: {s: 0 for s in LEADBOARD_STAGES} for o in ORIGENS_TRACK}
    vendidas_mes         = 0
    vendidas_by_origem   = {o: 0 for o in ORIGENS_TRACK}
    perdidas_mes         = 0
    perdidas_by_origem   = {o: 0 for o in ORIGENS_TRACK}
    historico_mes        = {}
    receita_avulso_mes   = 0.0
    mrr_mes              = 0.0
    receita_avulso_total = 0.0
    mrr_total            = 0.0
    receita_historico    = {}
    receita_by_origem    = {o: {"avulso": 0.0, "mrr": 0.0} for o in ORIGENS_TRACK}
    leads_by_origem_mes  = {o: 0 for o in ORIGENS_TRACK}
    leads_by_origem_ano      = {o: 0 for o in ORIGENS_TRACK}
    leads_historico          = {}   # { "2026-01": {"Meta Ads": N, ...} }
    vendidas_historico       = {}   # { "2026-01": {"Meta Ads": N, ...} }
    perdidas_historico       = {}   # { "2026-01": {"Meta Ads": N, ...} }
    receita_hist_by_origem   = {}   # { "2026-01": {"Meta Ads": {"avulso": N, "mrr": N}, ...} }
    ticket_por_produto       = {}

    for r in rows:
        origem = r.get("Contato: origem") or ""
        if origem not in ADS_ORIGENS:
            continue

        fase  = r.get("Leadboard: Fase") or ""
        etapa = (r.get("Leadboard: Etapa") or "").strip().lower()

        # Contagem de leads gerados (por data de criação)
        data_criacao = r.get("Leadboard: Data criação") or ""
        if origem in ORIGENS_TRACK:
            leads_by_origem_ano[origem] += 1
            if no_mes_atual(data_criacao):
                leads_by_origem_mes[origem] += 1
            # Histórico mês a mês
            mk_lead = mes_de(data_criacao)
            if mk_lead:
                if mk_lead not in leads_historico:
                    leads_historico[mk_lead] = {o: 0 for o in ORIGENS_TRACK}
                leads_historico[mk_lead][origem] = leads_historico[mk_lead].get(origem, 0) + 1

        # ── Pipeline ativo ──────────────────────────────
        if fase in FASES_ATIVAS:
            if "agendamento" in etapa:
                etapa_key = "Agendamento"
            elif "qualificada" in etapa:
                etapa_key = "Qualificada"
            elif "qualifica" in etapa:
                etapa_key = "Qualificação"
            else:
                etapa_key = "Contatos"
            pipeline[etapa_key] += 1
            if origem in ORIGENS_TRACK:
                pipeline_by_origem[origem][etapa_key] += 1

        # ── Vendidas ────────────────────────────────────
        elif fase in FASES_VENDIDA:
            date_conv = r.get("Data Conversão: Completa") or r.get("Leadboard: Data conclusão") or ""
            mk = mes_de(date_conv)
            if mk:
                historico_mes.setdefault(mk, {"vendidas": 0, "perdidas": 0})
                historico_mes[mk]["vendidas"] += 1
                if origem in ORIGENS_TRACK:
                    if mk not in vendidas_historico:
                        vendidas_historico[mk] = {o: 0 for o in ORIGENS_TRACK}
                    vendidas_historico[mk][origem] += 1
            if no_mes_atual(date_conv):
                vendidas_mes += 1
                if origem in ORIGENS_TRACK:
                    vendidas_by_origem[origem] += 1

        # ── Perdidas ────────────────────────────────────
        elif fase in FASES_PERDIDA:
            date_conclu = r.get("Leadboard: Data conclusão") or r.get("Leadboard: Data atualização") or ""
            mk = mes_de(date_conclu)
            if mk:
                historico_mes.setdefault(mk, {"vendidas": 0, "perdidas": 0})
                historico_mes[mk]["perdidas"] += 1
                if origem in ORIGENS_TRACK:
                    if mk not in perdidas_historico:
                        perdidas_historico[mk] = {o: 0 for o in ORIGENS_TRACK}
                    perdidas_historico[mk][origem] += 1
            if no_mes_atual(date_conclu):
                perdidas_mes += 1
                if origem in ORIGENS_TRACK:
                    perdidas_by_origem[origem] += 1

        # ── Receita (Oportunidade vinculada) ────────────
        val_avulso = 0.0
        val_mrr    = 0.0
        try: val_avulso = float(str(r.get("Oportunidade: Valor único") or 0).replace(",", "."))
        except: pass
        try: val_mrr = float(str(r.get("Oportunidade: Valor mensal (MRR)") or 0).replace(",", "."))
        except: pass

        if val_avulso or val_mrr:
            date_ref = (r.get("Data Conversão: Completa") or
                        r.get("Leadboard: Data conclusão") or
                        r.get("Leadboard: Data atualização") or "")
            mk = mes_de(date_ref)
            if mk:
                receita_historico.setdefault(mk, {"avulso": 0.0, "mrr": 0.0})
                receita_historico[mk]["avulso"] += val_avulso
                receita_historico[mk]["mrr"]    += val_mrr
                if origem in ORIGENS_TRACK:
                    if mk not in receita_hist_by_origem:
                        receita_hist_by_origem[mk] = {o: {"avulso": 0.0, "mrr": 0.0} for o in ORIGENS_TRACK}
                    receita_hist_by_origem[mk][origem]["avulso"] += val_avulso
                    receita_hist_by_origem[mk][origem]["mrr"]    += val_mrr
            receita_avulso_total += val_avulso
            mrr_total            += val_mrr
            if no_mes_atual(date_ref):
                receita_avulso_mes += val_avulso
                mrr_mes            += val_mrr
                if origem in ORIGENS_TRACK:
                    receita_by_origem[origem]["avulso"] += val_avulso
                    receita_by_origem[origem]["mrr"]    += val_mrr
            # Ticket por produto
            produto = detect_produto(r.get("Contato: Tags concatenadas"), r.get("Oportunidade: Funil"))
            ticket_por_produto.setdefault(produto, {"count": 0, "avulso": 0.0, "mrr": 0.0})
            ticket_por_produto[produto]["count"]  += 1
            ticket_por_produto[produto]["avulso"] += val_avulso
            ticket_por_produto[produto]["mrr"]    += val_mrr

    pipeline["Vendida"] = vendidas_mes
    for orig in ORIGENS_TRACK:
        pipeline_by_origem[orig]["Vendida"] = vendidas_by_origem[orig]

    for prod, d in ticket_por_produto.items():
        n = d["count"] or 1
        d["ticket_avulso"] = round(d["avulso"] / n, 2)
        d["ticket_mrr"]    = round(d["mrr"]    / n, 2)

    print(f"      Pipeline: {pipeline}")
    print(f"      Pipeline por origem: {pipeline_by_origem}")
    print(f"      Leads mês por origem: {leads_by_origem_mes}")
    print(f"      Vendidas no mês: {vendidas_mes} | Perdidas no mês: {perdidas_mes}")
    print(f"      Vendidas por origem: {vendidas_by_origem}")
    print(f"      Receita mês: avulso=R${receita_avulso_mes:.2f} | MRR=R${mrr_mes:.2f}")
    print(f"      Receita por origem: {receita_by_origem}")
    print(f"      Leads histórico ({len(leads_historico)} meses): { {m: sum(v.values()) for m, v in sorted(leads_historico.items())} }")

    return {
        "pipeline":             pipeline,
        "pipeline_by_origem":   pipeline_by_origem,
        "vendidas_mes":         vendidas_mes,
        "vendidas_by_origem":   vendidas_by_origem,
        "perdidas_mes":         perdidas_mes,
        "perdidas_by_origem":   perdidas_by_origem,
        "historico_mes":        historico_mes,
        "receita_avulso_mes":   receita_avulso_mes,
        "mrr_mes":              mrr_mes,
        "receita_avulso_total": receita_avulso_total,
        "mrr_total":            mrr_total,
        "receita_historico":    receita_historico,
        "receita_by_origem":    receita_by_origem,
        "leads_by_origem_mes":  leads_by_origem_mes,
        "leads_by_origem_ano":  leads_by_origem_ano,
        "leads_historico":         leads_historico,
        "vendidas_historico":      vendidas_historico,
        "perdidas_historico":      perdidas_historico,
        "receita_hist_by_origem":  receita_hist_by_origem,
        "ticket_por_produto":      ticket_por_produto,
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

def build_js_block(all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar=None, total_budget=0, rv_data=None, organic=None):
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

    active_ads_count = sum(1 for c in creatives if c.get("status") == "active")
    active_ads_js = f"var ACTIVE_ADS_COUNT = {active_ads_count};"

    # RIO VERDE
    rv_data_js = "var RV_DATA = " + json.dumps(rv_data or {}, ensure_ascii=False, separators=(',', ':')) + ";"

    # LEAD TYPE — Forms Nativos vs Frios/Nutrição
    # ON_AD (formulário nativo Meta) vs WEBSITE/UNDEFINED (tráfego frio para nutrição)
    FORMS_DEST = {"ON_AD", "MESSENGER", "INSTAGRAM_DIRECT"}
    adset_dest_map = {a["id"]: a.get("destination", "UNDEFINED") for a in adsets}
    lead_type_data = {}
    for aid, periods in adset_metrics.items():
        dest = adset_dest_map.get(aid, "UNDEFINED")
        tipo = "forms" if dest in FORMS_DEST else "frios"
        for period, m in periods.items():
            if period not in lead_type_data:
                lead_type_data[period] = {
                    "forms": {"leads": 0, "spend": 0.0, "impressions": 0, "clicks": 0},
                    "frios": {"leads": 0, "spend": 0.0, "impressions": 0, "clicks": 0},
                }
            lead_type_data[period][tipo]["leads"]       += m.get("leads", 0)
            lead_type_data[period][tipo]["spend"]       += m.get("spend", 0.0)
            lead_type_data[period][tipo]["impressions"] += m.get("impressions", 0)
            lead_type_data[period][tipo]["clicks"]      += m.get("clicks", 0)
    # Calcula CPL e CTR
    for period, types in lead_type_data.items():
        for tipo, v in types.items():
            v["cpl"] = round(v["spend"] / v["leads"], 2) if v["leads"] else None
            v["ctr"] = round(v["clicks"] / v["impressions"] * 100, 2) if v["impressions"] else 0
    lead_type_js = "var LEAD_TYPE_DATA = " + json.dumps(lead_type_data, ensure_ascii=False, separators=(',', ':')) + ";"

    # ORGÂNICO
    _default_organic = {
        "ig": {"username":"tron_sistemas","followers":8621,"following":412,"follower_gain":236,
               "reach_month":110522,"profile_views":945,"accounts_engaged":816,
               "total_interactions":1267,"website_clicks":49,"posts":[]},
        "fb": {"page_name":"Tron Sistemas","fans":8692,"talking_about":110,
               "reach_month":18400,"total_interactions":340,"posts":[]},
    }
    organic_js = "var ORGANIC_DATA = " + json.dumps(organic or _default_organic, ensure_ascii=False, separators=(',', ':')) + ";"

    block = f"""// DATA:START
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
{active_ads_js}

{rv_data_js}

{lead_type_js}

{organic_js}

// DATA:END"""

    return block

# ─────────────────────────────────────────────────────────
# 5b. DADOS ORGÂNICOS — Instagram e Facebook
# ─────────────────────────────────────────────────────────

IG_ID   = "17841405906455560"
FB_PAGE = "183895946291"

def fetch_organic_data():
    """Busca dados orgânicos do Instagram e Facebook."""
    today = date.today()
    mes_inicio = date(today.year, today.month, 1)
    since_str  = mes_inicio.isoformat()
    until_str  = today.isoformat()

    result = {
        "ig": {
            "username": "tron_sistemas",
            "followers": 0, "following": 0, "follower_gain": 0,
            "reach_month": 0, "profile_views": 0, "accounts_engaged": 0,
            "total_interactions": 0, "website_clicks": 0,
            "posts": [],
        },
        "fb": {
            "page_name": "Tron Sistemas",
            "fans": 0, "talking_about": 0,
            "reach_month": 0, "total_interactions": 0,
            "posts": [],
        },
    }

    # ── Instagram ────────────────────────────────────────
    try:
        ig_info = api_get(IG_ID, {"fields": "followers_count,follows_count,username"})
        result["ig"]["followers"] = ig_info.get("followers_count", 0)
        result["ig"]["following"] = ig_info.get("follows_count", 0)
        result["ig"]["username"]  = ig_info.get("username", "tron_sistemas")
        print(f"  → IG seguidores: {result['ig']['followers']}")
    except Exception as e:
        print(f"  ! IG info erro: {e}")

    # IG Insights com metric_type=total_value (alcance, engajamento, etc.)
    ig_metrics_tv = [
        "reach", "accounts_engaged", "total_interactions",
        "profile_views", "website_clicks",
    ]
    try:
        resp = api_get(f"{IG_ID}/insights", {
            "metric": ",".join(ig_metrics_tv),
            "metric_type": "total_value",
            "period": "day",
            "since": since_str,
            "until": until_str,
        })
        for item in resp.get("data", []):
            name = item.get("name", "")
            val  = item.get("total_value", {}).get("value", 0)
            if name == "reach":                 result["ig"]["reach_month"]       = int(val)
            elif name == "accounts_engaged":    result["ig"]["accounts_engaged"]   = int(val)
            elif name == "total_interactions":  result["ig"]["total_interactions"] = int(val)
            elif name == "profile_views":       result["ig"]["profile_views"]      = int(val)
            elif name == "website_clicks":      result["ig"]["website_clicks"]     = int(val)
        print(f"  → IG insights: alcance={result['ig']['reach_month']}, engaj={result['ig']['total_interactions']}")
    except Exception as e:
        print(f"  ! IG insights erro: {e}")

    # IG follower history — acumula deltas diários dos últimos 30 dias (limite da API)
    # Cada execução do script mescla os novos dados com o histórico persistente
    FOLLOWER_HIST_FILE = os.path.join(os.path.dirname(__file__), "follower_history.json")
    try:
        from datetime import timedelta

        # Carrega histórico existente
        existing_hist = {}
        if os.path.exists(FOLLOWER_HIST_FILE):
            try:
                with open(FOLLOWER_HIST_FILE, "r", encoding="utf-8") as _fh:
                    for entry in json.load(_fh):
                        existing_hist[entry["date"]] = entry["count"]
            except Exception:
                pass

        # Busca deltas dos últimos 30 dias (limite da API: máx 30 dias por chamada)
        since_30 = (today - timedelta(days=29)).isoformat()
        resp = api_get(f"{IG_ID}/insights", {
            "metric": "follower_count",
            "period": "day",
            "since": since_30,
            "until": until_str,
        })
        raw_values = resp.get("data", [{}])[0].get("values", [])

        # Monta deltas diários
        daily = []
        seen_dates = set()
        for v in raw_values:
            end_time = v.get("end_time", "")
            day = end_time[:10] if end_time else ""
            if day and day not in seen_dates:
                seen_dates.add(day)
                daily.append({"date": day, "delta": int(v.get("value", 0))})
        daily.sort(key=lambda x: x["date"])

        # Ganho do mês atual
        total_gain = sum(d["delta"] for d in daily if d["date"] >= since_str)
        result["ig"]["follower_gain"] = int(total_gain)

        # Reconstrói contagens absolutas para os últimos 30 dias
        current_count = result["ig"]["followers"]
        new_counts = {}
        cumulative = 0
        for item in reversed(daily):
            new_counts[item["date"]] = max(0, current_count - cumulative)
            cumulative += item["delta"]

        # Mescla com histórico existente (novos dados sobrescrevem entradas antigas)
        existing_hist.update(new_counts)

        # Salva histórico acumulado
        full_history = sorted(
            [{"date": d, "count": c} for d, c in existing_hist.items()],
            key=lambda x: x["date"]
        )
        with open(FOLLOWER_HIST_FILE, "w", encoding="utf-8") as _fh:
            json.dump(full_history, _fh)

        result["ig"]["follower_history"] = full_history
        print(f"  → IG ganho seguidores: {result['ig']['follower_gain']} | histórico acumulado: {len(full_history)} dias")
    except Exception as e:
        print(f"  ! IG follower_count erro: {e}")
        # Tenta usar histórico salvo mesmo sem nova chamada à API
        try:
            with open(FOLLOWER_HIST_FILE, "r", encoding="utf-8") as _fh:
                result["ig"]["follower_history"] = json.load(_fh)
        except Exception:
            result["ig"]["follower_history"] = []

    # IG posts — todos desde 01/01/2026 (paginado)
    try:
        cutoff = date(today.year, 1, 1).isoformat()  # 2026-01-01
        posts_all = []
        next_url = None
        page_num = 0
        stop = False

        while not stop:
            page_num += 1
            if next_url:
                import urllib.parse as _up
                parsed = _up.urlparse(next_url)
                params = dict(_up.parse_qsl(parsed.query))
                resp = api_get(f"{IG_ID}/media", params)
            else:
                resp = api_get(f"{IG_ID}/media", {
                    "fields": "id,media_type,timestamp,like_count,comments_count,caption,media_url,thumbnail_url,permalink",
                    "limit": "50",
                    "since": cutoff,
                })

            batch = resp.get("data", [])
            for p in batch:
                ts = p.get("timestamp", "")
                if ts and ts[:10] < cutoff:
                    stop = True
                    break
                posts_all.append(p)

            paging = resp.get("paging", {})
            next_url = paging.get("next")
            if not next_url or not batch:
                stop = True

            if page_num > 20:  # segurança: não paginar mais de 20 páginas
                break

        result["ig"]["posts"] = []
        for p in posts_all:
            result["ig"]["posts"].append({
                "id":        p.get("id", ""),
                "type":      p.get("media_type", "IMAGE"),
                "caption":   (p.get("caption") or "")[:120],
                "likes":     p.get("like_count", 0),
                "comments":  p.get("comments_count", 0),
                "timestamp": p.get("timestamp", ""),
                "thumb":     p.get("thumbnail_url") or p.get("media_url") or "",
                "url":       p.get("permalink", ""),
            })
        print(f"  → IG posts: {len(result['ig']['posts'])} encontrados (desde {cutoff}, {page_num} páginas)")
    except Exception as e:
        print(f"  ! IG media erro: {e}")

    # ── Facebook ─────────────────────────────────────────
    try:
        fb_info = api_get(FB_PAGE, {"fields": "name,fan_count,talking_about_count"})
        result["fb"]["page_name"]    = fb_info.get("name", "Tron Sistemas")
        result["fb"]["fans"]         = fb_info.get("fan_count", 0)
        result["fb"]["talking_about"] = fb_info.get("talking_about_count", 0)
        print(f"  → FB seguidores: {result['fb']['fans']}")
    except Exception as e:
        print(f"  ! FB info erro: {e}")

    # FB posts — todos desde 01/01/2026 (sem filtro since, filtra por data no cliente)
    try:
        fb_cutoff = date(today.year, 1, 1).isoformat()
        resp = api_get(f"{FB_PAGE}/posts", {
            "fields": "message,created_time,likes.summary(true),comments.summary(true),shares",
            "limit": "100",
        })
        posts_raw = resp.get("data", [])
        result["fb"]["posts"] = []
        total_interact = 0
        for p in posts_raw:
            ts = p.get("created_time", "")
            if ts and ts[:10] < fb_cutoff:
                continue
            likes    = p.get("likes",    {}).get("summary", {}).get("total_count", 0)
            comments = p.get("comments", {}).get("summary", {}).get("total_count", 0)
            shares   = p.get("shares",   {}).get("count", 0)
            total_interact += likes + comments + shares
            result["fb"]["posts"].append({
                "id":        p.get("id", ""),
                "message":   (p.get("message") or "")[:120],
                "likes":     likes,
                "comments":  comments,
                "shares":    shares,
                "timestamp": p.get("created_time", ""),
            })
        result["fb"]["total_interactions"] = total_interact
        result["fb"]["reach_month"]        = result["fb"]["fans"]  # estimativa
        print(f"  → FB posts: {len(result['fb']['posts'])} encontrados (desde {fb_cutoff}) | interações: {total_interact}")
    except Exception as e:
        print(f"  ! FB posts erro: {e}")

    return result

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

    print("\n[1/8] Buscando dados diários por campanha (30d)...")
    all_dates, all_data = fetch_daily_data()

    print("\n[2/8] Buscando adsets...")
    ADSETS_CACHE_FILE = os.path.join(os.path.dirname(__file__), "adsets_cache.json")
    adsets = fetch_adsets()
    if adsets:
        with open(ADSETS_CACHE_FILE, "w", encoding="utf-8") as _f:
            json.dump(adsets, _f, ensure_ascii=False, indent=2)
        print(f"      {len(adsets)} adsets encontrados. Cache salvo.")
    else:
        if os.path.exists(ADSETS_CACHE_FILE):
            with open(ADSETS_CACHE_FILE, encoding="utf-8") as _f:
                adsets = json.load(_f)
            print(f"      API sem dados — usando cache ({len(adsets)} adsets).")
        else:
            print(f"      API sem dados e sem cache disponível.")

    print("\n[3/8] Buscando métricas por adset (7d / 14d / 30d)...")
    adset_metrics = fetch_adset_metrics()
    print(f"      {len(adset_metrics)} adsets com métricas.")

    print("\n[4/8] Buscando criativos e thumbnails...")
    creatives = fetch_creatives()

    print("\n[5/8] Buscando Leadboard do Nectar CRM...")
    nectar = fetch_nectar_leadboard()

    print("\n[6/8] Buscando dados da Tron Rio Verde...")
    rv_data = fetch_rv_data()

    print("\n[7/8] Buscando dados orgânicos (Instagram + Facebook)...")
    organic = fetch_organic_data()

    print("\n[8/8] Calculando orçamentos e atualizando HTML...")
    camp_budgets = fetch_campaign_budgets()
    budgets = calc_budgets(adsets, camp_budgets)
    total_budget = fetch_total_daily_budget(adsets)
    js_block = build_js_block(all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar,
                               total_budget=total_budget, rv_data=rv_data, organic=organic)
    update_html(js_block)

    print("\n" + "=" * 60)
    print("Dashboard atualizado! Abra o arquivo no navegador.")
    print("=" * 60)

if __name__ == "__main__":
    main()
