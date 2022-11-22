# Copyright (c) 2019 SUSE LLC
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

# XML has random ordering; server names and fingerprints can be specified
# only once in the config for multiple IPs
def assert_xml_validity(smt_info_elems, region_data):
    ipv4s = [x.attrib['SMTserverIP'] for x in smt_info_elems]
    ipv6s = [x.attrib.get('SMTserverIPv6', None) for x in smt_info_elems]
    server_names = [x.attrib['SMTserverName'] for x in smt_info_elems]
    fingerprints = [x.attrib['fingerprint'] for x in smt_info_elems]
    regions = [x.attrib['region'] for x in smt_info_elems]

    xml_tuples = [
        (
            ipv4s[i], ipv6s[i], server_names[i], fingerprints[i], regions[i]
        ) for i in range(0, len(ipv4s))
    ]

    region_data.sort(key=lambda tup: tup[0])
    xml_tuples.sort(key=lambda tup: tup[0])

    assert xml_tuples == region_data
