# Encargos listos para copiar

Sirven en cualquier IA. Con terminal se usan tal cual; sin terminal, la IA sigue el mismo orden a mano (ver [portabilidad.md](portabilidad.md)).

## 1. Analizar el algoritmo (el encargo de Santi, corregido)

El original está en [video-santi.md](video-santi.md). Esta versión añade lo que la auditoría demostró que faltaba: fecha del código, evidencia por afirmación y la advertencia oficial sobre los pesos.

```text
X publica el código de su feed Para ti en https://github.com/xai-org/x-algorithm.
Clónalo y trabaja solo con lo que diga el código de hoy; anota el commit y su fecha.

Quiero saber cómo decide qué se distribuye y qué no: qué acciones pesan más, qué
formatos convienen, qué hace que una cuenta o un post pierda visibilidad y qué no
debo hacer.

Reglas:
- Cada afirmación lleva archivo y línea. Lo que no encuentres, dilo como «no está en
  el código», no como «no existe».
- Lee primero el README (sección Notable Updates) y los comentarios de
  home-mixer/params/param.rs: los pesos multiplican probabilidades predichas para
  cada lector, no conteos. No me des equivalencias del tipo «vale 40 likes».
- Compara home-mixer/params/param.rs con vm-ranker/params.rs y dime dónde difieren.
- Reparte la lectura por carpetas en varios agentes y, al final, que otro agente
  intente refutar cada afirmación contra el código. Entrégame solo lo que sobreviva
  y una lista aparte de lo que corregiste.
- Antes de empezar, pregúntame lo que necesites sobre mi cuenta y mis temas.

Entrega: reporte con el paso a paso para mi cuenta y una sección de límites del
análisis (lo que el repositorio no publica).
```

## 2. Revisión semanal del algoritmo

```text
Usa la skill x-viral del repositorio lianfixx/X. Clona xai-org/x-algorithm en una
carpeta temporal y corre
«python3 skills/x-viral/scripts/xviral.py pesos comparar --repo RUTA --sellar».
Si no hay cambios y el commit de X es el mismo, termina sin tocar nada. Si no hay
cambios pero X publicó un commit nuevo, sube el sello de verificación (data/pesos.json)
con su entrada en CHANGELOG.md. Si hay cambios: lee el diff y las
secciones nuevas de Notable Updates, actualiza references/algoritmo.md y lo que
dependa de ello, corre «pesos extraer» y las pruebas, registra en CHANGELOG.md y
abre un pull request que explique en lenguaje llano qué cambió y qué cambia para Emi
(esta tarea tiene su autorización permanente para abrirlo; no lo fusiones).
```

## 3. Semana de contenido

```text
Usa la skill x-viral. Lee cuenta/perfil.json, cuenta/voz.md, cuenta/aprendizajes.md
y el puente con Vox Studio. Corre «xviral.py balance» para saber qué pilar toca.
Pregúntame qué pasó esta semana (entrenos, casos de IA que usé, noticias que me
importan y mi postura sobre cada una). Con eso propón la semana: una o dos
publicaciones por día, separadas al menos cuatro horas, un tercio por pilar.
Valida con «xviral.py semana» hasta que no haya errores y enséñame cada texto
para corregirlo con mis palabras. No programes nada sin mi visto bueno, post por post,
y anótalo con «xviral.py aprobar» solo cuando te lo dé.
```

## 4. Un post a partir de una idea

```text
Usa la skill x-viral. Idea: {idea}. Pilar: {pilar}.
Si es política, antes pregúntame mi postura. Si cita derecho, verifica la fuente
oficial y pon el enlace. Dame tres versiones con ángulos distintos, cada una con
sus señales, sus riesgos y por qué alguien la mandaría a otra persona. Revísalas
con «xviral.py revisar» y dime cuál publicarías y por qué.
```

## 5. Revisión mensual

```text
Usa la skill x-viral. Pídeme las métricas del mes (o léelas de la analítica de X si
tengo sesión abierta en box) y anótalas con «xviral.py publicado ID --metricas».
Dime qué posts trajeron seguidores, respuestas y compartidos, cuáles no, y qué
patrón ves por pilar y formato. Si mi cuenta ya cumple los requisitos, revisa
conmigo el reporte Under the Hood. Guarda cada lección con «xviral.py aprender»,
propón ajustes al balance y deja ideas de video para Vox Studio con «xviral.py vox idea».
```
