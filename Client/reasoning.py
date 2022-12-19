import Client.Countries.country_evaluation as country_evaluation
import Client.Countries

# TODO set/rethink initial order from lowest to highest
order = {('fw0', 'id0', 'ac0'): 1,
         ('fw0', 'id0', 'ac1'): 2,
         ('fw0', 'id0', 'ac2'): 3,
         ('fw0', 'id0', 'ac3'): 4,
         ('fw0', 'id1', 'ac0'): 5,
         ('fw0', 'id1', 'ac1'): 6,
         ('fw0', 'id1', 'ac2'): 7,
         ('fw0', 'id1', 'ac3'): 8,
         ('fw0', 'id2', 'ac0'): 9,
         ('fw0', 'id2', 'ac1'): 10,
         ('fw0', 'id2', 'ac2'): 11,
         ('fw0', 'id2', 'ac3'): 12,
         ('fw0', 'id3', 'ac0'): 13,
         ('fw0', 'id3', 'ac1'): 14,
         ('fw0', 'id3', 'ac2'): 15,
         ('fw0', 'id3', 'ac3'): 16,
         ('fw1', 'id0', 'ac0'): 17,
         ('fw1', 'id0', 'ac1'): 18,
         ('fw1', 'id0', 'ac2'): 19,
         ('fw1', 'id0', 'ac3'): 20,
         ('fw1', 'id1', 'ac0'): 21,
         ('fw1', 'id1', 'ac1'): 22,
         ('fw1', 'id1', 'ac2'): 23,
         ('fw1', 'id1', 'ac3'): 24,
         ('fw1', 'id2', 'ac0'): 25,
         ('fw1', 'id2', 'ac1'): 26,
         ('fw1', 'id2', 'ac2'): 27,
         ('fw1', 'id2', 'ac3'): 28,
         ('fw1', 'id3', 'ac0'): 29,
         ('fw1', 'id3', 'ac1'): 30,
         ('fw1', 'id3', 'ac2'): 31,
         ('fw1', 'id3', 'ac3'): 32,
         ('fw2', 'id0', 'ac0'): 33,
         ('fw2', 'id0', 'ac1'): 34,
         ('fw2', 'id0', 'ac2'): 35,
         ('fw2', 'id0', 'ac3'): 36,
         ('fw2', 'id1', 'ac0'): 37,
         ('fw2', 'id1', 'ac1'): 38,
         ('fw2', 'id1', 'ac2'): 39,
         ('fw2', 'id1', 'ac3'): 40,
         ('fw2', 'id2', 'ac0'): 41,
         ('fw2', 'id2', 'ac1'): 42,
         ('fw2', 'id2', 'ac2'): 43,
         ('fw2', 'id2', 'ac3'): 44,
         ('fw2', 'id3', 'ac0'): 45,
         ('fw2', 'id3', 'ac1'): 46,
         ('fw2', 'id3', 'ac2'): 47,
         ('fw2', 'id3', 'ac3'): 48,
         ('fw3', 'id0', 'ac0'): 49,
         ('fw3', 'id0', 'ac1'): 50,
         ('fw3', 'id0', 'ac2'): 51,
         ('fw3', 'id0', 'ac3'): 52,
         ('fw3', 'id1', 'ac0'): 53,
         ('fw3', 'id1', 'ac1'): 54,
         ('fw3', 'id1', 'ac2'): 55,
         ('fw3', 'id1', 'ac3'): 56,
         ('fw3', 'id2', 'ac0'): 57,
         ('fw3', 'id2', 'ac1'): 58,
         ('fw3', 'id2', 'ac2'): 59,
         ('fw3', 'id2', 'ac3'): 60,
         ('fw3', 'id3', 'ac0'): 61,
         ('fw3', 'id3', 'ac1'): 62,
         ('fw3', 'id3', 'ac2'): 63,
         ('fw3', 'id3', 'ac3'): 64}


def reasoning(context_information_dict):
    fwl = ['fw0', 'fw1', 'fw2', 'fw3']
    idl = ['id0', 'id1', 'id2', 'id3']
    acl = ['ac0', 'ac1', 'ac2', 'ac3']

# compare the received country code with the list of the existing countries and compare the particular one with a list of malicious nations
    if country_evaluation.get_country_code(context_information_dict["location"]) in country_evaluation.get_malicious_countries():
        fwl.remove('fw0')
        fwl.remove('fw1')
        idl.remove('id0')
        idl.remove('id1')
        acl.remove('ac0')
        acl.remove('ac1')
        acl.remove('ac2')
    # TODO: add extended logic

    return permute_options(fwl, idl, acl)


def permute_options(fwl, idl, acl):
    possible_protection_settings = []
    for fw in range(len(fwl)):
        for id in range(len(idl)):
            for ac in range(len(acl)):
                possible_protection_settings.extend(list(zip(fwl, idl, acl)))
                acl.append(acl[0])
                acl = acl[1:]
            idl.append(idl[0])
            idl = idl[1:]
        fwl.append(fwl[0])
        fwl = fwl[1:]
    possible_protection_settings = list(dict.fromkeys(possible_protection_settings))  # remove duplicates

    possible_protection_settings = sorted(possible_protection_settings, key=lambda x: order[x])

    return possible_protection_settings
