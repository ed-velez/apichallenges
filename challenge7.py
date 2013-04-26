#!/usr/bin/env python
import argparse
import os
import sys
import pyrax
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', metavar='region', default='ORD', choices=['ORD','DFW','LON'], help="Cloud region (default: ORD)")
    parser.add_argument('--flavor', metavar='flavor', default=2, choices=range(2,9), help="Flavor ID (default: 2)")
    parser.add_argument('--prefix', metavar='prefix', default='node', help="Server name prefix.")
    parser.add_argument('uuid', metavar='uuid', help="UUID of image to build from.")
    args = parser.parse_args()

    pyrax.set_credential_file(os.path.expanduser('~/.rackspace_cloud_credentials'),region=args.region)
    cs = pyrax.cloudservers

    servers = {}

    for i in xrange(0,2):
        server_name = '%s%s' % (args.prefix,str(i+ 1))
        servers[server_name] = cs.servers.create(server_name, args.uuid, args.flavor)

    print "Building servers. This may take a few minutes..."

    building = []

    while 1:
        building = [server.status for server in servers.values() if server.status not in ['ACTIVE', 'ERROR' ]]
        progress = 0
        for server in servers.values():
            progress += server.progress

        percent = float(progress)/float(len(servers))
        print "\rProgress: %.1f%%" % percent,
        sys.stdout.flush()
        if not building:
            break

        map(lambda x: x.get(), servers.values())
        time.sleep(15)

    print "\nServer builds complete."
    print "Creating cloud load balancer."

    clb = pyrax.cloud_loadbalancers

    node_list = [ clb.Node(address=server.networks["private"][0], port=80, condition="ENABLED") 
                        for server in servers.values()]

    vip = clb.VirtualIP(type="PUBLIC")
    lb = clb.create("example_lb", port=80, protocol="HTTP", nodes=node_list, virtual_ips=[vip])

    print "Build complete."
    print "\n====> CLB Details\n"
    print "Name:", lb.name
    print "ID:", lb.id
    print "Status:", lb.status
    print "Virtual IPs:", lb.virtual_ips[0].address
    print "Algorithm:", lb.algorithm
    print "Protocol:", lb.protocol

    print "\n====> Server Details"
    for server in sorted(servers.values(), key=lambda x: x.name):
        print "\nName: %s" % server.name
        print "ID: %s" % server.id
        print "Admin Password: %s" % server.adminPass
        print "Networks:"
        for key, ips in server.networks.iteritems():
            for ip in ips:
                print "%s%s: %s" % (" "*4, key, ip)

    return

if __name__ == "__main__":
    main()
