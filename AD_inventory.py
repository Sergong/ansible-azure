#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''


Example dynamic inventory script which queries active directory.


Likely to need modification for each environment as there are likely
to be different versions of active directory in use needing different
connection parameters.


To use, create a configuration file in users's home dir
called .ansible_inventory.cfg


must contain a [domain] section
and then settings for the following values
domain_controller
connect_to_dc_with_ssl (either True or False)
query_domain
query_user
query_pass


'''


# import class and constants
from ldap3 import Server, Connection, ALL, NTLM, Tls
import json
import ssl
import pprint
import re
import ConfigParser, os


config = ConfigParser.ConfigParser()
user_dir = os.path.expanduser("~")
config.read(user_dir + '/.ansible_inventory.cfg')


domain_controller = config.get('domain', 'domain_controller')
connect_to_dc_with_ssl= config.getboolean('domain', 'connect_to_dc_with_ssl')
query_domain =  config.get('domain', 'query_domain')
query_user =  config.get('domain', 'query_user')
query_cred = config.get('domain', 'query_pass')


user = query_domain + "\\" + query_user


# define the server and the connection


# TODO see if not doing get_info speeds things up
server = Server(domain_controller, use_ssl=connect_to_dc_with_ssl, get_info='ALL')


# TODO remove debug statements
# print "showing server information"
# print (server.info)




# TODO determine if it is quicker to use auto_bind=True
#conn = Connection(server, user="playnetwork.com\\ldapusr", password=ldappwd, authentication=NTLM, auto_bind=True)


conn = Connection(server, user=user, password=query_cred, authentication=NTLM)


conn.open()
conn.bind()


# conn.entries
# print(conn)
conn.search('CN=Computers, DC=subdomain, DC=yourorg, DC=yourcompany, DC=com', '(objectclass=computer)', attributes=["name","OperatingSystem"])


#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint (conn.response)


# print conn.entries


# generate list of all servers (replace 'HOST' with something that matches machines you want to be part of inventory
names = []
for x in conn.response:
    atts = x['attributes']
    if 'operatingSystem' in atts:
         if atts["operatingSystem"] == 'Windows Server 2012 R2 Standard':
             if re.match('HOST', atts['name'] ):
                names.append(atts['name'])


# TODO add group.  This ought to be doable via a server naming convention


# TODO add _meta for speed as mentioned here: http://docs.ansible.com/ansible/developing_inventory.html


# TODO add vars


conn.unbind()


hosts = {}
hosts['hosts'] = names
var = {'a':True}


export = {}
export['main_group'] = hosts
export['main_group_win'] = hosts
#export['vars'] = var