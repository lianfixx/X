# Programar con aprobación de Emi

Emi eligió el 10/11/2026 que la skill programara en X con su visto bueno, post por post. El 11/11/2026 eso quedó en pausa porque X bloquea el inicio de sesión desde las máquinas de las IA: ahora la IA entrega y Emi publica. Nada se publica solo.

## Regla de oro

La IA no opera la cuenta. No da like, no sigue, no responde, no cita, no manda mensajes y no borra en nombre de Emi. El código clasifica como automatización las secuencias mecánicas de acciones y las interacciones sobre posts que nunca se mostraron en pantalla; una cuenta nueva no puede permitirse esa etiqueta. La conversación la lleva Emi; la IA le prepara borradores de respuesta si los pide.

## Requisitos de cada post

`xviral.py revisar BORRADOR --para programado` sin errores. Eso exige:

- El visto bueno de Emi a **ese texto exacto y a su foto o video**, anotado con `xviral.py aprobar ARCHIVO ID --medio "…"` solo después de que lo dio. La orden guarda la fecha, el medio y una huella del texto; si el texto cambia, `revisar` lo rechaza hasta que Emi lo vuelva a aprobar. Anotar una aprobación que Emi no dio es la falta más grave que puede cometer una IA en este repositorio.
- `fecha` (no pasada) y `hora`, en hora del centro de México.
- En política, `opinion_emi`; con cita legal, `fuentes`.

Una aprobación general («programa lo de la semana») no basta: se le enseña cada texto.

## Cómo sale un post (vigente desde el 11/11/2026)

**Emi publica o programa; la IA entrega.** X bloquea el inicio de sesión desde box y desde la máquina virtual de Muse («Sorry, you are not allowed to log in at this time», intentos del 10 y 11/11/2026, antes de pedir contraseña o código). Por decisión de Emi, **ninguna IA vuelve a intentar iniciar sesión en X**: insistir desde máquinas en la nube puede acabar en un bloqueo de la cuenta.

Para cada post aprobado, la IA entrega un bloque listo para copiar:

```text
POST 2026-11-17-a · martes 17/11, 08:30 (hora del centro de México) · pilar: ia-derecho
Archivo: (ninguno | la foto o el video aprobado)
----
(texto exacto aprobado)
```

Emi lo pega en X desde su teléfono o su computadora. Para programarlo: en x.com, cuadro de redacción → icono de calendario → fecha y hora → Programar. Si su aplicación no muestra el calendario, lo publica a la hora indicada. Después le dice a la IA «publicado» y, si puede, el enlace.

La IA no dice «programado» ni «publicado» por su cuenta: cambia el `estado` del borrador cuando Emi lo confirma.

### Con navegador y sesión de Emi (hoy no disponible)

Si algún día Emi abre él mismo una sesión de X en un navegador que la IA pueda usar, y lo pide de forma expresa:

1. Abrir `https://x.com/compose/post` y comprobar que la cuenta activa es `@emilianomilla_`. La IA no escribe contraseñas ni códigos.
2. Pegar el texto aprobado tal cual y adjuntar el archivo aprobado (foto o video); si es video, uno solo.
3. Icono de calendario. **Leer la zona horaria que muestra el cuadro** y convertir la hora del borrador a esa zona. Confirmar → **Programar**.
4. Abrir la lista de programados, verificar texto, archivo, fecha y hora, y tomar captura.
5. Cambiar `estado` a `programado` y avisar a Emi con la captura.

## Si un post programado tiene que cambiar

La IA no edita ni borra un post programado por su cuenta. Se le avisa a Emi; él lo edita o lo borra desde la lista de programados, o lo pide de forma expresa para ese post. Si cambia el texto, es un borrador nuevo: se revisa, Emi lo aprueba y se vuelve a programar.

## Después de publicar

```bash
python3 skills/x-viral/scripts/xviral.py publicado 2026-11-17-a --pilar ia-derecho --formato texto \
  --texto "texto tal como salió" --fecha 2026-11-17 --hora 08:30 --url https://x.com/emilianomilla_/status/…
python3 skills/x-viral/scripts/xviral.py publicado 2026-11-17-a --metricas vistas=1200 replies=4 compartidos=3 seguidores=5
```

Las métricas se anotan a las 48 horas, cuando el post ya salió de los índices de distribución. Lo que Emi observe se guarda con `xviral.py aprender`.

## Estado de esta función

- 10/11/2026: procedimiento con navegador documentado, sin ejecutar.
- 10 y 11/11/2026: Muse intentó iniciar sesión en X desde box y desde su máquina virtual; X lo bloqueó las dos veces. Emi indicó no volver a intentarlo.
- Desde el 11/11/2026 el modo vigente es la entrega para copiar. No se ha usado todavía con un post real: la primera semana empieza el 16/11/2026.
