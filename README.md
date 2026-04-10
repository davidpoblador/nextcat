# Xarter

Document fundacional de l'agència de programari Xarter.

Disponible en PDF i en línia a [davidpoblador.github.io/xarter](https://davidpoblador.github.io/xarter/).

## Requisits

- [uv](https://docs.astral.sh/uv/)
- [typst](https://typst.app/)
- [just](https://just.systems/)

## Ús

```
just pdf       # Genera PDFs per a tots els idiomes (build/xarter-{versió}.{lang}.pdf)
just lang ca   # Genera el PDF només per a un idioma
just site      # Genera el lloc web (site/)
just serve     # Serveix el lloc web localment
just clean     # Elimina fitxers generats
```

## Estructura

```
xarter/
  config.toml        -- Metadades (autor, email, repo)
  strings.toml       -- Cadenes traduïbles (títol, etiquetes, etc.)
  00-prefaci.md      -- Prefaci (front matter, sense numeració)
  01-introduccio.md  -- Capítol 1
  02-serveis.md      -- Capítol 2
  ...
  license.md         -- Llicència localitzada per al PDF
scripts/
  build.py           -- Genera document.typ, index.md i mkdocs.yml
templates/
  template.typ       -- Plantilla Typst (estil LaTeX, tokens de disseny)
  mkdocs.yml         -- Plantilla MkDocs (la nav es genera automàticament)
AUTHORS              -- Llista d'autors (Name <url>)
VERSION              -- Versió (gestionada per release-please)
```

## Contribuir

No cal saber Typst per modificar el document. Tot el contingut es gestiona amb fitxers Markdown i TOML.

### Editar contingut

1. Edita els fitxers `.md` dins de `xarter/`.
2. El prefix numèric (`01-`, `02-`, ...) determina l'ordre dels capítols.
3. Fitxers amb prefix `00-` són front matter (sense numeració, no apareixen a l'índex del PDF).
4. Executa `just pdf` per verificar el resultat.

### Afegir un capítol

1. Crea un fitxer `.md` a `xarter/` amb el prefix numèric adequat (p. ex. `05-nou-capitol.md`).
2. Comença el fitxer amb un encapçalament de nivell 1 (`# Títol del capítol`).
3. El capítol apareixerà automàticament a l'índex, la navegació web i la pàgina d'inici.

### Configuració

- `xarter/config.toml` -- Metadades no traduïbles: autor, email, URL del repositori.
- `xarter/strings.toml` -- Cadenes traduïbles: títol, subtítol, etiquetes de la portada, l'índex, l'annex i el colofó.

### Traduccions

El document canònic és en català. Les traduccions es col-loquen a `translations/<lang>/`:

```
translations/
  es/
    strings.toml       -- Cadenes en castellà (inclou [translation] notice)
    license.md         -- Llicència en castellà
    00-prefaci.md      -- Prefaci traduït
    01-introduccio.md  -- Capítols traduïts
    ...
  en/
    strings.toml
    license.md
    ...
```

Cada traducció necessita:

- `strings.toml` amb totes les cadenes traduïdes, incloent un camp `[translation] notice` que indica que és una traducció del document canònic en català.
- `license.md` amb el text de la llicència en l'idioma corresponent.
- Els fitxers `.md` dels capítols traduïts. Si un capítol no es tradueix, es fa servir la versió catalana.

La configuració no traduïble (`config.toml`) és compartida entre tots els idiomes.

## Contribuir

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) per a la guia completa.

## Llicència

[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ca)
