# Plan para @emilianomilla_

Adaptación del plan del video de Santi a una cuenta nueva, con tres pilares y con lo que el código dice hoy ([algoritmo.md](algoritmo.md)). Cada paso dice en qué se apoya. Lo marcado como **criterio** es recomendación de la skill, no una regla del código.

## Punto de partida (visto el 10/11/2026)

`@emilianomilla_` existe desde abril de 2026: 24 posts, 42 seguidos, 2 seguidores y **posts protegidos** (candado). Mientras siga protegida, nada de este plan funciona: solo ven los posts los seguidores aprobados, no se pueden citar ni repostear y el sistema no los recomienda a nadie más.

## Fase 0 · Preparar la cuenta (una vez)

0. **Quitar la protección**, cuando Emi lo decida: Configuración → Privacidad y seguridad → Audiencia, multimedia y etiquetas → desmarcar «Proteger tus posts». Antes, **revisar los 24 posts que ya existen**: al abrir la cuenta quedan públicos. Emi borra los que no quiera asociar a la cuenta o que choquen con sus límites ([pilares.md](pilares.md)). Después, poner `"protegida": false` en `cuenta/perfil.json`.
1. **Perfil completo**: foto propia, nombre, bio que diga los tres temas y de dónde habla Emi. El clic al perfil pesa 0; la bio sirve para que quien llega decida seguir, que pesa 4. **Criterio.**
2. **Habitar los temas**: seguir y leer cuentas **de otras personas** que Emi respete en IA y Derecho, en entrenamiento y en análisis político mexicano, y anotar de 5 a 10 por pilar en `cuenta/mutuals.md`. No son cuentas suyas ni cuentas desde las que se publique: son con quienes conversa. Sirven por dos razones del código: el historial de la propia cuenta y de quienes interactúan orienta a quién se recomienda, y cuando dos cuentas se siguen mutuamente pesa cuatro veces más que una responda a los posts de la otra. Con 2 seguidores, casi nadie ve hoy un post en su Inicio; estas conversaciones son la forma legítima de cambiarlo.
3. **Sin atajos**: nada de comprar seguidores, grupos de intercambio de likes, seguir y dejar de seguir, ni herramientas que interactúen solas. El código modela esas secuencias y una etiqueta de cuenta saca todos los posts de las recomendaciones a quienes no siguen a Emi.
4. **Decidir Premium**: sin Premium, 280 caracteres y sin artículos. El ranking no premia la suscripción. Si Emi la contrata, poner `"premium": true` en `cuenta/perfil.json`.
5. **Under the Hood no está disponible** hasta que la cuenta cumpla un año (abril de 2027, según `creada` en `cuenta/perfil.json`) y tenga 10 posts o más en el mes anterior.

## Fase 1 · Primeras semanas

6. **Uno o dos posts originales al día, separados al menos cuatro horas.** El segundo post del mismo autor en un feed vale ×0.625 y el tercero ×0.4375.
7. **Un tercio por pilar** y sin repetir pilar el mismo día. Ver [pilares.md](pilares.md).
8. **Cada post busca una señal cara**: que lo manden a alguien, que respondan, que lo citen o que sigan a Emi. Ver [redaccion.md](redaccion.md).
9. **Estar presente las dos primeras horas.** El empujón de arranque solo aplica a posts de menos de 2 horas y menos de 200 vistas en Inicio, y el sorteo favorece a los que tienen más likes por vista. Publicar cuando Emi puede quedarse a responder. **Criterio** sobre el horario: empezar por la mañana (7:30–9:00) y por la noche (19:30–21:30), hora del centro, y ajustar con las métricas.
10. **El primer like no se fabrica.** Mandar el enlace a un grupo para que entren a dar like no cuenta: la acción debe ocurrir sobre el post servido en Inicio. Lo que sí funciona es tener seguidores reales a los que el post les aparezca. Por eso la fase 0.
11. **Todo el valor en el post raíz.** Nada de hilos como formato base.

## Fase 2 · Conversación (permanente)

12. **Responder a quien responde**, sobre todo en las primeras horas y dentro de las primeras 24. Lo hace Emi; la IA puede proponerle respuestas.
13. **Seguir de vuelta a quien comenta con sustancia.** Con seguimiento mutuo, el peso de que esa persona responda a los posts originales de Emi pasa de 5 a 20.
14. **Comentar en cuentas grandes solo para conversar.** Las respuestas no se recomiendan a no seguidores en Para ti y cargan ×0.75. Pocas y con contenido: las respuestas en ráfaga se etiquetan.
15. **Para opinar con alcance sobre algo ajeno, citar.** La cita viaja como post original. Ojo: si el post citado recibe una restricción, la cita cae con él.
16. **No repostear lo propio** para «revivirlo»: el repost carga ×0.75 y puede desplazar al original.

## Fase 3 · Formatos

17. **Texto** con un remate que se entienda solo y se pueda capturar en pantalla.
18. **Foto propia** cuando muestra algo (el entreno, el documento, el lugar). No hay peso por llevar foto; ampliar la foto pesa 0.05.
19. **Video**: una sola pieza de más de 10 segundos. Da permanencia en los índices de video, no puntaje extra. Los shorts de Vox Studio entran aquí ([conexion-vox.md](conexion-vox.md)).
20. **Artículo** para el análisis jurídico largo, solo con Premium. Acompañarlo de un post que dé la tesis.
21. **Enlaces directos** a la fuente. Sin miedo al enlace; cuidado con el dominio.

## Fase 4 · Medir y aprender

22. **A las 48 horas** de cada post, anotar métricas (`xviral.py publicado ID --metricas …`): vistas, respuestas, citas, compartidos, seguidores ganados.
23. **Cada semana**: `xviral.py balance`, qué funcionó por pilar, una lección con `xviral.py aprender` y, si un tema pide video, `xviral.py vox idea`.
24. **Cada mes**: revisión con Emi (encargo 5 de [prompts.md](prompts.md)), nota en `cuenta/diagnosticos/AAAA-MM.md` y ajuste del balance si él lo decide.
25. **Lo que funcionó se reescribe**, no se repite: mismo tema, otro ángulo, pasadas las 48 horas.
26. **Señal de alarma**: los seguidores interactúan igual pero dejan de llegar lectores y seguidores nuevos durante una semana o más. Revisar los últimos posts contra la lista de abajo, parar lo dudoso y esperar: la etiqueta de cuenta por texto de IA dura 7 días.

## Lo que no se hace

| Qué | Por qué |
|---|---|
| Publicar el texto de una IA sin reescribir | Señal `llm_slop_user`: etiqueta de cuenta 7 días, todos los posts fuera de las recomendaciones a no seguidores. Qué la dispara no está publicado; el nombre apunta a texto de IA. |
| Anzuelos («RT y te mando», «comenta X») | Spam sin exención por tamaño. |
| Grupos de likes, bots, seguir y dejar de seguir, acciones automatizadas | Modelo de secuencias de automatización. |
| Provocar reportes, que lo silencien o «no me interesa» | Son los pesos más negativos y entrenan al sistema a no traer contenido parecido. |
| Repetir el mismo texto | Etiqueta de texto duplicado. |
| Respuestas en ráfaga en cuentas grandes | Etiquetas de spam de respuestas. |
| Enlazar dominios dudosos o fijar un post con uno | Etiquetas por reputación del dominio, también retroactivas. |
| Ráfagas de posts | Cada post extra en el mismo feed vale menos. |
| Contenido sensible «de broma» | Tres de cinco posts etiquetados sacan la cuenta de las recomendaciones 7 días. |
| Clientes, asuntos, Castorena, ataques personales, citas sin fuente | Límites de Emi ([pilares.md](pilares.md)). |
