#!/usr/bin/env python3
"""x-viral: utilidades de la skill de X de Emi. Solo biblioteca estándar de Python 3.9+.

Órdenes (ver `xviral.py -h` y skills/x-viral/SKILL.md):

  pesos extraer --repo RUTA     lee el código de xai-org/x-algorithm y escribe data/pesos.json
  pesos comparar --repo RUTA    compara el código vivo con data/pesos.json (sale con 1 si cambió)
  pesos ver                     muestra los pesos guardados
  revisar BORRADOR.json         revisa un borrador (o una semana) contra las reglas de la skill
  semana SEMANA.json            revisa cadencia, separación y balance de pilares de una semana
  balance                       reparto de pilares de lo ya publicado y qué pilar toca
  publicado ...                 anota un post publicado (y luego sus métricas)
  aprender "lección"            guarda una lección en cuenta/aprendizajes.md
  vox leer --repo RUTA          lee de Vox Studio el tono, aprendizajes e ideas de un espacio
  vox idea "texto"              deja una idea para Vox Studio en puente/para-vox.md

Nada aquí publica, programa ni llama a X: eso lo hace una persona o una IA con el
navegador, siempre después del visto bueno de Emi.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
RAIZ = SKILL.parent.parent
PESOS = SKILL / "data" / "pesos.json"
CUENTA = RAIZ / "cuenta"
PUENTE = RAIZ / "puente"

PILARES = ("ia-derecho", "lifestyle", "politica")
FORMATOS = ("texto", "foto", "video", "articulo", "quote")
ESTADOS = ("borrador", "aprobado", "programado", "publicado")

# Señal del borrador -> parámetro del código (home-mixer/params/param.rs).
SENALES = {
    "copiar_link": "ShareViaCopyLinkWeight",
    "dm": "ShareViaDmWeight",
    "reply": "ReplyWeight",
    "quote": "QuoteWeight",
    "follow": "FollowAuthorWeight",
    "share": "ShareWeight",
    "repost": "RetweetWeight",
    "like": "FavoriteWeight",
}
RIESGOS = {
    "report": "ReportWeight",
    "mute": "MuteAuthorWeight",
    "no_me_interesa": "NotInterestedWeight",
    "bloqueo": "BlockAuthorWeight",
}

NUMERICOS = {"f64", "f32", "u64", "i64", "usize", "u32", "i32", "u16", "u8"}
PARAM = re.compile(r'param!\(\s*(\w+)\s*,\s*([\w<>:]+)\s*,\s*"([^"]+)"\s*,\s*([^;]*?)\s*\);', re.S)
ACTUALIZACION = re.compile(r"^### +([A-Z][a-z]+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})\s*$", re.M)

# Anzuelo de interacción: categoría de spam sin exención por tamaño de cuenta.
ANZUELOS = [
    r"\b(dale|da|den|denle|haz|hagan)\s+(un\s+)?(rt|retuit|retweet|repost|like|me gusta|follow)\b",
    r"\b(rt|retuit|retweet|repost|like|follow|s[ií]gueme|comenta|responde)\b[^.\n]{0,40}\by\s+te\s+(mando|paso|env[ií]o|regalo|comparto|doy)\b",
    r"\bcomenta\s+[\"«“']?\w+[\"»”']?\s+(y|para)\b",
    r"\b(like|rt|retuit|repost)\s+si\b",
    r"\betiqueta\s+a\b",
    r"\bs[ií]gueme\s+para\s+(m[aá]s|recibir)\b",
    r"\bfollow\s*(x|por)\s*follow\b",
]
# Frases que delatan texto de IA sin reescribir. Avisos, no errores: decide Emi.
PLANTILLA_IA = [
    r"\ben el mundo actual\b", r"\ben la era (digital|de la)\b", r"\bes importante destacar\b",
    r"\bcabe (destacar|mencionar|señalar)\b", r"\bsum[eé]rgete\b", r"\bdescubre c[oó]mo\b",
    r"\ben resumen\b", r"\ben conclusi[oó]n\b", r"\bno se trata (solo )?de\b[^.\n]{0,60}\bsino\b",
    r"\bno es (solo|s[oó]lo)\b[^.\n]{0,60}\bes\b", r"\bun antes y un despu[eé]s\b",
    r"\bcambi[oó] las reglas del juego\b", r"\bdesbloquea\b", r"\bpotencia tu\b",
]
ACORTADORES = ("bit.ly", "tinyurl.com", "t.ly", "goo.gl", "ow.ly", "cutt.ly", "rebrand.ly",
               "is.gd", "buff.ly", "shorturl.at", "rb.gy", "tiny.cc")
# Nombres que nunca van en un post (límites fijados por Emi el 10/11/2026).
VETADOS = [r"\bcastorena\b", r"\bexpediente\s+(n[uú]m\.?\s*)?\d", r"\bmi cliente\b", r"\bnuestro cliente\b",
           r"\buna? clienta?\s+(m[ií]a|del despacho)\b"]
ATAQUES = [r"\b(idiota|imb[eé]cil|pendej\w+|est[uú]pid\w+|rata|basura|delincuente|corrupt\w+ de mierda)\b"]
URL = re.compile(r"https?://[^\s)>\]]+", re.I)
LIMITE = 280
LIMITE_PREMIUM = 25000
PESO_URL = 23  # X cuenta cada enlace como 23 caracteres


class Falla(Exception):
    pass


def leer_json(ruta: Path):
    try:
        return json.loads(Path(ruta).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise Falla(f"no existe {ruta}")
    except json.JSONDecodeError as exc:
        raise Falla(f"{ruta}: JSON inválido ({exc})")


def escribir_json(ruta: Path, dato) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(dato, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fecha_ok(v) -> bool:
    try:
        return isinstance(v, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", v)) and bool(dt.date.fromisoformat(v))
    except ValueError:
        return False


def hora_ok(v) -> bool:
    return isinstance(v, str) and bool(re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", v))


def hoy() -> str:
    return dt.date.today().isoformat()


def plano(texto: str) -> str:
    """Minúsculas sin acentos ni puntuación, para comparar textos."""
    sin = "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", sin)).strip()


def largo_x(texto: str) -> int:
    """Largo como lo cuenta X: cada enlace vale 23 y los emojis y CJK cuentan doble."""
    total = 0
    for trozo in re.split(f"({URL.pattern})", texto, flags=re.I):
        if URL.fullmatch(trozo or ""):
            total += PESO_URL
            continue
        for c in unicodedata.normalize("NFC", trozo or ""):
            o = ord(c)
            total += 1 if (o <= 0x10FF or 0x2000 <= o <= 0x200D or 0x2010 <= o <= 0x201F or 0x2032 <= o <= 0x2037) else 2
    return total


# ---------------------------------------------------------------- pesos

def valor(tipo: str, crudo: str):
    crudo = crudo.strip().replace("_", "")
    if tipo not in NUMERICOS:
        return None
    try:
        return float(crudo) if tipo.startswith("f") else int(crudo)
    except ValueError:
        return None


def leer_params(fuente: Path) -> tuple[dict, dict]:
    """(pesos, otros) de un archivo de `param!`. Falla si no entiende todos los parámetros."""
    texto = fuente.read_text(encoding="utf-8")
    esperados = len(re.findall(r"\bparam!\(", texto))
    hallados = PARAM.findall(texto)
    if esperados != len(hallados):
        raise Falla(f"{fuente.name}: el lector entendió {len(hallados)} de {esperados} parámetros: cambió el formato; "
                    "hay que actualizar la expresión PARAM antes de confiar en los pesos")
    pesos, otros = {}, {}
    for nombre, tipo, _clave, crudo in hallados:
        v = valor(tipo, crudo)
        if v is None:
            continue
        (pesos if re.search(r"Weight(Boost)?$", nombre) else otros)[nombre] = v
    return dict(sorted(pesos.items())), dict(sorted(otros.items()))


def extraer(repo: Path) -> dict:
    fuente = repo / "home-mixer" / "params" / "param.rs"
    if not fuente.is_file():
        raise Falla(f"{fuente} no existe: ¿es una copia de xai-org/x-algorithm?")
    pesos, otros = leer_params(fuente)
    faltan = [p for p in list(SENALES.values()) + list(RIESGOS.values()) if p not in pesos]
    if faltan:
        raise Falla("ya no existen en el código: " + ", ".join(faltan) + ". Revisar SENALES/RIESGOS y la skill.")
    vm = repo / "vm-ranker" / "params.rs"
    pesos_vm, otros_vm = leer_params(vm) if vm.is_file() else ({}, {})
    readme = repo / "README.md"
    actualizaciones = ACTUALIZACION.findall(readme.read_text(encoding="utf-8")) if readme.is_file() else []
    return {
        "fuente": "https://github.com/xai-org/x-algorithm",
        "archivos": ["home-mixer/params/param.rs", "vm-ranker/params.rs"],
        "commit": git(repo, "rev-parse", "HEAD"),
        "fecha_commit": git(repo, "log", "-1", "--format=%cs"),
        "extraido": hoy(),
        "nota": "Cada peso multiplica la probabilidad PREDICHA de la acción para cada lector; "
                "no multiplica conteos. No leer las razones entre pesos como equivalencias. "
                "Son valores por defecto del código: home-mixer y vm-ranker leen los mismos interruptores "
                "en producción, así que donde difieren el valor real está sin publicar.",
        "pesos": pesos,
        "pesos_vm_ranker": pesos_vm,
        "otros_parametros": otros,
        "otros_vm_ranker": otros_vm,
        "actualizaciones_readme": actualizaciones,
    }


def git(repo: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def diferencias(viejo: dict, nuevo: dict) -> list[str]:
    cambios = []
    for grupo in ("pesos", "pesos_vm_ranker", "otros_parametros", "otros_vm_ranker"):
        a, b = viejo.get(grupo, {}), nuevo.get(grupo, {})
        for k in sorted(set(a) | set(b)):
            if k not in a:
                cambios.append(f"NUEVO   {grupo}.{k} = {b[k]}")
            elif k not in b:
                cambios.append(f"QUITADO {grupo}.{k} (era {a[k]})")
            elif a[k] != b[k]:
                cambios.append(f"CAMBIÓ  {grupo}.{k}: {a[k]} -> {b[k]}")
    va, vb = viejo.get("actualizaciones_readme", []), nuevo.get("actualizaciones_readme", [])
    for fecha in vb:
        if fecha not in va:
            cambios.append(f"README  nueva sección «Notable Updates»: {fecha}")
    return cambios


def cmd_pesos(a) -> int:
    if a.accion == "ver":
        d = leer_json(PESOS)
        print(f"Pesos de {d['commit'][:10]} ({d['fecha_commit']}), extraídos el {d['extraido']}")
        vm = d.get("pesos_vm_ranker", {})
        for k, v in sorted(d["pesos"].items(), key=lambda kv: -kv[1]):
            otro = f"   (vm-ranker: {vm[k]})" if k in vm and vm[k] != v else ""
            print(f"  {v:>9}  {k}{otro}")
        print("\n" + d["nota"])
        return 0
    if not a.repo:
        raise Falla("falta --repo RUTA (copia local de xai-org/x-algorithm)")
    nuevo = extraer(Path(a.repo))
    if a.accion == "extraer":
        escribir_json(PESOS, nuevo)
        print(f"Escrito {PESOS.relative_to(RAIZ)}: {len(nuevo['pesos'])} pesos de home-mixer, "
              f"{len(nuevo['pesos_vm_ranker'])} de vm-ranker, commit {nuevo['commit'][:10]}")
        return 0
    viejo = leer_json(PESOS)
    cambios = diferencias(viejo, nuevo)
    print(f"Guardado: {viejo['commit'][:10]} ({viejo['fecha_commit']})  ·  vivo: {nuevo['commit'][:10]} ({nuevo['fecha_commit']})")
    if not cambios:
        print("Sin cambios en pesos, parámetros ni actualizaciones del README.")
        return 0
    print("\n".join(cambios))
    print(f"\n{len(cambios)} cambio(s). Actualizar references/algoritmo.md, correr «pesos extraer» y registrar en CHANGELOG.md.")
    return 1


# ---------------------------------------------------------------- borradores

def perfil() -> dict:
    ruta = CUENTA / "perfil.json"
    return leer_json(ruta) if ruta.is_file() else {}


def publicados() -> list[dict]:
    ruta = CUENTA / "publicados.jsonl"
    if not ruta.is_file():
        return []
    filas = []
    for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if linea.strip():
            try:
                filas.append(json.loads(linea))
            except json.JSONDecodeError as exc:
                raise Falla(f"{ruta}:{n}: línea inválida ({exc})")
    return filas


def nivel(valor_, campo: str, errores: list[str]) -> int:
    if isinstance(valor_, bool) or not isinstance(valor_, int) or not 0 <= valor_ <= 3:
        errores.append(f"{campo}: debe ser un entero de 0 (nulo) a 3 (alto)")
        return 0
    return valor_


def indice(senales: dict, pesos: dict) -> int:
    """0-100: suma de peso × nivel sobre el máximo posible. Sirve para comparar borradores entre sí,
    no predice alcance: la probabilidad real la calcula el modelo de X para cada lector."""
    maximo = sum(pesos[p] * 3 for p in SENALES.values())
    suma = sum(pesos[SENALES[s]] * n for s, n in senales.items())
    return round(100 * suma / maximo) if maximo else 0


def revisar(b: dict, pesos: dict, historial: list[dict], cfg: dict, para: str = "") -> tuple[list[str], list[str], int]:
    """Devuelve (errores, avisos, índice). `para` es el estado al que se quiere pasar."""
    e: list[str] = []
    w: list[str] = []
    if not isinstance(b, dict):
        return ["el borrador debe ser un objeto JSON"], [], 0
    texto = b.get("texto")
    if not isinstance(texto, str) or not texto.strip():
        return ["texto: falta"], [], 0
    pilar, formato, estado = b.get("pilar"), b.get("formato", "texto"), para or b.get("estado", "borrador")
    if pilar not in PILARES:
        e.append(f"pilar: debe ser uno de {', '.join(PILARES)}")
    if formato not in FORMATOS:
        e.append(f"formato: debe ser uno de {', '.join(FORMATOS)}")
    if estado not in ESTADOS:
        e.append(f"estado: debe ser uno de {', '.join(ESTADOS)}")

    limite = LIMITE_PREMIUM if (cfg.get("premium") or formato == "articulo") else LIMITE
    n = largo_x(texto)
    if n > limite:
        e.append(f"texto: {n} caracteres; el límite de la cuenta es {limite}")
    if formato == "articulo" and not cfg.get("premium"):
        w.append("formato articulo: los artículos de X piden suscripción Premium; confirmar que la cuenta la tiene")

    bajo = texto.lower()
    for patron in ANZUELOS:
        m = re.search(patron, bajo)
        if m:
            e.append(f"anzuelo de interacción («{m.group(0)}»): es spam sin exención en el código; pide compartir o conversar")
    for patron in VETADOS:
        m = re.search(patron, bajo)
        if m:
            e.append(f"límite de Emi («{m.group(0)}»): nunca clientes, asuntos ni Castorena")
    for patron in ATAQUES:
        m = re.search(patron, bajo)
        if m:
            e.append(f"ataque personal («{m.group(0)}»): se critican ideas y decisiones, no personas")
    for patron in PLANTILLA_IA:
        m = re.search(patron, bajo)
        if m:
            w.append(f"suena a plantilla de IA («{m.group(0)}»): reescribir con la voz de Emi")
    if texto.count("—") >= 2:
        w.append("dos o más rayas largas (—): marca típica de texto de IA; usar comas o puntos")
    etiquetas = re.findall(r"(?<!\w)#\w+", texto)
    if len(etiquetas) > 2:
        w.append(f"{len(etiquetas)} hashtags: el código no los premia; dejan el texto con aspecto de plantilla")
    for url in URL.findall(texto):
        dominio = re.sub(r"^https?://(www\.)?", "", url, flags=re.I).split("/")[0].lower()
        if dominio in ACORTADORES:
            w.append(f"acortador ({dominio}): el código juzga el destino final, no el acortador, pero el lector no ve a dónde va; mejor el enlace directo")

    base = plano(texto)
    for fila in historial:
        if fila.get("id") and fila.get("id") == b.get("id"):
            continue
        otro = plano(fila.get("texto", ""))
        if otro and difflib.SequenceMatcher(None, base, otro).ratio() >= 0.85:
            e.append(f"casi idéntico a «{fila.get('id', '?')}» ({fila.get('fecha', '?')}): el texto duplicado se etiqueta como spam; reescribir el ángulo")
            break

    senales = b.get("senales")
    if not isinstance(senales, dict):
        e.append("senales: falta (copiar_link, dm, reply, quote, follow, share, repost, like de 0 a 3)")
        senales = {}
    sobran = set(senales) - set(SENALES)
    if sobran:
        e.append("senales: claves desconocidas " + ", ".join(sorted(sobran)))
    niveles = {s: nivel(senales.get(s, 0), f"senales.{s}", e) for s in SENALES}
    caras = {s: niveles[s] for s in ("copiar_link", "dm", "reply", "quote", "follow")}
    if not any(v >= 2 for v in caras.values()):
        e.append("señal cara: ninguna de copiar_link, dm, reply, quote o follow llega a 2; si solo daría like, el post es débil")
    porque = b.get("por_que") if isinstance(b.get("por_que"), dict) else {}
    for s, v in caras.items():
        if v >= 2 and not str(porque.get(s, "")).strip():
            e.append(f"por_que.{s}: explicar en una frase por qué alguien haría eso (nivel {v})")

    riesgos = b.get("riesgos")
    if not isinstance(riesgos, dict):
        e.append("riesgos: falta (report, mute, no_me_interesa, bloqueo de 0 a 3)")
        riesgos = {}
    sobran = set(riesgos) - set(RIESGOS)
    if sobran:
        e.append("riesgos: claves desconocidas " + ", ".join(sorted(sobran)))
    for r in RIESGOS:
        v = nivel(riesgos.get(r, 0), f"riesgos.{r}", e)
        if v >= 2:
            e.append(f"riesgos.{r} = {v}: {RIESGOS[r]} vale {pesos[RIESGOS[r]]}; reescribir hasta bajarlo a 1 o menos")
        elif v == 1 and r == "report":
            w.append("riesgos.report = 1: es el peso más negativo del código; releer con ojos de quien piensa distinto")

    if pilar == "politica" and not str(b.get("opinion_emi", "")).strip():
        e.append("opinion_emi: en política la postura la da Emi con sus palabras; preguntársela antes de redactar")
    if b.get("cita_legal"):
        fuentes = b.get("fuentes")
        if not isinstance(fuentes, list) or not fuentes or not all(isinstance(f, str) and URL.match(f) for f in fuentes):
            e.append("fuentes: una cita legal exige al menos un enlace a fuente oficial verificada")
    elif re.search(r"\b(art[ií]culo|art\.)\s+\d+|\btesis\b|\bjurisprudencia\b|\bDOF\b|\bSCJN\b", texto):
        w.append("el texto parece citar derecho: marcar cita_legal y poner fuentes")
    if formato == "video":
        dur = b.get("duracion_s")
        if not isinstance(dur, (int, float)) or isinstance(dur, bool):
            e.append("duracion_s: en video hay que indicar la duración en segundos")
        elif dur <= cfg.get("video_min_s", 10):
            e.append(f"duracion_s = {dur}: el video debe durar más de {cfg.get('video_min_s', 10)} s")
        if b.get("piezas_media", 1) != 1:
            e.append("piezas_media: en video, una sola pieza por post")
    if formato in ("foto", "video") and not str(b.get("media", "")).strip():
        e.append("media: describir o enlazar el archivo propio que acompaña al post")

    if estado in ("aprobado", "programado", "publicado"):
        if not str(b.get("aprobado_por_emi", "")).strip():
            e.append(f"aprobado_por_emi: para pasar a «{estado}» hace falta la fecha y el medio del visto bueno de Emi")
        if not b.get("reescrito"):
            e.append("reescrito: debe ser true; nada sale con el texto crudo de una IA")
    if estado in ("programado", "publicado"):
        if not fecha_ok(b.get("fecha")):
            e.append("fecha: falta o no es una fecha válida AAAA-MM-DD")
        if not hora_ok(b.get("hora")):
            e.append("hora: falta o no es una hora válida HH:MM (00:00 a 23:59)")
    return e, w, indice(niveles, pesos)


def informe(nombre: str, e: list[str], w: list[str], idx: int) -> None:
    print(f"{nombre}: índice de señales {idx}/100 · {len(e)} error(es), {len(w)} aviso(s)")
    for linea in e:
        print(f"  ERROR  {linea}")
    for linea in w:
        print(f"  aviso  {linea}")


def cmd_revisar(a) -> int:
    dato = leer_json(Path(a.archivo))
    pesos = leer_json(PESOS)["pesos"]
    lista = dato.get("posts") if isinstance(dato, dict) and "posts" in dato else [dato]
    if not isinstance(lista, list):
        raise Falla("«posts» debe ser una lista")
    hist, cfg, malos = publicados(), perfil(), 0
    for i, b in enumerate(lista, 1):
        e, w, idx = revisar(b, pesos, hist, cfg, a.para or "")
        informe(str(b.get("id", f"post {i}")) if isinstance(b, dict) else f"post {i}", e, w, idx)
        malos += bool(e)
    return 1 if malos else 0


def minutos(hora: str) -> int:
    h, m = hora.split(":")
    return int(h) * 60 + int(m)


def revisar_semana(posts: list[dict], cfg: dict) -> tuple[list[str], list[str]]:
    e: list[str] = []
    w: list[str] = []
    tope = cfg.get("max_originales_dia", 2)
    separa = cfg.get("separacion_min_h", 4)
    por_dia: dict[str, list[dict]] = {}
    for b in posts:
        if not fecha_ok(b.get("fecha")) or not hora_ok(b.get("hora")):
            e.append(f"{b.get('id', '?')}: en una semana cada post lleva fecha AAAA-MM-DD y hora HH:MM válidas")
            continue
        por_dia.setdefault(b["fecha"], []).append(b)
    for fecha, del_dia in sorted(por_dia.items()):
        if len(del_dia) > tope:
            e.append(f"{fecha}: {len(del_dia)} posts; el máximo es {tope} (cada post extra del mismo autor vale menos en el mismo feed)")
        horas = sorted(minutos(b["hora"]) for b in del_dia)
        for x, y in zip(horas, horas[1:]):
            if y - x < separa * 60:
                e.append(f"{fecha}: dos posts a {(y - x) / 60:.1f} h; separarlos al menos {separa} h")
        if len(del_dia) > 1 and len({b.get("pilar") for b in del_dia}) == 1:
            w.append(f"{fecha}: los posts del día son del mismo pilar; alternar")
    cuenta = {p: sum(1 for b in posts if b.get("pilar") == p) for p in PILARES}
    total = sum(cuenta.values())
    objetivo = cfg.get("balance", {p: 1 / 3 for p in PILARES})
    tol = cfg.get("tolerancia_balance", 0.15)
    if total >= 6:
        for p in PILARES:
            parte = cuenta[p] / total
            if abs(parte - objetivo.get(p, 1 / 3)) > tol:
                e.append(f"balance: {p} es {parte:.0%} de la semana; el objetivo es {objetivo.get(p, 1 / 3):.0%} ± {tol:.0%}")
    elif total:
        faltan = [p for p in PILARES if not cuenta[p]]
        if faltan and total >= 3:
            w.append("balance: la semana no tiene posts de " + ", ".join(faltan))
    return e, w


def cmd_semana(a) -> int:
    dato = leer_json(Path(a.archivo))
    posts = dato.get("posts") if isinstance(dato, dict) else None
    if not isinstance(posts, list) or not posts:
        raise Falla("la semana debe ser {\"semana\": \"AAAA-Wnn\", \"posts\": [...]}")
    pesos, hist, cfg = leer_json(PESOS)["pesos"], publicados(), perfil()
    malos = 0
    textos: list[dict] = list(hist)
    for i, b in enumerate(posts, 1):
        e, w, idx = revisar(b, pesos, textos, cfg)
        if not isinstance(b, dict):
            informe(f"post {i}", e, w, idx)
            malos += 1
            continue
        informe(str(b.get("id", f"post {i}")), e, w, idx)
        malos += bool(e)
        textos.append({"id": b.get("id"), "texto": str(b.get("texto", "")), "fecha": b.get("fecha")})
    e, w = revisar_semana([b for b in posts if isinstance(b, dict)], cfg)
    if any(not isinstance(b, dict) for b in posts):
        e.append("la semana tiene elementos que no son borradores (objetos JSON)")
    posts = [b for b in posts if isinstance(b, dict)]
    cuenta = {p: sum(1 for b in posts if b.get("pilar") == p) for p in PILARES}
    print("Semana: " + " · ".join(f"{p} {n}" for p, n in cuenta.items()))
    for linea in e:
        print(f"  ERROR  {linea}")
    for linea in w:
        print(f"  aviso  {linea}")
    return 1 if (malos or e) else 0


def cmd_balance(a) -> int:
    cfg = perfil()
    desde = (dt.date.today() - dt.timedelta(days=a.dias)).isoformat()
    filas = [f for f in publicados() if str(f.get("fecha", "")) >= desde]
    cuenta = {p: sum(1 for f in filas if f.get("pilar") == p) for p in PILARES}
    total = sum(cuenta.values())
    objetivo = cfg.get("balance", {p: 1 / 3 for p in PILARES})
    print(f"Publicados en {a.dias} días: {total}")
    if not total:
        print("Aún no hay publicados: empezar con un post de cada pilar.")
        return 0
    deuda = {}
    for p in PILARES:
        parte = cuenta[p] / total
        deuda[p] = objetivo.get(p, 1 / 3) - parte
        print(f"  {p:<11} {cuenta[p]:>3}  {parte:>4.0%}  (objetivo {objetivo.get(p, 1 / 3):.0%})")
    print(f"Toca: {max(deuda, key=deuda.get)}")
    return 0


def cmd_publicado(a) -> int:
    ruta = CUENTA / "publicados.jsonl"
    filas = publicados()
    if a.metricas:
        try:
            metricas = {k: int(v) for k, v in (par.split("=", 1) for par in a.metricas)}
        except ValueError:
            raise Falla("--metricas va como clave=número, por ejemplo vistas=1200 replies=4")
        for f in filas:
            if f.get("id") == a.id:
                f.setdefault("metricas", {}).update(metricas)
                f["metricas_fecha"] = hoy()
                break
        else:
            raise Falla(f"no hay un publicado con id {a.id}")
    else:
        if any(f.get("id") == a.id for f in filas):
            raise Falla(f"ya existe un publicado con id {a.id}")
        if a.pilar not in PILARES:
            raise Falla(f"--pilar debe ser uno de {', '.join(PILARES)}")
        if not a.texto:
            raise Falla("falta --texto (el texto tal como se publicó)")
        filas.append({"id": a.id, "fecha": a.fecha or hoy(), "hora": a.hora or "", "pilar": a.pilar,
                      "formato": a.formato, "texto": a.texto, "url": a.url or ""})
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8")
    print(f"Anotado {a.id} en {ruta.relative_to(RAIZ)}")
    return 0


def cmd_aprender(a) -> int:
    leccion = " ".join(a.leccion.split())
    if len(leccion) < 15:
        raise Falla("la lección debe decir qué pasó y qué regla queda")
    ruta = CUENTA / "aprendizajes.md"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if not ruta.is_file():
        ruta.write_text("# Aprendizajes de la cuenta de X\n\n", encoding="utf-8")
    marca = f" [{a.pilar}]" if a.pilar else ""
    with ruta.open("a", encoding="utf-8") as fh:
        fh.write(f"- {hoy()}{marca} · {leccion}\n")
    print(f"Guardado en {ruta.relative_to(RAIZ)}")
    return 0


# ---------------------------------------------------------------- vox

VOX_RAW = "https://raw.githubusercontent.com/lianfixx/VIDEOS-IA-SKILL-MILLA/{ref}/{ruta}"
VOX_ARCHIVOS = ("espacios/APRENDIZAJES.md", "espacios/{e}/perfil.json", "espacios/{e}/MARCA.md",
                "espacios/{e}/aprendizajes.md", "espacios/{e}/ideas.md")
ESPACIOS = ("personal", "milla", "castorena", "pan")


def traer(ruta: str, repo: str | None, ref: str) -> str | None:
    if repo:
        archivo = Path(repo) / ruta
        return archivo.read_text(encoding="utf-8") if archivo.is_file() else None
    try:
        with urllib.request.urlopen(VOX_RAW.format(ref=ref, ruta=ruta), timeout=20) as r:
            return r.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def cmd_vox(a) -> int:
    if a.accion == "idea":
        idea = " ".join((a.texto or "").split())
        if len(idea) < 15:
            raise Falla("la idea debe decir tema, por qué funcionó en X y fuente o post de origen")
        if a.espacio not in ESPACIOS:
            raise Falla(f"--espacio debe ser uno de {', '.join(ESPACIOS)}")
        ruta = PUENTE / "para-vox.md"
        if not ruta.is_file():
            raise Falla(f"falta {ruta}")
        with ruta.open("a", encoding="utf-8") as fh:
            fh.write(f"- {hoy()} · [{a.espacio}] {idea}\n")
        print(f"Idea dejada en {ruta.relative_to(RAIZ)}")
        return 0
    if a.espacio not in ESPACIOS:
        raise Falla(f"--espacio debe ser uno de {', '.join(ESPACIOS)}")
    hallado = 0
    for plantilla in VOX_ARCHIVOS:
        ruta = plantilla.format(e=a.espacio)
        texto = traer(ruta, a.repo, a.ref)
        print(f"===== Vox Studio · {ruta}")
        if texto is None:
            print("(no disponible)")
        else:
            hallado += 1
            print(texto.strip())
    if not hallado:
        print(f"\nNo se pudo leer nada de Vox Studio ({'copia ' + a.repo if a.repo else 'rama ' + a.ref}). "
              "Trabajar con cuenta/voz.md y decirle a Emi que el puente no respondió.")
        return 1
    return 0


# ---------------------------------------------------------------- entrada

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="xviral.py", description="Utilidades de la skill x-viral.")
    sub = p.add_subparsers(dest="orden", required=True)

    s = sub.add_parser("pesos", help="pesos del algoritmo")
    s.add_argument("accion", choices=("extraer", "comparar", "ver"))
    s.add_argument("--repo", help="copia local de xai-org/x-algorithm")
    s.set_defaults(fn=cmd_pesos)

    s = sub.add_parser("revisar", help="revisa un borrador o una lista de borradores")
    s.add_argument("archivo")
    s.add_argument("--para", choices=ESTADOS, help="revisar como si fuera a pasar a este estado")
    s.set_defaults(fn=cmd_revisar)

    s = sub.add_parser("semana", help="revisa una semana completa")
    s.add_argument("archivo")
    s.set_defaults(fn=cmd_semana)

    s = sub.add_parser("balance", help="reparto de pilares de lo publicado")
    s.add_argument("--dias", type=int, default=30)
    s.set_defaults(fn=cmd_balance)

    s = sub.add_parser("publicado", help="anota un post publicado o sus métricas")
    s.add_argument("id")
    s.add_argument("--pilar")
    s.add_argument("--formato", default="texto", choices=FORMATOS)
    s.add_argument("--texto")
    s.add_argument("--fecha")
    s.add_argument("--hora")
    s.add_argument("--url")
    s.add_argument("--metricas", nargs="+", metavar="CLAVE=N")
    s.set_defaults(fn=cmd_publicado)

    s = sub.add_parser("aprender", help="guarda una lección")
    s.add_argument("leccion")
    s.add_argument("--pilar", choices=PILARES)
    s.set_defaults(fn=cmd_aprender)

    s = sub.add_parser("vox", help="puente con Vox Studio")
    s.add_argument("accion", choices=("leer", "idea"))
    s.add_argument("texto", nargs="?")
    s.add_argument("--espacio", default="personal")
    s.add_argument("--repo", help="copia local de lianfixx/VIDEOS-IA-SKILL-MILLA")
    s.add_argument("--ref", default="main", help="rama de Vox Studio al leer por red")
    s.set_defaults(fn=cmd_vox)

    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except Falla as exc:
        print(f"xviral: {exc}", file=sys.stderr)
        return 2
    except BrokenPipeError:  # salida cortada por «| head»
        sys.stderr.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
