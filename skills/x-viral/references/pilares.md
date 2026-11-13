# Pilares, balance y límites

Decidido por Emi el 10/11/2026. Cuenta: `@emilianomilla_`, personal, nueva.

## Para qué es la cuenta

Marca personal, influencia política y comunidad de IA + Derecho. No es un canal de captación de clientes: un post no ofrece servicios del despacho ni promete resultados.

## Los tres pilares, a partes iguales

| Pilar | Clave | Qué es | Qué no es |
|---|---|---|---|
| IA + Derecho en México | `ia-derecho` | Cómo usa Emi la IA en trabajo jurídico real, qué sirve y qué falla, regulación y criterios mexicanos sobre IA, datos y tecnología. | Tutoriales genéricos de IA, hilos de «10 prompts», noticias traducidas sin postura. |
| Estilo de vida y gym | `lifestyle` | Entrenos, disciplina, rutina, estudio (maestría), lo que Emi hace y aprende. Fotos y video propios. | Frases motivacionales sin experiencia propia, consejos médicos o de nutrición con tono de experto. |
| Opinión política | `politica` | Lectura de hechos y decisiones públicas como analista jurídico con postura, crítico e independiente. | Vocería de partido, consignas, ataques a personas. |

Un tercio cada uno, medido sobre los últimos 30 días con `xviral.py balance`. Una semana de seis o más posts no pasa la validación si un pilar se aleja más de 15 puntos de su tercio. Emi puede cambiar el reparto en `cuenta/perfil.json`.

### Por qué importa mezclar bien

El modelo de X decide a quién enseñar un post según el historial de quien interactúa. Tres públicos que no se tocan (gym, abogados, política) le dan tres señales distintas. Lo que une a la cuenta es **una persona con criterio propio**, y eso se construye con posts puente:

- Gym con Derecho: disciplina, hábito y método aplicados al estudio o al litigio.
- IA con política: qué significa una iniciativa o una sentencia para quien usa IA.
- Política con Derecho: el argumento jurídico detrás de la opinión, con la fuente.

Procurar un post puente por cada tres o cuatro. Cuenta para el pilar que domine el texto.

## Opinión política: analista jurídico con postura, crítico independiente

1. **La postura es de Emi.** Antes de redactar se le pregunta qué piensa, qué quiere criticar o defender y por qué. Se guarda en `opinion_emi`; sin eso el validador rechaza el borrador. Es la misma regla de Vox Studio.
2. **Primero el hecho y su fuente**, después la opinión. La crítica va a decisiones, argumentos y resultados.
3. **Independiente**: critica a quien corresponda, sin bandera. Emi participa en Acción Política Juvenil; la cuenta personal no habla a nombre del PAN ni de Acción Juvenil, no usa sus logotipos y no publica su material como propio. Si un post trata de ellos, se dice la relación.
4. **Sin ataques personales**: ni insultos, ni apodos, ni burlas al físico o a la vida privada.
5. **Riesgo**: es el pilar que más puede provocar que lo silencien, lo bloqueen o lo reporten, que son los pesos negativos más grandes del código. Un borrador con riesgo de reporte o de silencio (`mute`) en 2 o más se reescribe. Releerlo con ojos de quien piensa distinto: ¿le daría motivos para reportar o solo para discutir? Discutir es lo que se busca.
6. **Periodos electorales**: revisar las reglas vigentes (veda, propaganda) antes de publicar sobre candidatos o partidos, y preguntarle a Emi.

## Límites permanentes

- **Nunca clientes ni asuntos**: ni de MILLA ni de Castorena, ni anonimizados ni «un caso que vi». Los ejemplos jurídicos son hipotéticos y se dicen como tales.
- **No nombrar a Castorena Abogados** ni a sus licenciados.
- **Nunca decir que algo lo hizo una IA** (Emi, 13/11/2026: «jamás en nada digas que lo armó una IA»). Las herramientas, los textos y los videos los construye Emi, con IA: «armé», «construí», «uso IA para…» sí; «lo escribió una IA», «generado por IA» no.
- **Sin ataques personales.**
- **Toda cita legal verificada**: artículo, tesis, criterio o dato con enlace a fuente oficial vigente (DOF, Cámara de Diputados, SCJN/SJF, autoridad emisora) antes de publicar. Sin fuente, no se afirma.
- Un post informa u opina; no es asesoría para un caso concreto ni promete resultados.
- Nada de datos personales de terceros.

El validador es una red, no el juez. Detecta el nombre del despacho vetado, menciones a clientes («un cliente», «mi clienta», «mis clientes»), números de expediente o de juicio y los insultos más comunes, y avisa de palabras dudosas. Se le escapan las paráfrasis («alguien que me contrató»), los apodos y el sarcasmo. Un asunto público con fuente o un ejemplo claramente hipotético se declaran en `excepcion_limite` con su motivo. Lo demás es criterio de quien redacta y de Emi al aprobar.

## Los espacios de Vox Studio

Vox Studio separa cuatro espacios: personal, MILLA, Castorena y PAN/Acción Juvenil. **Esta cuenta de X es el espacio `personal`.** Los videos de los otros espacios no se publican aquí salvo que Emi lo pida de forma expresa para uno concreto, y aun así valen los límites de arriba. Ver [conexion-vox.md](conexion-vox.md).
