# NextCat

**Estratègia Digital de Catalunya** — Guia per a responsables de política i administració pública.

Un document que proposa una estratègia pragmàtica i informada per a la transformació digital de Catalunya en l'era de la intel·ligència artificial. Es dirigeix a responsables de política pública, administradors i professionals que necessiten un marc de referència amb diagnòstic, principis i recomanacions concretes.

## De què parla

El document s'estructura en set blocs:

1. **El context** — La transformació global que impulsa la IA i les seves implicacions per al sector del programari i l'economia del coneixement.
2. **El diagnòstic** — La situació actual de Catalunya: actius diferencials, debilitats estructurals i oportunitats perdudes per falta d'actuació.
3. **Referents internacionals** — Lliçons d'Estònia, el Regne Unit, França i els EUA aplicables al context català.
4. **Principis estratègics** — Els criteris que haurien de guiar les decisions en l'àmbit digital, independentment de quin govern les implementi.
5. **Recomanacions** — Accions concretes, organitzades per horitzó temporal i dificultat d'implementació.
6. **La visió a llarg termini** — El punt d'arribada i el camí incremental per arribar-hi.

Cada afirmació factual inclou la seva font; cada recomanació, la seva lògica.

## Disponible a

- Web: [nextcat.poblador.cat](https://nextcat.poblador.cat/)
- PDF (última versió): [nextcat.ca.pdf](https://github.com/davidpoblador/nextcat/releases/latest/download/nextcat.ca.pdf)
- Repositori: [github.com/davidpoblador/nextcat](https://github.com/davidpoblador/nextcat)

## Requisits

- [uv](https://docs.astral.sh/uv/)
- [just](https://just.systems/)

El compilador [Typst](https://typst.app/) i la família Libertinus Serif s'instal-len automàticament via `uv sync` i `fonts/`.

## Ús

```
just pdf       # Genera PDFs per a tots els idiomes (build/nextcat-{versió}.{lang}[-full].pdf)
just lang ca   # Genera el PDF només per a un idioma
just site      # Genera el lloc web estàtic (public/)
just book      # Àlies de `just site`
just clean     # Elimina fitxers generats
```

## Estructura

```
book/
  config.toml        -- Metadades (autor, email, repo)
  strings.toml       -- Cadenes traduïbles (títol, etiquetes, etc.)
  00-prefaci.md      -- Prefaci (front matter, sense numeració)
  01-introduccio.md  -- Capítol 1
  02-context.md      -- Capítol 2
  ...
  license.md         -- Llicència localitzada per al PDF
scripts/
  build.py           -- CLI de generació de PDF
  site.py            -- Generador del lector HTML
  generate.py        -- Lògica compartida (chapters, changelog, Typst)
config.toml          -- Metadades (autor, email, repo)
templates/
  template.typ       -- Plantilla Typst (estil LaTeX, tokens de disseny)
  site/              -- Plantilles Jinja2 i CSS del lector HTML
fonts/               -- Libertinus Serif (SIL OFL, inclòs al repositori)
AUTHORS              -- Llista d'autors (Name <url>)
VERSION              -- Versió (gestionada per release-please)
```

## Contribuir

No cal saber Typst per modificar el document. Tot el contingut es gestiona amb fitxers Markdown i TOML. Consulta [CONTRIBUTING.md](CONTRIBUTING.md) per a la guia completa i el [codi de conducta](CODE_OF_CONDUCT.md).

### Editar contingut

1. Edita els fitxers `.md` dins de `book/`.
2. El prefix numèric (`01-`, `02-`, ...) determina l'ordre dels capítols.
3. Fitxers amb prefix `00-` són front matter (sense numeració, no apareixen a l'índex del PDF).
4. Executa `just pdf` o `just book` per verificar el resultat.

### Afegir un capítol

1. Crea un fitxer `.md` a `book/` amb el prefix numèric adequat (p. ex. `05-nou-capitol.md`).
2. Comença el fitxer amb un encapçalament de nivell 1 (`# Títol del capítol`).
3. El capítol apareixerà automàticament a l'índex, la navegació i la pàgina d'inici.

### Configuració

- `config.toml` (arrel) — Metadades no traduïbles: autor, email, URL del repositori.
- `book/strings.toml` — Cadenes traduïbles: títol, subtítol, etiquetes de la portada, l'índex, l'annex i el colofó.

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
```

Cada traducció necessita:

- `strings.toml` amb totes les cadenes traduïdes, incloent un camp `[translation] notice`.
- `license.md` amb el text de la llicència en l'idioma corresponent.
- Els fitxers `.md` dels capítols traduïts. Si un capítol no es tradueix, es fa servir la versió catalana.

La configuració no traduïble (`config.toml`) és compartida entre tots els idiomes.

## Llicència

[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ca)
