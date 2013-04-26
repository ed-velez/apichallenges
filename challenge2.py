#!/usr/bin/env python
import os
import sys
import pyrax
import argparse
import time

def progress_monitor(obj):
    attempts = 30
    interval = 15
    i = 0
    while obj.status not in ['ACTIVE','ERROR'] and i < attempts:
        obj.get()
        print "\rProgress: %s%%" % obj.progress,
        sys.stdout.flush()
        time.sleep(15)
        i += 1
    if obj.status == 'ACTIVE':
        print "\rProgress: Complete."
        sys.stdout.flush()
    elif obj.status == 'ERROR':
        obj.delete()
        raise SystemExit("ERROR: Object in ERROR status. Deleting and exiting..")
    else:
        raise SystemExit("ERROR: Taking too long. Exiting...")
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', metavar='region', default='ORD', choices=['ORD','DFW','LON'], help="Cloud region (default: ORD)")
    parser.add_argument('--flavor',metavar='flavor', default=2, choices=range(2,9), help="Flavor ID (default: 2)")
    parser.add_argument('uuid', metavar='uuid', help="UUID of server that you would like cloned")
    args = parser.parse_args()

    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"),region=args.region)
    cs = pyrax.cloudservers

    print "Creating image of server %s..." %  args.uuid
    server = cs.servers.get(args.uuid)
    image_id = server.create_image("Image of " + server.name)
    image = cs.images.get(image_id)
    progress_monitor(image)
    print "Building new server from image. This may take a few minutes..."

    name = "Clone of %s" % server.name
    server = cs.servers.create(name, image_id, args.flavor)
    progress_monitor(server)

    print "\n====> Server Details\n"
    print "ID: %s" % server.id
    print "Name: %s" % name
    print "Admin Password: %s" % server.adminPass
    print "Networks:"
    for key, ips in server.networks.iteritems():
        for ip in ips:
            print "%s%s: %s" % (" "*4, key, ip)

    return

if __name__ == '__main__':
    main()
