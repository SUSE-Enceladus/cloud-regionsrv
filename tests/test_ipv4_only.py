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

region_data = {
    'smt_ipsv4': '10.10.10.10,20.20.20.20',
    'smt_ipsv6': None,
    'smt_names': '10.susecloud.net,20.susecloud.net',
    'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b'
}

region_map = {'antarctica-central': region_data}

ip_map = pytricia.PyTricia()
ip_map.insert('123.123.0.0/16', region_data)

def test_with_region_hint():
    xml = region_srv.get_response_xml(
        '0.0.0.0',
        'antarctica-central',
        region_map,
        ip_map
    )

    assert type(xml) is str

    smt_info_elems = etree.fromstring(xml).findall('.//smtInfo')
    xml_helper.assert_xml_validity(smt_info_elems, region_data)


def test_with_known_ip():
    xml = region_srv.get_response_xml(
        '123.123.1.1',
        None,
        region_map,
        ip_map
    )

    assert type(xml) is str

    smt_info_elems = etree.fromstring(xml).findall('.//smtInfo')
    xml_helper.assert_xml_validity(smt_info_elems, region_data)


def test_with_ip_fallback():
    xml = region_srv.get_response_xml(
        '123.123.1.1',
        'unknown-region',
        region_map,
        ip_map
    )

    assert type(xml) is str

    smt_info_elems = etree.fromstring(xml).findall('.//smtInfo')
    xml_helper.assert_xml_validity(smt_info_elems, region_data)


def test_with_unknown_ip():
    xml = region_srv.get_response_xml(
        '1.1.1.1',
        None,
        region_map,
        ip_map
    )

    assert xml is None
