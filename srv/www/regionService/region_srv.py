import random


def get_response_xml(requester_ip, region_hint, region_name_to_smt_data_map, ip_range_to_smt_data_map):
    smt_server_data = None

    if region_hint:
        smt_server_data = region_name_to_smt_data_map.get(region_hint, None)

    if not smt_server_data:
        smt_server_data = ip_range_to_smt_data_map.get(requester_ip)

    if not smt_server_data:
        return

    smt_ipsv4 = smt_server_data['smt_ipsv4'].split(',')
    num_smt_ipsv4 = len(smt_ipsv4)
    smt_ipsv6 = ['fc00::/7'] * num_smt_ipsv4
    if smt_server_data['smt_ipsv6']:
        smt_ipsv6 = smt_server_data['smt_ipsv6'].split(',')
    smt_names = smt_server_data['smt_names'].split(',')
    num_smt_names = len(smt_names)
    smt_cert_fingerprints = smt_server_data['smt_fps'].split(',')
    num_smt_fingerprints = len(smt_cert_fingerprints)
    smt_info_xml = '<regionSMTdata>'

    # Randomize the order of the SMT server information provided to the client
    while num_smt_ipsv4:
        entry = random.randint(0, num_smt_ipsv4 - 1)
        smt_ip = smt_ipsv4[entry]
        smt_ipv6 = smt_ipsv6[entry]
        del (smt_ipsv4[entry])
        if num_smt_names > 1:
            smt_name = smt_names[entry]
            del (smt_names[entry])
        else:
            smt_name = smt_names[0]
        if num_smt_fingerprints > 1:
            smt_fingerprint = smt_cert_fingerprints[entry]
            del (smt_cert_fingerprints[entry])
        else:
            smt_fingerprint = smt_cert_fingerprints[0]
        num_smt_ipsv4 -= 1
        smt_info_xml += '<smtInfo SMTserverIP="%s" ' % smt_ip
        smt_info_xml += 'SMTserverIPv6="%s" ' % smt_ipv6
        smt_info_xml += 'SMTserverName="%s" ' % smt_name
        smt_info_xml += 'fingerprint="%s"/>' % smt_fingerprint

    smt_info_xml += '</regionSMTdata>'
    return smt_info_xml
