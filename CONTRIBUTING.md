# Contribuir a Xarter

Gràcies per l'interès en contribuir al xàrter. Aquesta guia explica com fer-ho.

## Requisits

- [uv](https://docs.astral.sh/uv/) (gestor de paquets Python)
- [typst](https://typst.app/) (compilador de documents)
- [just](https://just.systems/) (executor de tasques)

Instal-la les dependències:

```
uv sync
```

## Flux de treball

1. Crea una branca des de `main`.
2. Fes els canvis.
3. Executa `just pdf` i verifica el PDF resultant.
4. Fes commit amb un missatge que segueixi les [Conventional Commits](https://www.conventionalcommits.org/).
5. Obre un pull request contra `main`.

## Tipus de commits

| Prefix | Ús |
|---|---|
| `feat:` | Contingut nou o funcionalitat nova |
| `fix:` | Correccions |
| `docs:` | Documentació (README, CONTRIBUTING, etc.) |
| `chore:` | Manteniment (dependències, CI, etc.) |
| `refactor:` | Reestructuració sense canvi funcional |
| `ci:` | Canvis a workflows de CI/CD |

El versionat és automàtic: `feat:` incrementa la versió menor, `fix:` incrementa el pegat.

## Editar contingut

- Edita els fitxers `.md` dins de `xarter/`.
- El prefix numèric (`01-`, `02-`, ...) determina l'ordre.
- Fitxers amb prefix `00-` són front matter (sense numeració).
- Cada capítol comença amb un encapçalament `# Títol`.

## Afegir un capítol

1. Crea `xarter/NN-slug.md` amb el prefix numèric adequat.
2. Comença amb `# Títol del capítol`.
3. Apareixerà automàticament a l'índex del PDF, la navegació web i la pàgina d'inici.

## Modificar cadenes i etiquetes

- `xarter/strings.toml` conté totes les cadenes traduïbles (títol, subtítol, etiquetes).
- `xarter/config.toml` conté les metadades no traduïbles (autor, email, repo).
- Mai escriguis cadenes directament en els templates o scripts.

## Traduccions

El document canònic és en català. Per traduir:

1. Crea `translations/<lang>/` (p. ex. `translations/es/`).
2. Afegeix `strings.toml` amb totes les cadenes traduïdes, incloent `[translation] notice`.
3. Afegeix `license.md` amb el text de la llicència en l'idioma corresponent.
4. Tradueix els fitxers `.md` dels capítols. Els capítols sense traducció es serviran en català.

## Autors

Si ets un contribuïdor nou, afegeix-te al fitxer `AUTHORS`:

```
Nom Complet <https://elsiteweb.example/>
```

## Fitxers generats

No editis manualment:

- `mkdocs.yml` (generat per `scripts/build.py`)
- `xarter/index.md` (generat per `scripts/build.py`)
- `build/` (artefactes de compilació)
- `VERSION` (gestionat per release-please)
- `CHANGELOG.md` (gestionat per release-please)
- `.release-please-manifest.json` (gestionat per release-please)

## Verificar

Abans d'obrir un PR:

```
just clean
just pdf       # Verifica que el PDF es genera correctament
just site      # Verifica que el lloc web es genera correctament
```
