# Contributing / Contribución

¡Gracias por tu interés en mejorar este proyecto! Sigue estas pautas para mantener la calidad y consistencia del código base.

## Flujo de trabajo

1. Haz un fork del repositorio y crea una rama descriptiva:
   ```bash
   git checkout -b feat/nombre-de-la-mejora
   ```
2. Realiza cambios pequeños y enfocados.
3. Escribe o actualiza pruebas para cubrir tu cambio.
4. Verifica localmente lint y tests:
   ```bash
   pip install -e ".[dev]"
   ruff check .
   ruff format --check .
   pytest
   ```
5. Envía un pull request contra `main`.

## Convenciones

- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `ci:`, `chore:`).
- **Estilo de código:** `ruff check` y `ruff format` (100 columnas).
- **Idioma:** los identificadores, docstrings y mensajes de commit en inglés; los comentarios explicativos pueden ser en español.

## Reglas de código

- Sigue **DRY/KISS/SOLID**: reutiliza los módulos de `src/manutd_analysis/` antes de duplicar lógica.
- No introduzcas secretos ni credenciales: usa variables de entorno y `.env.example`.
- Toda función pública debe tener docstring y anotaciones de tipos donde aporte claridad.

## Reportar problemas

Usa [GitHub Issues](https://github.com/alvarosalinaso/manchester-united-analisis/issues) con un título claro y una descripción que incluya el paso para reproducirlo.