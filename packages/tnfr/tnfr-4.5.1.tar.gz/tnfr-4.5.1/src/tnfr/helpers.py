"""
helpers.py — TNFR canónica

Utilidades transversales + cálculo de Índice de sentido (Si).
"""
from __future__ import annotations
from typing import Iterable, Dict, Any
import math
from collections import deque
from statistics import fmean, StatisticsError

try:
    import networkx as nx  # solo para tipos
except Exception:  # pragma: no cover
    nx = None  # type: ignore

from .constants import DEFAULTS, ALIAS_VF, ALIAS_THETA, ALIAS_DNFR, ALIAS_EPI, ALIAS_SI, ALIAS_EPI_KIND

# -------------------------
# Utilidades numéricas
# -------------------------

def clamp(x: float, a: float, b: float) -> float:
    """Constriñe ``x`` al intervalo cerrado [a, b]."""
    return a if x < a else b if x > b else x


def clamp_abs(x: float, m: float) -> float:
    """Limita ``x`` al rango simétrico [-m, m] usando ``abs(m)``."""
    m = abs(m)
    return clamp(x, -m, m)


def clamp01(x: float) -> float:
    """Ataja ``x`` a la banda [0, 1]."""
    return clamp(x, 0.0, 1.0)


def list_mean(xs: Iterable[float], default: float = 0.0) -> float:
    """Promedio aritmético o ``default`` si ``xs`` está vacío."""
    try:
        return fmean(xs)
    except StatisticsError:
        return default


def _wrap_angle(a: float) -> float:
    """Envuelve ángulo a (-π, π]."""
    pi = math.pi
    a = (a + pi) % (2 * pi) - pi
    return a


def phase_distance(a: float, b: float) -> float:
    """Distancia de fase normalizada en [0,1]. 0 = misma fase, 1 = opuesta."""
    return abs(_wrap_angle(a - b)) / math.pi


# -------------------------
# Acceso a atributos con alias
# -------------------------

def _get_attr(d: Dict[str, Any], aliases: Iterable[str], default: float = 0.0) -> float:
    for k in aliases:
        if k in d:
            try:
                return float(d[k])
            except Exception:
                continue
    return float(default)

def _set_attr(d, aliases, value: float) -> None:
    for k in aliases:
        if k in d:
            d[k] = float(value)
            return
    d[next(iter(aliases))] = float(value)


def _get_attr_str(d: Dict[str, Any], aliases: Iterable[str], default: str = "") -> str:
    for k in aliases:
        if k in d:
            try:
                return str(d[k])
            except Exception:
                continue
    return str(default)


def _set_attr_str(d, aliases, value: str) -> None:
    for k in aliases:
        if k in d:
            d[k] = str(value)
            return
    d[next(iter(aliases))] = str(value)

# -------------------------
# Estadísticos vecinales
# -------------------------

def media_vecinal(G, n, aliases: Iterable[str], default: float = 0.0) -> float:
    """Media del atributo indicado por ``aliases`` en los vecinos de ``n``."""
    vals = (_get_attr(G.nodes[v], aliases, default) for v in G.neighbors(n))
    return list_mean(vals, default)


def fase_media(G, n) -> float:
    """Promedio circular de las fases de los vecinos."""
    x = y = 0.0
    count = 0
    for v in G.neighbors(n):
        th = _get_attr(G.nodes[v], ALIAS_THETA, 0.0)
        x += math.cos(th)
        y += math.sin(th)
        count += 1
    if count == 0:
        return _get_attr(G.nodes[n], ALIAS_THETA, 0.0)
    return math.atan2(y / count, x / count)


# -------------------------
# Historial de glifos por nodo
# -------------------------

def push_glifo(nd: Dict[str, Any], glifo: str, window: int) -> None:
    """Añade ``glifo`` al historial del nodo con tamaño máximo ``window``."""
    hist = nd.setdefault("hist_glifos", deque(maxlen=window))
    hist.append(str(glifo))


def reciente_glifo(nd: Dict[str, Any], glifo: str, ventana: int) -> bool:
    """Indica si ``glifo`` apareció en las últimas ``ventana`` emisiones"""
    hist = nd.get("hist_glifos")
    gl = str(glifo)
    from itertools import islice
    if hist and any(g == gl for g in islice(reversed(hist), ventana)):
        return True
    # fallback al glifo dominante actual
    return _get_attr_str(nd, ALIAS_EPI_KIND, "") == gl

# -------------------------
# Utilidades de historial global
# -------------------------

def ensure_history(G) -> Dict[str, Any]:
    """Garantiza G.graph['history'] y la devuelve."""
    return G.graph.setdefault("history", {})


def last_glifo(nd: Dict[str, Any]) -> str | None:
    """Retorna el glifo más reciente del nodo o ``None``."""
    kind = _get_attr_str(nd, ALIAS_EPI_KIND, "")
    if kind:
        return kind
    hist = nd.get("hist_glifos")
    if not hist:
        return None
    try:
        return hist[-1]
    except Exception:
        return None

# -------------------------
# Callbacks Γ(R)
# -------------------------

def _ensure_callbacks(G):
    """Garantiza la estructura de callbacks en G.graph."""
    cbs = G.graph.setdefault("callbacks", {
        "before_step": [],
        "after_step": [],
        "on_remesh": [],
    })
    # normaliza claves por si vienen incompletas
    for k in ("before_step", "after_step", "on_remesh"):
        cbs.setdefault(k, [])
    return cbs

def register_callback(
    G,
    event: str | None = None,
    func=None,
    *,
    when: str | None = None,
    name: str | None = None,
):
    """Registra ``func`` como callback del ``event`` indicado.

    Permite tanto la forma posicional ``register_callback(G, "after_step", fn)``
    como la forma con palabras clave ``register_callback(G, when="after_step", func=fn)``.
    El parámetro ``name`` se acepta por compatibilidad pero actualmente no se
    utiliza.
    """
    event = event or when
    if event not in ("before_step", "after_step", "on_remesh"):
        raise ValueError(f"Evento desconocido: {event}")
    if func is None:
        raise TypeError("func es obligatorio")
    cbs = _ensure_callbacks(G)
    cbs[event].append(func)
    return func

def invoke_callbacks(G, event: str, ctx: dict | None = None):
    """Invoca todos los callbacks registrados para `event` con el contexto `ctx`."""
    cbs = _ensure_callbacks(G).get(event, [])
    strict = bool(G.graph.get("CALLBACKS_STRICT", DEFAULTS["CALLBACKS_STRICT"]))
    ctx = ctx or {}
    for fn in list(cbs):
        try:
            fn(G, ctx)
        except Exception as e:
            if strict:
                raise
            G.graph.setdefault("_callback_errors", []).append({
                "event": event, "step": ctx.get("step"), "error": repr(e), "fn": repr(fn)
            })

# -------------------------
# Índice de sentido (Si)
# -------------------------

def compute_Si(G, *, inplace: bool = True) -> Dict[Any, float]:
    """Calcula Si por nodo y lo escribe en G.nodes[n]["Si"].

    Fórmula:
        Si = α·νf_norm + β·(1 - disp_fase_local) + γ·(1 - |ΔNFR|/max|ΔNFR|)
    También guarda en ``G.graph`` los pesos normalizados y la
    sensibilidad parcial (∂Si/∂componente).
    """
    alpha = float(G.graph.get("SI_WEIGHTS", DEFAULTS["SI_WEIGHTS"]).get("alpha", 0.34))
    beta = float(G.graph.get("SI_WEIGHTS", DEFAULTS["SI_WEIGHTS"]).get("beta", 0.33))
    gamma = float(G.graph.get("SI_WEIGHTS", DEFAULTS["SI_WEIGHTS"]).get("gamma", 0.33))
    s = alpha + beta + gamma
    if s <= 0:
        alpha = beta = gamma = 1/3
    else:
        alpha, beta, gamma = alpha/s, beta/s, gamma/s
    G.graph["_Si_weights"] = {"alpha": alpha, "beta": beta, "gamma": gamma}
    G.graph["_Si_sensitivity"] = {"dSi_dvf_norm": alpha, "dSi_ddisp_fase": -beta, "dSi_ddnfr_norm": -gamma}

    # Normalización de νf y ΔNFR en red
    vfmax = max((abs(_get_attr(G.nodes[n], ALIAS_VF, 0.0)) for n in G.nodes()), default=1.0)
    dnfrmax = max((abs(_get_attr(G.nodes[n], ALIAS_DNFR, 0.0)) for n in G.nodes()), default=1.0)

    out: Dict[Any, float] = {}
    for n in G.nodes():
        nd = G.nodes[n]
        vf = _get_attr(nd, ALIAS_VF, 0.0)
        vf_norm = 0.0 if vfmax == 0 else clamp01(abs(vf)/vfmax)

        # dispersión de fase local
        th_i = _get_attr(nd, ALIAS_THETA, 0.0)
        th_bar = fase_media(G, n)
        disp_fase = phase_distance(th_i, th_bar)  # [0,1]

        dnfr = _get_attr(nd, ALIAS_DNFR, 0.0)
        dnfr_norm = 0.0 if dnfrmax == 0 else clamp01(abs(dnfr)/dnfrmax)

        Si = alpha*vf_norm + beta*(1.0 - disp_fase) + gamma*(1.0 - dnfr_norm)
        Si = clamp01(Si)
        out[n] = Si
        if inplace:
            _set_attr(nd, ALIAS_SI, Si)
    return out
