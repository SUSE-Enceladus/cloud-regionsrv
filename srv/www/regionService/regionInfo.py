# Copyright (c) 2022 SUSE LLC, Robert Schweikert <rjschwei@suse.com>
#
# This file is part of cloud-regionsrv.
#
# cloud-regionsrv is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cloud-regionsrv is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cloud-regionsrv.  If not, see <http://www.gnu.org/licenses/>.

"""
Service that returns update server information based on a region
hint or the IP address of the requesting client.

The service works with two configuration files, the configuration for
the service itself, /etc/regionService/regionInfo.cfg by default or
specified with -f on the command line; and the configuration for the
region update server data, /etc/regionService/regionData.cfg, or as configured.

The regionInfo.cfg file is in ini format containing a [server] section
with the logFile and regionConfig options.

[server]
logFile = PATH_TO_LOGFILE_INCLUDING_LOGNAME
regionConfig = PATH_TO_REGION_DATA_FILE_INCLUDING_FILENAME

The region data configuration file is also in ini format. Each section
defines a region and contains options for public-ips, smt-server-ip,
smt-server-name, and smt-fingerprint. IPv6 region IP addresses and
update server addresses are specified by the respective *v6 entries. The
IPv6 entries are optional. It is assumed that there is no DNS
resolution of the name, thus both fields -ip and -name are expected.

[region]
public-ips = COMMA_SEPARATED_LIST_OF_IP_ADDRESSES_WITH_MASK_POSTFIX
public-ipsv6 = COMMA_SEPARATED_LIST_OF_IPv6_ADDRESSES_WITH_MASK_POSTFIX
smt-server-ip = IP_OF_SMT_SERVER_FOR_THIS_REGION
smt-server-ipv6 = IPv6_OF_SMT_SERVER_FOR_THIS_REGION
smt-server-name = HOSTNAME_OF_SMT_SERVER_FOR_THIS_REGION
smt-fingerprint = SMT_CERT_FINGERPRINT
"""

import configparser
import getopt
import ipaddress
import logging
import os
import pytricia
import sys
import region_srv

from flask import Flask
from flask import request


# ============================================================================
def create_smt_region_map(conf):
    """Create two mappings:
         ip_to_smt_data_map:
             maps all IP ranges to their respective update server info in a
             tree structure
         region_name_to_smt_data_map:
             maps all region names to their respective update server info"""
    ipv4_ranges_map = pytricia.PyTricia()
    ipv6_ranges_map = pytricia.PyTricia(128)
    region_name_to_smt_data_map = {}
    region_data_cfg = configparser.RawConfigParser()
    try:
        parsed = region_data_cfg.read(conf)
    except Exception as e:
        logging.error('Could not parse configuration file %s.' % conf)
        logging.error(str(e))
        return
    if not parsed:
        logging.error('Error parsing config file: %s' % conf)
        return

    for section in region_data_cfg.sections():
        try:
            region_public_ip_ranges = ''
            region_public_ip_ranges = region_data_cfg.get(
                section,
                'public-ips'
            )
        except Exception:
            info_msg = 'public-ips data not configured in section %s.' % section
            info_msg += ' No IPv4 address based fallback possible.'
            logging.info(info_msg)
        try:
            region_public_ipv6_ranges = ''
            region_public_ipv6_ranges = region_data_cfg.get(
                section,
                'public-ipsv6'
            )
        except Exception:
            info_msg = 'public-ipsv6 data not configured in section '
            info_msg += '%s. No IPv6 address based fallback possible.' % section
            logging.info(info_msg)
        try:
            region_smt_ips = None
            region_smt_ips = region_data_cfg.get(section, 'smt-server-ip')
        except Exception:
            info_msg = 'smt-server-ip data in section %s not ' % section
            info_msg += 'configured. Update servers cannot be reached over IPv4'
            logging.info(info_msg)
        try:
            region_smt_ipsv6 = None
            region_smt_ipsv6 = region_data_cfg.get(section, 'smt-server-ipv6')
        except Exception:
            info_msg = 'smt-server-ipv6 data in section %s not ' % section
            info_msg += 'configured. Update servers cannot be reached over IPv6'
            logging.info(info_msg)
        try:
            region_smt_names = region_data_cfg.get(section, 'smt-server-name')
        except Exception:
            logging.error(
                'Missing smt-server-name data in section %s.' % section
            )
            sys.exit(1)
        try:
            region_smt_registry_names = region_data_cfg.get(section, 'smt-registry-name')
        except Exception:
            logging.info(
                'Missing smt-registry-name data in section %s.' % section
            )
        try:
            region_smt_cert_fingerprints = region_data_cfg.get(
                section,
                'smt-fingerprint'
            )
        except Exception:
            logging.error(
                'Missing smt-fingerprint data in section %s' % section
            )
            sys.exit(1)

        if not region_smt_ips and not region_smt_ipsv6:
            err_msg = 'Missing update server IPs for either protocol at '
            err_msg += 'least one of smt-server-ip and smt-server-ipv6 '
            err_msg += 'must be configured'
            logging.error(err_msg)
            sys.exit(1)

        try:
            smt_info = region_srv.parse_region_info(
                region_smt_ips,
                region_smt_ipsv6,
                region_smt_names,
                region_smt_registry_names,
                region_smt_cert_fingerprints,
                section.lower()
            )
        except ValueError as e:
            logging.error(
                '%s in section "%s"' % (e, section)
            )
            sys.exit(1)

        region_name_to_smt_data_map[section.lower()] = smt_info
        for ip_range in region_public_ip_ranges.split(','):
            if not ip_range:
                continue
            try:
                ipaddress.IPv4Network(ip_range)
            except ValueError:
                msg = 'Could not process IPv4 range, improper format: %s'
                logging.error(msg % ip_range)
                continue

            ipv4_ranges_map.insert(ip_range, smt_info)

        for ip_range in region_public_ipv6_ranges.split(','):
            if not ip_range:
                continue
            try:
                ipaddress.IPv6Network(ip_range)
            except ValueError:
                msg = 'Could not process IPv6 range, improper format: %s'
                logging.error(msg % ip_range)
                continue

            ipv6_ranges_map.insert(ip_range, smt_info)

    return ipv4_ranges_map, ipv6_ranges_map, region_name_to_smt_data_map

# ============================================================================
def usage():
    """Print a usage message"""
    msg = '-f, --file       -> specify the service configuration file\n'
    msg += '-h, --help       -> print this message\n'
    msg += '-l, --log        -> specify the log file\n'
    msg += '-r, --regiondata -> specify the region data configuration file\n'
    print(msg)


# ============================================================================
# Process the command line options
try:
    cmd_opts, args = getopt.getopt(sys.argv[1:], 'f:hl:r:',
                                   ['file=', 'help', 'log=', 'regiondata='])
except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(1)

region_info_config_name = '/etc/regionService/regionInfo.cfg'
region_data_config_name = None
log_name = None
for option, option_value in cmd_opts:
    if option in ('-f', '--file'):
        region_info_config_name = option_value
        if not os.path.isfile(region_info_config_name):
            msg = 'Could not find specified configuration file "%s"'
            print(msg % region_info_config_name)
            sys.exit(1)
    elif option in ('-h', '--help'):
        usage()
        sys.exit(0)
    elif option in ('-l', '--log'):
        log_name = option_value
        log_dir = os.path.dirname(os.path.abspath(log_name))
        if not os.access(log_dir, os.W_OK):
            print('Log directory "%s" is not writable' % log_dir)
            sys.exit(1)
    elif option in ('-r', '--regiondata'):
        region_data_config_name = option_value
        if not os.path.isfile(region_data_config_name):
            msg = 'Could not find specified configuration file "%s"'
            print(msg % region_data_config_name)
            sys.exit(1)

srvConfig = configparser.RawConfigParser()
try:
    parsed = srvConfig.read(region_info_config_name)
except Exception as e:
    msg = 'Could not parse configuration file "%s"'
    print(msg % region_info_config_name)
    print(str(e))
    sys.exit(1)

if not parsed:
    print('Error parsing configuration file "%s"' % region_info_config_name)
    sys.exit(1)

# Assign default log file if not provided
if not log_name:
    log_name = srvConfig.get('server', 'logFile')

# Assign default region data config if not provided
if not region_data_config_name:
    region_data_config_name = srvConfig.get('server', 'regionConfig')
    if not os.path.isfile(region_data_config_name):
        msg = 'Default configuration file "%s" not found'
        print(msg % region_data_config_name)
        sys.exit(1)

# Set up logging
try:
    logging.basicConfig(
        filename=log_name,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )
except IOError:
    print('Could not open log file "%s" for writing.' % log_name)
    sys.exit(1)


# Build the map initially
ipv4_ranges_map, ipv6_ranges_map, region_name_to_smt_data_map = \
    create_smt_region_map(region_data_config_name)

# Implement the REST API
app = Flask(__name__)


@app.route('/regionInfo')
def index():
    requester_ip = request.remote_addr
    region_hint = request.args.get('regionHint')

    logging.info('Data request from: %s' % requester_ip)

    if region_hint:
        region_hint = region_hint.lower()
        logging.info('\tRegion hint: %s' % region_hint)

    response_xml = region_srv.get_response_xml(
        requester_ip,
        region_hint,
        region_name_to_smt_data_map,
        ipv4_ranges_map,
        ipv6_ranges_map
    )

    if response_xml:
        logging.info('Provided: %s' % response_xml)
        return response_xml, 200
    else:
        logging.info('\tDenied')
        return 'Not found', 404

# Run the service
if __name__ == '__main__':
    app.run(debug=True)
