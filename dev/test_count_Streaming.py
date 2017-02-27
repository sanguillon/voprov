from __future__ import unicode_literals
from collections import Counter
import os
from yajl import YajlParser, YajlContentHandler


@profile
def count_records(filename):
    handler = ProvRecordCounter()
    parser = YajlParser(handler)
    with open(filename) as f:
        parser.parse(f)
    return handler.n_records, handler.counter

class ProvRecordCounter(YajlContentHandler):
    def __init__(self):
        # self.out = sys.stdout
        self.counter = Counter()
        self.n_records = 0
        self.bundles = 0
        self.in_graph = 0
        self.in_record = 0
        self.expecting_record_type = False

    def yajl_null(self, ctx):
        # self.out.write("null\n")
        pass

    def yajl_boolean(self, ctx, boolVal):
        # self.out.write("bool: %s\n" %('true' if boolVal else 'false'))
        pass

    def yajl_integer(self, ctx, integerVal):
        # self.out.write("integer: %s\n" %integerVal)
        pass

    def yajl_double(self, ctx, doubleVal):
        # self.out.write("double: %s\n" %doubleVal)
        pass

    def yajl_number(self, ctx, stringNum):
        # num = float(stringNum) if '.' in stringNum else int(stringNum)
        # self.out.write("number: %s\n" %num)
        pass

    def yajl_string(self, ctx, stringVal):
        if self.expecting_record_type:
            self.counter[stringVal] += 1
            self.expecting_record_type = False  # ignore the rest

    def yajl_start_map(self, ctx):
        if self.in_graph:
            if not self.in_record:
                # this is a new record
                self.n_records += 1
            self.in_record += 1

    def yajl_map_key(self, ctx, stringVal):
        if stringVal == "@graph":
            self.in_graph = 1
        if self.in_record == 1 and stringVal == "@type":
            self.expecting_record_type = True

    def yajl_end_map(self, ctx):
        if self.in_graph:
            self.in_record -= 1

    def yajl_start_array(self, ctx):
        pass

    def yajl_end_array(self, ctx):
        if self.in_graph and not self.in_record:
            self.in_graph = 0


dataset = os.getenv("DATASET")
filename = "%s.jsonld" % dataset
print("Opening %s..." % filename)
n_recs, counter = count_records(filename)
print("Seen %d records." % n_recs)
print("\n".join(map(lambda t: "- %s: %d" % t, counter.items())))
assert(sum(counter.values()) == n_recs)
