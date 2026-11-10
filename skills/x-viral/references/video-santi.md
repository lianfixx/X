# El video de Santi: qué hizo, qué dijo y qué se sostiene

Fuente: «Esto es lo que Claude encontró en el algoritmo de X (no es lo que piensas)», Santiago Muñoz (@SantiMunozIA), publicado el 15/08/2026, 19:14 min, <https://youtu.be/lWoj_liZqOI>. Analizado el 10/11/2026 a partir de los subtítulos automáticos y la descripción del video, del reporte que publicó (<https://claude.ai/code/artifact/ee0f8fff-89d9-4248-85bf-e2f98da9ccc7>) y del código de <https://github.com/xai-org/x-algorithm> en su commit `660cd74` (10/11/2026).

Los subtítulos son automáticos: escriben «Cloud» por Claude y cortan frases. Las citas de abajo están limpiadas de muletillas, no inventadas.

## Qué hizo, paso a paso

| Minuto | Paso |
|---|---|
| 0:00 | Presenta la noticia: X publicó el código que ordena y filtra el feed Para ti. |
| 1:04 | Enseña la publicación oficial y el repositorio. |
| 1:41 | Abre la app de escritorio de Claude Code, pega el enlace del repositorio y dicta el encargo. |
| 3:29 | Cambia el modelo a Fable, pega el texto completo de la publicación oficial, activa el modo automático y el esfuerzo máximo. Aclara que tiene el plan 20x y que casi no ha publicado en X («creo que he publicado como dos veces»). |
| 4:52 | Mientras corre, recorre las carpetas del repositorio. Claude le hace preguntas, clona el código y lanza 8 agentes de Sonnet; después vienen una síntesis y una auditoría. |
| 6:04 | 34 minutos y más de 4 millones de tokens después, termina. |
| 6:36 | Lee el reporte por primera vez frente a la cámara (documento y versión web). |
| 17:01 | Lee el plan de acción. |
| 18:42 | Anuncia una clase en su comunidad de pago para crear «los skills y automatizaciones» que apliquen el plan. Esa clase no es pública; esta skill es nuestra propia versión. |

El pie del reporte publicado dice 14 subagentes, 2,014 archivos, 842 lecturas de código y 28 afirmaciones auditadas (25 confirmadas, 3 corregidas). En el video dice 8 agentes: es el número que vio al arrancar.

## El encargo que dictó

Es un solo encargo hablado, sin plantilla. Reconstruido de los subtítulos (1:55 a 3:25):

> X (Twitter) acaba de hacer público su algoritmo, lo hicieron open source. Quiero que investigues el algoritmo para ver cómo hacerme viral en X. Analiza cómo determina quién se hace viral y quién no, y dame un análisis a detalle no solo de cómo hacerme viral, sino de qué otras cosas tengo que considerar: qué importa más, qué tipo de formatos tengo que hacer, qué toma en cuenta la plataforma para silenciarme, qué no tengo que hacer. La meta es que me generes un reporte donde me des el paso a paso para hacerme viral en X. Para esto quiero que uses ultracode para hacer todo este análisis y lances muchos agentes con diferentes tareas. Si tienes alguna pregunta antes de empezar, por favor dime. Quiero que hagas el plan usando Fable y los subagentes con modelos como Opus o Sonnet.

Lo que acompañó al encargo: el enlace del repositorio, el texto completo de la publicación oficial de X, modelo Fable, modo automático y esfuerzo máximo.

Por qué funcionó:

1. **Dio la fuente primaria** (el código y el anuncio oficial), no artículos sobre el código.
2. **Pidió un resultado concreto** (reporte con paso a paso) y enumeró las preguntas que debía contestar.
3. **Invitó a que le preguntaran antes de empezar.** Las respuestas (cuenta chica, contenido educativo de IA en español, su comunidad) son las que volvieron personal el plan.
4. **Repartió el trabajo**: un modelo fuerte planea y sintetiza, varios más baratos leen carpetas en paralelo, y al final una auditoría que intenta tumbar cada afirmación.

La versión reutilizable de este encargo, ya corregida, está en [prompts.md](prompts.md).

## Lo que afirmó y cómo quedó al cotejarlo con el código de hoy

Detalle con archivo y línea en [algoritmo.md](algoritmo.md). Resumen:

| Dijo en el video | Veredicto al 10/11/2026 |
|---|---|
| «Un copiar link vale 40 likes»; «todo lo que ganas te lo puede restar» un reporte | **Lectura incorrecta.** X lo aclaró en el propio código el 14/08/2026: los pesos multiplican la probabilidad que el modelo predice para cada lector, no los conteos. Lo que sí se sostiene: el contenido que la gente manda a otra gente es la familia que más pesa. |
| Copiar enlace es la acción con más peso (20) | Confirmado. |
| «Reply de un mutual» vale 20 | Confirmado el número (5 + 15), descrito al revés: sube el peso de que **el lector responda** a un post original de alguien con quien se sigue mutuamente. |
| Like 0.5; «no me interesa» −43.2; share 2.0 | Cambiaron o difieren entre los dos archivos de parámetros (like 0.708 / 0.5; «no me interesa» −53.07 / −47.52; share 2.118 / 2.0). |
| Con menos de 1,000 seguidores X te da un empujón, y «después de los 1,000 muere» | **Cambió.** El empujón de arranque hoy admite autores de hasta 50,000 seguidores, pero solo para posts de menos de 2 horas y menos de 200 vistas en Inicio. El índice para cuentas de menos de 1,000 seguidores existe, pero su fuente está apagada por defecto. |
| Publicar en ráfaga te canibaliza (segundo post ×0.625) | Confirmado. Santi leyó «vale 0.75 menos»; el factor correcto es ×0.625, ×0.4375 y piso ×0.25. |
| El post vive 48 horas; lo importante pasa en las primeras 24 | Confirmado: 48 horas como máximo en Para ti y 24 en los índices de un día. Falta en el video la ventana de 2 horas del empujón de arranque. |
| «El shadow ban existe», 54 reglas | La idea se sostiene, los números no: hoy son 40 reglas para todos y 26 más solo al recomendar a no seguidores (66). El archivo que cita el reporte ya no existe. |
| El contenido crudo de IA se castiga | Confirmado con matiz: el modelo `llm_slop_user` etiqueta la cuenta **7 días**, no 30. |
| Las respuestas «nunca se indexan» | Cambió: tienen índices propios cuando reciben likes; siguen fuera de Para ti para no seguidores. |
| El anzuelo es la única categoría de spam sin exención | Son tres categorías sin exención, no una. |
| «No castiga que lo hagas en español» | No hay filtro de idioma, pero el idioma del post y del lector sí son datos del modelo. |
| Nunca acortadores de terceros | Sin sustento: el código juzga el destino final del enlace. |
| Entrar a Under the Hood para el diagnóstico | Exige una cuenta de al menos un año y 10 posts al mes; una cuenta nueva no puede. |
| Los enlaces no matan el alcance; no hay «hora dorada» | Confirmado: abrir enlace pesa +0.2 y no existe variable de velocidad. |
| «Esto también va a aplicar a Instagram, a Facebook» | Sin sustento: el código es de X. |
| Paso 05 del plan: conseguir el primer like compartiendo el post «donde vive tu gente» | **Contradicho por el código.** Una acción solo cuenta si ocurre sobre un post servido en Inicio; llegar directo al post, por ejemplo desde un grupo de chat, no tiene efecto en el ranking. |

## Qué se queda y qué se cambia para Emi

Se queda el método: fuente primaria, preguntas antes de empezar, trabajo repartido y auditoría adversarial. También el núcleo del plan: post original, una o dos publicaciones al día separadas por horas, señales caras, conversación con mutuals, nada de anzuelos ni texto crudo de IA, y medir cada mes.

Se cambia:

- **Los números se leen del código vivo**, no del video: `scripts/xviral.py pesos comparar` avisa cuando cambian.
- **Nada de equivalencias** entre acciones («vale 40 likes»).
- **El primer like no se fabrica** en grupos: se gana con seguidores reales que ven el post en su Inicio.
- **El plan es para otra cuenta**: Santi enseña IA en español; Emi mezcla estilo de vida y gym, IA + Derecho y opinión política, con límites profesionales que Santi no tiene. Ver [playbook.md](playbook.md) y [pilares.md](pilares.md).
