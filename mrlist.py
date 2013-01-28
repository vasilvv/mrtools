#!/usr/bin/python

#
## mrlist
##
## This program provides an interface to read and manipulate Moira lists.
#

import common
import re, argparse

import pymoira
from pymoira import List, ListMember, ListTracer

def resolve_member(name, default_to_string):
    """Resolve the list member name."""
    
    member = ListMember.resolveName(client, name)
    if member:
        return member
    if re.match( "^[a-z0-9_]{3,8}.(root|extra|dbadmin)$", name ):
        return ListMember( client, MoiraListMember.Kerberos, name + '@ATHENA.MIT.EDU' )
    
    if default_to_string:
        return ListMember( client, MoiraListMember.String, name )
    else:
        return None

def output_member_list(members, hook = None):
    """Output the list of list members."""
    
    members = list(members)
    members.sort()
    type_headers = (
        ('USER', 'Users'),
        ('KERBEROS', 'Kerberos principals'),
        ('LIST', 'Sublists'),
        ('STRING', 'String entries (includes non-MIT emails)'),
        ('MACHINE', 'Machines'),
    )
    for list_type, header in type_headers:
        displayed = [member for member in members if member.mtype == list_type]
        if displayed:
            common.section_header(header)
            for member in displayed:
                if hasattr(member, 'tag') and member.tag:
                    print "* %s [%s]" % (member.name, member.tag)
                else:
                    print "* %s" % member.name
                if hook:
                    hook(member)
            print    # FIXME: this should not be done in case of last entry

def show_info():
    """Handle 'mrlist info'."""

    mlist = List(common.client, args.list)
    mlist.loadInfo()

    common.section_header("Information about list %s" % common.emph_text(mlist.name) )
    common.show_fields(
        ('Description', mlist.description),
        ('Active', mlist.active),
        ('Public', mlist.public),
        ('Visible', not mlist.hidden),
        ('Mailing list', mlist.is_mailing),
        ('AFS group', "GID #%s" % mlist.gid if mlist.is_afsgroup else mlist.is_afsgroup),
        ('Unix group', mlist.is_nfsgroup) if mlist.is_afsgroup else None,
        ('Mailman list', "On server %s" % mlist.mailman_server if mlist.is_mailman_list else mlist.is_mailman_list),
        ('Owner', "%s %s" % (mlist.owner_type.lower(), mlist.owner_name) ),
        ('Membership ACL', "%s %s" % (mlist.memacl_type.lower(), mlist.memacl_name) if mlist.memacl_type != 'NONE' else 'None' ),
        ('Last modified', "%s ago by %s using %s" % (common.last_modified_date(mlist.lastmod_datetime), mlist.lastmod_by, mlist.lastmod_with)),
    )

def show_inverse():
    """Handle 'mrlist inverse'."""

    member = resolve_member(args.member, False)
    if not member:
        print "Impossible to determine the type of a member. Please specify it explicitly by prefixing the member with type, seperated by colon, like this: string:test@example.com"
        return

    memberships = list( member.getMemberships(recursive = args.recursive) )
    memberships.sort()
    common.section_header( "Memberships of %s" % common.emph_text( str(member) ) )
    for mlist in memberships:
        print "* %s" % mlist.name

def show_members():
    """Handle 'mrlist members'."""

    mlist = List(common.client, args.list)
    members = mlist.getExplicitMembers(tags = args.verbose)
    output_member_list(members)

def expand_list():
    """Handle 'mrlist expand'."""
    
    mlist = List(common.client, args.list)
    if args.server_side:
        members = mlist.getAllMembers(server_side = True, include_lists = args.include_lists)
        if args.trace:
            print "Server-side tracing is not supported"
            return
    else:
        if args.trace:
            tracer = ListTracer(mlist)
            members = tracer.members
            inaccessible = tracer.inaccessible
            lists = tracer.lists

            # List tracer includes lists by default
            if not args.include_lists:
                    members = [member for member in members if member.mtype != ListMember.List]
        else:
            members, inaccessible, lists = mlist.getAllMembers(include_lists = args.include_lists)
        
        print "List %s contains %i members, found by expanding %i nested lists (access denied to %i)" % (mlist.name, len(members), len(lists), len(inaccessible))
    
    if args.trace:
        def show_trace(member):
            pathways = tracer.trace(member)
            if len(pathways) > 3 and not args.verbose:
                print "   [%i inclusion pathways]" % len(pathways)
            else:
                for pathway in pathways:
                    print "   - " + " -> ".join( pathway + (member.name,) )
        
        output_member_list(members, show_trace)
    else:
        output_member_list(members)

def add_member():
    """Handle 'mrlist add'."""

    mlist = List(client.client, args.list)
    member = resolve_member(args.member, True)
    mlist.addMember(member)
    print "Added %s to list %s" % (common.emph_text( str(member) ), common.emph_text( mlist.name ))

def remove_member():
    """Handle 'mrlist remove'."""

    mlist = List(client.client, args.list)
    member = resolve_member(args.member, True)
    mlist.removeMember(member)
    print "Removed %s from list %s" % (common.emph_text( str(member) ), common.emph_text( mlist.name ))

def rename_list():
    """Handle 'mrlist rename'."""

    mlist = List(client, args.old_name)
    mlist.rename(args.new_name)
    print "Successfully renamed %s to %s" % (args.old_name, args.new_name)

def setup_subcommands(argparser, subparsers):
    """Sets up all the subcommands."""

    parser_add = subparsers.add_parser('add', help = 'Add a member to the list')
    parser_add.add_argument('list', help = 'The list to which the member will be added')
    parser_add.add_argument('member', help = 'The member to add to the list')

    parser_expand = subparsers.add_parser('expand', help = 'Recursively expands all sublists in the specified list')
    parser_expand.add_argument('list', help = 'The name of the list to show information about')
    parser_expand.add_argument('-l', '--include-lists', action = 'store_true', help = 'Display all the nested lists')
    parser_expand.add_argument('-s', '--server-side', action = 'store_true', help = argparse.SUPPRESS)    # for debug purposes
    parser_expand.add_argument('-t', '--trace', action = 'store_true', help = 'Show the paths through which the given user is included')
    parser_expand.add_argument('-v', '--verbose', action = 'store_true', help = 'Do not hide the inclusion pathways even if there are many of them')

    parser_info = subparsers.add_parser('info', help = 'Provide the information about the list')
    parser_info.add_argument('list', help = 'User, Kerberos principal or ')

    parser_inverse = subparsers.add_parser('inverse', help = 'Show the lists into which certain member is included')
    parser_inverse.add_argument('member', help = 'The name of the list to show information about')
    parser_inverse.add_argument('-r', '--recursive', action = 'store_true', help = 'Show the lists into which a member is included through other lists')

    parser_members = subparsers.add_parser('members', help = 'Shows the members explicitly included into the list')
    parser_members.add_argument('list', help = 'The name of the list to show information about')
    parser_members.add_argument('-v', '--verbose', action = 'store_true', help = 'Output explicitly the members of the list')

    parser_remove = subparsers.add_parser('remove', help = 'Remove a member from the list')
    parser_remove.add_argument('list', help = 'The list from which the member will be removed')
    parser_remove.add_argument('member', help = 'The member to remove from the list')

    parser_rename = subparsers.add_parser('rename', help = 'Rename a list')
    parser_rename.add_argument('old_name')
    parser_rename.add_argument('new_name')

    parser_add.set_defaults(handler = add_member)
    parser_expand.set_defaults(handler = expand_list)
    parser_info.set_defaults(handler = show_info)
    parser_inverse.set_defaults(handler = show_inverse)
    parser_members.set_defaults(handler = show_members)
    parser_remove.set_defaults(handler = remove_member)
    parser_rename.set_defaults(handler = rename_list)

if __name__ == '__main__':
    client, args = common.init('mrlist', 'Inspect and modify Moira lists', setup_subcommands)
    common.main()
