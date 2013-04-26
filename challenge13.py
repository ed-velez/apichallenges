#!/usr/bin/env python
import pyrax
import argparse 
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', metavar='region', default='ORD', choices=['ORD','DFW','LON'], help="Cloud region (default: ORD)")
    args = parser.parse_args()

    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"),region=args.region)
    cs = pyrax.cloudservers
    cf = pyrax.cloudfiles
    cdb = pyrax.cloud_databases
    cnw = pyrax.cloud_networks
    cbs = pyrax.cloud_blockstorage

    print "Delete all CBS Volumes..."

    for vol in cbs.list():
        try:
            vol.delete(force=True)
        except:
            print "The API lies...volume deleted."
            pass

    print "Deleting all Cloud Servers..."

    for server in cs.servers.list():
            server.delete()

    print "Deleting all Custom Images..."

    for image in cs.list_snapshots():
        image.delete()

    print "Deleting all Cloud Files Containers and Objects..."

    for cont in cf.get_all_containers():
        cont.delete_all_objects()
        cont.delete()

    print "Deletings all Databases..."

    for db in cdb.list():
        db.delete()

    print "Deleting all Networks..."

    for network in cnw.list():
        if network.id not in ['00000000-0000-0000-0000-000000000000',
                                '11111111-1111-1111-1111-111111111111']:
            network.delete()


if __name__ == '__main__':
    main()
