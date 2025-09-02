"""Templates"""
WEB_TEMPLATE = """
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
