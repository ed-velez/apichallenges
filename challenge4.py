#!/usr/bin/env python
import argparse
import sys
import time
import pyrax
import os
import pyrax.exceptions as exc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ttl', metavar='ttl', default=300, help="TTL for record (default: 300)")
    parser.add_argument('--comment', metavar='comment', default="", type=str, help="Comment for record")
    parser.add_argument('fqdn', metavar='fqdn', help="FQDN to use for A record")
    parser.add_argument('ip', help="IP address")
    args = parser.parse_args()

    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))
    dns = pyrax.cloud_dns 

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

    print "Adding record to zone: %s" % zone_name

    a_rec = {
            "type": "A",
            "name": args.fqdn,
            "data": args.ip,
            "ttl": args.ttl,
            "comment": '"%s"' % args.comment
            }

    try:
        recs = zone.add_records([a_rec])
    except exc.BadRequest as e:
        print "ERROR: %s - Invalid input." % e
    except exc.DomainRecordAdditionFailed:
        print ("ERROR: Record already exists.")
    except exception as e:
        print ("ERROR:  %s" % e) 
    print "Record successfully added."

    return

if __name__ == "__main__":
    main()
