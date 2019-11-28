import os
import sys
import pytricia
from lxml import etree

test_path = os.path.abspath(os.path.dirname(__file__))
code_path = os.path.abspath('%s/../srv/www/regionService' % test_path)

sys.path.insert(0, code_path)
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

import region_srv
from helpers import xml_helper

region_data = [
    ('10.10.10.10', '1010::', '10.susecloud.net', '0a:0a:0a:0a'),
    ('20.20.20.20', '2020::', '20.susecloud.net', '0b:0b:0b:0b')
]

region_map = {'antarctica-central': region_data}

ipv4_ranges_map = pytricia.PyTricia()
ipv4_ranges_map.insert('123.123.0.0/16', region_data)

ipv6_ranges_map = pytricia.PyTricia(128)
ipv6_ranges_map.insert('2000::/16', region_data)

def test_with_region_hint():
    xml = region_srv.get_response_xml(
        '0.0.0.0',
        'antarctica-central',
        region_map,
        ipv4_ranges_map,
        ipv6_ranges_map
    )

    assert type(xml) is str

    smt_info_elems = etree.fromstring(xml).findall('.//smtInfo')
    xml_helper.assert_xml_validity(smt_info_elems, region_data)

def test_with_known_ipv6():
    xml = region_srv.get_response_xml(
        '2000::1',
        None,
        region_map,
        ipv4_ranges_map,
        ipv6_ranges_map
    )

    assert type(xml) is str

    smt_info_elems = etree.fromstring(xml).findall('.//smtInfo')
    xml_helper.assert_xml_validity(smt_info_elems, region_data)

def test_with_unknown_ipv6():
    xml = region_srv.get_response_xml(
        '1000::1',
        None,
        region_map,
        ipv4_ranges_map,
        ipv6_ranges_map
    )

    assert xml is None
