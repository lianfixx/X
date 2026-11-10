# Auditoría del 10/11/2026

Qué se revisó, cómo y qué se corrigió antes de publicar la versión 1.0.0.

## 1. El reporte de Santi contra el código de hoy

Método: clon de `xai-org/x-algorithm` en el commit `660cd74` (10/11/2026). Tres agentes de solo lectura verificaron por separado 40 afirmaciones del reporte (puntaje, ciclo de vida, visibilidad), cada una con archivo y línea. Las de mayor consecuencia las comprobó después, directamente en el código, el agente principal.

| # | Afirmación del reporte | Resultado | Corrección aplicada en la skill |
|---|---|---|---|
| 1 | «Copiar link vale 40 likes», «un reporte pesa como perder 468 likes» | Incorrecta según el propio código (`home-mixer/params/param.rs:382-410`) | Regla 5 de la skill; sin equivalencias en ningún archivo. |
| 2 | Primer like compartiendo el post «donde vive tu gente» | Contradicha: solo cuentan acciones sobre posts servidos en Inicio | Paso 10 del plan. |
| 3 | Like 0.5, share 2.0, «no me interesa» −43.2 | Cambiaron o difieren entre home-mixer y vm-ranker | `data/pesos.json` guarda ambos archivos. |
| 4 | Empujón para cuentas de ≤1,000 seguidores con <1,000 vistas, top 85 % | Cambió: ≤50,000 seguidores, <200 vistas en Inicio, <2 horas, top 97 % | Plan, paso 9; algoritmo.md. |
| 5 | Índice `tail` como ventaja de la cuenta chica | Existe, pero su fuente está apagada por defecto | No se cuenta con él. |
| 6 | «Reply de un mutual vale 20» | Número correcto, sentido invertido: es la respuesta del lector | Redactado bien en todos los archivos. |
| 7 | Respuestas «nunca se indexan» | Cambió: índices `1fav_reply` y `32fav_reply` | algoritmo.md. |
| 8 | 54 reglas en `rules/registry.rs` (28 + 26) | Cambió: 40 + 26 = 66 en `rules/levels.rs`; el archivo citado no existe | algoritmo.md. |
| 9 | `llm_slop_user` etiqueta la cuenta 30 días | Cambió: 7 días | algoritmo.md, plan, redaccion.md. |
| 10 | El anzuelo es la única categoría sin exención | Son tres | algoritmo.md. |
| 11 | Escudo: reputación ≥ 54 **o** >25,000 seguidores | Los seguidores solo cuentan si no hay puntaje | algoritmo.md. |
| 12 | Si el sistema falla, siempre se resuelve a favor del autor | Mixto: a veces el post se descarta | algoritmo.md. |
| 13 | El idioma no cuenta | No hay filtro, pero sí es dato del modelo | algoritmo.md. |
| 14 | Nunca acortadores de terceros | Sin sustento: se juzga el destino | El validador avisa, no bloquea. |
| 15 | 17 filtros; 47 elementos por respuesta; filtro de visibilidad después de cortar a 35 | 21 filtros; 48; el filtro corre sobre los 50 | algoritmo.md. |
| 16 | La selección por diversidad «sobrescribe el puntaje» | Elige y conserva el puntaje; lo no elegido queda en 0 | algoritmo.md. |
| 17 | Recuperación entrenada solo con likes | Desde octubre también con lectura detenida | algoritmo.md. |
| 18 | Agatha baja el alcance | En lo publicado afecta a búsqueda y notificaciones | algoritmo.md. |
| 19 | Diagnóstico inmediato en Under the Hood, `x.com/i/under_the_hood` | Requiere cuenta de un año; la dirección oficial es `x.com/i/jf/under_the_hood` | Plan, paso 5. |

Confirmadas sin cambios: copiar enlace 20; responder, mensaje y cita 5; seguir 4; reportar −234, silenciar −58.8, bloquear −31.2; diversidad de autor ×0.625/×0.4375/piso ×0.25; descuento fuera de red ×0.75 también para respuestas y reposts propios; 48 horas de vida; un post por conversación; la cita viaja como original; video de más de 10 segundos en todas las piezas; sin castigo a enlaces ni a hashtags; sin variable de velocidad; sin ventaja de Premium en el ranking; clic al perfil 0; historial de 1,024 acciones; 3 de 5 posts sensibles apagan la cuenta 7 días; el modelo de automatización cuenta ráfagas de menos de un segundo e interacciones sin impresión.

## 2. El video

Transcripción obtenida de los subtítulos automáticos de YouTube desde box (YouTube bloquea la máquina de la sesión). Se leyó completa. El encargo dictado se reconstruyó sin añadir contenido. No se guardó la transcripción en el repositorio: es obra de su autor.

## 3. La skill

| Control | Resultado |
|---|---|
| `python3 -m unittest discover -s skills/x-viral/scripts -p 'test_*.py'` | Aprobado, 46 pruebas. |
| `python3 -m unittest discover -s ia -p 'test_*.py'` | Aprobado, 3 pruebas. |
| `python3 ia/check_skill.py skills/x-viral .claude/skills/x-viral .agents/skills/x-viral` | Aprobado. |
| `xviral.py pesos extraer` y `pesos comparar` contra el clon real | Aprobado, sin diferencias. |
| Revisión independiente de la skill por otro agente | Hecha; ver sección 4. |

## 4. Revisión independiente de la skill

Un agente sin contexto previo recibió el repositorio (no las conclusiones) con el encargo de encontrar defectos. Corrió el script con entradas límite en una copia, cotejó 37 afirmaciones contra el código de X y revisó enlaces, órdenes, privacidad y redacción.

- Hechos: 29 confirmados y 8 imprecisos (líneas citadas, alcance del escudo de cuenta grande, mecánica exacta del empujón de arranque, qué significa `llm_slop`, residuo del filtro de Brasil, ventanas de video). Todos corregidos.
- Código: 8 defectos altos y 14 medios. El más serio: la compuerta de aprobación aceptaba valores falsos. Todos corregidos y cubiertos con pruebas (de 35 a 46).
- Documentación: sin enlaces rotos; órdenes que no existían solo en el protocolo común (ahora explicado en `ia/REGLAS.md`).
- Privacidad: sin secretos ni datos de contacto. Queda a decisión de Emi que el repositorio sea público (ver `CHANGELOG.md`).

Detalle de cada corrección en la entrada 1.0.1 de `CHANGELOG.md`.

## 5. Lo que no se pudo probar

- **La cuenta real.** Está protegida, con 2 seguidores y 24 posts que no se pudieron leer (visto el 10/11/2026 desde box, sin sesión). No hay métricas ni correcciones de Emi. La voz en X queda como candidata.
- **Programar en X.** Procedimiento documentado, no ejecutado.
- **El efecto real de cada regla.** Se leyó código; no se midió ninguna cuenta.
- **La tarea semanal**: creada, primera ejecución el 16/11/2026.
- **Lo que X no publica**: instrucciones de Grox, algunos umbrales y reglas.
- **Lectura de Vox Studio desde `main`.** Vox Studio aún vive en su rama de trabajo `claude/magical-cori-8bdu3a`; el puente se probó con copia local y por red contra esa rama (`--ref`). Con la rama `main` responde «no disponible» hasta que allá se fusione.
