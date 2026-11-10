# Redactar y revisar un post

## Antes de escribir

1. Leer `cuenta/voz.md`, `cuenta/aprendizajes.md` y el puente con Vox Studio (`xviral.py vox leer`).
2. `xviral.py balance`: qué pilar toca.
3. Preguntar a Emi por el material real: qué entrenó, qué caso de uso de IA tuvo, qué noticia le importa y qué piensa. **La IA no inventa vivencias, cifras ni opiniones de Emi.** En política, su postura va en `opinion_emi`.
4. Si el post cita derecho: buscar la fuente oficial vigente, leerla y guardar el enlace en `fuentes`.

## La pregunta que decide

El código suma, para cada lector, el peso de cada acción por la probabilidad de que ese lector la haga. Las acciones que más pesan son las de mandar el post a otra persona y conversar. Antes de dar por bueno un borrador:

- ¿Alguien copiaría el enlace o lo mandaría por mensaje a una persona concreta? ¿A quién y por qué?
- ¿Alguien respondería algo que no sea «de acuerdo»?
- ¿Alguien que no conoce a Emi lo seguiría por esto?
- ¿A alguien le daría motivos para silenciarlo, marcar «no me interesa», bloquear o reportar?

Si la única respuesta honesta es «le darían like», el post es débil: se cambia el ángulo, no los adjetivos.

## Formas que suelen ganarse esas acciones

- **Útil y guardable**: un criterio, un paso a paso corto, un antes y después real. Se manda a quien lo necesita.
- **Postura con argumento**: una tesis clara y la razón. Invita a responder.
- **Experiencia propia con dato**: lo que Emi hizo, qué pasó, qué aprendió.
- **Pregunta genuina** al final, cuando Emi quiere leer las respuestas. No es obligatoria.

Lo que el texto debe cumplir:

- El valor completo va en el post raíz. Un hilo compite contra sí mismo: en cada feed sobrevive un solo post por conversación.
- Post original siempre. Para comentar algo ajeno con alcance, cita (quote); el repost y la respuesta sirven para conversar, no para crecer.
- Enlaces directos a la fuente. Abrir un enlace suma; lo que cuenta es la reputación del dominio de destino. Un acortador no se castiga en el código, pero le oculta al lector adónde lleva.
- Video: una sola pieza y más de 10 segundos. Foto: propia.
- Los hashtags no suman ni restan en el código; se usan solo si aportan al lector.
- 280 caracteres mientras la cuenta no tenga Premium (cada enlace cuenta 23 y cada emoji 2; el validador lo aproxima, X tiene la última palabra).

## Pedir la acción sin anzuelo

El anzuelo de interacción («RT y te mando…», «comenta X y te paso…», «like si…», «etiqueta a…») está entre las categorías de spam sin exención por tamaño de cuenta. No se usa nunca.

Sí vale decir para quién es el post y dejar que el lector decida: «Si conoces a alguien que está por firmar un contrato de renta, esto le sirve». Sí vale invitar al mensaje directo cuando hay algo real que conversar. No se promete un regalo a cambio de una acción.

## Que no suene a IA

El código tiene un modelo con nombre propio para el texto de IA publicado en serie (`llm_slop_user`): etiqueta la cuenta 7 días y saca todos sus posts de las recomendaciones a no seguidores (ver [algoritmo.md](algoritmo.md)). La regla de la skill: **la IA propone, Emi reescribe**. Ningún borrador pasa a aprobado sin `reescrito: true`.

Señales de las que avisa el validador: frases de relleno («en el mundo actual», «es importante destacar», «en resumen»), la fórmula «no es X, es Y», la raya larga, las listas con viñetas de emoji y más de dos hashtags. No detecta, y conviene quitar igual: tres adjetivos seguidos y los cierres con moraleja. Mejor: una frase que solo Emi diría, un detalle concreto, un número con su fuente.

No reciclar: el código etiqueta los grupos de texto duplicado, y un post casi igual a otro tampoco le da nada nuevo a quien ya sigue a Emi. Para repetir una idea que funcionó, se escribe de nuevo con otro ángulo.

## El borrador

```json
{
  "id": "2026-11-17-a",
  "pilar": "ia-derecho",
  "formato": "texto",
  "texto": "…",
  "fecha": "2026-11-17",
  "hora": "08:30",
  "senales": {"copiar_link": 2, "dm": 1, "reply": 2, "quote": 0, "follow": 1, "share": 1, "repost": 0, "like": 2},
  "por_que": {"copiar_link": "le sirve a quien…", "reply": "abre la discusión sobre…"},
  "riesgos": {"report": 0, "mute": 0, "no_me_interesa": 1, "bloqueo": 0},
  "opinion_emi": "",
  "cita_legal": false,
  "fuentes": [],
  "media": "",
  "estado": "borrador",
  "reescrito": false,
  "aprobado_por_emi": ""
}
```

- `pilar`: `ia-derecho`, `lifestyle` o `politica`. `formato`: `texto`, `foto`, `video`, `articulo` o `quote`.
- `senales` y `riesgos`: de 0 (nulo) a 3 (alto), estimados con honestidad por quien redacta. Toda señal cara (copiar enlace, mensaje, respuesta, cita, seguir) en 2 o más lleva su frase en `por_que`.
- Video: además `duracion_s` y `piezas_media: 1`.
- `estado`: `borrador` → `aprobado` → `programado` → `publicado`.
- `aprobado_por_emi`, `aprobado_huella` y `reescrito` no se escriben a mano: los anota `xviral.py aprobar` cuando Emi ya dio el visto bueno a ese texto. La huella ata la aprobación al texto exacto.
- `excepcion_limite`: motivo, solo cuando el texto menciona un asunto público con fuente o un cliente claramente hipotético.

Una semana es un archivo así (también vale una lista de borradores):

```json
{"semana": "2026-W47", "posts": [ { "id": "2026-11-17-a", "…": "…" }, { "id": "2026-11-17-b", "…": "…" } ]}
```

```bash
python3 skills/x-viral/scripts/xviral.py revisar cuenta/privado/borrador.json
python3 skills/x-viral/scripts/xviral.py semana cuenta/privado/2026-W47.json
python3 skills/x-viral/scripts/xviral.py aprobar cuenta/privado/2026-W47.json 2026-11-17-a --medio "chat de Claude"
python3 skills/x-viral/scripts/xviral.py revisar cuenta/privado/2026-W47.json --para programado
```

## Qué significa el índice de señales

`revisar` da un número de 0 a 100: la suma de peso por nivel sobre el máximo posible, con los pesos vigentes de `data/pesos.json`. Sirve para **comparar borradores entre sí** y para que el orden cambie solo cuando X cambie los pesos. No predice alcance: la probabilidad real la calcula el modelo de X para cada lector, y un nivel puesto con optimismo infla el número. Un índice alto con riesgos altos no se publica.

## Semana

Una o dos publicaciones originales por día (contando lo ya publicado), separadas al menos cuatro horas aunque crucen la medianoche, y con un tercio por pilar: desde tres posts, ningún pilar puede alejarse más de un post (o del 15 %) de lo que le toca. `semana` da error si algo de eso falla, revisa cada borrador y avisa, sin bloquear, cuando los posts de un día son del mismo pilar o una fecha cae fuera de la semana. La hora se elige según cuándo está activa la audiencia de Emi; no hay una hora mágica en el código.
