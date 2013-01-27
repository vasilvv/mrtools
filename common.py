#
## mrtools shared code
#

import datetime, colorama, argparse, sys
import pymoira

mrtools_version = '0.1'

def get_version(program):
    """Return the displayable version of the program"""

    return "%s from mrtools %s" % (program, mrtools_version)

def section_header(text):
    """Output a section header"""

    print "---- %s ----" % text

def emph_text(text):
    """Make a text bold, unless the text formatting is disabled."""

    if not args.no_color:
        return colorama.Style.BRIGHT + text + colorama.Style.RESET_ALL
    else:
        return text

def color_text(text, color_name):
    """Make the text of a specific color, unless the text formatting is disabled."""

    if not args.no_color:
        return colorama.Fore.__dict__[color_name.upper()] + text + colorama.Style.RESET_ALL
    else:
        return text

def show_fields(*fields):
    """Output the {field label -> field value} dictionary. Does the alignment
    and formats certain specific types of values."""

    fields = filter( lambda x: x, fields )
    target_len = max( len(name) for name, value in fields ) + 2
    for name, value in fields:
        line = name + ':' + " " * (target_len - len(name))
        if type(value) == bool:
            line += color_text("Yes", 'green') if value else color_text("No", 'red')
        else:
            line += str(value)
        print line

def plural(num, one, many):
    """Convenience function for displaying a numeric value, where the attached noun
    may be both in singular and in plural form."""

    return "%i %s" % (num, one if num == 1 else many)

def last_modified_date(when):
    """Formats the last modification date in a human-readable format."""

    # FIXME: this should use the Moira server timezone
    delta = datetime.datetime.now() - when
    if delta.days > 0:
        if delta.days > 365:
            return "%.2f years" % (delta.days / 365.25)
        else:
            return plural(delta.days, "day", "days")
    else:
        if delta.seconds > 3600:
            hours = delta.seconds / 3600
            minutes = (delta.seconds - hours * 3600) / 60
            return plural(hours, "hour", "hours") + ' ' + plural(minutes, "minute", "minutes")
        elif delta.seconds > 60:
            return plural(delta.seconds / 60, "minute", "minutes")
        else:
            return plural(delta.seconds, "second", "seconds")

# ------------------------------------------------------------------------------

def init(name, description, subparsers_generator):
    """Parses the command-line arguments, initializes the client and then returns both the client
    and the arguments."""

    global client, args

    argparser = argparse.ArgumentParser(description = description)
    argparser.add_argument('--version', action = 'version', version = get_version(name), help = 'Output program version and quit')
    argparser.add_argument('--no-color', action = 'store_true', help = 'Disable the color output')
    argparser.add_argument('-a', '--anonymous', action = 'store_true', help = 'Do not log into Moira')
    subparsers = argparser.add_subparsers()
    
    if subparsers_generator:
        subparsers_generator(argparser, subparsers)
    
    args = argparser.parse_args()
    
    try:
        client = pymoira.Client()
        if not args.anonymous:
            client.authenticate(name)

        return client, args
    except pymoira.BaseError as err:
        sys.stderr.write( "%s\n" % err )

def main():
    """Executes the relevant subcommand."""

    try:
        args.handler()
    except pymoira.BaseError as err:
        sys.stderr.write( "%s\n" % err )
