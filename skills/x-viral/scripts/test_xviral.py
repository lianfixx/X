#!/usr/bin/env python3
"""Pruebas de xviral.py. Correr: python3 -m unittest discover -s skills/x-viral/scripts -p 'test_*.py'"""
from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import tempfile
import unicodedata
import unittest
from pathlib import Path

import xviral as x

PESOS = json.loads(x.PESOS.read_text(encoding="utf-8"))["pesos"]
MANANA = (dt.date.today() + dt.timedelta(days=1)).isoformat()

PARAM_RS = '''
param!(FavoriteWeight, f64, "a", 0.708);
param!(
    ReplyWeight,
    f64,
    "b",
    5.0
);
param!(BidirectionalFollowReplyWeightBoost, f64, "c", 15.0);
param!(RetweetWeight, f64, "d", 1.0);
param!(ShareWeight, f64, "e", 2.118);
param!(ShareViaDmWeight, f64, "f", 5.0);
param!(ShareViaCopyLinkWeight, f64, "g", 20.0);
param!(QuoteWeight, f64, "h", 5.0);
param!(FollowAuthorWeight, f64, "i", 4.0);
param!(NotInterestedWeight, f64, "j", -53.07);
param!(BlockAuthorWeight, f64, "k", -31.2);
param!(MuteAuthorWeight, f64, "l", -58.8);
param!(ReportWeight, f64, "m", -234.0);
param!(ColdStartSlotMax, u32, "n", 16);
param!(EnableSidSource, bool, "o", false);
param!(Nombre, String, "p", "x".to_string());
param!(Lista, Vec<String>, "q", vec![]);
'''


def carpeta(caso: unittest.TestCase) -> Path:
    tmp = tempfile.TemporaryDirectory()
    caso.addCleanup(tmp.cleanup)
    return Path(tmp.name)


def base(**cambios) -> dict:
    b = {
        "id": "p1", "pilar": "ia-derecho", "formato": "texto", "estado": "borrador",
        "texto": "Le pedí a una IA que revisara un contrato de arrendamiento. Encontró la cláusula que yo pasé por alto.",
        "senales": {"copiar_link": 2, "reply": 1, "like": 2},
        "por_que": {"copiar_link": "sirve para mandárselo a quien renta"},
        "riesgos": {"report": 0, "mute": 0, "no_me_interesa": 0, "bloqueo": 0},
    }
    b.update(cambios)
    return b


def rev(b, hist=(), cfg=None, para=""):
    return x.revisar(b, PESOS, list(hist), cfg or {}, para)


def errores(texto: str, **cambios) -> list[str]:
    return rev(base(texto=texto, **cambios))[0]


class Pesos(unittest.TestCase):
    def repo(self, texto=PARAM_RS, readme="### October 26th, 2026\n\n### August 13th, 2026\n", cfg="48"):
        d = carpeta(self)
        (d / "home-mixer" / "params").mkdir(parents=True)
        (d / "home-mixer" / "params" / "param.rs").write_text(texto, encoding="utf-8")
        (d / "home-mixer" / "params" / "config.rs").write_text(cfg, encoding="utf-8")
        (d / "vm-ranker").mkdir()
        (d / "vm-ranker" / "params.rs").write_text(
            'param!(FavoriteWeight, f64, "a", 0.5);\nparam!(OonWeightFactor, f64, "q", 0.75);\n'
            'param!(EnableAuthorDiversity, bool, "r", true);\n', encoding="utf-8")
        (d / "README.md").write_text(readme, encoding="utf-8")
        return d

    def test_extrae_y_clasifica(self):
        d = x.extraer(self.repo())
        self.assertEqual(d["pesos"]["ShareViaCopyLinkWeight"], 20.0)
        self.assertEqual(d["pesos"]["ReplyWeight"], 5.0)
        self.assertEqual(d["pesos"]["BidirectionalFollowReplyWeightBoost"], 15.0)
        self.assertEqual(d["otros_parametros"], {"ColdStartSlotMax": 16})
        self.assertEqual(d["interruptores"], {"EnableSidSource": False, "Nombre": "x"})
        self.assertEqual(d["pesos_vm_ranker"], {"FavoriteWeight": 0.5})
        self.assertEqual(d["otros_vm_ranker"], {"OonWeightFactor": 0.75})
        self.assertEqual(d["interruptores_vm_ranker"], {"EnableAuthorDiversity": True})
        self.assertEqual(d["actualizaciones_readme"], ["October 26th, 2026", "August 13th, 2026"])
        self.assertEqual(d["archivos_citados"]["visibility-filtering/rules/levels.rs"], "AUSENTE")
        self.assertEqual(len(d["archivos_citados"]["home-mixer/params/config.rs"]), 16)

    def test_formato_desconocido_falla(self):
        with self.assertRaises(x.Falla):
            x.extraer(self.repo(PARAM_RS + "param!(Raro f64 sin comas);\n"))

    def test_peso_necesario_ausente_falla(self):
        with self.assertRaises(x.Falla):
            x.extraer(self.repo(PARAM_RS.replace("ReportWeight", "ReportPeso")))

    def test_sin_param_rs_falla(self):
        with self.assertRaises(x.Falla):
            x.extraer(carpeta(self))

    def test_diferencias(self):
        a = x.extraer(self.repo())
        b = x.extraer(self.repo(
            PARAM_RS.replace("0.708", "0.9").replace("ColdStartSlotMax", "ColdStartSlotMin").replace('"o", false', '"o", true'),
            "### November 1st, 2026\n### October 26th, 2026\n### August 13th, 2026\n", cfg="24"))
        d = "\n".join(x.diferencias(a, b))
        self.assertIn("CAMBIÓ  pesos.FavoriteWeight: 0.708 -> 0.9", d)
        self.assertIn("NUEVO   otros_parametros.ColdStartSlotMin", d)
        self.assertIn("QUITADO otros_parametros.ColdStartSlotMax", d)
        self.assertIn("CAMBIÓ  interruptores.EnableSidSource: False -> True", d)
        self.assertIn("ARCHIVO home-mixer/params/config.rs", d)
        self.assertIn("November 1st, 2026", d)
        self.assertNotIn("ARCHIVO README.md", d)
        self.assertEqual(x.diferencias(a, a), [])

    def test_pesos_guardados_cubren_las_senales(self):
        for nombre in list(x.SENALES.values()) + list(x.RIESGOS.values()):
            self.assertIn(nombre, PESOS)
        for nombre in x.RIESGOS.values():
            self.assertLess(PESOS[nombre], 0)


class Borrador(unittest.TestCase):
    def test_valido(self):
        e, w, idx = rev(base())
        self.assertEqual(e, [])
        self.assertEqual(w, [])
        self.assertTrue(0 < idx <= 100)

    def test_indice_sigue_a_los_pesos(self):
        self.assertGreater(x.indice({"copiar_link": 3}, PESOS), x.indice({"like": 3}, PESOS))
        self.assertEqual(x.indice({s: 3 for s in x.SENALES}, PESOS), 100)
        self.assertEqual(x.indice({}, PESOS), 0)

    def test_solo_like_es_debil(self):
        e, _, _ = rev(base(senales={"like": 3}, por_que={}))
        self.assertTrue(any("señal cara" in m for m in e))

    def test_senal_cara_pide_por_que(self):
        self.assertTrue(any("por_que.copiar_link" in m for m in rev(base(por_que={}))[0]))
        self.assertTrue(any("por_que.copiar_link" in m for m in rev(base(por_que={"copiar_link": 7}))[0]))

    def test_niveles_fuera_de_rango(self):
        for mal in (5, True, "2", 2.5, -1):
            e, _, _ = rev(base(senales={"copiar_link": mal}))
            self.assertTrue(any("0 (nulo) a 3" in m for m in e), mal)
        e, _, _ = rev(base(senales={"copiar_link": 2, "aplausos": 1}))
        self.assertTrue(any("desconocidas" in m for m in e))
        self.assertTrue(any("riesgos: falta" in m for m in rev(base(riesgos=[]))[0]))

    def test_anzuelos_detectados(self):
        for texto in ("Dale RT y te mando el prompt completo.", "Comenta IA y te paso el PDF.",
                      "Like si estás de acuerdo.", "Etiqueta a ese amigo que no entrena pierna.",
                      "Sígueme para más consejos legales.", "Síganme para más tips legales.",
                      "Comenta la palabra CONTRATO y te lo mando por DM.", "Responde SÍ y te lo envío.",
                      "Retuitea si estás harto.", "Regálame un RT.", "Denme follow y les sigo de vuelta.",
                      "Sígueme y te sigo."):
            self.assertTrue(any("anzuelo" in m for m in errores(texto)), texto)

    def test_frases_normales_no_son_anzuelo(self):
        for texto in ("Mi mamá me da like en todo y con eso soy feliz.",
                      "Nadie te va a dar like si no ve el post en su Inicio.",
                      "X etiqueta a las cuentas que publican texto de IA en serie.",
                      "El juez comenta algo y nadie en la sala lo escucha.",
                      "La ministra comenta eso para justificar su voto.",
                      "Si no estás de acuerdo, responde con tu argumento y te doy la razón si me convences.",
                      "Si conoces a alguien que renta, mándale esto. ¿Tú qué cláusula revisarías primero?"):
            self.assertFalse(any("anzuelo" in m for m in errores(texto)), texto)

    def test_limites_detectados(self):
        casos = {
            "Hoy en Castorena vimos un caso curioso.": "no se nombra",
            "Hoy una clienta me preguntó si la IA puede redactar su demanda.": "clientes ni asuntos",
            "Un cliente me dijo ayer que ChatGPT le redactó el contrato.": "clientes ni asuntos",
            "Mis clientes ya usan IA para leer contratos.": "clientes ni asuntos",
            "Nuestro cliente ganó ayer.": "clientes ni asuntos",
            "En el despacho llevamos un asunto de amparo 512/2026 contra el SAT.": "clientes ni asuntos",
            "Llevo el exp. 45/2026 desde enero.": "clientes ni asuntos",
            "Revisé el expediente 123/2026 completo.": "clientes ni asuntos",
            "Ese diputado es un imbécil.": "ataque personal",
            "Esos diputados son unos imbéciles.": "ataque personal",
            "Son unos idiotas.": "ataque personal",
        }
        for texto, esperado in casos.items():
            self.assertTrue(any(esperado in m for m in errores(texto)), texto)

    def test_texto_nfd_no_esquiva_los_limites(self):
        texto = unicodedata.normalize("NFD", "Ese diputado es un imbécil. Sígueme para más.")
        e = errores(texto)
        self.assertTrue(any("ataque personal" in m for m in e))
        self.assertTrue(any("anzuelo" in m for m in e))

    def test_frases_normales_no_tocan_limites(self):
        for texto in ("Saqué la basura y me fui al gym a las 6.",
                      "La reforma trata al contribuyente como delincuente.",
                      "Qué estupidez de iniciativa: castiga al que cumple.",
                      "Fui un idiota por no leer el contrato antes de firmar."):
            self.assertEqual(errores(texto), [], texto)
        _, w, _ = rev(base(texto="Ese senador es un ratero y un payaso."))
        self.assertTrue(any("no a una persona" in m for m in w))

    def test_excepcion_documentada(self):
        texto = "El expediente 1234/2024 de la Suprema Corte es público y vale la pena leerlo."
        self.assertTrue(errores(texto))
        e, w, _ = rev(base(texto=texto, excepcion_limite="asunto público de la SCJN, con enlace"))
        self.assertEqual(e, [])
        self.assertTrue(any("excepción declarada" in m for m in w))
        self.assertTrue(errores("En Castorena no usan IA.", excepcion_limite="lo que sea"))

    def test_plantilla_de_ia_avisa(self):
        _, w, _ = rev(base(texto="En el mundo actual, la IA cambia todo — de verdad."))
        self.assertTrue(any("plantilla de IA" in m for m in w))
        self.assertTrue(any("raya larga" in m for m in w))
        _, w, _ = rev(base(texto="No es un trámite, es un derecho."))
        self.assertTrue(any("plantilla de IA" in m for m in w))
        _, w, _ = rev(base(texto="Tres ideas:\n✅ leer\n✅ firmar\n✅ guardar"))
        self.assertTrue(any("viñetas" in m for m in w))

    def test_largo(self):
        self.assertTrue(any("281 caracteres" in m for m in errores("a" * 281)))
        self.assertEqual(rev(base(texto="a" * 281), cfg={"premium": True})[0], [])
        self.assertTrue(rev(base(texto="a" * 281), cfg={"premium": "false"})[0])
        self.assertEqual(x.largo_x("a" * 250 + " https://ejemplo.mx/una/ruta/larguisima/que/no/cuenta/entera"), 274)
        self.assertEqual(x.largo_x("Ver https://dof.gob.mx/nota."), 4 + 23 + 1)
        self.assertEqual(x.largo_x("ver dof.gob.mx/nota"), 4 + 23)
        self.assertEqual(x.largo_x("niño"), 4)
        self.assertEqual(x.largo_x(unicodedata.normalize("NFD", "niño")), 4)
        for emoji in ("💪", "💪🏽", "👨‍👩‍👧", "🇲🇽", "❤️"):
            self.assertLessEqual(x.largo_x(emoji), 2, emoji)
        self.assertEqual(x.largo_x("💪💪"), 4)

    def test_acortador_solo_avisa(self):
        e, w, _ = rev(base(texto="La nota completa: https://bit.ly/abc"))
        self.assertEqual(e, [])
        self.assertTrue(any("acortador" in m for m in w))
        self.assertEqual(rev(base(texto="La nota completa: https://www.dof.gob.mx/nota"))[1], [])

    def test_duplicado(self):
        hist = [{"id": "viejo", "fecha": "2026-11-01", "texto": base()["texto"].replace("Encontró", "Halló")}]
        self.assertTrue(any("casi idéntico" in m for m in rev(base(), hist)[0]))
        largo = ("Le pedí a tres modelos de IA que revisaran un contrato de arrendamiento de vivienda en la Ciudad de "
                 "México. Dos inventaron una cláusula de penalización que no existe en el documento y solo uno marcó "
                 "el problema real del depósito en garantía. Moraleja práctica: léelo tú también antes de firmar.")
        hist = [{"id": "largo", "texto": largo.replace("depósito en garantía", "fiador")}]
        self.assertTrue(any("casi idéntico" in m for m in rev(base(texto=largo, senales={"copiar_link": 2}), hist)[0]))
        revuelto = ". ".join(reversed(largo.rstrip(".").split(". "))) + "."
        self.assertTrue(any("casi idéntico" in m for m in rev(base(texto=revuelto), [{"id": "l", "texto": largo}])[0]))
        self.assertEqual(rev(base(), [{"id": "otro", "texto": "Hoy tocó pierna y después audiencia a las nueve."}])[0], [])
        mismo = base()
        self.assertEqual(rev(mismo, [mismo])[0], [])

    def test_riesgo_alto_bloquea(self):
        self.assertTrue(any("riesgos.mute = 2" in m for m in rev(base(riesgos={"mute": 2}))[0]))
        self.assertTrue(any("riesgos.report = 1" in m for m in rev(base(riesgos={"report": 1}))[1]))

    def test_politica_pide_opinion(self):
        self.assertTrue(any("opinion_emi" in m for m in rev(base(pilar="politica"))[0]))
        self.assertTrue(any("opinion_emi" in m for m in rev(base(pilar="politica", opinion_emi=True))[0]))
        self.assertEqual(rev(base(pilar="politica", opinion_emi="La reforma concentra poder y lo voy a criticar."))[0], [])

    def test_cita_legal_pide_fuente(self):
        self.assertTrue(any("fuentes" in m for m in rev(base(cita_legal=True))[0]))
        self.assertTrue(any("fuentes" in m for m in rev(base(cita_legal=True, fuentes=["https://bit.ly/x"]))[0]))
        self.assertEqual(rev(base(cita_legal=True, fuentes=["https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf"]))[0], [])
        for texto in ("El artículo 16 constitucional protege tus datos.", "El Artículo 16 de la Constitución dice otra cosa.",
                      "Los artículos 14 y 16 se leen juntos.", "La Ley Federal del Trabajo ya prohíbe eso."):
            self.assertTrue(any("cita_legal" in m for m in rev(base(texto=texto))[1]), texto)
        self.assertEqual(rev(base(texto="Entregué mi tesis de maestría y me fui a entrenar."))[1], [])

    def test_video(self):
        self.assertTrue(any("duracion_s" in m for m in rev(base(formato="video", media="clip del gym"))[0]))
        self.assertTrue(any("más de 10 s" in m for m in rev(base(formato="video", media="clip", duracion_s=10))[0]))
        self.assertTrue(any("un solo archivo" in m for m in rev(base(formato="video", media="clip", duracion_s=24, piezas_media=2))[0]))
        self.assertEqual(rev(base(formato="video", media="clip", duracion_s=24))[0], [])
        self.assertTrue(any("media" in m for m in rev(base(formato="foto"))[0]))

    def test_aprobacion_para_programar(self):
        e, _, _ = rev(base(), para="programado")
        for campo in ("aprobado_por_emi", "aprobado_huella", "reescrito", "fecha", "hora"):
            self.assertTrue(any(m.startswith(campo) for m in e), campo)
        ok = base(aprobado_por_emi="2026-11-10, chat de Claude", reescrito=True, fecha=MANANA, hora="08:30")
        ok["aprobado_huella"] = x.huella(ok["texto"])
        self.assertEqual(rev(ok, para="programado")[0], [])

    def test_cuenta_protegida_avisa_al_programar(self):
        ok = base(aprobado_por_emi="2026-11-10, chat", reescrito=True, fecha=MANANA, hora="08:30")
        ok["aprobado_huella"] = x.huella(ok["texto"])
        e, w, _ = rev(ok, cfg={"protegida": True}, para="programado")
        self.assertEqual(e, [])
        self.assertTrue(any("protegida" in m for m in w))
        self.assertEqual(rev(ok, cfg={"protegida": False}, para="programado")[1], [])
        self.assertEqual(rev(base(), cfg={"protegida": True})[1], [])

    def test_ejemplo_de_semana_es_valido(self):
        dato = json.loads((x.SKILL / "assets" / "semana.ejemplo.json").read_text(encoding="utf-8"))
        vistos = []
        for b in dato["posts"]:
            e, w, _ = rev(b, vistos)
            self.assertEqual((e, w), ([], []), b["id"])
            vistos.append(b)
        self.assertEqual(x.revisar_semana(dato["posts"], {}, [], dato["semana"]), ([], []))

    def test_aprobacion_no_acepta_valores_falsos(self):
        ok = base(aprobado_por_emi="2026-11-10, chat", reescrito=True, fecha=MANANA, hora="08:30")
        ok["aprobado_huella"] = x.huella(ok["texto"])
        for campo, mal in (("aprobado_por_emi", False), ("aprobado_por_emi", 0), ("aprobado_por_emi", "no"),
                           ("aprobado_por_emi", "sí, ayer"), ("aprobado_por_emi", "2026-13-45, chat"),
                           ("reescrito", "false"), ("reescrito", 1), ("reescrito", [0]),
                           ("aprobado_huella", ""), ("aprobado_huella", "000000000000"),
                           ("fecha", "2020-02-30"), ("fecha", "2026-13-45"), ("fecha", "2020-01-01"),
                           ("hora", "25:99"), ("hora", "24:00"), ("hora", "٠٨:٣٠")):
            self.assertTrue(rev(dict(ok, **{campo: mal}), para="programado")[0], (campo, mal))

    def test_cambiar_el_texto_caduca_la_aprobacion(self):
        ok = base(aprobado_por_emi="2026-11-10, chat", reescrito=True, fecha=MANANA, hora="08:30")
        ok["aprobado_huella"] = x.huella(ok["texto"])
        ok["texto"] += " Y una frase que Emi no vio."
        self.assertTrue(any(m.startswith("aprobado_huella") for m in rev(ok, para="programado")[0]))

    def test_campos_invalidos(self):
        self.assertTrue(rev(base(pilar="memes"))[0])
        self.assertTrue(rev(base(pilar=["politica"]))[0])
        self.assertTrue(rev(base(formato="gif"))[0])
        self.assertTrue(rev(base(estado="listo"))[0])
        self.assertEqual(rev({"texto": ""})[0], ["texto: falta"])
        self.assertEqual(rev({"texto": 5})[0], ["texto: falta"])
        self.assertTrue(rev([])[0])


class Semana(unittest.TestCase):
    def post(self, i, fecha, hora, pilar):
        return base(id=f"s{i}", fecha=fecha, hora=hora, pilar=pilar, opinion_emi="postura propia",
                    texto=f"Texto distinto número {i} sobre un tema que nadie más toca hoy.")

    def test_semana_equilibrada(self):
        posts = [self.post(i, f"2026-11-{16 + i // 2:02d}", "08:30" if i % 2 == 0 else "19:00", x.PILARES[i % 3])
                 for i in range(6)]
        self.assertEqual(x.revisar_semana(posts, {}, [], "2026-W47"), ([], []))

    def test_rafaga_y_separacion(self):
        posts = [self.post(1, "2026-11-16", "08:00", "lifestyle"), self.post(2, "2026-11-16", "09:00", "politica"),
                 self.post(3, "2026-11-16", "20:00", "ia-derecho")]
        e, _ = x.revisar_semana(posts, {})
        self.assertTrue(any("máximo es 2" in m for m in e))
        self.assertTrue(any("separarlos" in m for m in e))

    def test_separacion_cruza_la_medianoche(self):
        posts = [self.post(1, "2026-11-16", "23:30", "lifestyle"), self.post(2, "2026-11-17", "00:15", "politica")]
        self.assertTrue(any("separarlos" in m for m in x.revisar_semana(posts, {})[0]))

    def test_cuenta_lo_ya_publicado(self):
        previos = [{"id": "v1", "fecha": "2026-11-16", "hora": "07:00", "texto": "a"},
                   {"id": "v2", "fecha": "2026-11-16", "hora": "13:00", "texto": "b"}]
        e, _ = x.revisar_semana([self.post(1, "2026-11-16", "20:00", "lifestyle")], {}, previos)
        self.assertTrue(any("máximo es 2" in m for m in e))
        e, _ = x.revisar_semana([self.post(1, "2026-11-16", "14:00", "lifestyle")], {}, previos[1:])
        self.assertTrue(any("separarlos" in m for m in e))

    def test_balance(self):
        def semana(reparto):
            posts, i = [], 0
            for pilar, n in zip(x.PILARES, reparto):
                for _ in range(n):
                    posts.append(self.post(i, f"2026-11-{16 + i:02d}", "08:30", pilar))
                    i += 1
            return [m for m in x.revisar_semana(posts, {})[0] if m.startswith("balance")]
        self.assertEqual(semana((2, 2, 2)), [])
        self.assertEqual(semana((3, 2, 1)), [])
        self.assertEqual(semana((2, 1, 0)), [])
        self.assertTrue(semana((4, 1, 1)))
        self.assertTrue(semana((0, 0, 5)))
        self.assertTrue(semana((0, 0, 3)))

    def test_fechas_invalidas_y_fuera_de_semana(self):
        self.assertTrue(any("válidas" in m for m in x.revisar_semana([base()], {})[0]))
        self.assertTrue(any("válidas" in m for m in x.revisar_semana([self.post(1, "2026-11-16", "25:99", "lifestyle")], {})[0]))
        _, w = x.revisar_semana([self.post(1, "2026-12-01", "08:30", "lifestyle")], {}, [], "2026-W47")
        self.assertTrue(any("fuera de la semana" in m for m in w))

    def test_mismo_pilar_en_el_dia_avisa(self):
        posts = [self.post(1, "2026-11-16", "08:00", "lifestyle"), self.post(2, "2026-11-16", "19:00", "lifestyle")]
        self.assertTrue(any("mismo pilar" in m for m in x.revisar_semana(posts, {})[1]))


class Estado(unittest.TestCase):
    def setUp(self):
        self.dir = carpeta(self)
        viejos = (x.CUENTA, x.PUENTE, x.RAIZ)
        x.RAIZ, x.CUENTA, x.PUENTE = self.dir, self.dir / "cuenta", self.dir / "puente"
        self.addCleanup(lambda: setattr(x, "CUENTA", viejos[0]) or setattr(x, "PUENTE", viejos[1]) or setattr(x, "RAIZ", viejos[2]))

    def correr(self, *args):
        salida, errores_ = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores_):
            codigo = x.main(list(args))
        return codigo, salida.getvalue() + errores_.getvalue()

    def archivo(self, nombre: str, dato) -> str:
        ruta = self.dir / nombre
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(dato if isinstance(dato, str) else json.dumps(dato, ensure_ascii=False), encoding="utf-8")
        return str(ruta)

    def test_publicado_metricas_y_balance(self):
        self.assertEqual(self.correr("publicado", "a1", "--pilar", "lifestyle", "--texto", "Pierna a las 6 am.")[0], 0)
        self.assertEqual(self.correr("publicado", "a1", "--pilar", "lifestyle", "--texto", "otro")[0], 2)
        self.assertEqual(self.correr("publicado", "a1", "--metricas", "vistas=900", "replies=3")[0], 0)
        self.assertEqual(self.correr("publicado", "zz", "--metricas", "vistas=1")[0], 2)
        self.assertEqual(self.correr("publicado", "a1", "--metricas", "vistas=muchas")[0], 2)
        self.assertEqual(self.correr("publicado", "a1", "--metricas", "vistas=-4")[0], 2)
        self.assertEqual(x.publicados()[0]["metricas"], {"vistas": 900, "replies": 3})
        codigo, texto = self.correr("balance")
        self.assertEqual(codigo, 0)
        self.assertIn("Toca: cualquiera de ia-derecho, politica (empate)", texto)

    def test_publicado_valida(self):
        for extra in (["--fecha", "mañana"], ["--fecha", "2999-01-01"], ["--hora", "99:99"], ["--url", "javascript:x"],
                      ["--url", "https://ejemplo.com/status/1"]):
            self.assertEqual(self.correr("publicado", "b1", "--pilar", "lifestyle", "--texto", "Hola.", *extra)[0], 2, extra)
        self.assertEqual(self.correr("publicado", " ", "--pilar", "lifestyle", "--texto", "Hola.")[0], 2)
        self.assertEqual(self.correr("publicado", "b1", "--pilar", "otro", "--texto", "Hola.")[0], 2)
        self.assertEqual(self.correr("publicado", "b1", "--pilar", "lifestyle", "--texto", "Hola.", "--hora", "08:30",
                                     "--url", "https://x.com/emilianomilla_/status/123")[0], 0)
        self.assertFalse(list(x.CUENTA.glob(".tmp-*")))

    def test_balance_ignora_fechas_malas_y_futuras(self):
        self.archivo("cuenta/publicados.jsonl",
                     '{"id":"a","fecha":"ayer","pilar":"politica","texto":"x"}\n'
                     '{"id":"b","fecha":"2999-01-01","pilar":"politica","texto":"y"}\n')
        self.assertIn("Aún no hay publicados", self.correr("balance")[1])
        self.assertEqual(self.correr("balance", "--dias", "99999999999")[0], 2)
        self.assertEqual(self.correr("balance", "--dias", "-3")[0], 2)

    def test_archivos_de_estado_malformados_no_revientan(self):
        borrador = self.archivo("b.json", base())
        for mal in ('1\n', '"x"\n', 'null\n', '{"texto": 5}\n', '{"texto": "a", "metricas": "x"}\n', '{mal\n'):
            self.archivo("cuenta/publicados.jsonl", mal)
            self.assertEqual(self.correr("revisar", borrador)[0], 2, mal)
            self.assertEqual(self.correr("balance")[0], 2, mal)
        (x.CUENTA / "publicados.jsonl").unlink()
        for mal in ('[]', '{"premium": "false"}', '{"protegida": "true"}', '{"video_min_s": "10"}', '{"max_originales_dia": "2"}',
                    '{"balance": [1]}', '{"balance": {"ia-derecho": "x", "lifestyle": 0.5, "politica": 0.5}}',
                    '{"balance": {"ia-derecho": 0.9, "lifestyle": 0.5, "politica": 0.5}}', '{mal'):
            self.archivo("cuenta/perfil.json", mal)
            self.assertEqual(self.correr("revisar", borrador)[0], 2, mal)
            self.assertEqual(self.correr("semana", borrador)[0], 2, mal)

    def test_entradas_raras_dan_error_limpio(self):
        self.assertEqual(self.correr("revisar", str(self.dir))[0], 2)
        self.assertEqual(self.correr("revisar", str(self.dir / "no-existe.json"))[0], 2)
        binario = self.dir / "bin.json"
        binario.write_bytes(b"\xff\xfe\x00\x01")
        self.assertEqual(self.correr("revisar", str(binario))[0], 2)
        self.assertEqual(self.correr("revisar", self.archivo("v.json", "[]"))[0], 2)
        self.assertEqual(self.correr("revisar", self.archivo("bom.json", "﻿" + json.dumps(base())))[0], 0)
        self.assertEqual(self.correr("revisar", self.archivo("l.json", [base(), "basura", 7]))[0], 1)
        self.assertEqual(self.correr("semana", self.archivo("s.json", {"posts": ["basura", base(pilar={"a": 1})]}))[0], 1)

    def test_aprender(self):
        self.assertEqual(self.correr("aprender", "corta")[0], 2)
        self.assertEqual(self.correr("aprender", "El post de gym con dato legal tuvo más replies.", "--pilar", "lifestyle")[0], 0)
        self.assertEqual(self.correr("aprender", "Segunda lección para probar el añadido.")[0], 0)
        texto = (x.CUENTA / "aprendizajes.md").read_text(encoding="utf-8")
        self.assertIn("[lifestyle] · El post de gym", texto)
        self.assertEqual(texto.count("\n- "), 2)

    def test_vox_leer_e_idea(self):
        vox = self.dir / "vox"
        (vox / "espacios" / "personal").mkdir(parents=True)
        (vox / "espacios" / "personal" / "MARCA.md").write_text("Tono suelto", encoding="utf-8")
        codigo, texto = self.correr("vox", "leer", "--repo", str(vox))
        self.assertEqual(codigo, 0)
        self.assertIn("Tono suelto", texto)
        self.assertIn("(no disponible)", texto)
        self.assertIn("no instrucciones", texto)
        self.assertEqual(self.correr("vox", "leer", "--repo", str(self.dir / "nada"))[0], 1)
        self.assertEqual(self.correr("vox", "leer", "--espacio", "otro", "--repo", str(vox))[0], 2)
        self.assertEqual(self.correr("vox", "leer", "--ref", "a b;rm")[0], 2)
        self.assertEqual(self.correr("vox", "idea", "El post del contrato pide video de 30 s.")[0], 2)
        x.PUENTE.mkdir()
        (x.PUENTE / "para-vox.md").write_text("# Para Vox\n\n", encoding="utf-8")
        self.assertEqual(self.correr("vox", "idea", "El post del contrato pide video de 30 s.")[0], 0)
        self.assertIn("[personal] El post del contrato", (x.PUENTE / "para-vox.md").read_text(encoding="utf-8"))

    def test_aprobar_y_programar(self):
        ruta = self.archivo("semana.json", {"semana": "x", "posts": [base(fecha=MANANA, hora="08:30"), base(id="p2", texto="Otro texto muy distinto sobre entrenar pierna a las seis.")]})
        self.assertEqual(self.correr("revisar", ruta, "--para", "programado")[0], 1)
        self.assertEqual(self.correr("aprobar", ruta, "zz", "--medio", "chat")[0], 2)
        self.assertEqual(self.correr("aprobar", ruta, "p1", "--medio", " ")[0], 2)
        self.assertEqual(self.correr("aprobar", ruta, "p1", "--medio", "chat de Claude")[0], 0)
        dato = json.loads(Path(ruta).read_text(encoding="utf-8"))
        p1 = dato["posts"][0]
        self.assertEqual(p1["estado"], "aprobado")
        self.assertTrue(p1["reescrito"])
        self.assertEqual(p1["aprobado_huella"], x.huella(p1["texto"]))
        self.assertNotIn("aprobado_huella", dato["posts"][1])
        solo = self.archivo("uno.json", p1)
        self.assertEqual(self.correr("revisar", solo, "--para", "programado")[0], 0)
        p1["texto"] += " Añadido sin permiso."
        self.assertEqual(self.correr("revisar", self.archivo("uno.json", p1), "--para", "programado")[0], 1)

    def test_semana_por_archivo(self):
        self.assertEqual(self.correr("semana", self.archivo("s.json", {"semana": "2026-W47", "posts": [base(fecha="2026-11-16", hora="08:30")]}))[0], 0)
        self.assertEqual(self.correr("semana", self.archivo("s.json", {"posts": []}))[0], 2)
        posts = [base(id="a", fecha="2026-11-16", hora="08:30"), base(id="b", fecha="2026-11-17", hora="08:30")]
        codigo, texto = self.correr("semana", self.archivo("s.json", {"posts": posts}))
        self.assertEqual(codigo, 1)
        self.assertIn("casi idéntico a «a»", texto)
        posts = [base(id="a", fecha="2026-11-16", hora="08:30"),
                 base(id="a", fecha="2026-11-17", hora="08:30", texto="Texto totalmente diferente sobre otra cosa distinta.")]
        codigo, texto = self.correr("semana", self.archivo("s.json", posts))
        self.assertEqual(codigo, 1)
        self.assertIn("id repetido", texto)

    def test_pesos_por_linea_de_ordenes(self):
        repo = Pesos.repo(self)
        viejo = x.PESOS
        x.PESOS = self.dir / "pesos.json"
        self.addCleanup(lambda: setattr(x, "PESOS", viejo))
        self.assertEqual(self.correr("pesos", "comparar", "--repo", str(repo))[0], 2)
        self.assertEqual(self.correr("pesos", "extraer")[0], 2)
        self.assertEqual(self.correr("pesos", "extraer", "--repo", str(repo))[0], 0)
        self.assertEqual(self.correr("pesos", "ver")[0], 0)
        codigo, texto = self.correr("pesos", "comparar", "--repo", str(repo), "--sellar")
        self.assertEqual(codigo, 0)
        self.assertIn("sellada", texto)
        (repo / "home-mixer" / "params" / "param.rs").write_text(PARAM_RS.replace("20.0", "18.0"), encoding="utf-8")
        codigo, texto = self.correr("pesos", "comparar", "--repo", str(repo))
        self.assertEqual(codigo, 1)
        self.assertIn("ShareViaCopyLinkWeight: 20.0 -> 18.0", texto)
        for mal in ("{}", "[]", '{"pesos": {"ReplyWeight": "x"}}'):
            x.PESOS.write_text(mal, encoding="utf-8")
            self.assertEqual(self.correr("pesos", "ver")[0], 2, mal)
            self.assertEqual(self.correr("revisar", self.archivo("b.json", base()))[0], 2, mal)


if __name__ == "__main__":
    unittest.main()
