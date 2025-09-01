# Functions dealing with text

def linewrap(tokens, prefix="", llen=72):
    """Return string of tokens with lines wrapped at whitespace (generator)."""
    next_line = prefix
    first = True
    for token in tokens:
        tlen = len(token)
        if first:
            next_line += token
            first = False
        elif len(next_line) + tlen >= llen:
            yield next_line
            next_line = prefix + token
        else:            
            next_line += " " + token
    yield next_line
    
