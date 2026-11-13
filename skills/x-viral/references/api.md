# Publicar por la API oficial de X

Decisión de Emi del 13/11/2026: «usaremos la API». Los posts que Emi apruebe se publican por la API oficial de X, desde el panel de la Matriz de Redes o desde un chat de Claude. Nadie inicia sesión en la cuenta como persona: la API usa llaves de una app que Emi autoriza.

**Estado:** Emi abrió la cuenta de desarrollador el 13/11/2026. La conexión todavía no está hecha ni probada; hasta entonces sigue valiendo la entrega para copiar de [programacion.md](programacion.md).

## Qué hace y qué no hace la API aquí

| Sí | No |
|---|---|
| Publicar un post aprobado, con su foto o video aprobado | Publicar algo sin aprobación de Emi a ese texto exacto |
| Leer las métricas de los posts propios | Dar like, seguir, responder, citar o mandar mensajes por Emi |
| Borrar un post solo si Emi lo pide por escrito para ese post | Leer o guardar mensajes directos |

La regla de [programacion.md](programacion.md) se mantiene: **la IA no opera la cuenta**, solo publica lo aprobado. Uno o dos posts al día aprobados por una persona no se parecen a la automatización que el código de X etiqueta.

## Arquitectura

```text
Emi aprueba ──► Panel de la Matriz de Redes (Cloudflare Worker, con contraseña)
  (en el panel        │  guarda borradores, aprobaciones y la cola
   o en Claude)       │  firma y envía a X con las llaves (secretos del Worker)
                      ▼
               API oficial de X ──► @emilianomilla_
```

- **El panel lo construye la Matriz de Redes** (`lianfixx/REDES`), porque es el panel de todas las redes. x-viral define cómo se ve y se valida un post de X y la regla de publicación.
- **Las llaves de X viven solo en el Worker**, como secretos de Cloudflare. Nunca en un repositorio, en un chat, en un correo ni en una variable de entorno de una sesión.
- **Desde Claude**: cuando Emi aprueba en el chat, la sesión anota la aprobación (`xviral.py aprobar`) y manda el post a la cola del panel con su propia llave de acceso, que guarda el formulario seguro de credenciales de Claude (`request_credential`), nunca escrita en el chat.
- **A la hora indicada**, el Worker publica lo aprobado y devuelve el enlace. Si algo falla, no reintenta en bucle: avisa.
- El Worker comprueba **otra vez** la huella del texto aprobado antes de publicar. Si el texto cambió, no publica.

## Costos (precio oficial de X al 13/11/2026; cambia, revisar antes de presupuestar)

X cobra por uso, con créditos prepagados en la consola de desarrollador. Según docs.x.com:

| Operación | Precio por solicitud |
|---|---|
| Crear un post | 0.015 USD |
| Crear un post **con enlace** | **0.200 USD** (unas 13 veces más) |
| Leer un post (métricas) | alrededor de 0.005 USD, según fuentes de terceros |

Con dos posts al día sin enlace y dos lecturas de métricas por post: 60 × 0.015 + 120 × 0.005 ≈ **1.50 USD al mes**. Con un enlace en cada post serían unos 12 USD solo de publicación.

Reglas de gasto:

1. **Tope en la consola**: fijar un límite de gasto por ciclo. Propuesta: **10 USD al mes** para empezar. Si se alcanza, X bloquea las llamadas hasta el siguiente ciclo y el panel lo avisa.
2. **Sin recarga automática** hasta ver un mes real de consumo.
3. **Enlaces en la bio, no en el post**, salvo que el enlace sea el valor del post. El código no castiga los enlaces, pero por API cuestan 13 veces más. `revisar` avisa cuando un post lleva enlace.
4. **Métricas a las 48 horas**, una lectura por post, más una a los 7 días para los que funcionaron. Nada de consultar cada hora.
5. Cada publicación y cada lectura queda anotada con su costo estimado, para cuadrar contra la consola cada mes.

## Llaves: qué app crear

En la consola de desarrollador de X, una sola app:

- **Nombre**: algo como «emi-redes».
- **Permisos de la app**: lectura y escritura. **Sin** mensajes directos.
- **Autenticación**: OAuth 1.0a con «Access Token and Secret» de `@emilianomilla_`. Esos tokens no caducan solos, lo que conviene para publicar a una hora fija. Si la consola solo ofrece OAuth 2.0, el panel guarda el token de renovación y lo rota en cada uso.
- Las llaves se pegan **solo** en la página de configuración del panel, que las guarda como secretos y no las vuelve a mostrar. Si una llave se filtra, se regenera en la consola y se vuelve a pegar.

## Limitaciones conocidas

- La API de X no programa posts por sí misma: el Worker los guarda y los publica a su hora.
- Por API no se puede saber si X distribuye distinto un post publicado desde una app. No está en el código revisado; no se afirma nada.
- Si X cambia precios o permisos, el panel debe fallar cerrado (no publica) y avisar.

## Fuentes

- Precios: <https://docs.x.com/x-api/getting-started/pricing> (consultado en resumen el 13/11/2026).
- Introducción a la API: <https://docs.x.com/x-api/getting-started/>.
