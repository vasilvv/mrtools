#!/usr/bin/env python

#
## mrfilesys
##
## This program provides an interface to retrieve information about Moira filesystems.
## It could also provide the writing functions, but the developer of this software does
## not have access to test that functionality nor is insane enough to set up a test Moira
## server.
#

from pymoira import Filesys
import common

def show_info():
    """Handle 'mrfilesys info'."""

    fs = Filesys(client, args.filesys)
    fs.loadInfo()
    show_info_for_fs(fs)
    # FIXME: here, if fs is FSGROUP this should expand all included filesystems
    # Unfortunately, for some reasons the query to get filesystems in a group
    # is not publicly accessible, so I am unable to test it.

def show_info_for_fs(fs):
    """Outputs an information about a filesystem. Used by 'mrfilesys info'
    to show info about filesytems and FS groups."""

    common_fields = (
        ('Description', fs.description),
        ('Owner (user)', fs.owner_user),
        ('Owner (list)', fs.owner_group),
        ('Type code', fs.locker_type),
        ('Quota', "%i megabytes" % (fs.quota / 1000) if fs.quota else False ),
        ('Last modified', "%s ago by %s using %s" % (common.last_modified_date(fs.lastmod_datetime), fs.lastmod_by, fs.lastmod_with))
    )

    if fs.quota:
        common_fields += ( ('Quota last modified', "%s ago by %s using %s" % (common.last_modified_date(fs.quota_lastmod_datetime), fs.quota_lastmod_by, fs.quota_lastmod_with) ), )

    if fs.type == 'AFS':
        common.section_header( 'AFS filesystem %s' % common.emph_text(fs.label) )
        common.show_fields( *((
            ('Cell', fs.machine),
            ('Location', fs.name),
            ('Mount point', fs.mountpoint),
        ) + common_fields) )
    else:
        common.section_header( 'Filesystem %s' % common.emph_text(fs.label) )
        common.show_fields( *((
            ('Filesystem type', fs.type),
            ('Machine', fs.machine),
            ('Location/Name', fs.name),
            ('Mount point', fs.mountpoint),
            ('Description', fs.description),
        ) + common_fields) )

def setup_subcommands(argparser):
    """Sets up all the subcommands."""

    subparsers = argparser.add_subparsers()

    parser_info = subparsers.add_parser('info', help = 'Provide the information about the filesystem')
    parser_info.add_argument('filesys', help = 'The filesystem to inspect')
  
    parser_info.set_defaults(handler = show_info)

if __name__ == '__main__':
    client, args = common.init('mrfilesys', 'Inspect Moira filesystems', setup_subcommands)
    common.main()
