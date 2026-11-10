# x-viral · la skill de X de Emi

Skill para planear, redactar, revisar, programar con aprobación y medir las publicaciones de `@emilianomilla_` en X, apoyada en el código público del algoritmo de X ([xai-org/x-algorithm](https://github.com/xai-org/x-algorithm)).

Tres pilares a partes iguales: **IA + Derecho en México**, **estilo de vida y gym** y **opinión política**. Sirve en cualquier IA.

## De dónde sale

Del video de Santi Muñoz [«Esto es lo que Claude encontró en el algoritmo de X»](https://youtu.be/lWoj_liZqOI) (15/08/2026) y de su reporte. El 10/11/2026 se cotejó todo contra el código vigente: buena parte se sostiene y varias cifras e ideas cambiaron o estaban mal leídas. El detalle está en [video-santi.md](skills/x-viral/references/video-santi.md) y en la [auditoría](docs/AUDITORIA-2026-11-10.md).

## Mapa

| Ruta | Qué es |
|---|---|
| [`skills/x-viral/SKILL.md`](skills/x-viral/SKILL.md) | La skill: reglas, flujo y a dónde ir según el encargo. |
| [`references/algoritmo.md`](skills/x-viral/references/algoritmo.md) | Lo que dice el código de X, con archivo y línea. |
| [`references/playbook.md`](skills/x-viral/references/playbook.md) | El plan para la cuenta, paso a paso. |
| [`references/pilares.md`](skills/x-viral/references/pilares.md) | Pilares, balance, política y límites. |
| [`references/redaccion.md`](skills/x-viral/references/redaccion.md) | Cómo se escribe y se revisa un post. |
| [`references/programacion.md`](skills/x-viral/references/programacion.md) | Programar en X con aprobación. |
| [`references/conexion-vox.md`](skills/x-viral/references/conexion-vox.md) | Puente con Vox Studio (videos). |
| [`references/prompts.md`](skills/x-viral/references/prompts.md) | Encargos listos para copiar. |
| [`references/portabilidad.md`](skills/x-viral/references/portabilidad.md) | Cómo cargarla en cada IA. |
| [`scripts/xviral.py`](skills/x-viral/scripts/xviral.py) | Pesos del algoritmo, revisión de borradores y semanas, balance, registro. |
| [`data/pesos.json`](skills/x-viral/data/pesos.json) | Pesos vigentes extraídos del código, con commit y fecha. |
| [`cuenta/`](cuenta/README.md) | Estado de la cuenta: perfil, voz, aprendizajes, mutuals, publicados. |
| [`puente/`](puente/README.md) | Lo que x-viral deja para Vox Studio. |
| [`ia/`](ia/REGLAS.md) | Reglas, protocolo entre IA y control. |
| [`CHANGELOG.md`](CHANGELOG.md) | Registro de cada cambio. |

## Uso rápido

```bash
X="python3 skills/x-viral/scripts/xviral.py"
$X pesos ver                                  # pesos vigentes
$X balance                                    # qué pilar toca
$X revisar cuenta/privado/borrador.json       # revisar un post
$X semana cuenta/privado/2026-W47.json        # revisar una semana
$X vox leer --espacio personal                # tono y lecciones de Vox Studio
python3 ia/verificar.py ci                    # control completo antes de un commit
```

Python 3.9 o posterior, sin dependencias. Sin terminal: [portabilidad.md](skills/x-viral/references/portabilidad.md).

## Cómo se mantiene al día

- Cada lunes, GitHub compara el código de X con los pesos guardados ([`algoritmo.yml`](.github/workflows/algoritmo.yml)) y marca en rojo si algo cambió.
- Una tarea programada semanal de Claude hace la misma comparación, actualiza la skill y propone el cambio en un pull request.
- Cada push pasa el control de [`control.yml`](.github/workflows/control.yml).

## Estado

Versión 1.0.0 (10/11/2026). Probado: script y control. **No probado todavía**: la cuenta es nueva, así que no hay posts, métricas ni correcciones de voz de Emi, y la programación en X no se ha ejecutado contra la cuenta real.

Uso personal de Emiliano García Milla. El video y el reporte de Santi Muñoz y el código de X son de sus autores; aquí se citan y se enlazan, no se redistribuyen.
