

# XML has random ordering; server names and fingerprints can be specified
# only once in the config for multuple IPs
def assert_xml_validity(smt_info_elems, region_data):
    region_ipv4s = region_data['smt_ipsv4'].split(',')
    region_fqdns = region_data['smt_names'].split(',')
    region_fps = region_data['smt_fps'].split(',')

    max_len = max([len(region_ipv4s), len(region_fqdns), len(region_fps)])

    region_ipv6s = ['fc00::/7'] * max_len

    if len(region_fqdns) != max_len:
        region_fqdns = [region_fqdns[0]] * max_len

    if len(region_fps) != max_len:
        region_fps = [region_fps[0]] * max_len

    region_tuples = [
        (
            region_ipv4s[i], region_ipv6s[i], region_fqdns[i], region_fps[i]
        ) for i in range(0, len(region_ipv4s))
    ]

    ipv4s = [x.attrib['SMTserverIP'] for x in smt_info_elems]
    ipv6s = [x.attrib['SMTserverIPv6'] for x in smt_info_elems]
    server_names = [x.attrib['SMTserverName'] for x in smt_info_elems]
    fingerprints = [x.attrib['fingerprint'] for x in smt_info_elems]

    xml_tuples = [
        (
            ipv4s[i], ipv6s[i], server_names[i], fingerprints[i]
        ) for i in range(0, len(ipv4s))
    ]

    region_tuples.sort(key=lambda tup: tup[0])
    xml_tuples.sort(key=lambda tup: tup[0])

    assert xml_tuples == region_tuples
