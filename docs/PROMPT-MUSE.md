# Encargo para Muse

Texto para pegarle a Muse (el agente que opera las cuentas de Emi en el navegador). Preparado el 10/11/2026. Cubre lo que la sesión de Claude Code no puede hacer por falta de herramienta o de sesión iniciada.

```text
Hola, Muse. Soy Emi. Necesito que dejes listo lo siguiente para mi skill de X (repositorio lianfixx/X).
Haz las tareas en orden, no te saltes ninguna y al final dame un reporte de cada una: hecha, no hecha
y por qué. Si algo pide mi contraseña, un código o una verificación en mi teléfono, detente y avísame;
no adivines ni busques otra vía.

TAREA 1 · GitHub: rama por defecto
1. Abre https://github.com/lianfixx/X/settings (con mi sesión de GitHub).
2. En «General», sección «Default branch», cambia la rama por defecto a «main» y confirma.
3. Comprueba en https://github.com/lianfixx/X que arriba a la izquierda diga «main».
No borres ninguna rama ni cambies nada más.

TAREA 2 · box: iniciar sesión en X
1. Abre https://box.simular.ai/box/cb-5f57672cf6a0/live (mi box «main»).
2. Dentro de box, abre Chrome y entra a https://x.com/login.
3. Inicia sesión en mi cuenta @emilianomilla_ (uso «Continuar con Google» con mi cuenta personal).
   Si pide verificación en mi teléfono, avísame y espera.
4. Cuando cargue el Inicio de X, comprueba que la cuenta activa sea @emilianomilla_ y deja la sesión
   abierta. No cierres Chrome.
En X no publiques, no borres, no sigas a nadie, no des like y no cambies ningún ajuste. En particular,
NO quites todavía la protección de mis posts: eso se hace después de revisar los posts que ya existen.

TAREA 3 · Claude: darle GitHub a la tarea semanal
1. Abre https://claude.ai y ve a mis tareas programadas (Routines / Tareas programadas).
2. Abre la que se llama «Revisión semanal del algoritmo de X (x-viral)».
3. Añádele el conector de GitHub y, si lo pide, el repositorio lianfixx/X. Guarda.
4. No cambies su horario (lunes 12:47, hora de México) ni su texto.
Si la pantalla no ofrece conectores para esa tarea, déjala como está y dímelo.

TAREA 4 · Claude: instalar la skill x-viral
1. Descarga https://github.com/lianfixx/X/archive/refs/heads/main.zip y descomprímelo.
2. Dentro, ve a la carpeta skills/x-viral y comprímela sola en un archivo x-viral.zip
   (el zip debe contener la carpeta x-viral con su SKILL.md adentro).
3. En https://claude.ai abre Ajustes → Capacidades → Skills, sube x-viral.zip y actívala.
4. Comprueba que aparezca en la lista con el nombre «x-viral».
Si ya existe una skill con ese nombre, reemplázala por esta.

TAREA 5 · Datos que necesito que me traigas (solo leer)
1. Con la sesión de la tarea 2, abre https://x.com/emilianomilla_ y dime: fecha exacta de «Se unió»,
   número de posts, seguidores y seguidos, y si aparece el candado de cuenta protegida.
2. Abre https://x.com/i/premium_sign_up y dime qué planes y precios muestra para México.
   NO contrates nada ni metas datos de pago.

Reporte final: una línea por tarea con su resultado, y cualquier cosa rara que hayas visto.
```

## Lo que Muse no debe hacer

- Quitar la protección de la cuenta, borrar posts o publicar: eso se decide con Emi después de revisar los posts existentes.
- Contratar Premium o cualquier pago.
- Tocar el repositorio de Vox Studio.
