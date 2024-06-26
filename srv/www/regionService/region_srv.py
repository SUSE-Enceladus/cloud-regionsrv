import random
import ipaddress


def get_response_xml(
        requester_ip, region_hint, region_name_to_smt_data_map,
        ipv4_ranges_map, ipv6_ranges_map
):
    smt_server_data = None

    if region_hint:
        smt_server_data = region_name_to_smt_data_map.get(region_hint, None)

    if not smt_server_data:
        parsed_address = ipaddress.ip_address(requester_ip)

        if type(parsed_address) == ipaddress.IPv4Address:
            smt_server_data = ipv4_ranges_map.get(requester_ip)
        else:
            smt_server_data = ipv6_ranges_map.get(requester_ip)

    if not smt_server_data:
        return

    # Randomize the order of the update server information
    # provided to the client
    smt_server_data = random.sample(smt_server_data, len(smt_server_data))

    smt_info_xml = '<regionSMTdata>\n'
    for update_server in smt_server_data:
        smt_info_xml += '<smtInfo SMTserverIP="%s" ' % update_server[0]
        if update_server[1]:
            smt_info_xml += 'SMTserverIPv6="%s" ' % update_server[1]
        smt_info_xml += 'SMTserverName="%s" ' % update_server[2]
        smt_info_xml += 'SMTregistryName="%s" ' % update_server[3]
        smt_info_xml += 'fingerprint="%s" ' % update_server[4]
        smt_info_xml += 'region="%s"/>\n' % update_server[5]

    smt_info_xml += '</regionSMTdata>'
    return smt_info_xml


def parse_region_info(
        region_smt_ips, region_smt_ipsv6, region_smt_names,
        region_smt_registry_names, region_smt_cert_fingerprints, region
):
    num_ips_v4 = None
    ipsv4 = []
    if region_smt_ips:
        ipsv4 = region_smt_ips.split(',')
        num_ips_v4 = len(ipsv4)

    num_ips_v6 = None
    ipsv6 = []
    if region_smt_ipsv6:
        ipsv6 = region_smt_ipsv6.split(',')
        num_ips_v6 = len(ipsv6)
        if num_ips_v4 and num_ips_v6 != num_ips_v4:
            msg = 'Number of configured IPv4 adresses does not '
            msg += 'match number of configured IPv6 addresses'
            raise ValueError(msg)

    if not num_ips_v4 and not num_ips_v6:
        raise ValueError('Neither IPv4 nor IPv6 configured for update server')

    num_ips = num_ips_v4 or num_ips_v6
    if not ipsv4:
        ipsv4 = [None] * num_ips
    if not ipsv6:
        ipsv6 = [None] * num_ips

    fqdns = region_smt_names.split(',')
    if len(fqdns) > 1 and len(fqdns) != num_ips:
        raise ValueError('Ambiguous update server name and IP pairings')

    if len(fqdns) == 1 and len(fqdns) != num_ips:
        fqdns = [fqdns[0]] * num_ips

    registry_fqdns = region_smt_registry_names.split(',')
    if len(registry_fqdns) > 1 and len(registry_fqdns) != num_ips:
        raise ValueError('Ambiguous update registry name and IP pairings')

    if len(registry_fqdns) == 1 and len(registry_fqdns) != num_ips:
        registry_fqdns = [registry_fqdns[0]] * num_ips

    fingerprints = region_smt_cert_fingerprints.split(',')
    if len(fingerprints) > 1 and len(fingerprints) != num_ips:
        raise ValueError(
            'Ambiguous update server name and finger print pairings'
        )

    if len(fingerprints) == 1 and len(fingerprints) != num_ips:
        fingerprints = [fingerprints[0]] * num_ips

    region_info = [
        (
            ipsv4[i], ipsv6[i], fqdns[i], registry_fqdns[i],
            fingerprints[i], region
        ) for i in range(0, len(ipsv4))
    ]

    return region_info
