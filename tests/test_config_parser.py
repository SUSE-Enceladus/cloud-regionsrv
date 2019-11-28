import os
import sys
import pytest

test_path = os.path.abspath(os.path.dirname(__file__))
code_path = os.path.abspath('%s/../srv/www/regionService' % test_path)

sys.path.insert(0, code_path)
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

import region_srv

def test_with_implicit_names_and_fps():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20,30.30.30.30',
        'smt_ipsv6': None,
        'smt_names': 'example.susecloud.net',
        'smt_fps': '00:00:00:00'
    }

    expected_output = [
        ('10.10.10.10', None, 'example.susecloud.net', '00:00:00:00'),
        ('20.20.20.20', None, 'example.susecloud.net', '00:00:00:00'),
        ('30.30.30.30', None, 'example.susecloud.net', '00:00:00:00')
    ]

    output = region_srv.parse_region_info(*input.values())

    assert output == expected_output

def test_with_explicit_names_and_fps():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20',
        'smt_ipsv6': None,
        'smt_names': 'one.susecloud.net,two.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b'
    }

    expected_output = [
        ('10.10.10.10', None, 'one.susecloud.net', '0a:0a:0a:0a'),
        ('20.20.20.20', None, 'two.susecloud.net', '0b:0b:0b:0b')
    ]

    output = region_srv.parse_region_info(*input.values())

    assert output == expected_output

def test_with_ipsv6():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20',
        'smt_ipsv6': '::0001,::0002',
        'smt_names': 'one.susecloud.net,two.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b'
    }

    expected_output = [
        ('10.10.10.10', '::0001', 'one.susecloud.net', '0a:0a:0a:0a'),
        ('20.20.20.20', '::0002', 'two.susecloud.net', '0b:0b:0b:0b')
    ]

    output = region_srv.parse_region_info(*input.values())

    assert output == expected_output

def test_with_ipsv6_mismatch():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20',
        'smt_ipsv6': '::0001',
        'smt_names': 'one.susecloud.net,two.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b'
    }

    with pytest.raises(ValueError, match='does not match number of configured IPv6 addresses'):
        region_srv.parse_region_info(*input.values())

def test_with_names_mismatch():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20,30.30.30.30',
        'smt_ipsv6': '::0001,::0002,:0003',
        'smt_names': 'one.susecloud.net,two.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b,0c:0c:0c:0c'
    }

    with pytest.raises(ValueError, match='Ambiguous SMT name and SMT IP pairings'):
        region_srv.parse_region_info(*input.values())

def test_with_fingerprints_mismatch():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20,30.30.30.30',
        'smt_ipsv6': '::0001,::0002,:0003',
        'smt_names': 'one.susecloud.net,two.susecloud.net,three.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b'
    }

    with pytest.raises(ValueError, match='Ambiguous SMT name and finger print pairings'):
        region_srv.parse_region_info(*input.values())
