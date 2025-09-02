"""Libraries"""
import markdown
from flask import Flask, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Markdown Preview</title>
</head>
<body>
    {{ content|safe }}
</body>
</html>
"""

@app.route("/")
def index():
    """
    Index webpage
    """
    markdown_text = app.config.get("MARKDOWN_TEXT", "")
    rendered = markdown.markdown(markdown_text, extensions=["fenced_code", "tables"])
    return render_template_string(TEMPLATE, content=rendered)

def run(md: str):
    """
    Run a localhost Flask server to preview markdown.
    :param md: The markdown text as a string
    """
    app.config["MARKDOWN_TEXT"] = md
    app.run(debug=True, use_reloader=False)
