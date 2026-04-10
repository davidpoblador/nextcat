# Xarter

Document fundacional de l'agència de programari Xarter.

## Estructura

```
xarter/
  config.toml        -- Metadades del document (autor, data)
  strings.toml       -- Cadenes traduïbles (títol, subtítol, etiquetes)
  01-introduccio.md  -- Capítol 1
  02-serveis.md      -- Capítol 2
  ...
scripts/
  build.py           -- Genera document.typ a partir dels capítols i la configuració
template.typ         -- Plantilla Typst amb estil LaTeX
justfile             -- Comandes de construcció
```

## Requisits

- [uv](https://docs.astral.sh/uv/)
- [typst](https://typst.app/)
- [just](https://just.systems/)

## Ús

```
just pdf       # Genera document.typ i compila a PDF
just typst     # Només genera document.typ
just watch     # Recompila automàticament quan canvia document.typ
just clean     # Elimina fitxers generats
just chapters  # Llista els capítols
```

## Contribuir

No cal saber Typst per modificar el document. Tot el contingut es gestiona amb fitxers Markdown i TOML.

### Editar contingut

1. Edita els fitxers `.md` dins de `xarter/`. Cada fitxer és un capítol.
2. El prefix numèric (`01-`, `02-`, ...) determina l'ordre dels capítols.
3. Utilitza Markdown estàndard: encapçalaments (`#`, `##`, `###`), llistes, negreta, cursiva, etc.

### Afegir un capítol

1. Crea un fitxer `.md` a `xarter/` amb el prefix numèric adequat (p. ex. `05-nou-capitol.md`).
2. Comença el fitxer amb un encapçalament de nivell 1 (`# Títol del capítol`).
3. Executa `just pdf` per generar el PDF. El nou capítol apareixerà automàticament a l'índex.

### Modificar metadades

- `xarter/config.toml` -- Autor i data del document.
- `xarter/strings.toml` -- Títol, subtítol i cadenes de la interfície (etiquetes del peu de pàgina, títol de l'índex).

### Traduccions

El document canònic és en català. Les traduccions es col·loquen a `translations/<lang>/`:

```
translations/
  es/
    strings.toml       -- Cadenes en castellà
    01-introduccio.md  -- Capítols traduïts
    ...
  en/
    strings.toml
    ...
```

Cada traducció necessita el seu propi `strings.toml` amb les cadenes localitzades. La configuració no traduïble (`config.toml`) és compartida.

### Generar el PDF

```
just pdf
```

Això executa `scripts/build.py` (que llegeix la configuració, les cadenes i els capítols per generar `document.typ`) i després compila el Typst a PDF. La portada inclou automàticament la data de generació i la data de l'última modificació del contingut.
