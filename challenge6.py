#!/usr/bin/env python
import argparse
import os
import pyrax
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', metavar='region',  default='ORD', choices=['ORD','DFW','LON'], help="Cloud region (default: ORD)")
    parser.add_argument('--ttl', metavar='ttl', default=259200, type=int, help="CDN container TTL in seconds (default: 259200)")
    parser.add_argument('--enable-log', action='store_true', help="Enable CDN log retention")
    parser.add_argument('container', metavar='container', help="Cloud Files container name. Container will be created if it does not exist")
    
    args = parser.parse_args()

    pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"),region=args.region)
    cf = pyrax.cloudfiles 

    if args.container not in cf.list_containers():
        print "Container does not exist and will be created."

    # if container already exists, create_container will still return existing container.
    cont = cf.create_container(args.container)

    cf.make_container_public(args.container, ttl=args.ttl)
    cf.set_cdn_log_retention(cont, args.enable_log)
    cont = cf.get_container(args.container)

    print "Container CDN Enabled."
    print "name:", cont.name
    print "ttl:", cont.cdn_ttl
    print "uri:", cont.cdn_uri
    print "ssl uri:", cont.cdn_ssl_uri
    print "streaming uri:", cont.cdn_streaming_uri
    print "ios uri:", cont.cdn_ios_uri
    print "log retention:", cont.cdn_log_retention

    return

if __name__ == "__main__":
    main()
