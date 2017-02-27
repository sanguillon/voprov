from __future__ import unicode_literals
from collections import Counter
import json
import os


@profile
def count_records(filename):
    n_recs = 0
    counter = Counter()
    with open(filename) as f:
        content = json.load(f)
        if "@graph" in content:
            records = content["@graph"]
            n_recs = len(records)
            for record in records:
                try:
                    types = record["@type"]
                    t = types[0] if isinstance(types, list) else types
                except KeyError:
                    # if "prov:alternateOf" in record:
                    #     t = "prov:Alternate"
                    # elif "prov:specializationOf" in record:
                    #     t = "prov:Specialization"
                    # elif "prov:hadMember" in record:
                    #     t = "prov:Membership"
                    # else:
                        t = "unknown"
                counter[t] += 1
    return n_recs, counter

dataset = os.getenv("DATASET")
filename = "%s.jsonld" % dataset
print("Opening %s..." % filename)
n_recs, counter = count_records(filename)
print("Seen %d records." % n_recs)
print("\n".join(map(lambda t: "- %s: %d" % t, counter.items())))
assert(sum(counter.values()) == n_recs)
