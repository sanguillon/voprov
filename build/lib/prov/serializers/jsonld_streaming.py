from yajl import YajlGen
from prov.constants import *
from prov.model import Literal, Identifier, QualifiedName, ProvDocument, first
from prov.serializers import Serializer
from prov.serializers.provjsonld import PROV_JSONLD_CONTEXT, encode_multiple_jsonld_values, qn_to_string


class StreamSerializer(Serializer):
    WRITER_CLS = None
    READER_CLS = None

    def __init__(self, document=None, writer_cls=None, reader_cls=None):
        super(StreamSerializer, self).__init__(document)
        self.writer_cls = self.WRITER_CLS if writer_cls is None else writer_cls
        self.reader_cls = self.READER_CLS if reader_cls is None else reader_cls

    def serialize(self, stream, **kwargs):
        """
        Default method for serializing a PROV document
        """
        document = self.document
        writer = self.writer_cls(stream, **kwargs)
        writer.open(document.namespaces, document.get_default_namespace())
        for record in document.records:
            writer.write_record(record)
        writer.no_more_record()
        for bundle in document.bundles:
            writer.open_bundle(bundle.identifier, bundle.namespaces, bundle.default_ns_uri)
            for record in bundle.records:
                writer.write_record(record)
            writer.close_bundle()
        writer.close()

    def deserialize(self, stream, **kwargs):
        raise NotImplementedError


class PROVRecordWriter(object):
    STATUS_UNOPENED = 0
    STATUS_IN_DOCUMENT = 1
    STATUS_IN_DOCUMENT_NO_MORE_RECORD = 2
    STATUS_IN_BUNDLE = 4
    STATUS_CLOSED = -1

    def __init__(self, stream, **kwargs):
        self._stream = stream
        self._status = PROVRecordWriter.STATUS_UNOPENED

    def open(self, namespaces=None, default_ns_uri=None):
        self._status = PROVRecordWriter.STATUS_IN_DOCUMENT

    def close(self):
        self._status = PROVRecordWriter.STATUS_CLOSED

    def open_bundle(self, idenfitier, namespaces=None, default_ns_uri=None):
        self._status = PROVRecordWriter.STATUS_IN_BUNDLE

    def close_bundle(self):
        self._status = PROVRecordWriter.STATUS_IN_DOCUMENT

    def write_record(self, record):
        pass

    def no_more_record(self):
        self._status = PROVRecordWriter.STATUS_IN_DOCUMENT_NO_MORE_RECORD


class PROVRecordReader(object):
    STATUS_UNOPENED = 0
    STATUS_IN_DOCUMENT = 1
    STATUS_IN_DOCUMENT_NO_MORE_RECORD = 2
    STATUS_IN_BUNDLE = 4
    STATUS_CLOSED = -1

    def __init__(self, stream, **kwargs):
        self._stream = stream
        self._status = PROVRecordWriter.STATUS_UNOPENED

    def next(self):
        pass


class ProvJSONLDRecordWriter(PROVRecordWriter):
    def __init__(self, stream, **kwargs):
        super(ProvJSONLDRecordWriter, self).__init__(stream, **kwargs)
        self.yajl_gen = YajlGen(**kwargs)
        self.prefixes = {}

    def open(self, namespaces=None, default_ns_uri=None, has_bundles=False):
        super(ProvJSONLDRecordWriter, self).open(namespaces, default_ns_uri)
        self.yajl_gen.yajl_gen_array_open()
        self.yajl_gen.yajl_gen_map_open()
        self.yajl_gen.yajl_gen_string("@context")
        self.prefixes = self.gen_prefixes(namespaces, default_ns_uri)
        contexts = [PROV_JSONLD_CONTEXT, self.prefixes] if self.prefixes else PROV_JSONLD_CONTEXT
        self.encode(contexts)
        self.yajl_gen.yajl_gen_string("@graph")
        self.yajl_gen.yajl_gen_array_open()

    def close(self):
        self.yajl_gen.yajl_gen_array_close()
        self.flush_to_console()
        super(ProvJSONLDRecordWriter, self).close()

    def open_bundle(self, idenfitier, namespaces=None, default_ns_uri=None):
        super(ProvJSONLDRecordWriter, self).open_bundle(idenfitier, namespaces, default_ns_uri)
        self.yajl_gen.yajl_gen_map_open()
        self.yajl_gen.yajl_gen_string("@context")
        prefixes = self.gen_prefixes(namespaces, default_ns_uri, self.prefixes)
        contexts = [PROV_JSONLD_CONTEXT, prefixes] if prefixes else PROV_JSONLD_CONTEXT
        self.encode(contexts)
        self.yajl_gen.yajl_gen_string("@id")
        self.yajl_gen.yajl_gen_string(qn_to_string(idenfitier))
        self.yajl_gen.yajl_gen_string("@graph")
        self.yajl_gen.yajl_gen_array_open()

    def close_bundle(self):
        self.yajl_gen.yajl_gen_array_close()
        self.yajl_gen.yajl_gen_map_close()
        self.flush_to_console()
        super(ProvJSONLDRecordWriter, self).close_bundle()

    def write_record(self, record):
        super(ProvJSONLDRecordWriter, self).write_record(record)
        self.yajl_gen.yajl_gen_map_open()
        if record.identifier:
            self.yajl_gen.yajl_gen_string("@id")
            self.yajl_gen.yajl_gen_string(qn_to_string(record.identifier))
        types = [record.get_type()]  # collecting all the types here
        if record._attributes:
            for (attr, values) in record._attributes.items():
                if not values:
                    continue
                if attr == PROV_TYPE:  # Special case for prov:type
                    prov_type_values = []
                    for value in values:
                        if isinstance(value, Identifier):
                            types.append(value)
                        else:
                            prov_type_values.append(value)
                    if prov_type_values:
                        # Overide the values variable
                        values = prov_type_values
                    else:
                        break
                self.yajl_gen.yajl_gen_string(qn_to_string(attr))
                if attr in PROV_ATTRIBUTE_QNAMES:
                    # TODO: QName export
                    self.yajl_gen.yajl_gen_string(qn_to_string(first(values)))
                elif attr in PROV_ATTRIBUTE_LITERALS:
                    self.yajl_gen.yajl_gen_string(first(values).isoformat())
                else:
                    self.encode(encode_multiple_jsonld_values(values))
        self.yajl_gen.yajl_gen_string("@type")
        self.encode(encode_multiple_jsonld_values(types, expecting_iris=True))
        self.yajl_gen.yajl_gen_map_close()
        self.flush_to_console()

    def no_more_record(self):
        self.yajl_gen.yajl_gen_array_close()
        self.yajl_gen.yajl_gen_map_close()
        self.flush_to_console()
        super(ProvJSONLDRecordWriter, self).no_more_record()

    def gen_prefixes(self, namespaces=None, default_ns_uri=None, parent=None):
        prefixes = dict(parent) if parent else {}
        if namespaces:
            prefixes.update({namespace.prefix: namespace.uri for namespace in namespaces})
        if default_ns_uri is not None:
            prefixes["@base"] = default_ns_uri
        return prefixes

    def encode(self, o):
        if isinstance(o, basestring):
            self.yajl_gen.yajl_gen_string(o)
        elif o is None:
            self.yajl_gen.yajl_gen_null()
        elif o is True:
            self.yajl_gen.yajl_gen_bool(o)
        elif o is False:
            self.yajl_gen.yajl_gen_bool(o)
        elif isinstance(o, (int, long)):
            self.yajl_gen.yajl_gen_integer(o)
        elif isinstance(o, float):
            self.yajl_gen.yajl_gen_double(o)
        elif isinstance(o, (list, tuple)):
            # a JSON array
            self.yajl_gen.yajl_gen_array_open()
            for value in o:
                self.encode(value)
            self.yajl_gen.yajl_gen_array_close()
        elif isinstance(o, dict):
            # a JSON object
            self.yajl_gen.yajl_gen_map_open()
            for key, value in o.items():
                self.yajl_gen.yajl_gen_string(key)
                self.encode(value)
            self.yajl_gen.yajl_gen_map_close()
        else:
            raise

    def flush_to_console(self):
        buffer = self.yajl_gen.yajl_gen_get_buf()
        if buffer:
            print(buffer)


class ProvJSONLDStreamingSerializer(StreamSerializer):
    WRITER_CLS = ProvJSONLDRecordWriter