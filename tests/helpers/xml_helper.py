

# XML has random ordering; server names and fingerprints can be specified
# only once in the config for multuple IPs
def assert_xml_validity(smt_info_elems, region_data):
    ipv4s = [x.attrib['SMTserverIP'] for x in smt_info_elems]
    ipv6s = [x.attrib.get('SMTserverIPv6', None) for x in smt_info_elems]
    server_names = [x.attrib['SMTserverName'] for x in smt_info_elems]
    fingerprints = [x.attrib['fingerprint'] for x in smt_info_elems]

    xml_tuples = [
        (
            ipv4s[i], ipv6s[i], server_names[i], fingerprints[i]
        ) for i in range(0, len(ipv4s))
    ]

    region_data.sort(key=lambda tup: tup[0])
    xml_tuples.sort(key=lambda tup: tup[0])

    assert xml_tuples == region_data
