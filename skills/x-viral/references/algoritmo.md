# Lo que dice el código de X

Fuente: <https://github.com/xai-org/x-algorithm>, commit `30647a8` (14/11/2026; `param.rs` sincronizado desde producción el 13/11/2026). Verificado el 10/11/2026 sobre el commit `660cd74` por tres agentes de IA que leyeron el código por separado, más comprobaciones directas del agente principal y una revisión independiente posterior; la revisión semanal del 16/11/2026 releyó lo que cambió en `30647a8` (pesos, interruptores y archivos citados) y actualizó lo afectado. Las rutas son del repositorio de X; cuando se abrevian, `scoring.rs`, `weights.rs` e `inputs.rs` son los de `xai-value-model/`, `filters/…` son los de `home-mixer/filters/` y `eventProcessing.strato` es `phoenix-rankall-strato/lib/eventProcessing.strato`.

Cuando `xviral.py pesos comparar` avise de cambios, este archivo se actualiza antes de seguir publicando.

## Cómo leer los números

1. **Los pesos multiplican probabilidades predichas, no conteos.** Para cada lector y cada post, el modelo (Phoenix) predice la probabilidad de cada acción; el puntaje es la suma de peso × probabilidad. X lo aclaró en el código el 14/08/2026 (`home-mixer/params/param.rs:418-446`, `README.md`): decir «un reporte cancela 468 likes» o «copiar el enlace vale 40 likes» es incorrecto. La probabilidad base de un reporte es más de mil veces menor que la de un like; por eso su peso es tan grande.
2. **Solo cuenta lo que pasa en Inicio.** Una acción entra al sistema si ocurre sobre un post servido en la línea de tiempo de Inicio. Llegar directo al post, por ejemplo coordinándose en un grupo de chat, «no tiene efecto en el ranking» (`home-mixer/params/param.rs:442-446`).
3. **Las recomendaciones son personales.** Los reportes o bloqueos de un grupo afectan sobre todo a lectores parecidos a ese grupo, no a todos.
4. **Son valores por defecto.** `home-mixer/params/param.rs` y `vm-ranker/params.rs` leen los mismos interruptores en producción y sus valores por defecto difieren en nueve pesos. El ranking vivo lo hace `vm-ranker`; home-mixer solo sirve su cálculo si esa llamada falla. Donde difieren, el valor real no está publicado. Una pista: la primera línea de `home-mixer/params/param.rs` dice que es copia de los valores por defecto de la configuración (última sincronización: 13/11/2026), mientras que `vm-ranker` carga la configuración viva al arrancar (`vm-ranker/config_sync.rs`).
5. **Lo que no está en el repositorio no está probado.** X no publica las instrucciones del clasificador Grox ni algunas reglas, y oculta umbrales con valores ficticios, declarados como tales (`12.34`, `9.99`).

## Pesos de las acciones

`data/pesos.json` tiene la lista completa y vigente. Los principales:

| Acción que el modelo predice | home-mixer | vm-ranker |
|---|---|---|
| Responder a un post original de alguien con quien el lector se sigue mutuamente | 5.0 + 15.0 | igual |
| Responder | 5.0 | 5.0 |
| Mandarlo por mensaje directo | 5.0 | 5.0 |
| Citar | 5.0 | 5.0 |
| Seguir al autor desde el post | 4.0 | 4.0 |
| Copiar el enlace del post | **0.0** (era 20.0) | 20.0 |
| Compartir (menú) | 2.118 | 2.0 |
| Repostear | 1.0 | 1.0 |
| Like | 0.708 | 0.5 |
| Tiempo de lectura tras abrir el post | 0.385 | 0.4 |
| Abrir el post | 0.274 | 0.3 |
| Abrir un enlace | 0.2 | 0.2 |
| Ampliar foto, detenerse, clic en lo citado | 0.05 | 0.05 |
| Clic al perfil | 0.0 | 0.0 |
| Pasar de largo sin detenerse | −0.02 | −0.02 |
| Bloquear al autor | −31.2 | −31.2 |
| «No me interesa» | −53.07 | −47.52 |
| Silenciar al autor | −58.8 | −58.8 |
| Reportar | −234.0 | −234.0 |

**Copiar el enlace (cambio del 14/11/2026).** Hasta el commit `660cd74` era la acción con más peso (20 en los dos archivos). En `30647a8` home-mixer lo bajó a 0.0 (`home-mixer/params/param.rs:495-500`) y vm-ranker conserva 20.0 como valor por defecto (`vm-ranker/params.rs:34-39`); los dos leen el mismo interruptor, `rust_home_mixer_share_via_copy_link_weight`. Como `param.rs` dice reflejar la configuración de producción, lo más probable es que hoy valga 0, pero no está probado. El modelo de reordenamiento por página (`home-mixer/scorers/page_decode_rerank_scorer.rs:54`, `phoenix/xrex/models/page_rl.py:72`) ya lo tenía en 0. Regla práctica: no contar con que copien el enlace; las señales caras que siguen firmes son responder, mandar por mensaje y citar (5) y seguir (4).

La fórmula tiene 30 términos (`xai-value-model/scoring.rs:79-218`). No hay término para video, foto, enlace, largo del texto, idioma ni hashtags: esas características entran solo como datos al modelo que predice.

Sobre el refuerzo de seguimiento mutuo: sube de 5 a 20 el peso de que **el lector responda**, cuando el post es original (ni respuesta ni repost) y autor y lector se siguen mutuamente (`xai-value-model/inputs.rs:20-22`, `weights.rs:86-93`). Historia: prueba A/B el 10/07/2026, lanzado en 20 el 13/07 y bajado a 15 el 24/07 (`docs/BIDIRECTIONAL_BOOST_CHANGE.md`).

## Ajustes después de la suma

Orden en `vm-ranker` (`xai-value-model/scoring.rs:360-406`): suma y desplazamiento → empujón de arranque → diversidad de autor × descuento fuera de red → selección por diversidad.

| Ajuste | Valor hoy | Dónde |
|---|---|---|
| Puntajes negativos | Todo post con suma negativa queda comprimido por debajo de cualquier post positivo (`NEGATIVE_SCORES_OFFSET = 0.001`). | `weights.rs:4`, `scoring.rs:239-248` |
| Empujón de arranque | A un post por petición se le sube el puntaje al del lugar 16; después se le aplican los ajustes de abajo, así que un post de fuera de red termina más abajo. Requisitos: post original, autor con hasta **50,000** seguidores, menos de **2 horas** de publicado, menos de **200** vistas en Inicio y ya dentro del 97 % superior de los candidatos con puntaje. Entre los que cumplen se elige por sorteo ponderado por likes por vista (un post con cero likes puede salir). No aplica en feeds de tema y depende de grupos de experimento. | `home-mixer/scorers/author_cold_start.rs`, `param.rs:663-736` |
| Diversidad de autor | El segundo post del mismo autor en un feed vale ×0.625, el tercero ×0.4375, con piso ×0.25 (0.75 × 0.5^k + 0.25). | `vm-ranker/params.rs:175-192`, `scoring.rs:261-263` |
| Fuera de red | ×0.75 para posts de cuentas que el lector no sigue, **y también** para respuestas y reposts de cuentas que sí sigue. ×0.5 en feeds de tema. | `vm-ranker/params.rs:193-222`, `scoring.rs:284-293` |
| Selección por diversidad (DPP) | De los 150 mejores elige hasta 50 que no se parezcan entre sí (θ = 0.65). Los elegidos conservan su puntaje; los demás quedan en 0. Desde el 14/11 existe un modo de ventana que además compara con lo que el lector vio justo antes (`DppWindow`), **apagado por defecto** (ventana 0); home-mixer ya manda ese historial (hasta 50 posts). | `vm-ranker/params.rs:241-272`, `vm-ranker/dpp.rs`, `home-mixer/params/param.rs:633-644`, `home-mixer/scorers/vm_ranker_request.rs:31-32` |

El reporte de Santi decía que el empujón era para cuentas de hasta 1,000 seguidores con menos de 1,000 vistas: esos umbrales cambiaron.

## De dónde salen los candidatos

Cada vez que alguien abre Para ti (`home-mixer/candidate_pipeline/phoenix_candidate_pipeline.rs`):

- El modelo lee las últimas 1,024 acciones del lector, consultadas en cada petición (`param.rs:1082-1093`).
- Fuentes activas por defecto: hasta 1,200 posts de cuentas que sigue (Thunder), 1,000 de la recuperación de Phoenix, 800 de SimClusters y 500 de una lista de populares.
- 21 filtros antes de puntuar: duplicados, más de 48 horas, propios, ya vistos, autores bloqueados o silenciados, palabras silenciadas, y **reposts y respuestas de cuentas que el lector no sigue** (`filters/oon_retweet_reply_filter.rs`).
- Se toman los 50 mejores, pasan por el filtro de visibilidad y quedan 35. Con módulos, la respuesta tiene hasta 48 elementos.
- Por conversación sobrevive un solo post, el de mayor puntaje (`filters/dedup_conversation_filter.rs`). Entre un post y su repost queda el que llegó primero (`filters/retweet_deduplication_filter.rs`).

## Cómo llega un post a quien no sigue al autor

Índices de recuperación (`phoenix-rankall-strato/…/phoenixRankAllCandidateProcessor.strato:538-601`, `phoenix-rankall/src/config/mod.rs`):

- Quedan fuera: posts de comunidades, reposts, y posts marcados por el filtro de visibilidad o como contenido adulto.
- **Las citas pasan** como post original.
- Las respuestas no entran al índice principal, pero tienen índices propios (`1fav_reply`, `32fav_reply`) cuando reciben likes. El reporte de Santi decía que nunca se indexan; hoy no es así, aunque el filtro de arriba las sigue quitando de Para ti para no seguidores.
- El índice que alimenta Inicio (`1fav_1day`) se escribe cuando llega un like. El primero dispara la indexación (con unos 2 minutos de retraso del flujo) y hay reintentos al llegar a 2, 4, 8… likes. Las copias del índice se publican cada 180 segundos.
- Existe un índice `tail` para autores con menos de 1,000 seguidores que admite posts con 0 likes, pero pertenece a una fuente (`EnableSidSource`) **apagada por defecto**. No contar con él.
- La recuperación compara el historial del lector con el post (modelo de dos torres). Para Inicio se entrena con likes y, desde octubre de 2026, también con posts en los que la gente se detiene a leer (`phoenix/xrex/configs/xrecsys_two_tower.py:279-296`).
- Desde el 14/11/2026 hay un índice más, `ai_video_model`, para posts con video inmersivo que un modelo marca como generado por IA (`phoenixRankAllCandidateProcessor.strato:413-422`, `583-586`). El código no dice cómo se usa ese índice en Inicio.
- SimClusters: un post hereda los intereses de quienes le dan like (vida media de 8 horas) y se sirve a lectores afines.

**Consecuencia práctica:** quién interactúa primero orienta a quién se le enseña después. Y solo vale si esa persona vio el post en su Inicio.

## El reloj

| Momento | Qué pasa |
|---|---|
| 0 a 2 h | Ventana del empujón de arranque (menos de 200 vistas en Inicio). |
| Primer like | Entra al índice de descubrimiento. |
| 24 h | Sale de los índices de un día (`1fav_1day`, `post_creation`). Se mide desde la publicación. |
| 48 h | Fuera de Para ti (`MAX_POST_AGE`), de Thunder y de SimClusters. |
| 72 h | SimClusters ignora likes sobre posts de 3 días o más. |

No existe una variable de velocidad ni de «hora dorada». Sí existen estas ventanas.

Video: para entrar a los índices de video, **todas** las piezas del post deben ser video de más de 10 segundos; un clip corto o una imagen añadida lo descalifica (`eventProcessing.strato:403-418`). Esos índices tienen ventanas más largas que las de un post normal (la mayoría de 48 a 720 horas). Los pesos propios de video están en 0 o casi.

Idioma: no hay filtro que exija coincidencia de idioma, pero el idioma del post y del lector sí son datos del modelo. Decir que «el idioma no cuenta» es ir más lejos que el código.

Editar: solo se descartan las versiones viejas; no hay castigo por editar.

## Visibilidad y etiquetas

No hay un interruptor secreto: hay reglas con nombre en `visibility-filtering/rules/levels.rs` (el archivo `registry.rs` que cita el reporte de Santi ya no existe).

- Posts de cuentas que el lector sigue: nivel `TimelineHome`, **40 reglas**.
- Posts recomendados a quien no sigue al autor: esas 40 **más 26** (66 en total). Once de las 26 son etiquetas de cuenta: sacan todos los posts del autor de las recomendaciones a quienes no lo siguen, mientras sus seguidores no notan nada. Eso es lo que se suele llamar *shadowban*.

| Etiqueta | Qué la dispara | Efecto | Duración |
|---|---|---|---|
| `SpamHighRecall` (cuenta) | Señal `llm_slop_user`, cuenta que publica sobre todo spam, fijar un post con enlace malo. | Todos los posts fuera de las recomendaciones a no seguidores. | **7 días** por `llm_slop_user` (el reporte de Santi decía 30). |
| `SpamHighRecall` (post) | Texto sin sentido, respuestas en ráfaga, categorías de spam de Grox, enlace de mala reputación. | Ese post fuera de recomendaciones a no seguidores y de notificaciones. | 30 días en las dos primeras; las demás sin caducidad declarada. |
| `RiskyHighVizReply` | Señal `llm_slop_post`; respuesta en hilo ajeno con puntaje de spam ≥ 0.97. | Se usa en notificaciones de menciones y respuestas a no seguidores, no en Para ti. | 30 y 14 días. |
| `COPYPASTA_SPAM` | Grupos de texto duplicado. | Ninguna regla publicada la lee. | Sin caducidad. |
| `SPAM` | Enlace con veredicto «BAD», aplicado también a posts antiguos. | Invisible para todos menos el autor. | — |
| `MALICIOUS_URL`, `DO_NOT_AMPLIFY` | Reputación del dominio enlazado. | Fuera de recomendaciones a no seguidores. | — |
| Contenido sensible (cuenta) | 3 de los últimos 5 posts con la etiqueta, en 60 días. | Todo fuera de recomendaciones. | 7 días. |
| `FOSNR_CIVIC_INTEGRITY`, `FOSNR_VIOLENT_SPEECH`, conducta de odio, abuso | Según la herramienta oficial, «en respuesta a un reporte de usuario». | Invisible para todos menos el autor, que ve un aviso apelable. | — |
| Retención legal por país | Orden legal o ley local. | El post no se muestra en ese país. | — |

Precisiones que importan:

- **Qué es `llm_slop`**: el código solo muestra el nombre de la señal (literalmente «bazofia de modelo de lenguaje») y su consecuencia. Qué la dispara exactamente no está publicado. Que apunte a texto de IA publicado sin editar es una inferencia a partir del nombre, razonable pero no demostrada.
- **Anzuelo de interacción**: Grox etiqueta `SpamHighRecall` **sin exención** para cuentas grandes cuatro categorías: `SpamEngagementBaiting`, `SpamEngagementFarming`, `SpamCardManipulation` y, desde el 14/11/2026, `SpamPromotesShares`, es decir, **pedir que compartan el post** (`grox/flows/ptos/task_write_safety_post_annotations_result_sink.py:233-242`). Otras dos categorías nuevas, `SpamPromotesClicks` y `SpamPromotesReplies` (pedir clics o respuestas), no ponen `SpamHighRecall` pero sí dejan su propia etiqueta, `PromotesClicks` o `PromotesReplies` (líneas 243-279); ninguna regla publicada lee esas etiquetas todavía.
- **Escudo de cuenta grande**: en las reglas de botmaker y Grox, puntaje de reputación `user-cred-v2` ≥ 54 (o ≥ 66 para spam de respuestas); los 25,000 seguidores solo cuentan si no hay puntaje. En el servicio que aplica `llm_slop_user` los umbrales de exención son ficticios (`12.34`), es decir, desconocidos. Una cuenta nueva no tiene escudo en ningún caso.
- **Automatización** (`bdsm/`): un modelo mira secuencias de acciones; cuenta ráfagas con menos de un segundo entre acciones e interacciones sobre posts que nunca se mostraron en pantalla. Los umbrales están ocultos.
- **Acortadores**: no hay castigo específico. El veredicto se calcula sobre el destino final de la cadena de redirecciones (`scarecrow/legacy/UrlVerdictRegistry.scala:67-79`). Lo que cuenta es el dominio de destino.
- **Agatha** (reportes y bloqueos frente a likes de no seguidores): sus etiquetas duran una semana y, en lo publicado, afectan a búsqueda y notificaciones, no a Para ti. Cada persona que reporta cuenta contra un máximo de 100 cuentas.
- **Fallas del sistema**: no siempre se resuelven a favor del autor. Si falla la consulta de etiquetas, el post se trata como sin etiqueta; si el post falta en la respuesta del filtro, se descarta.
- **Política**: no hay reglas para México ni una categoría general de «contenido político». El filtro electoral de Brasil se retiró de home-mixer el 26/10/2026; queda una regla que solo aplica a lectores en Brasil. Grox enumera integridad cívica pero no la clasifica, y su etiqueta automática de insultos solo se aplica a posts en inglés. El riesgo real para opinión política está en los pesos negativos (silenciar, «no me interesa», bloquear, reportar) y en los reportes que acaban en una etiqueta `FOSNR`.

## Under the Hood

Herramienta oficial, en piloto: <https://x.com/i/jf/under_the_hood>. Muestra las etiquetas que limitan la visibilidad de la cuenta y de sus posts y, desde septiembre de 2026, las retenciones legales por país.

Requisitos (`under-the-hood/strato/columns/underTheHoodReport.User.strato:18-22`): cuenta de al menos **365 días** y 10 o más posts en el mes anterior. El reporte de un mes sale unos 10 días después de que termina. Depende de un interruptor que X va abriendo.

**Una cuenta nueva no puede usarla durante su primer año.** Mientras tanto, la señal a vigilar es: los seguidores interactúan como siempre pero dejan de llegar lectores nuevos.

## Lo que el código no respalda

| Se dice | En el código |
|---|---|
| «Los enlaces matan el alcance» | Abrir un enlace pesa +0.2. Cuenta la reputación del dominio. |
| «Los hashtags penalizan» | No aparecen en el cálculo. Tampoco premian. |
| «Hay una hora dorada» | No hay variable de velocidad. Hay ventanas de 2, 24 y 48 horas. |
| «Premium te sube en el feed» | No hay peso ni multiplicador por suscripción en el ranking. |
| «Importa la proporción seguidores/seguidos» | No aparece. |
| «Los hilos tienen ventaja» | Al revés: un post por conversación en cada feed. |
| «Hay que optimizar para clics al perfil» | Ese peso es 0. Seguir desde el post pesa 4. |
| «Copiar el enlace es lo que más pesa» | Lo era hasta el 14/11/2026. Hoy home-mixer lo tiene en 0 y vm-ranker en 20; el valor real no está publicado. |
| «Una acción vale N likes» | Lectura incorrecta de los pesos, según el propio código. |

«No está en el código publicado» no prueba que no exista en otra parte de X.

## Límites de este análisis

- Lo verificó una IA leyendo código, sin ejecutarlo ni medir cuentas reales. Describe reglas, no resultados.
- Los valores son los publicados el 14/11/2026 y X experimenta de forma continua.
- No se publican las instrucciones de Grox (qué cuenta exactamente como texto de IA o como anzuelo), algunos umbrales ni algunas reglas.
- El modelo que predice las probabilidades es aprendido: ningún documento puede decir cuánto alcance tendrá un post.
