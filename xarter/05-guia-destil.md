# Guia d'estil

## Tipografia i format

### Negreta i cursiva

Fem servir **negreta** per destacar conceptes clau i *cursiva* per a termes tècnics o estrangers. També es pot combinar ***negreta i cursiva*** quan cal.

### Llistes

Llistes no ordenades:

- Element de primer nivell
- Un altre element
  - Subelement aniuat
  - Un altre subelement
- Tercer element

Llistes ordenades:

1. Primer pas
2. Segon pas
3. Tercer pas

### Codi

Codi en línia: `python build.py` o `just pdf`.

Blocs de codi amb sintaxi:

```python
def saluda(nom: str) -> str:
    return f"Hola, {nom}!"
```

```toml
[document]
author = "Xarter S.L."
repo = "https://github.com/davidpoblador/xarter"
```

## Estructura de contingut

### Encapçalaments de tercer nivell

Utilitzem fins a tres nivells d'encapçalaments dins de cada capítol. El primer nivell (`#`) és el títol del capítol, el segon (`##`) són les seccions principals i el tercer (`###`) les subseccions.

#### Encapçalaments de quart nivell

En casos excepcionals, es pot fer servir un quart nivell per a subdivisions molt específiques. Cal evitar abusar-ne per mantenir la llegibilitat.

## Enllaços i referències

Els enllaços externs es marquen amb la sintaxi habitual de Markdown: [lloc web de Typst](https://typst.app/) o [repositori del projecte](https://github.com/davidpoblador/xarter).

## Cites i blocs

> Les cites es fan servir per destacar fragments textuals d'altres fonts o per emfatitzar un principi important del xàrter.

## Taules

| Tecnologia | Àmbit | Maduresa |
|---|---|---|
| Python | Backend | Alta |
| Typst | Documents | Mitjana |
| MkDocs | Web | Alta |

## Separadors

El separador horitzontal es fa servir per dividir seccions temàticament diferents dins d'un mateix capítol.

---

Aquesta secció, per exemple, està separada de l'anterior per un separador horitzontal.
