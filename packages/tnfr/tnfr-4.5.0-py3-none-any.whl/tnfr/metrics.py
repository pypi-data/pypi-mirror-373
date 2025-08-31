from __future__ import annotations
from typing import Dict, Any, List, Tuple
from collections import defaultdict, Counter
import statistics
import csv
import json
from math import cos

from .constants import DEFAULTS, ALIAS_EPI, ALIAS_THETA, ALIAS_DNFR
from .helpers import (
    register_callback,
    ensure_history,
    last_glifo,
    _get_attr,
    clamp01,
    list_mean,
    fmean,
)
from .sense import GLYPHS_CANONICAL

# -------------
# DEFAULTS
# -------------
DEFAULTS.setdefault("METRICS", {
    "enabled": True,
    "save_by_node": True,     # guarda Tg por nodo (más pesado)
    "normalize_series": False # glifograma normalizado a fracción por paso
})

    
    
# -------------
# Utilidades internas
# -------------


# -------------
# Estado nodal para Tg
# -------------

def _tg_state(nd: Dict[str, Any]) -> Dict[str, Any]:
    """Estructura interna por nodo para acumular tiempos de corrida por glifo.
    Campos: curr (glifo actual), run (tiempo acumulado en el glifo actual)
    """
    return nd.setdefault("_Tg", {"curr": None, "run": 0.0})


# -------------
# Callback principal: actualizar métricas por paso
# -------------

def _metrics_step(G, *args, **kwargs):
    """Actualiza métricas operativas TNFR por paso.

    - Tg (tiempo glífico): sumatoria de corridas por glifo (global y por nodo).
    - Índice de latencia: fracción de nodos en SH’A.
    - Glifograma: conteo o fracción por glifo en el paso.

    Todos los resultados se guardan en G.graph['history'].
    """
    if not G.graph.get("METRICS", DEFAULTS.get("METRICS", {})).get("enabled", True):
        return

    hist = ensure_history(G)
    dt = float(G.graph.get("DT", 1.0))
    t = float(G.graph.get("_t", 0.0))

    # --- Glifograma (conteos por glifo este paso) ---
    counts = Counter()

    # --- Índice de latencia: proporción de nodos en SH’A ---
    n_total = 0
    n_latent = 0

    # --- Tg: acumular corridas por nodo ---
    save_by_node = bool(G.graph.get("METRICS", DEFAULTS["METRICS"]).get("save_by_node", True))
    tg_total = hist.setdefault("Tg_total", defaultdict(float))  # tiempo total por glifo (global)
    tg_by_node = hist.setdefault("Tg_by_node", {})             # nodo → {glifo: [runs,...]}

    for n in G.nodes():
        nd = G.nodes[n]
        g = last_glifo(nd)
        if not g:
            continue

        n_total += 1
        if g == "SH’A":
            n_latent += 1

        counts[g] += 1

        st = _tg_state(nd)
        # Si seguimos en el mismo glifo, acumulamos; si cambiamos, cerramos corrida
        if st["curr"] is None:
            st["curr"] = g
            st["run"] = dt
        elif g == st["curr"]:
            st["run"] += dt
        else:
            # cerramos corrida anterior
            prev = st["curr"]
            dur = float(st["run"])
            tg_total[prev] += dur
            if save_by_node:
                rec = tg_by_node.setdefault(n, defaultdict(list))
                rec[prev].append(dur)
            # reiniciamos corrida
            st["curr"] = g
            st["run"] = dt

    # Al final del paso, no cerramos la corrida actual: se cerrará cuando cambie.

    # Guardar glifograma (conteos crudos y normalizados)
    norm = bool(G.graph.get("METRICS", DEFAULTS["METRICS"]).get("normalize_series", False))
    row = {"t": t}
    total = max(1, sum(counts.values()))
    for g in GLYPHS_CANONICAL:
        c = counts.get(g, 0)
        row[g] = (c / total) if norm else c
    hist.setdefault("glifogram", []).append(row)

    # Guardar índice de latencia
    li = (n_latent / max(1, n_total)) if n_total else 0.0
    hist.setdefault("latency_index", []).append({"t": t, "value": li})

    # --- Soporte y norma de la EPI ---
    thr = float(G.graph.get("EPI_SUPPORT_THR", DEFAULTS.get("EPI_SUPPORT_THR", 0.0)))
    supp_nodes = [n for n in G.nodes() if abs(_get_attr(G.nodes[n], ALIAS_EPI, 0.0)) >= thr]
    norm = (
        sum(abs(_get_attr(G.nodes[n], ALIAS_EPI, 0.0)) for n in supp_nodes) / len(supp_nodes)
        if supp_nodes else 0.0
    )
    hist.setdefault("EPI_support", []).append({"t": t, "size": len(supp_nodes), "norm": float(norm)})

    # --- Métricas morfosintácticas ---
    total = max(1, sum(counts.values()))
    id_val = counts.get("O’Z", 0) / total
    cm_val = (counts.get("Z’HIR", 0) + counts.get("NA’V", 0)) / total
    ne_val = (counts.get("I’L", 0) + counts.get("T’HOL", 0)) / total
    pp_val = counts.get("SH’A", 0) / max(1, counts.get("RE’MESH", 0))
    hist.setdefault("morph", []).append({"t": t, "ID": id_val, "CM": cm_val, "NE": ne_val, "PP": pp_val})


# -------------
# Registro del callback
# -------------

def register_metrics_callbacks(G) -> None:
    register_callback(G, when="after_step", func=_metrics_step, name="metrics_step")
    # Nuevas funcionalidades canónicas
    register_coherence_callbacks(G)
    register_diagnosis_callbacks(G)


# -------------
# Consultas / reportes
# -------------

def Tg_global(G, normalize: bool = True) -> Dict[str, float]:
    """Tiempo glífico total por clase. Si normalize=True, devuelve fracciones del total."""
    hist = ensure_history(G)
    tg_total: Dict[str, float] = hist.get("Tg_total", {})
    total = sum(tg_total.values()) or 1.0
    if normalize:
        return {g: float(tg_total.get(g, 0.0)) / total for g in GLYPHS_CANONICAL}
    return {g: float(tg_total.get(g, 0.0)) for g in GLYPHS_CANONICAL}


def Tg_by_node(G, n, normalize: bool = False) -> Dict[str, float | List[float]]:
    """Resumen por nodo: si normalize, devuelve medias por glifo; si no, lista de corridas."""
    hist = ensure_history(G)
    rec = hist.get("Tg_by_node", {}).get(n, {})
    if not normalize:
        # convertir default dict → list para serializar
        return {g: list(rec.get(g, [])) for g in GLYPHS_CANONICAL}
    out = {}
    for g in GLYPHS_CANONICAL:
        runs = rec.get(g, [])
        out[g] = float(statistics.mean(runs)) if runs else 0.0
        
    return out


def latency_series(G) -> Dict[str, List[float]]:
    hist = ensure_history(G)
    xs = hist.get("latency_index", [])
    return {
        "t": [float(x.get("t", i)) for i, x in enumerate(xs)],
        "value": [float(x.get("value", 0.0)) for x in xs],
    }


def glifogram_series(G) -> Dict[str, List[float]]:
    hist = ensure_history(G)
    xs = hist.get("glifogram", [])
    if not xs:
        return {"t": []}
    out = {"t": [float(x.get("t", i)) for i, x in enumerate(xs)]}
    for g in GLYPHS_CANONICAL:
        out[g] = [float(x.get(g, 0.0)) for x in xs]
    return out


def glyph_top(G, k: int = 3) -> List[Tuple[str, float]]:
    """Top-k operadores estructurales por Tg_global (fracción)."""
    tg = Tg_global(G, normalize=True)
    return sorted(tg.items(), key=lambda kv: kv[1], reverse=True)[:max(1, int(k))]


def glyph_dwell_stats(G, n) -> Dict[str, Dict[str, float]]:
    """Estadísticos por nodo: mean/median/max de corridas por glifo."""
    hist = ensure_history(G)
    rec = hist.get("Tg_by_node", {}).get(n, {})
    out = {}
    for g in GLYPHS_CANONICAL:
        runs = list(rec.get(g, []))
        if not runs:
            out[g] = {"mean": 0.0, "median": 0.0, "max": 0.0, "count": 0}
        else:
            out[g] = {
                "mean": float(statistics.mean(runs)),
                "median": float(statistics.median(runs)),
                "max": float(max(runs)),
                "count": int(len(runs)),
            }
    return out


# -----------------------------
# Export history to CSV/JSON
# -----------------------------

def export_history(G, base_path: str, fmt: str = "csv") -> None:
    """Vuelca glifograma y traza σ(t) a archivos CSV o JSON compactos."""
    hist = ensure_history(G)
    glifo = glifogram_series(G)
    sigma_mag = hist.get("sense_sigma_mag", [])
    sigma = {
        "t": list(range(len(sigma_mag))),
        "sigma_x": hist.get("sense_sigma_x", []),
        "sigma_y": hist.get("sense_sigma_y", []),
        "mag": sigma_mag,
        "angle": hist.get("sense_sigma_angle", []),
    }
    morph = hist.get("morph", [])
    epi_supp = hist.get("EPI_support", [])
    fmt = fmt.lower()
    if fmt == "csv":
        with open(base_path + "_glifogram.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["t", *GLYPHS_CANONICAL])
            ts = glifo.get("t", [])
            default_col = [0] * len(ts)
            for i, t in enumerate(ts):
                row = [t] + [glifo.get(g, default_col)[i] for g in GLYPHS_CANONICAL]
                writer.writerow(row)
        with open(base_path + "_sigma.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["t", "x", "y", "mag", "angle"])
            for i, t in enumerate(sigma["t"]):
                writer.writerow([t, sigma["sigma_x"][i], sigma["sigma_y"][i], sigma["mag"][i], sigma["angle"][i]])
        if morph:
            with open(base_path + "_morph.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["t", "ID", "CM", "NE", "PP"])
                for row in morph:
                    writer.writerow([row.get("t"), row.get("ID"), row.get("CM"), row.get("NE"), row.get("PP")])
        if epi_supp:
            with open(base_path + "_epi_support.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["t", "size", "norm"])
                for row in epi_supp:
                    writer.writerow([row.get("t"), row.get("size"), row.get("norm")])
    else:
        data = {"glifogram": glifo, "sigma": sigma, "morph": morph, "epi_support": epi_supp}
        with open(base_path + ".json", "w") as f:
            json.dump(data, f)


# =========================
# COHERENCIA W_ij^t (TNFR)
# =========================


def _norm01(x, lo, hi):
    if hi <= lo:
        return 0.0
    v = (float(x) - float(lo)) / (float(hi) - float(lo))
    return 0.0 if v < 0 else (1.0 if v > 1.0 else v)


def _similarity_abs(a, b, lo, hi):
    return 1.0 - _norm01(abs(float(a) - float(b)), 0.0, float(hi - lo) if hi > lo else 1.0)


def _coherence_components(G, ni, nj, epi_min, epi_max, vf_min, vf_max):
    ndi = G.nodes[ni]
    ndj = G.nodes[nj]
    th_i = _get_attr(ndi, ALIAS_THETA, 0.0)
    th_j = _get_attr(ndj, ALIAS_THETA, 0.0)
    s_phase = 0.5 * (1.0 + cos(th_i - th_j))
    epi_i = _get_attr(ndi, ALIAS_EPI, 0.0)
    epi_j = _get_attr(ndj, ALIAS_EPI, 0.0)
    s_epi = _similarity_abs(epi_i, epi_j, epi_min, epi_max)
    vf_i = float(_get_attr(ndi, "νf", 0.0))
    vf_j = float(_get_attr(ndj, "νf", 0.0))
    s_vf = _similarity_abs(vf_i, vf_j, vf_min, vf_max)
    si_i = clamp01(float(_get_attr(ndi, "Si", 0.0)))
    si_j = clamp01(float(_get_attr(ndj, "Si", 0.0)))
    s_si = 1.0 - abs(si_i - si_j)
    return s_phase, s_epi, s_vf, s_si


def coherence_matrix(G):
    cfg = G.graph.get("COHERENCE", DEFAULTS["COHERENCE"])
    if not cfg.get("enabled", True):
        return None, None

    nodes = list(G.nodes())
    n = len(nodes)
    if n == 0:
        return nodes, []

    # Precompute indices to avoid repeated list.index calls within loops
    node_to_index = {node: idx for idx, node in enumerate(nodes)}

    epi_vals = [float(_get_attr(G.nodes[v], ALIAS_EPI, 0.0)) for v in nodes]
    vf_vals = [float(_get_attr(G.nodes[v], "νf", 0.0)) for v in nodes]
    epi_min, epi_max = min(epi_vals), max(epi_vals)
    vf_min, vf_max = min(vf_vals), max(vf_vals)

    wdict = dict(cfg.get("weights", {}))
    for k in ("phase", "epi", "vf", "si"):
        wdict.setdefault(k, 0.0)
    wsum = sum(float(v) for v in wdict.values()) or 1.0
    wnorm = {k: float(v) / wsum for k, v in wdict.items()}

    scope = str(cfg.get("scope", "neighbors")).lower()
    neighbors_only = scope != "all"
    self_diag = bool(cfg.get("self_on_diag", True))
    mode = str(cfg.get("store_mode", "sparse")).lower()
    thr = float(cfg.get("threshold", 0.0))
    if mode not in ("sparse", "dense"):
        mode = "sparse"

    if mode == "dense":
        W = [[0.0] * n for _ in range(n)]
    else:
        W = []

    row_sum = [0.0] * n
    row_count = [0] * n

    for i, ni in enumerate(nodes):
        if self_diag:
            if mode == "dense":
                W[i][i] = 1.0
            else:
                W.append((i, i, 1.0))
            row_sum[i] += 1.0
            row_count[i] += 1

        neighs = G.neighbors(ni) if neighbors_only else nodes
        for nj in neighs:
            if nj == ni:
                continue
            j = node_to_index[nj]
            s_phase, s_epi, s_vf, s_si = _coherence_components(
                G, ni, nj, epi_min, epi_max, vf_min, vf_max
            )
            wij = (
                wnorm["phase"] * s_phase
                + wnorm["epi"] * s_epi
                + wnorm["vf"] * s_vf
                + wnorm["si"] * s_si
            )
            wij = clamp01(wij)
            if mode == "dense":
                W[i][j] = wij
            else:
                if wij >= thr:
                    W.append((i, j, wij))
            row_sum[i] += wij
            row_count[i] += 1

    Wi = [row_sum[i] / max(1, row_count[i]) for i in range(n)]
    vals = []
    if mode == "dense":
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                vals.append(W[i][j])
    else:
        for (i, j, w) in W:
            if i == j:
                continue
            vals.append(w)

    stats = {
        "min": min(vals) if vals else 0.0,
        "max": max(vals) if vals else 0.0,
        "mean": (sum(vals) / len(vals)) if vals else 0.0,
        "n_edges": len(vals),
        "mode": mode,
        "scope": scope,
    }

    hist = ensure_history(G)
    hist.setdefault(cfg.get("history_key", "W_sparse"), []).append(W)
    hist.setdefault(cfg.get("Wi_history_key", "W_i"), []).append(Wi)
    hist.setdefault(cfg.get("stats_history_key", "W_stats"), []).append(stats)

    return nodes, W


def local_phase_sync_weighted(G, n, nodes_order=None, W_row=None):
    import cmath

    cfg = G.graph.get("COHERENCE", DEFAULTS["COHERENCE"])
    scope = str(cfg.get("scope", "neighbors")).lower()
    neighbors_only = scope != "all"

    if W_row is None or nodes_order is None:
        vec = [
            cmath.exp(1j * float(_get_attr(G.nodes[v], ALIAS_THETA, 0.0)))
            for v in (G.neighbors(n) if neighbors_only else (set(G.nodes()) - {n}))
        ]
        if not vec:
            return 0.0
        mean = sum(vec) / len(vec)
        return abs(mean)

    i = nodes_order.index(n)
    if isinstance(W_row, list) and W_row and isinstance(W_row[0], (int, float)):
        weights = W_row
    else:
        weights = [0.0] * len(nodes_order)
        for (ii, jj, w) in W_row:
            if ii == i:
                weights[jj] = w

    num = 0 + 0j
    den = 0.0
    for j, nj in enumerate(nodes_order):
        if nj == n:
            continue
        w = weights[j]
        den += w
        th_j = float(_get_attr(G.nodes[nj], ALIAS_THETA, 0.0))
        num += w * cmath.exp(1j * th_j)
    return abs(num / den) if den else 0.0


def _coherence_step(G, ctx=None):
    if not G.graph.get("COHERENCE", DEFAULTS["COHERENCE"]).get("enabled", True):
        return
    coherence_matrix(G)


def register_coherence_callbacks(G) -> None:
    register_callback(G, when="after_step", func=_coherence_step, name="coherence_step")


# =========================
# DIAGNÓSTICO NODAL (TNFR)
# =========================


def _dnfr_norm(nd, dnfr_max):
    val = abs(float(_get_attr(nd, ALIAS_DNFR, 0.0)))
    if dnfr_max <= 0:
        return 0.0
    x = val / dnfr_max
    return 1.0 if x > 1 else x


def _symmetry_index(G, n, k=3, epi_min=None, epi_max=None):
    nd = G.nodes[n]
    epi_i = float(_get_attr(nd, ALIAS_EPI, 0.0))
    vec = list(G.neighbors(n))
    if not vec:
        return 1.0
    epi_bar = fmean(float(_get_attr(G.nodes[v], ALIAS_EPI, epi_i)) for v in vec)
    if epi_min is None or epi_max is None:
        epis = [float(_get_attr(G.nodes[v], ALIAS_EPI, 0.0)) for v in G.nodes()]
        epi_min, epi_max = min(epis), max(epis)
    return _similarity_abs(epi_i, epi_bar, epi_min, epi_max)


def _state_from_thresholds(Rloc, dnfr_n, cfg):
    stb = cfg.get("stable", {"Rloc_hi": 0.8, "dnfr_lo": 0.2, "persist": 3})
    dsr = cfg.get("dissonance", {"Rloc_lo": 0.4, "dnfr_hi": 0.5, "persist": 3})
    if (Rloc >= float(stb["Rloc_hi"])) and (dnfr_n <= float(stb["dnfr_lo"])):
        return "estable"
    if (Rloc <= float(dsr["Rloc_lo"])) and (dnfr_n >= float(dsr["dnfr_hi"])):
        return "disonante"
    return "transicion"


def _recommendation(state, cfg):
    adv = cfg.get("advice", {})
    key = {"estable": "stable", "transicion": "transition", "disonante": "dissonant"}[state]
    return list(adv.get(key, []))


def _diagnosis_step(G, ctx=None):
    dcfg = G.graph.get("DIAGNOSIS", DEFAULTS["DIAGNOSIS"])
    if not dcfg.get("enabled", True):
        return

    hist = ensure_history(G)
    key = dcfg.get("history_key", "nodal_diag")

    dnfr_vals = [abs(float(_get_attr(G.nodes[v], ALIAS_DNFR, 0.0))) for v in G.nodes()]
    dnfr_max = max(dnfr_vals) if dnfr_vals else 1.0
    epi_vals = [float(_get_attr(G.nodes[v], ALIAS_EPI, 0.0)) for v in G.nodes()]
    epi_min, epi_max = (min(epi_vals) if epi_vals else 0.0), (max(epi_vals) if epi_vals else 1.0)

    CfgW = G.graph.get("COHERENCE", DEFAULTS["COHERENCE"])
    Wkey = CfgW.get("Wi_history_key", "W_i")
    Wm_key = CfgW.get("history_key", "W_sparse")
    Wi_series = hist.get(Wkey, [])
    Wi_last = Wi_series[-1] if Wi_series else None
    Wm_series = hist.get(Wm_key, [])
    Wm_last = Wm_series[-1] if Wm_series else None

    nodes = list(G.nodes())
    diag = {}
    for i, n in enumerate(nodes):
        nd = G.nodes[n]
        Si = clamp01(float(_get_attr(nd, "Si", 0.0)))
        EPI = float(_get_attr(nd, ALIAS_EPI, 0.0))
        vf = float(_get_attr(nd, "νf", 0.0))
        dnfr_n = _dnfr_norm(nd, dnfr_max)

        Rloc = 0.0
        if Wm_last is not None:
            if Wm_last and isinstance(Wm_last[0], list):
                row = Wm_last[i]
            else:
                row = Wm_last
            Rloc = local_phase_sync_weighted(G, n, nodes_order=nodes, W_row=row)
        else:
            Rloc = local_phase_sync_weighted(G, n)

        symm = _symmetry_index(G, n, epi_min=epi_min, epi_max=epi_max) if dcfg.get("compute_symmetry", True) else None
        state = _state_from_thresholds(Rloc, dnfr_n, dcfg)

        alerts = []
        if state == "disonante" and dnfr_n >= float(dcfg.get("dissonance", {}).get("dnfr_hi", 0.5)):
            alerts.append("tensión estructural alta")

        advice = _recommendation(state, dcfg)

        rec = {
            "node": n,
            "Si": Si,
            "EPI": EPI,
            "νf": vf,
            "dnfr_norm": dnfr_n,
            "W_i": (Wi_last[i] if (Wi_last and i < len(Wi_last)) else None),
            "R_local": Rloc,
            "symmetry": symm,
            "state": state,
            "advice": advice,
            "alerts": alerts,
        }
        diag[n] = rec

    hist.setdefault(key, []).append(diag)


def dissonance_events(G, ctx=None):
    """Emite eventos de inicio/fin de disonancia estructural por nodo."""
    hist = ensure_history(G)
    evs = hist.setdefault("events", [])
    norms = G.graph.get("_sel_norms", {})
    dnfr_max = float(norms.get("dnfr_max", 1.0)) or 1.0
    step_idx = len(hist.get("C_steps", []))
    for n in G.nodes():
        nd = G.nodes[n]
        dn = abs(_get_attr(nd, ALIAS_DNFR, 0.0)) / dnfr_max
        Rloc = local_phase_sync_weighted(G, n)
        st = bool(nd.get("_disr_state", False))
        if (not st) and dn >= 0.5 and Rloc <= 0.4:
            nd["_disr_state"] = True
            evs.append(("disonance_start", {"node": n, "step": step_idx}))
        elif st and dn <= 0.2 and Rloc >= 0.7:
            nd["_disr_state"] = False
            evs.append(("disonance_end", {"node": n, "step": step_idx}))


def register_diagnosis_callbacks(G) -> None:
    register_callback(G, when="after_step", func=_diagnosis_step, name="diagnosis_step")
    register_callback(G, when="after_step", func=dissonance_events, name="dissonance_events")

