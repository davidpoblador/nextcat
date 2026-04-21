# Contribuir a Xarter

Gràcies per l'interès en contribuir al xàrter. Aquesta guia explica com fer-ho.

## Requisits

- [uv](https://docs.astral.sh/uv/) (gestor de paquets Python)
- [just](https://just.systems/) (executor de tasques)

El compilador [Typst](https://typst.app/) s'instal-la automàticament com a paquet Python i les fonts Libertinus Serif viuen al directori `fonts/`, així que no cal cap instal-lació addicional.

Instal-la les dependències:

```
uv sync
```

## Flux de treball

1. Crea una branca des de `main` amb un nom descriptiu (p. ex. `feat/nou-capitol-seguretat`).
2. Fes els canvis en commits petits i freqüents.
3. Cada commit ha de seguir la sintaxi de [Conventional Commits](https://www.conventionalcommits.org/) (vegeu la secció següent).
4. Executa `just clean && just pdf && just site` per verificar que tot compila correctament.
5. Puja la branca i obre un pull request contra `main`.

## Pull requests

- El títol del PR ha de seguir la sintaxi de Conventional Commits (p. ex. `feat: afegir capítol de seguretat`).
- La descripció ha d'explicar breument què canvia i per què.
- Cada PR ha de contenir canvis cohesius: no barregis canvis de contingut amb canvis d'infraestructura.
- Els PRs es fusionen amb squash merge. El títol del PR es converteix en el missatge del commit a `main`.
- Release-please utilitza els commits a `main` per generar el changelog i decidir el tipus de versió, per tant els prefixos dels commits són importants.
- Mai pushis directament a `main`.

## Commits convencionals

Els missatges de commit (i títols de PR) han d'estar en anglès i seguir el format:

```
<tipus>: <descripció curta>
```

| Prefix | Ús | Efecte al versionat |
|---|---|---|
| `feat:` | Contingut nou o funcionalitat nova | Incrementa versió menor (0.X.0) |
| `fix:` | Correccions | Incrementa pegat (0.0.X) |
| `docs:` | Documentació (README, CONTRIBUTING, etc.) | Apareix al changelog |
| `chore:` | Manteniment (dependències, CI, etc.) | Apareix al changelog |
| `refactor:` | Reestructuració sense canvi funcional | Apareix al changelog |
| `ci:` | Canvis a workflows de CI/CD | Apareix al changelog |

Exemples:

```
feat: add security chapter
fix: correct Catalan spelling in methodology chapter
docs: update translation instructions in README
chore: update mkdocs-material to 9.8
```

Release-please genera automàticament el changelog i les versions a partir d'aquests commits. Commits que no segueixen la convenció no apareixen al changelog.

## Editar contingut

- Edita els fitxers `.md` dins de `book/`.
- El prefix numèric (`01-`, `02-`, ...) determina l'ordre.
- Fitxers amb prefix `00-` són front matter (sense numeració).
- Cada capítol comença amb un encapçalament `# Títol`.

## Afegir un capítol

1. Crea `book/NN-slug.md` amb el prefix numèric adequat.
2. Comença amb `# Títol del capítol`.
3. Apareixerà automàticament a l'índex del PDF, la navegació web i la pàgina d'inici.

## Modificar cadenes i etiquetes

- `book/strings.toml` conté totes les cadenes traduïbles (títol, subtítol, etiquetes).
- `config.toml` conté les metadades no traduïbles (autor, email, repo).
- Mai escriguis cadenes directament en els templates o scripts.

## Traduccions

El document canònic és en català. Per traduir:

1. Crea `translations/<lang>/` (p. ex. `translations/es/`).
2. Afegeix `strings.toml` amb totes les cadenes traduïdes, incloent `[translation] notice`.
3. Afegeix `license.md` amb el text de la llicència en l'idioma corresponent.
4. Tradueix els fitxers `.md` dels capítols. Els capítols sense traducció es serviran en català.

## IA i transparència

Si fas servir eines d'intel-ligència artificial per generar contingut o codi, indica-ho al commit amb un `Co-Authored-By` o una nota a la descripció del PR. Exemples:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

La transparència és important perquè els revisors puguin avaluar el contingut adequadament.

## Contribuïdors

Si ets un contribuïdor nou, afegeix-te al fitxer `AUTHORS`:

```
Nom Complet <https://elsiteweb.example/>
```

## Fitxers generats

No editis manualment:

- `mkdocs.yml` (generat per `scripts/build.py`)
- `book/index.md` (generat per `scripts/build.py`)
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
