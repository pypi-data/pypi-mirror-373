# -*- fill-column: 72 -*-
"""Do sane SIGINT and SIGPIPE handling in a decorator.

Other than is traditional (and reasonable) in Unix programs, Python
makes a big fuss when it catches a SIGINT or SIGPIPE. That includes a
stacktrace and ugly error messages for totally normal conditions, in
which the apppropriate reaction is nothing but "shut TF up and exit".

But not only is Python's default handler for these signals so
over-excited; even if you catch the exception and end the program, an
unwanted message to stderr still crops up. You have to suppress that by
explicitly closing sys.stderr -- only then Python shuts TF up.

Stupid, stupid Python! This is the more aggravating as Python usually
makes all the right choices, much more so than many other languages.
*sigh*

This decorator repairs that. Wrap it around your main() and be set.

"""

def sanesighandler(func):
    """Decorator: exit the program silently on SIGINT and SIGPIPE."""
    import sys
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            # get the prompt nicely on a fresh new line, not after a ^C
            print(file=sys.stderr)
            sys.stderr.close()
            sys.exit(130)
        except BrokenPipeError:
            sys.stderr.close()
            sys.exit(141)
    return wrapper


def exit_on_error(func):
    """Decorator: exit the program with error message on exception."""
    import os
    import sys

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            sys.exit(f"{os.path.basename(sys.argv[0])}: {e}")
    return wrapper
