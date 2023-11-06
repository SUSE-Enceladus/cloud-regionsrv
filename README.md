Region Service
==============

The Region Service is a REST service that integrates with Apache. It will
provide information about Update Servers in a cloud environment based on
a regionHint or the IP address of the client requesting the information.

The service is implemented in Python using the [Flask microframework](http://flask.pocoo.org).

The service works with 2 configuration files:

- the configuration file for the service itself
  `/etc/regionService/regionInfo.cfg`
- the configuration of the region Update Server information
  `/etc/regionService/regionData.cfg`

Pretty much everything is configurable or changeable via command line options.

Client IPv4 and IPv6 address ranges can be configured per region with the
public-ips and public-ipsv6 options, respectively. Information provided
with these options is stored in a patree using [pytricia](https://github.com/jsommers/pytricia). The information is used if the client provides no regionHint
or the provided regionHint cannot be found.

Configuration of client side IP addresses is optional. If client IPs are not
configured and the region provided with the regionHint by the client cannot
be found the server returns a 404 status code.

The Update Server info is returned as an XML string.

To integrate the code into a cloud VM that serves as regionInfo server one
must substitude the _SUBSTITUTE_WITH_CLOUD_SPECIFIC_NAME_ string with the
real hostname or the static IP address in

`/etc/apache2/vhosts.d/regionsrv_vhost.conf`

which happens automatically when running the certificate generation code.


/usr/sbin/genRegionServerCert --help

provides information about the expected arguments.

The region service is intended to be accessible via https only and thus a
certificate needs to be created. Use the .pem file generated in
`/root/regionServCert` and add it in the client (Cloud Guest VM) in
`/var/lib/regionService/certs`. The _genRegionServerCert_ generates a
self signed certificate, thus the .pem file must be included in the client
or the client VM will not be able to connect.


The WSGI daemon process is restricted to not run as root, thus a regionsrv
user and group is assigned in the `regionsrv_vhost.conf` file for the process.

The service is generic and can be used for all cloud environments.

Notable::
The Wsgi application is not executed when Apache starts, execution of the
application occurs when the first request is received.

Tradeoffs::
IP adresses are stored in a tree rather than doing calculation on the fly
when requests arrive. Caching all IP addresses in the tree speeds up the
response and reduces code complexity at the expense of memory usage.
