#!/usr/bin/env python

#
## mruser
##
## This program provides an interface to retrieve information about Moira users.
## It could also provide the writing functions, but the developer of this software does
## not have access to test that functionality nor is insane enough to set up a test Moira
## server.
#

from pymoira import User
import common
import colorama

def format_user_status(user):
    statuses = {
        0  : ('Registerable',                 'blue',    False),
        1  : ('Active',                       'green',   False),
        2  : ('Half-registered',              'blue',    True ),
        3  : ('Deleted',                      'red',     False),
        4  : ('Non-registerable',              None,     False),
        5  : ('Enrolled -- Registerable',     'cyan',    False),
        6  : ('Enrolled -- Unregisterable',    None,     False),
        7  : ('Half-enrolled',                 None,     False),
        8  : ('Registered -- Kerberos-only',  'yellow',  False),
        9  : ('Active -- Kerberos-only',      'yellow',  False),
        10 : ('Supsended',                    'red',     True ),
    }

    if user.status not in statuses:
        return "Unknown status code (%i)" % user.status

    text, color, bold = statuses[user.status]
    if color: text = common.color_text(text, color)
    if bold : text = common.emph_text(text)

    if user.status in {User.Registerable, User.HalfRegistered}:
        if user.secure:
            text += " (needs secure Account Coupun)"
        else:
            text += " (no Account Coupon needed)"

    return text

def show_info():
    """Handle 'mruser info'."""

    user = User(client, args.user)
    user.loadInfo()

    if user.middle_name:
        realname = "%s %s %s" % (user.first_name, user.middle_name, user.last_name)
    else:
        realname = "%s %s" % (user.first_name, user.last_name)

    common.section_header( "Information about user %s" % common.emph_text(user.name) )
    common.show_fields(
        ('Login name', user.name),
        ('Real name', realname),
        ('Status', format_user_status(user)),
        ('User ID', user.uid),
        ('MIT ID', user.mit_id),
        ('Class', user.user_class),
        ('Shell (Unix)', user.shell),
        ('Shell (Windows)', user.windows_shell),
        ('Comments', user.comments) if user.comments else None,
        ('Sponsor', str(user.sponsor) if user.sponsor else 'None'),
        ('Expires', user.expiration) if user.expiration else None,
        ('Alternate email', user.alternate_email) if user.alternate_email else None,
        ('Alternate phone', user.alternate_phone) if user.alternate_phone else None,
        ('Created', "%s by %s" % (common.last_modified_date(user.created_date), user.created_by)),
        ('Last modified', "%s by %s using %s" % (common.last_modified_date(user.lastmod_datetime), user.lastmod_by, user.lastmod_with)),
    )

def setup_subcommands(argparser):
    """Sets up all the subcommands."""

    subparsers = argparser.add_subparsers()

    parser_info = subparsers.add_parser('info', help = 'Provide the information about the user')
    parser_info.add_argument('user', help = 'The user to inspect')
  
    parser_info.set_defaults(handler = show_info)

if __name__ == '__main__':
    client, args = common.init('mruser', 'Inspect Moira users', setup_subcommands)
    common.main()
