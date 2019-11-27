import os
import sys
from lxml import etree

test_path = os.path.abspath(os.path.dirname(__file__))
code_path = os.path.abspath('%s/../srv/www/regionService' % test_path)

sys.path.insert(0, code_path)
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

import region_srv
from helpers import xml_helper

region_data = {
    'smt_ipsv4': '10.10.10.10,20.20.20.20,30.30.30.30',
    'smt_ipsv6': None,
    'smt_names': 'example.susecloud.net',
    'smt_fps': '00:00:00:00'
}

region_map = {'antarctica-central': region_data}

def test_with_implicit_names_and_fps():
    xml = region_srv.get_response_xml(
        '0.0.0.0',
        'antarctica-central',
        region_map,
        {}
    )

    assert type(xml) is str

    smt_info_elems = etree.fromstring(xml).findall('.//smtInfo')
    xml_helper.assert_xml_validity(smt_info_elems, region_data)
