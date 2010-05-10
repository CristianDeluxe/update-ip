import sys
import os
import tempfile
from optparse import OptionParser

from update_ip import updater

VERSION = '0.1'

def main():
    # Parse command line options
    usage = "usage: %prog [options] SERVICE"
    parser = OptionParser(usage=usage, version='%prog version ' + VERSION)
    parser.add_option(
        "-d", "--domains",
        dest="domains",
        default=None,
        help="Designate specific domains to update, separated by commas",
        metavar="DOMAINS")
    parser.add_option(
        "-f", "--file",
        dest="ip_file",
        default=os.path.join(tempfile.gettempdir(), 'public_ip'),
        help="Designate the local file used to store your current IP address",
        metavar="FILE")
    parser.add_option(
        "-u", "--username",
        dest="username",
        default=None,
        help="Designate the username to use with the selected DNS service",
        metavar="USER")
    parser.add_option(
        "-p", "--password",
        dest="password",
        default=None,
        help="Designate the password to use with the selected DNS service",
        metavar="PASS")
    parser.add_option(
        "-q", "--quiet",
        action="store_true",
        dest="quiet",
        default=False,
        help="Hide all status messages")
    (options, args) = parser.parse_args()
    
    if not args:
        sys.stderr.write('Please provide a service name to use for the'
                         'update.\n')
        sys.exit(1)
    
    if not args[0] in updater.get_list():
        # TODO: Find out why the join call below doesn't work
        sys.stderr.write('That is not a valid service name. Please choose '
                         'from: %s\n' % ','.join(updater.get_list()))
        sys.exit(1)
    
    service_class = updater.get_service()
    service = service_class(options.get('username'), options.get('password'))
    
    # Run the update with the options provided
    try:
        ip_updater = updater.IPUpdater(service,
                                       options.get('ip_file'),
                                       options.get('quiet'))
        ip_updater.update(options.get('domains'))
    except updater.InvalidIPError, e:
        sys.stderr.write(e)
        sys.exit(1)

if __name__ == '__main__':
    main()