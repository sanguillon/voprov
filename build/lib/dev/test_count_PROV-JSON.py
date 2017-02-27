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
        for term, records in content.items():
            if term != "prefix":
                n_recs += len(records)
                counter[term] += len(records)
    return n_recs, counter

dataset = os.getenv("DATASET")
filename = "%s.json" % dataset
print("Opening %s..." % filename)
n_recs, counter = count_records(filename)
print("Seen %d records." % n_recs)
print("\n".join(map(lambda t: "- %s: %d" % t, counter.items())))
assert(sum(counter.values()) == n_recs)
