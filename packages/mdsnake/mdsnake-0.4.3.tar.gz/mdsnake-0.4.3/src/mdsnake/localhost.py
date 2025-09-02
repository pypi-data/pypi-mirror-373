"""Libraries"""
import markdown
from flask import Flask, render_template_string

from .templates import WEB_TEMPLATE

app = Flask(__name__)

"""Functions"""
@app.route("/")
def index():
    """
    Localhost Index
    """
    markdown_text = app.config.get("MARKDOWN_TEXT", "")
    rendered = markdown.markdown(markdown_text, extensions=["fenced_code", "tables"])
    return render_template_string(WEB_TEMPLATE, content=rendered)

def run_localhost(md: str):
    """
    Run a localhost
    :param md:
    """
    app.config["MARKDOWN_TEXT"] = md
    app.run(debug=True, use_reloader=False)
