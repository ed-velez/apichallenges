#!/usr/bin/env python
import argparse
import pyrax
import os
import sys
import time
import pyrax.exceptions as exc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', metavar='region', default='ORD', choices=['ORD','DFW','LON'], help="Cloud region (default: ORD)")
    parser.add_argument('--flavor',metavar='flavor', default=2, choices=range(2,9), help="Flavor ID (default: 2)")
    parser.add_argument('uuid', metavar='uuid', help="UUID of image to build from")
    parser.add_argument('fqdn',metavar='fqdn', help="fqdn for server")
    args = parser.parse_args()

    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"),region=args.region)
    cs = pyrax.cloudservers
    dns = pyrax.cloud_dns

    print "Building new server from image. This may take a few minutes..."

    server = cs.servers.create(args.fqdn, args.uuid, args.flavor)
    interval = 15
    while server.status not in ['ACTIVE','ERROR']:
        server.get()
        print "\rProgress: %s%%" % server.progress,
        sys.stdout.flush()
        time.sleep(15)
    if server.status == 'ERROR':
        obj.delete()
        raise SystemExit("ERROR: Object in ERROR status. Deleting and exiting..")

    print
    print "ID: %s" % server.id
    print "Name: %s" % server.name
    print "Admin Password: %s" % server.adminPass
    print "Networks:"
    for key, ips in server.networks.iteritems():
        for ip in ips:
            print "%s%s: %s" % (" "*4, key, ip)

    print "\nAdding DNS record for server..."

    # Find possible zone (accounts for subdomain delegation)
    fqdn_split = str.split(args.fqdn, '.')
    zone_list = [zone.name for zone in dns.list()]
    zone  = None
    for i in xrange(-len(fqdn_split), -1):
        zone_name = '.'.join(fqdn_split[ i:])
        if zone_name in zone_list:
            zone = dns.find(name=zone_name)
            break

    if not zone:
        raise SystemExit("Zone not found for record to added to.")

    a_rec = {
            "type": "A",
            "name": args.fqdn,
            "data": server. accessIPv4,
            "ttl": "300"
            }

    recs = None

    try:
        recs = zone.add_records([a_rec])
    except exc.BadRequest as e:
        raise SystemExit("ERROR: %s - Invalid input." % e)
    except exc.DomainRecordAdditionFailed:
        raise SystemExit("ERROR: Record already exists.")

    if recs:
        print "%s => %s successfully added." % (server.accessIPv4, args.fqdn)

    return

if __name__ == '__main__':
    main()
