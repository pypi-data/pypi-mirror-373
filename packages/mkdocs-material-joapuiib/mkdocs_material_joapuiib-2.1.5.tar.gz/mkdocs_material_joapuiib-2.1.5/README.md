# mkdocs-material-joapuiib
[![Built with Material for MkDocs](https://img.shields.io/badge/Material_for_MkDocs-526CFE?style=for-the-badge&logo=MaterialForMkDocs&logoColor=white)](https://squidfunk.github.io/mkdocs-material/)
[![PyPi](https://img.shields.io/badge/pypi-3775A9?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/mkdocs-material-joapuiib/)

Tema de [MkDocs](https://www.mkdocs.org/) basat en [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
per a la creació de material didàctic.

Podeu veure una demostració del tema a [joapuiib.github.io/mkdocs-material-joapuiib](https://joapuiib.github.io/mkdocs-material-joapuiib/).

## Característiques
Aquest tema inclou les següents característiques:
- Portades per als documents amb la plantilla `document.html`.
- Plantilla `slides.html` per a la creació de presentacions amb [Reveal.js](https://revealjs.com/).
- [Admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/): S'inclouen les alertes `docs`, `spoiler` i `solution`.
- S'habilita per defecte KaTeX per a escriure fórmules matemàtiques.
- Exemple per la traducció dels títols de les alertes (admonitions) al valencià (fitxer `mkdocs.yml`).
- S'ha extés el ressaltat de sintaxi amb [pygments-shell-console](https://github.com/joapuiib/pygments-shell-console/)
    per a ressaltar el prompt de la consola i l'eixida de les comandes de Git.

## Instal·lació
Aquest tema es pot instal·lar a través de pip:

```bash
pip install mkdocs-material-joapuiib
```

Afegeix el següent al teu fitxer de configuració `mkdocs.yml`:

```yaml
theme:
  name: 'material-joapuiib'
```
