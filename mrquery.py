#!/usr/bin/python

#
## mrquery
##
## This program provides an interface to send arbitrary queries to Moira.
#

import common
import re, argparse, json

import pymoira

class QueryInfo:
    def __init__(self, name):
        info, = client.query('_help', (name,))

        # FIXME: the format Moira server uses is horrible.
        # There should be a saner way to do this
        description = ' '.join(info)
        match = re.match( r"\s*(\S+), (\S+) \((.+)\)( => (.+))?", description )
        if not match:
            raise pymoira.UserError( "Unable to parse the Moira query description" )

        self.name, self.shortname, inputs, output_whole, outputs = match.groups()
        self.inputs = inputs.split(' ')
        self.outputs = outputs.split(' ') if outputs else []

def setup_arguments(argparser):
    """Sets up the arguments."""

    argparser.add_argument('query', help = 'The Moira query name to execute')
    argparser.add_argument('arg', nargs = '*', help = 'The arguments to the query')

    argparser.add_argument('-j', '--json', action = 'store_true', help = 'Output the results of the query in JSON')

def do_query():
    """Runs the query and returns the result with query information."""

    info = QueryInfo(args.query)
    if len(info.inputs) != len(args.arg):
        raise pymoira.UserError( "Query argument count mismatch (%i expected, %i supplied)" % (len(info.inputs), len(args.arg)) )

    output = client.query(info.name, args.arg)
    result = []
    for row in output:
        new_row = {}
        if len(row) != len(info.outputs):
            raise pymoira.UserError("Moira server returned unexpected amount of columns in a row")
        for name, value in zip(info.outputs, row):
            new_row[name] = value
        result.append(new_row)
    return result, info

def show_help():
    try:
        query = args.arg[0]
    except IndexError:
        common.error( "Query name was not specified" )
        return

    info, = client.query('_help', (query,))
    print ' '.join(info).strip()

def show_queries_list():
    queries = client.query('_list_queries', ())
    for query, in queries:
        print query

def show_user_list():
    users = client.query('_list_users', ())
    for user in users:
        print "%s from %s %s, since %s %s" % user

def handle_query():
    """Outputs the results of the query or an error message."""

    if args.json:
        try:
            result, info = do_query()
            print json.dumps({ 'status' : 'ok', 'result' : result })
        except pymoira.BaseError as e:
            print json.dumps({ 'status' : 'error', 'message' : str(e) })
    else:
        try:
            # Those are not real queries, and QueryInfo() would fail for them
            if args.query == '_help':
                show_help()
                return
            if args.query == '_list_queries':
                show_queries_list()
                return
            if args.query == '_list_users':
                show_user_list()
                return

            result, info = do_query()
            for row in result:
                fields = [ (field_name, row[field_name]) for field_name in info.outputs ]
                common.show_fields(*fields)
                print ""
        except pymoira.BaseError as err:
           common.error(err)

if __name__ == '__main__':
    client, args = common.init('mrquery', 'Send raw queries to Moira', setup_arguments)
    handle_query()
