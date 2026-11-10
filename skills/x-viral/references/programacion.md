# Programar con aprobación de Emi

Emi eligió el 10/11/2026: la skill puede dejar posts programados en X, **uno por uno y solo después de su visto bueno**. Nada se publica solo.

## Regla de oro

La IA solo toca el botón de programar. No da like, no sigue, no responde, no cita, no manda mensajes y no borra en nombre de Emi. El código clasifica como automatización las secuencias mecánicas de acciones y las interacciones sobre posts que nunca se mostraron en pantalla; una cuenta nueva no puede permitirse esa etiqueta. La conversación la lleva Emi; la IA le prepara borradores de respuesta si los pide.

## Requisitos de cada post

`xviral.py revisar BORRADOR --para programado` sin errores. Eso exige:

- El visto bueno de Emi a **ese texto exacto y a su foto o video**, anotado con `xviral.py aprobar ARCHIVO ID --medio "…"` solo después de que lo dio. La orden guarda la fecha, el medio y una huella del texto; si el texto cambia, `revisar` lo rechaza hasta que Emi lo vuelva a aprobar. Anotar una aprobación que Emi no dio es la falta más grave que puede cometer una IA en este repositorio.
- `fecha` (no pasada) y `hora`, en hora del centro de México.
- En política, `opinion_emi`; con cita legal, `fuentes`.

Una aprobación general («programa lo de la semana») no basta: se le enseña cada texto.

## Cómo se programa

X permite programar desde la web: en el cuadro de redacción, el icono de calendario. No se usan servicios de terceros ni la API.

Con box (la computadora en la nube de Emi) u otro navegador con su sesión:

1. Abrir `https://x.com/compose/post`. Si pide iniciar sesión, verificación en dos pasos o un captcha, darle a Emi el enlace para que lo haga él; la IA no escribe ni guarda contraseñas ni códigos.
2. Comprobar que la cuenta activa es `@emilianomilla_`.
3. Pegar el texto aprobado tal cual. Adjuntar el archivo aprobado (foto o video); si es video, uno solo.
4. Icono de calendario. **Leer la zona horaria que muestra el cuadro**: X usa la del navegador o de la cuenta, y box es una máquina en la nube que puede no estar en hora de México. Convertir la hora del borrador a esa zona, elegir fecha y hora, confirmar → **Programar**.
5. Abrir la lista de programados y verificar texto, archivo adjunto, fecha y hora (ya convertida). Tomar captura.
6. Cambiar `estado` a `programado` en el borrador y avisar a Emi con la captura.

Sin navegador con sesión: entregar a Emi el texto listo para copiar, con fecha y hora, y decirlo así. No decir «programado» si no se verificó en la lista de programados.

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

El 10/11/2026 se documentó el procedimiento; **no se ha ejecutado** contra la cuenta real porque es nueva y no había sesión abierta. La primera vez se hace con Emi mirando, y lo que cambie en la interfaz de X se corrige aquí.
