#!/usr/bin/env python
import os
import pyrax

def main():
    pyrax.set_credential_file(os.path.expanduser('~/.rackspace_cloud_credentials'))
    cs = pyrax.cloudservers
    # Ubuntu 12.04 Image
    image_id = '5cebb13a-f783-4f8c-8058-c4182c724ccd'
    # 512M Server
    flavor_id = 2
    # Server name prefix
    prefix = 'web'
    password_dict = {}

    def print_server_details(server):
        print "\nid: %s" % server.id
        print "name: %s" % server.name
        print "adminPass: %s" % password_dict.get(server.id)
        print "networks: %s" % server.networks
        return

    def build_check_callback(server):
        if not server:
            print 'ERROR: One of your servers does not appear to be building properly'
        elif server.status == "ACTIVE":
            print_server_details(server)
        else:
            print "ERROR: Server %s (%s) is in ERROR" % (server.id, server.name)
            print_server_details(server)
        return

    for i in xrange(0,3):
        server = cs.servers.create('%s%s' % (prefix,str(i+ 1)), image_id, flavor_id)
        password_dict[server.id] = server.adminPass
        pyrax.utils.wait_until(server,'status',['ACTIVE','ERROR'],build_check_callback, interval=15, attempts=30)
    print "Your Ubuntu 12.04 512M 3-pack is now building! Server details provided upon build completion. This may take a minute or so..."

    return

if __name__ == "__main__":
    main()
