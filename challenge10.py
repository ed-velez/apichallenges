#!/usr/bin/env python
import argparse
import os
import sys
import pyrax
import time
import pyrax.exceptions as exc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', metavar='region', default='ORD', choices=['ORD','DFW','LON'], help="Cloud region (default: ORD)")
    parser.add_argument('--flavor', metavar='flavor', default=2, choices=range(2,9), help="Cloud Server Flavor")
    parser.add_argument('--prefix', metavar='prefix', default='node', help="Server name prefix.")
    parser.add_argument("ssh_key", metavar='ssh-key-file',  help="SSH key to configure for root at build")
    parser.add_argument('uuid', metavar='uuid', help="UUID of image to build from")
    parser.add_argument('fqdn', metavar='fqdn', help="fqdn to point to CLB vip")
    args = parser.parse_args()

    pyrax.set_credential_file(os.path.expanduser('~/.rackspace_cloud_credentials'),region=args.region)
    cs = pyrax.cloudservers
    dns = pyrax.cloud_dns

    servers = {}

    with open(args.ssh_key) as f:
        content = f.read()

    files = {"/root/.ssh/authorized_keys": content}

    print "Provided ssh key will be added to /root/.ssh/authorized_keys"

    for i in xrange(0,2):
        server_name = '%s%s' % (args.prefix,str(i+ 1))
        servers[server_name] = cs.servers.create(server_name, args.uuid, args.flavor, files=files)

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
    print "Creating cloud load balancer..."

    clb = pyrax.cloud_loadbalancers

    node_list = [ clb.Node(address=server.networks["private"][0], port=80, condition="ENABLED") 
                        for server in servers.values()]
    vip = clb.VirtualIP(type="PUBLIC")
    lb = clb.create(args.fqdn, port=80, protocol="HTTP", nodes=node_list, virtual_ips=[vip])
    lb = pyrax.utils.wait_until(lb,'status',['ACTIVE', 'ERROR'], interval=15)

    if lb.status == 'ERROR':
        raise SystemExit("ERROR: Error creating load balancer. Exiting...")

    print "Adding health monitor to CLB..."
    lb.add_health_monitor(type="CONNECT", delay=10, timeout=10,
                    attemptsBeforeDeactivation=3)

    lb = pyrax.utils.wait_until(lb,'status',['ACTIVE', 'ERROR'], interval=15)

    if lb.status == 'ERROR':
        raise SystemExit("ERROR: Error adding health monitor. Exiting...")

    print "Adding custom error page to CLB..."
    html = "<html><body>Site down for maintenance!</body></html>"
    lb.set_error_page(html)

    lb = pyrax.utils.wait_until(lb,'status',['ACTIVE', 'ERROR'], interval=15)

    print "Adding DNS record for CLB..."

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
            "data": lb.virtual_ips[0].address,
            "ttl": "300"
            }

    recs = None

    try:
        recs = zone.add_records([a_rec])
    except exc.BadRequest as e:
        print "ERROR: %s - Invalid input." % e
    except exc.DomainRecordAdditionFailed:
        print "ERROR: Record already exists."
    except exception as e:
        print ("ERROR:  %s" % e)

    print "Build complete."

    if recs:
        print "\b====> DNS\n"
        print "%s -> %s" % (lb.virtual_ips[0].address, args.fqdn) 
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
