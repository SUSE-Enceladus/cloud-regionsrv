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
        'smt_fps': '00:00:00:00',
        'region': 'test'
    }

    expected_output = [
        ('10.10.10.10', None, 'example.susecloud.net', '00:00:00:00', 'test'),
        ('20.20.20.20', None, 'example.susecloud.net', '00:00:00:00', 'test'),
        ('30.30.30.30', None, 'example.susecloud.net', '00:00:00:00', 'test')
    ]

    output = region_srv.parse_region_info(*input.values())

    assert output == expected_output

def test_with_explicit_names_and_fps():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20',
        'smt_ipsv6': None,
        'smt_names': 'one.susecloud.net,two.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b',
        'region': 'test'
    }

    expected_output = [
        ('10.10.10.10', None, 'one.susecloud.net', '0a:0a:0a:0a', 'test'),
        ('20.20.20.20', None, 'two.susecloud.net', '0b:0b:0b:0b', 'test')
    ]

    output = region_srv.parse_region_info(*input.values())

    assert output == expected_output

def test_with_ipsv6():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20',
        'smt_ipsv6': '::0001,::0002',
        'smt_names': 'one.susecloud.net,two.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b',
        'region': 'test'
    }

    expected_output = [
        ('10.10.10.10', '::0001', 'one.susecloud.net', '0a:0a:0a:0a', 'test'),
        ('20.20.20.20', '::0002', 'two.susecloud.net', '0b:0b:0b:0b', 'test')
    ]

    output = region_srv.parse_region_info(*input.values())

    assert output == expected_output

def test_with_ipsv6_mismatch():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20',
        'smt_ipsv6': '::0001',
        'smt_names': 'one.susecloud.net,two.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b',
        'region': 'test'
    }

    with pytest.raises(
            ValueError,
            match='does not match number of configured IPv6 addresses'
    ):
        region_srv.parse_region_info(*input.values())

def test_with_names_mismatch():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20,30.30.30.30',
        'smt_ipsv6': '::0001,::0002,:0003',
        'smt_names': 'one.susecloud.net,two.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b,0c:0c:0c:0c',
        'region': 'test'
    }

    with pytest.raises(
            ValueError,
            match='Ambiguous update server name and IP pairings'
    ):
        region_srv.parse_region_info(*input.values())

def test_with_fingerprints_mismatch():
    input = {
        'smt_ipsv4': '10.10.10.10,20.20.20.20,30.30.30.30',
        'smt_ipsv6': '::0001,::0002,:0003',
        'smt_names': 'one.susecloud.net,two.susecloud.net,three.susecloud.net',
        'smt_fps': '0a:0a:0a:0a,0b:0b:0b:0b',
        'region': 'test'
    }

    with pytest.raises(
            ValueError,
            match='Ambiguous update server name and finger print pairings'
    ):
        region_srv.parse_region_info(*input.values())
