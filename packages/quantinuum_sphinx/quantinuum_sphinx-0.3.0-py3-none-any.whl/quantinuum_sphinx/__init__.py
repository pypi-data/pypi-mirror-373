from pathlib import Path

from sphinx.application import Sphinx


def setup(app: Sphinx):
    app.add_html_theme("quantinuum_sphinx", str(Path(__file__).resolve().parent))
    app.add_js_file("injectNav.global.js")
    app.add_js_file("syncTheme.global.js")
    app.add_css_file("styles/quantinuum-sphinx.css")
    app.add_css_file("styles/quantinuum-ui-tailwind.css")
    app.add_css_file("styles/quantinum-ui-tokens.css")
