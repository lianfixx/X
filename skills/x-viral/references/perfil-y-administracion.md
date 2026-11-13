# Perfil completo y administración de la cuenta

Guía para dejar `@emilianomilla_` completa y administrarla bien. Escrita el 13/11/2026 con lo que Emi decidió: prestigio primero y después empleo; marca personal, no currículum; abogado con maestría en Alta Dirección; solo espacio personal; postura de riesgo alta en los ganchos, con sus límites intactos.

Las opciones de X cambian de nombre y de lugar. Si algo no aparece donde dice, buscar la función por su nombre en Configuración.

## 1. Perfil (una sola vez, desde el teléfono)

| Elemento | Qué poner | Por qué |
|---|---|---|
| Foto | La foto profesional que Emi ya tiene: rostro de frente, fondo limpio, buena luz. | Se ve en miniatura en cada respuesta: tiene que reconocerse a 40 píxeles. |
| Portada (1500×500) | Algo propio y sobrio que cuente el oficio sin texto largo: por ejemplo, su escritorio de trabajo con la pantalla de la Matriz (sin datos del despacho ni de asuntos), o una foto suya trabajando. Nada de plantillas con frases motivacionales. | Primera impresión de quien llega desde un post. |
| Nombre | Emiliano García Milla | Con acento; así lo buscan. |
| Biografía | La elegida en [cuenta/perfil-publico.md](../../../cuenta/perfil-publico.md), ajustada a «abogado con maestría en Alta Dirección» si Emi lo quiere ahí. | Seguir desde un post pesa 4 en el código; la bio cierra esa decisión. |
| Ubicación | México | |
| Sitio web | emilianomilla.site | Es el lugar del enlace que no conviene poner en cada post (por API un post con enlace cuesta 13 veces más). |
| Fecha de nacimiento | Oculta al público. | Dato personal sin valor para la marca. |
| Categoría profesional | Abogado (la que diga abogado); tipo Creador. | Se ve bajo la bio. No interviene en el ranking. |
| Post fijado | El post de lanzamiento cuando salga; después, el post que mejor explique a Emi. | Es lo primero que lee quien visita el perfil. |
| Destacados | Los 3 a 5 mejores posts de cada pilar, cuando existan (requiere Premium). | Portafolio vivo. |

## 2. Privacidad y seguridad

- **Quitar la protección de posts** (prerrequisito de todo; ver la fase 0 de [playbook.md](playbook.md)).
- **Verificación en dos pasos**: dejarla activa, con app de autenticación o llave, no SMS si se puede.
- **Apps conectadas** (Configuración → Seguridad y acceso a la cuenta → Apps y sesiones): solo debe quedar la app de la API de Emi. Revisarlo cada mes y quitar lo que no reconozca.
- **Sesiones abiertas**: cerrar las que no sean sus equipos.
- **Mensajes directos**: abiertos solo a quien sigue, o a todos con filtro de calidad. Para «prestigio primero» conviene permitir mensajes de cualquiera con el filtro activo: de ahí salen oportunidades de trabajo. Decisión de Emi.
- **Etiquetado en fotos**: solo de quienes sigue.
- **Palabras silenciadas**: insultos frecuentes y spam. Silenciar no afecta su alcance; solo lo que él ve.
- **Ubicación en posts**: desactivada.

## 3. Notificaciones

- Activar las de respuestas y menciones de **cuentas que sigue** y de **cuentas verificadas**: son las conversaciones de las primeras dos horas, que más pesan.
- Filtro de calidad activado.
- Apagar las de recomendaciones y tendencias: distraen.

## 4. Premium

Emi piensa contratarlo. Lo que sí da, según X y fuentes de terceros (verificar en la pantalla de suscripción, los precios en México cambian):

- Posts largos y artículos (útil para el análisis jurídico extenso).
- Editar un post ya publicado.
- Destacados en el perfil.
- Herramientas de creador y requisito para los programas de pago a creadores.

Lo que **no** da: ventaja en el ranking. En el código público no hay ningún peso ni multiplicador por suscripción. Recomendación: el plan intermedio (Premium); Premium+ no aporta nada a esta estrategia. Cuando esté activo, poner `"premium": true` en `cuenta/perfil.json`.

## 5. Herramientas de creador (Creator Studio y afines)

Lo que conviene usar, y cuándo:

| Herramienta | Para qué | Cuándo |
|---|---|---|
| **Analítica** de la cuenta y de cada post | Vistas, interacciones, seguidores ganados por post. Es la fuente de las métricas que la skill anota. | Desde el primer post. Si la API lee métricas, Emi ya no tiene que mandar capturas. |
| **Creator Studio** | Ver el estado de elegibilidad a los programas de creador. | Una vez al mes, en la revisión mensual. |
| **Original Content Rewards** (el programa de pago que reemplazó al reparto de ingresos el 07/09/2026) | Pago por impresiones de contenido original. Requiere Premium y requisitos altos que X no ha publicado completos. | No es meta hoy: con 2 seguidores está lejos. Se revisa cuando la cuenta crezca. El objetivo de Emi es prestigio, no ingresos. |
| **Media Studio** | Subir y administrar videos (incluidos los de Vox Studio), poner subtítulos y miniatura. | Cada vez que salga un video. Los videos deben ir solos en su post y durar más de 10 s. |
| **Artículos** (con Premium) | Análisis jurídico largo con postura. | Uno al mes como máximo, acompañado de un post que dé la tesis. |
| **Listas** (privadas) | Tres listas, una por pilar, con las cuentas de [cuenta/mutuals.md](../../../cuenta/mutuals.md). Emi las lee cada día para responder con sustancia. | Desde ya. |
| **Carpetas de guardados** | Guardar ideas y fuentes por pilar. | Desde ya. |
| **Comunidades** | Unirse a 1 o 2 de derecho o IA en español para leer; publicar ahí no entra al índice de descubrimiento. | Opcional. |
| **Spaces** (audio en vivo) | Conversación con abogados o estudiantes sobre IA y Derecho. | Más adelante, con al menos unos cientos de seguidores. |

## 6. Rutina de administración

| Cuándo | Qué | Quién |
|---|---|---|
| Cada post | Quedarse las dos primeras horas para responder. | Emi |
| Cada día, 15 min | Leer las tres listas y responder con sustancia a 3 o 5 posts ajenos. | Emi |
| Cada semana | Aprobar el paquete de la Matriz de Redes; seguir de vuelta a quien conversó con sustancia. | Emi |
| A las 48 h de cada post | Métricas (por API cuando esté conectada). | La skill |
| Cada mes | Revisión mensual ([prompts.md](prompts.md), encargo 5), apps conectadas, consumo de la API contra la consola, elegibilidad en Creator Studio. | La skill y Emi |
| Cada lunes | Revisión del algoritmo de X. | Tarea programada |

## 7. Gasto: sin miedo, sin derroche

| Concepto | Recomendación | Estimado |
|---|---|---|
| API de X | Tope de 10 USD al mes, sin recarga automática; enlaces en la bio. | Unos 1.50 USD al mes con dos posts diarios sin enlace. Ver [api.md](api.md). |
| Premium | Plan intermedio, cuando Emi decida. | Ver precio en México en la app. |
| Anuncios pagados | **No** por ahora. Con una cuenta sin historial, pagar alcance compra vistas de gente que no conversa. Se reconsidera a los tres meses con datos. | 0 |
| Herramientas de terceros para programar | No: la API y el panel cubren eso. | 0 |
| Producción de video | Lo decide Vox Studio con sus saldos y la Matriz de Redes con su presupuesto. | Ver Vox Studio |

## Fuentes

- Programa de pago a creadores: <https://help.x.com/using-x/original-content-rewards> y <https://help.x.com/en/using-x/creator-revenue-sharing>.
- Precios de la API: <https://docs.x.com/x-api/getting-started/pricing>.
- Ranking sin ventaja por Premium: [algoritmo.md](algoritmo.md).
