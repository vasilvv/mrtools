#
## Shows items owned by different Moira objects
#

import common
import pymoira

def show_ownerships(client, args, owner):
    owned = list(owner.getOwnedObjects(recursive = args.recursive))
    type_headers = (
        (pymoira.Container, 'Windows machine containers'),
        (pymoira.ContainerMembershipACL, 'Windows machine containers ACL'),
        (pymoira.Filesys, 'Lockers'),
        (pymoira.List, 'Lists'),
        (pymoira.Host, 'Machines'),
        (pymoira.Query, 'Queries'),
        (pymoira.Quota, 'Quotas'),
        (pymoira.Service, 'Service'),
        (pymoira.ZephyrClass, 'Zephyr classes'),
    )

    for object_type, header in type_headers:
        displayed = [obj for obj in owned if type(obj) == object_type]
        displayed.sort()
        if displayed:
            common.section_header(header)
            for member in displayed:
                print "* %s" % member.name
            print    # FIXME: this should not be done in case of last entry

