#!/usr/bin/env python
import pyrax
import argparse
import os
import sys
from urlparse import urlparse
import pyrax.exceptions as exc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', metavar='region',  default='ORD', choices=['ORD','DFW','LON'], help="Cloud region (default: ORD)")
    parser.add_argument('--cdn-ttl', metavar='cdn-ttl', dest='cdnttl', default=259200, type=int, help="CDN container TTL in seconds (default: 259200)")
    parser.add_argument('--dns-ttl', metavar='dns-ttl', dest='dnsttl', default=3600, type=int, help="DNS TTL in seconds (default: 259200)")
    parser.add_argument('--enable-log', action='store_true', help="Enable CDN log retention")
    parser.add_argument('container', metavar='container', help="Container name")
    parser.add_argument('fqdn', metavar='fqdn', help='FQDN to point to container')
    args = parser.parse_args()

    index_page = 'index.html'
    page_data = args.fqdn

    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))
    dns = pyrax.cloud_dns
    cf = pyrax.cloudfiles

    # Check container
    if args.container in cf.list_containers():
        raise SystemExit("ERROR: Specified container already exists.")

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
        raise SystemExit("ERROR: Zone not found for record to added to.")

    cont = cf.create_container(args.container)
    print "Container created."

    cf.make_container_public(args.container, ttl=args.cdnttl)
    
    cont = cf.get_container(args.container)
    dest = urlparse(cont.cdn_uri).netloc

    cont.set_web_index_page(index_page)
    cont.store_object(index_page, page_data, content_type='text/html')
    print "Index Page: %s" % index_page
    print "Page Data: %s" % page_data

    cname = {
            "type": "CNAME",
            "name": args.fqdn,
            "data": dest,
            "ttl": args.dnsttl
            }

    recs = None

    try:
        recs = zone.add_records([cname])
    except exc.DomainRecordAdditionFailed:
        print "ERROR: Record already exists."

    if recs:
        print "CNAME record created for CDN."
        print "%s => %s" % (dest, args.fqdn)

    return

if __name__ == '__main__':
    main()
