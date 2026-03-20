HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Syntax Highlighted</title>
<style>
body {{ background: #1e1e1e; color: #d4d4d4; font-family: monospace; padding: 1em; }}
pre {{ margin: 0; }}
.kw {{ color: #569cd6; font-weight: bold; }}
.id {{ color: #9cdcfe; }}
.fn {{ color: #dcdcaa; }}
.cls {{ color: #4ec9b0; font-weight: bold; }}
.num {{ color: #b5cea8; }} 
.str {{ color: #ce9178; }}
.fstr {{ color: #ce9178; }}
.cmt {{ color: #6a9955; font-style: italic; }}
.op {{ color: #d4d4d4; }}
.punc {{ color: #ffffff; }}
.paren {{ color: #ffff00; }}
.err {{ color: #f44747; text-decoration: underline wavy; }}
</style>
</head>
<body>
<pre>{content}</pre>    
</body>
</html>
"""

# Colors and formatting used in the HTML template:
# - Keywords: #569cd6 - cornflower blue, bold
# - Identifiers: #9cdcfe - sky blue
# - Function names: #dcdcaa - light khaki
# - Class names: #4ec9b0 - turquoise, bold
# - Numbers: #b5cea8 - sage green
# - Strings: #ce9178 - salmon orange
# - F-strings: #ce9178 - salmon orange
# - Comments: #6a9955 - fern green, italicized
# - Operators: #d4d4d4 - silver gray
# - Punctuation: #ffffff - pure white
# - Parentheses: #ffff00 - bright yellow
# - Errors: #f44747 - sunset red, underlined with a wavy line