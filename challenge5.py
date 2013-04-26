#!/usr/bin/env python
import argparse
import os
import pyrax

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--region', default="ORD", choices=['ORD','DFW','LON'], help="Cloud region (default: ORD)")
    parser.add_argument('--flavor', type=int, default=1, choices=range(1,7), help="Flavor ID (default: 1)")
    parser.add_argument('--volume', default=1, help="Size of disk in GB (default:1, Max:150)")
    parser.add_argument('user', help="Database User")
    parser.add_argument('password', help="Database Password")
    parser.add_argument('database', metavar='database-name', help="Database Name")
    parser.add_argument('instance', metavar='instance-name', help="Instance name")
    args = parser.parse_args()

    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"),region=args.region)
    cdb = pyrax.cloud_databases

    db_dict = [{"name": args.database}]
    user_dict = [
                    {
                        "name": args.user,
                        "password": args.password,
                        "databases": db_dict
                    }
                ]
    print "Building database instance. This may take a few minutes..."
    instance = cdb.create(args.instance, flavor=args.flavor, volume=args.volume, users=user_dict, databases=db_dict)
    instance = pyrax.utils.wait_until(instance,'status',['ACTIVE','ERROR'], interval=15)
    if instance.status == 'ACTIVE':
        print "Instance built successfully."
    else:
        raise SystemExit("ERROR: Instance build was unsuccessful")

    return

if __name__ == "__main__":
    main()
