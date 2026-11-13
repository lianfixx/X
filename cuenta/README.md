# Estado de la cuenta @emilianomilla_

| Archivo | Qué guarda |
|---|---|
| `perfil.json` | Configuración: balance, cadencia, si hay Premium (`true`/`false` sin comillas), `creada` (fecha de creación de la cuenta, para saber cuándo habrá Under the Hood), `protegida` (si los posts tienen candado), `observado` (lo último que se vio en el perfil público) y `vox_ref` (rama de respaldo de Vox Studio). Lo lee `xviral.py`. |
| `perfil-publico.md` | Nombre, biografía, ubicación y enlace propuestos para el perfil de X. |
| `voz.md` | Cómo escribe Emi en X y sus correcciones. |
| `aprendizajes.md` | Lecciones de cada publicación. |
| `mutuals.md` | Cuentas con las que conversa. Son cuentas públicas de terceros: solo el usuario y el tema, sin opiniones sobre personas. |
| `publicados.jsonl` | Lo ya publicado y sus métricas (`xviral.py publicado`). Se crea con el primer post. |
| `diagnosticos/` | Notas de cada revisión mensual. |
| `privado/` | Borradores y semanas sin publicar. **No se sube a GitHub**: este repositorio es público. |

Si Emi quiere que los borradores también viajen entre IA por GitHub, hay que volver privado el repositorio y quitar `cuenta/privado/` de `.gitignore`.
