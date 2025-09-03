from kfp import dsl


def apply_bootstrap(html_body):
    replacements = {
        # "<h1>": '<h1 class="display-4">',
        # "<h2>": '<h2 class="display-5">',
        # "<h3>": '<h3 class="display-6">',
        "<ul>": '<ul class="list-group">',
        "<li>": '<li class="list-group-item">',
        "<code>": '<code class="language-python">',
        # "<code>": '<code class="text-dark px-2 py-1">',
    }
    for key, value in replacements.items():
        html_body = html_body.replace(key, value)
    html_body = f'<div class="container" style="max-width: 800px; margin: auto;">{html_body}</div>'
    return html_body


class Markdown:
    integration = "dsl.Markdown"

    def __init__(self, text):
        self._text = text

    def show(self, title="MAMMOth-commons Markdown"):
        import markdown2
        from mammoth_commons.exports.HTML import HTML

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                details {{
                    border: 1px solid var(--bs-gray-400);
                    border-radius: 0.5rem;
                    padding: 0.2rem;
                    background-color: var(--bs-light);
                    margin-bottom: 1rem;
                }}
                summary {{
                    cursor: pointer;
                    font-weight: bold;
                    color: var(--bs-dark);
                    padding: 0.5rem;
                }}
                summary:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            {apply_bootstrap(markdown2.markdown(self._text, extras=["tables", "fenced-code-blocks", "code-friendly"]))}
            
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">",
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>"
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/default.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
            <script>hljs.highlightAll();</script>
        </body>
        </html>
        """
        HTML(html).show()

    def text(self):
        import markdown2
        from mammoth_commons.exports.HTML import HTML

        return HTML(
            apply_bootstrap(
                markdown2.markdown(
                    self._text, extras=["tables", "fenced-code-blocks", "code-friendly"]
                )
            )
        ).text()

    def export(self, output: dsl.Output[integration]):
        with open(output.path, "w") as f:
            output.name = "result.md"
            f.write(self._text)
