# table templates and associated functions

templates = dict(
    minimal="""
0000000
0000000
0000000
0000000
0000000
0000000
0000000""",
    columns="""
0000000
0 | | 0
0-|-|-0
0 | | 0
0000000
0 | | 0
0000000""",
    full="""
.-----.
| | | |
|=====|
| | | |
|-+-+-|
| | | |
.-----.""",
    heads="""
0000000
0     0
0- - -0
0     0
0000000
0     0
0000000""",
    box="""
╒═╦═╤═╕
│ ║ │ │
╞═╬═╪═╡
│ ║ │ │
├─╫─┼─┤
│ ║ │ │
╘═╩═╧═╛""",
    markdown="""
0000000
| | | |
|-|-|-|
| | | |
0000000
| | | |
0000000""",
)

example_data = [
    ["(O:O)", "col 1", "col 2", "col 3"],
    ["row 1", "cell 12", "cell 13", "cell 14"], 
    ["row 2", "cell 22", "cell 23", "cell 24"], 
    ["row 3", "cell 32", "cell 33", "cell 34"], 
]

def template_names():
    """Return the available template name, in alphabetical order."""
    return sorted(templates.keys())


def store_template(name, template, replace=False):
    """Store a table template for later use."""
    # Check table parameters before storing.
    template_params(template)
    if name in templates and not replace:
        raise ValueError("template {} already exists".format(repr(name)))
    templates[name] = template


def remove_template(name, mustexist=True):
    """Remove a stored table template."""
    global templates
    try:
        del templates[name]
    except KeyError:
        if mustexist:
            raise KeyError("template {} does not exist".format(repr(name)))


def get_template(name):
    if name is None:
        return None
    try:
        return templates[name]
    except KeyError:
        raise KeyError("not a valid template name: {}".format(repr(name)))


def template_params(template):
    """Make a table parameter set out of a template."""
    def zero(*args):
        return ["" if char == "0" else char for char in args]

    # If a line ends with blanks, this can confuse the reader, as well as
    # the author and maybe even a text editor. To avoid that, a template
    # line may end with a guard character ";", which is then stripped from
    # the line.
    tl = [l.rstrip(";") for l in template.split("\n") if l]
    if len(tl) != 7:
        raise ValueError("template must have 7 lines, not {}"
                         .format(len(tl)))
    for i, l in enumerate(tl):
        if len(l) != 7:
            raise ValueError("template line {} must be 7 chars long, but is {}"
                             .format(i, len(l)))
    return dict(
        corner=zero(tl[0][0], tl[0][6], tl[6][0], tl[6][6]),
        border=zero(tl[0][1], tl[1][0], tl[1][6], tl[6][1]),
        hsep=zero(tl[1][2], tl[1][4]),
        vsep=zero(tl[2][1], tl[4][1]),
        tb_cross=zero(tl[0][2], tl[0][4]),
        lb_cross=zero(tl[2][0], tl[4][0]),
        rb_cross=zero(tl[2][6], tl[4][6]),
        bb_cross=zero(tl[6][2], tl[6][4]),
        hl_cross=zero(tl[2][2], tl[2][4]),
        nl_cross=zero(tl[4][2], tl[4][4]),
    )

# EOF
