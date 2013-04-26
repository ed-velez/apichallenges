#!/usr/bin/env python
import argparse
import os
import sys
import time
import pyrax

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', metavar='region', default='ORD', choices=['ORD','DFW','LON'], help="Cloud region:e (default: ORD)")
    parser.add_argument('dir', metavar='dir', help="Directory contents to be uploaded")
    parser.add_argument('container', metavar='container', help="Cloud Files container to upload to")
    args = parser.parse_args()

    abs_path = os.path.abspath(args.dir)

    if not os.path.isdir(abs_path):
        raise SystemExit("Error: The directory you provided does not exist.")

    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"), region=args.region)
    cf = pyrax.cloudfiles
    if args.container not in cf.list_containers():
        print "Specified container does not exist and will be created."

    upload_key, total_bytes = cf.upload_folder(abs_path, container=args.container)
    
    print "Total bytes to upload:", total_bytes
    uploaded = 0
    while uploaded < total_bytes:
        uploaded = cf.get_uploaded(upload_key)
        print "\rProgress: %4.2f%%" % ((uploaded * 100.0) / total_bytes),
        sys.stdout.flush()
        time.sleep(1) 

    return

if __name__ == "__main__":
    main()
