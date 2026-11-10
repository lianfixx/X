#!/usr/bin/env python3
"""Pruebas de xviral.py. Correr: python3 -m unittest discover -s skills/x-viral/scripts -p 'test_*.py'"""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import xviral as x

PESOS = json.loads(x.PESOS.read_text(encoding="utf-8"))["pesos"]

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
param!(EnableAlgo, bool, "o", true);
param!(Nombre, String, "p", "x".to_string());
'''


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


class Pesos(unittest.TestCase):
    def repo(self, texto=PARAM_RS, readme="### October 26th, 2026\n\n### August 13th, 2026\n"):
        d = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (d / "home-mixer" / "params").mkdir(parents=True)
        (d / "home-mixer" / "params" / "param.rs").write_text(texto, encoding="utf-8")
        (d / "vm-ranker").mkdir()
        (d / "vm-ranker" / "params.rs").write_text(
            'param!(FavoriteWeight, f64, "a", 0.5);\nparam!(OonWeightFactor, f64, "q", 0.75);\n', encoding="utf-8")
        (d / "README.md").write_text(readme, encoding="utf-8")
        return d

    def test_extrae_pesos_y_separa_otros(self):
        d = x.extraer(self.repo())
        self.assertEqual(d["pesos"]["ShareViaCopyLinkWeight"], 20.0)
        self.assertEqual(d["pesos"]["ReplyWeight"], 5.0)
        self.assertEqual(d["pesos"]["BidirectionalFollowReplyWeightBoost"], 15.0)
        self.assertEqual(d["otros_parametros"], {"ColdStartSlotMax": 16})
        self.assertEqual(d["pesos_vm_ranker"], {"FavoriteWeight": 0.5})
        self.assertEqual(d["otros_vm_ranker"], {"OonWeightFactor": 0.75})
        self.assertEqual(d["actualizaciones_readme"], ["October 26th, 2026", "August 13th, 2026"])

    def test_formato_desconocido_falla(self):
        with self.assertRaises(x.Falla):
            x.extraer(self.repo(PARAM_RS + "param!(Raro f64 sin comas);\n"))

    def test_peso_necesario_ausente_falla(self):
        with self.assertRaises(x.Falla):
            x.extraer(self.repo(PARAM_RS.replace("ReportWeight", "ReportPeso")))

    def test_sin_param_rs_falla(self):
        with tempfile.TemporaryDirectory() as d, self.assertRaises(x.Falla):
            x.extraer(Path(d))

    def test_diferencias(self):
        a = x.extraer(self.repo())
        b = x.extraer(self.repo(PARAM_RS.replace("0.708", "0.9").replace("ColdStartSlotMax", "ColdStartSlotMin"),
                                "### November 1st, 2026\n### October 26th, 2026\n### August 13th, 2026\n"))
        d = "\n".join(x.diferencias(a, b))
        self.assertIn("CAMBIÓ  pesos.FavoriteWeight: 0.708 -> 0.9", d)
        self.assertIn("NUEVO   otros_parametros.ColdStartSlotMin", d)
        self.assertIn("QUITADO otros_parametros.ColdStartSlotMax", d)
        self.assertIn("November 1st, 2026", d)
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
        alto = x.indice({"copiar_link": 3}, PESOS)
        bajo = x.indice({"like": 3}, PESOS)
        self.assertGreater(alto, bajo)
        self.assertEqual(x.indice({s: 3 for s in x.SENALES}, PESOS), 100)
        self.assertEqual(x.indice({}, PESOS), 0)

    def test_solo_like_es_debil(self):
        e, _, _ = rev(base(senales={"like": 3}, por_que={}))
        self.assertTrue(any("señal cara" in m for m in e))

    def test_senal_cara_pide_por_que(self):
        e, _, _ = rev(base(por_que={}))
        self.assertTrue(any("por_que.copiar_link" in m for m in e))

    def test_niveles_fuera_de_rango(self):
        e, _, _ = rev(base(senales={"copiar_link": 5}))
        self.assertTrue(any("0 (nulo) a 3" in m for m in e))
        e, _, _ = rev(base(senales={"copiar_link": True}))
        self.assertTrue(any("0 (nulo) a 3" in m for m in e))
        e, _, _ = rev(base(senales={"copiar_link": 2, "aplausos": 1}))
        self.assertTrue(any("desconocidas" in m for m in e))

    def test_anzuelos(self):
        for texto in ("Dale RT y te mando el prompt completo.", "Comenta IA y te paso el PDF.",
                      "Like si estás de acuerdo.", "Etiqueta a ese amigo que no entrena pierna.",
                      "Sígueme para más consejos legales."):
            e, _, _ = rev(base(texto=texto))
            self.assertTrue(any("anzuelo" in m for m in e), texto)

    def test_cta_legitimo_no_es_anzuelo(self):
        e, _, _ = rev(base(texto="Si conoces a alguien que renta, mándale esto. ¿Tú qué cláusula revisarías primero?"))
        self.assertEqual(e, [])

    def test_limites_de_emi(self):
        for texto in ("Hoy en Castorena vimos un caso curioso.", "Mi cliente llegó con el expediente 123/2026.",
                      "Ese diputado es un imbécil."):
            e, _, _ = rev(base(texto=texto))
            self.assertTrue(any("límite de Emi" in m or "ataque personal" in m for m in e), texto)

    def test_plantilla_de_ia_avisa(self):
        _, w, _ = rev(base(texto="En el mundo actual, la IA no es solo una herramienta — es un aliado — para todos."))
        self.assertTrue(any("plantilla de IA" in m for m in w))
        self.assertTrue(any("rayas largas" in m for m in w))

    def test_largo(self):
        e, _, _ = rev(base(texto="a" * 281))
        self.assertTrue(any("281 caracteres" in m for m in e))
        self.assertEqual(rev(base(texto="a" * 281), cfg={"premium": True})[0], [])
        self.assertEqual(x.largo_x("a" * 250 + " https://ejemplo.mx/una/ruta/larguisima/que/no/cuenta/entera"), 274)
        self.assertEqual(x.largo_x("niño"), 4)
        self.assertEqual(x.largo_x("💪"), 2)

    def test_acortador(self):
        e, w, _ = rev(base(texto="La nota completa: https://bit.ly/abc"))
        self.assertEqual(e, [])
        self.assertTrue(any("acortador" in m for m in w))
        self.assertEqual(rev(base(texto="La nota completa: https://www.dof.gob.mx/nota"))[0], [])

    def test_duplicado(self):
        hist = [{"id": "viejo", "fecha": "2026-11-01", "texto": base()["texto"].replace("Encontró", "Halló")}]
        e, _, _ = rev(base(), hist)
        self.assertTrue(any("casi idéntico" in m for m in e))
        self.assertEqual(rev(base(), [{"id": "p1", "texto": base()["texto"]}])[0], [])

    def test_riesgo_alto_bloquea(self):
        e, _, _ = rev(base(riesgos={"mute": 2}))
        self.assertTrue(any("riesgos.mute = 2" in m for m in e))
        _, w, _ = rev(base(riesgos={"report": 1}))
        self.assertTrue(any("riesgos.report = 1" in m for m in w))

    def test_politica_pide_opinion(self):
        e, _, _ = rev(base(pilar="politica"))
        self.assertTrue(any("opinion_emi" in m for m in e))
        self.assertEqual(rev(base(pilar="politica", opinion_emi="La reforma concentra poder y lo voy a criticar."))[0], [])

    def test_cita_legal_pide_fuente(self):
        e, _, _ = rev(base(cita_legal=True))
        self.assertTrue(any("fuentes" in m for m in e))
        self.assertEqual(rev(base(cita_legal=True, fuentes=["https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf"]))[0], [])
        _, w, _ = rev(base(texto="El artículo 16 constitucional protege tus datos."))
        self.assertTrue(any("cita_legal" in m for m in w))

    def test_video(self):
        e, _, _ = rev(base(formato="video", media="clip del gym"))
        self.assertTrue(any("duracion_s" in m for m in e))
        e, _, _ = rev(base(formato="video", media="clip", duracion_s=10))
        self.assertTrue(any("más de 10 s" in m for m in e))
        e, _, _ = rev(base(formato="video", media="clip", duracion_s=24, piezas_media=2))
        self.assertTrue(any("una sola pieza" in m for m in e))
        self.assertEqual(rev(base(formato="video", media="clip", duracion_s=24))[0], [])
        e, _, _ = rev(base(formato="foto"))
        self.assertTrue(any("media" in m for m in e))

    def test_aprobacion_para_programar(self):
        e, _, _ = rev(base(), para="programado")
        self.assertTrue(any("aprobado_por_emi" in m for m in e))
        self.assertTrue(any("reescrito" in m for m in e))
        self.assertTrue(any("fecha" in m for m in e))
        ok = base(aprobado_por_emi="2026-11-10, chat", reescrito=True, fecha="2026-11-11", hora="08:30")
        self.assertEqual(rev(ok, para="programado")[0], [])

    def test_campos_invalidos(self):
        self.assertTrue(rev(base(pilar="memes"))[0])
        self.assertTrue(rev(base(formato="gif"))[0])
        self.assertEqual(rev({"texto": ""})[0], ["texto: falta"])
        self.assertTrue(rev([])[0])


class Semana(unittest.TestCase):
    def post(self, i, fecha, hora, pilar):
        return base(id=f"s{i}", fecha=fecha, hora=hora, pilar=pilar, opinion_emi="postura propia",
                    texto=f"Texto distinto número {i} sobre un tema que nadie más toca hoy.")

    def test_semana_equilibrada(self):
        posts = [self.post(i, f"2026-11-{16 + i // 2:02d}", "08:30" if i % 2 == 0 else "19:00", x.PILARES[i % 3])
                 for i in range(6)]
        e, w = x.revisar_semana(posts, {})
        self.assertEqual(e, [])
        self.assertEqual(w, [])

    def test_rafaga_y_separacion(self):
        posts = [self.post(1, "2026-11-16", "08:00", "lifestyle"), self.post(2, "2026-11-16", "09:00", "politica"),
                 self.post(3, "2026-11-16", "20:00", "ia-derecho")]
        e, _ = x.revisar_semana(posts, {})
        self.assertTrue(any("máximo es 2" in m for m in e))
        self.assertTrue(any("separarlos" in m for m in e))

    def test_desbalance(self):
        posts = [self.post(i, f"2026-11-{16 + i:02d}", "08:30", "politica") for i in range(5)]
        posts.append(self.post(9, "2026-11-22", "08:30", "lifestyle"))
        e, _ = x.revisar_semana(posts, {})
        self.assertTrue(any("balance: politica" in m for m in e))
        self.assertTrue(any("balance: ia-derecho" in m for m in e))

    def test_sin_fecha(self):
        e, _ = x.revisar_semana([base()], {})
        self.assertTrue(any("fecha AAAA-MM-DD" in m for m in e))

    def test_mismo_pilar_en_el_dia_avisa(self):
        posts = [self.post(1, "2026-11-16", "08:00", "lifestyle"), self.post(2, "2026-11-16", "19:00", "lifestyle")]
        _, w = x.revisar_semana(posts, {})
        self.assertTrue(any("mismo pilar" in m for m in w))


class Estado(unittest.TestCase):
    def setUp(self):
        self.dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.viejos = (x.CUENTA, x.PUENTE, x.RAIZ)
        x.RAIZ, x.CUENTA, x.PUENTE = self.dir, self.dir / "cuenta", self.dir / "puente"
        self.addCleanup(self.restaurar)

    def restaurar(self):
        x.CUENTA, x.PUENTE, x.RAIZ = self.viejos

    def correr(self, *args):
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = x.main(list(args))
        return codigo, salida.getvalue() + errores.getvalue()

    def test_publicado_metricas_y_balance(self):
        self.assertEqual(self.correr("publicado", "a1", "--pilar", "lifestyle", "--texto", "Pierna a las 6 am.")[0], 0)
        self.assertEqual(self.correr("publicado", "a1", "--pilar", "lifestyle", "--texto", "otro")[0], 2)
        self.assertEqual(self.correr("publicado", "a1", "--metricas", "vistas=900", "replies=3")[0], 0)
        self.assertEqual(self.correr("publicado", "zz", "--metricas", "vistas=1")[0], 2)
        self.assertEqual(self.correr("publicado", "a1", "--metricas", "vistas=muchas")[0], 2)
        fila = x.publicados()[0]
        self.assertEqual(fila["metricas"], {"vistas": 900, "replies": 3})
        codigo, texto = self.correr("balance")
        self.assertEqual(codigo, 0)
        self.assertIn("Toca: ", texto)
        self.assertNotIn("Toca: lifestyle", texto)

    def test_balance_vacio(self):
        codigo, texto = self.correr("balance")
        self.assertEqual(codigo, 0)
        self.assertIn("Aún no hay publicados", texto)

    def test_aprender(self):
        self.assertEqual(self.correr("aprender", "corta")[0], 2)
        self.assertEqual(self.correr("aprender", "El post de gym con dato legal tuvo más replies.", "--pilar", "lifestyle")[0], 0)
        self.assertIn("[lifestyle] · El post de gym", (x.CUENTA / "aprendizajes.md").read_text(encoding="utf-8"))

    def test_vox_leer_e_idea(self):
        vox = self.dir / "vox"
        (vox / "espacios" / "personal").mkdir(parents=True)
        (vox / "espacios" / "personal" / "MARCA.md").write_text("Tono suelto", encoding="utf-8")
        codigo, texto = self.correr("vox", "leer", "--repo", str(vox))
        self.assertEqual(codigo, 0)
        self.assertIn("Tono suelto", texto)
        self.assertIn("(no disponible)", texto)
        self.assertEqual(self.correr("vox", "leer", "--repo", str(self.dir / "nada"))[0], 1)
        self.assertEqual(self.correr("vox", "leer", "--espacio", "otro", "--repo", str(vox))[0], 2)
        self.assertEqual(self.correr("vox", "idea", "El post del contrato pide video de 30 s.")[0], 2)
        x.PUENTE.mkdir()
        (x.PUENTE / "para-vox.md").write_text("# Para Vox\n\n", encoding="utf-8")
        self.assertEqual(self.correr("vox", "idea", "El post del contrato pide video de 30 s.")[0], 0)
        self.assertIn("[personal] El post del contrato", (x.PUENTE / "para-vox.md").read_text(encoding="utf-8"))

    def test_revisar_y_semana_por_archivo(self):
        ruta = self.dir / "b.json"
        ruta.write_text(json.dumps(base()), encoding="utf-8")
        self.assertEqual(self.correr("revisar", str(ruta))[0], 0)
        self.assertEqual(self.correr("revisar", str(ruta), "--para", "programado")[0], 1)
        ruta.write_text("{mal", encoding="utf-8")
        self.assertEqual(self.correr("revisar", str(ruta))[0], 2)
        ruta.write_text(json.dumps({"semana": "2026-W47", "posts": [base(fecha="2026-11-16", hora="08:30")]}), encoding="utf-8")
        self.assertEqual(self.correr("semana", str(ruta))[0], 0)
        ruta.write_text(json.dumps({"posts": []}), encoding="utf-8")
        self.assertEqual(self.correr("semana", str(ruta))[0], 2)

    def test_semana_detecta_duplicado_interno(self):
        ruta = self.dir / "s.json"
        posts = [base(id="a", fecha="2026-11-16", hora="08:30"), base(id="b", fecha="2026-11-17", hora="08:30")]
        ruta.write_text(json.dumps({"posts": posts}), encoding="utf-8")
        codigo, texto = self.correr("semana", str(ruta))
        self.assertEqual(codigo, 1)
        self.assertIn("casi idéntico a «a»", texto)


if __name__ == "__main__":
    unittest.main()
