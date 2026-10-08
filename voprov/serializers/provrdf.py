# -*- coding: utf-8 -*-
"""RDF serializer for VOProv documents.

The mapping follows PROV-O (https://www.w3.org/TR/prov-o/) and extends it in the ``voprov`` namespace:

* an element is a resource typed with its PROV-O class and with its VOProv class::

      ex:data a prov:Entity, voprov:DatasetEntity ; prov:name "image" .

* a relation is written twice: as the PROV-O shortcut between the two elements, and as a *qualified* node holding
  its identifier, role, time and other attributes (PROV-O qualification pattern)::

      ex:run prov:used ex:data ;
          prov:qualifiedUsage [ a prov:Usage, voprov:Usage ; prov:entity ex:data ; prov:hadRole "input" ] .

  The relations that PROV-O does not qualify, and the VOProv relations, use ``voprov:qualified...`` properties.
* a bundle is a named graph (TriG), and is typed ``prov:Bundle`` in the default graph.

Everything is written, so that reading the result back gives the same document. Plain PROV-O (written by prov or by
other tools) can also be read: PROV-O classes give plain prov records, and shortcuts without qualified nodes give
relations.

The module only needs the optional dependency rdflib (``pip install voprov[rdf]``) and the public API of prov.
"""
import hashlib
import io
import logging
from collections import defaultdict, namedtuple

import prov.model
from prov import constants as pc
from prov.identifier import Identifier, Namespace, QualifiedName
from prov.serializers import Serializer
from rdflib import BNode, Dataset, Graph, RDF, RDFS, URIRef, XSD
from rdflib import Literal as RDFLiteral
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

from voprov import constants as vc

__author__ = 'Mathieu Servillat'

logger = logging.getLogger(__name__)

PROV_URI = pc.PROV.uri
VOPROV_URI = vc.VOPROV.uri


def _prov(name):
    return URIRef(PROV_URI + name)


def _voprov(name):
    return URIRef(VOPROV_URI + name)


# -- Attributes -----------------------------------------------------------------------------------------------------

# prov attribute -> PROV-O property. Any other attribute is written with its own URI.
ATTRIBUTE_TO_PROPERTY = {
    pc.PROV['label']: RDFS.label,
    pc.PROV['location']: _prov('atLocation'),
    pc.PROV['startTime']: _prov('startedAtTime'),
    pc.PROV['endTime']: _prov('endedAtTime'),
    pc.PROV['time']: _prov('atTime'),
    pc.PROV['role']: _prov('hadRole'),
}
PROPERTY_TO_ATTRIBUTE = dict((uri, attr) for attr, uri in ATTRIBUTE_TO_PROPERTY.items())

# -- Elements -------------------------------------------------------------------------------------------------------

# VOProv element types, and the PROV-O class they are also instances of
ELEMENT_CLASSES = {
    vc.VOPROV_ACTIVITY: _prov('Activity'),
    vc.VOPROV_AGENT: _prov('Agent'),
}
for _type in (vc.VOPROV_ENTITY, vc.VOPROV_VALUE_ENTITY, vc.VOPROV_DATASET_ENTITY, vc.VOPROV_CONFIGURATION_FILE,
              vc.VOPROV_CONFIGURATION_PARAMETER, vc.VOPROV_ACTIVITY_DESCRIPTION, vc.VOPROV_ENTITY_DESCRIPTION,
              vc.VOPROV_VALUE_DESCRIPTION, vc.VOPROV_DATASET_DESCRIPTION, vc.VOPROV_USAGE_DESCRIPTION,
              vc.VOPROV_GENERATION_DESCRIPTION, vc.VOPROV_CONFIG_FILE_DESCRIPTION,
              vc.VOPROV_PARAMETER_DESCRIPTION):
    ELEMENT_CLASSES[_type] = _prov('Entity')
# plain prov elements
ELEMENT_CLASSES.update({pc.PROV_ENTITY: _prov('Entity'), pc.PROV_ACTIVITY: _prov('Activity'),
                        pc.PROV_AGENT: _prov('Agent')})
VOPROV_ELEMENT_TYPES = [t for t in ELEMENT_CLASSES if t.namespace.uri == VOPROV_URI]
PROV_ELEMENT_TYPES = [t for t in ELEMENT_CLASSES if t.namespace.uri == PROV_URI]
PROV_ELEMENT_BY_CLASS = dict((ELEMENT_CLASSES[t], t) for t in PROV_ELEMENT_TYPES)

# -- Relations ------------------------------------------------------------------------------------------------------

#: How a relation is written. The subject of the relation (its first formal attribute) is the resource the
#: qualified node hangs from, and the object (second formal attribute) is the target of the shortcut.
Relation = namedtuple('Relation', 'voprov_type prov_type shortcut qualified prov_class properties')


def _relation(voprov_type, prov_type, shortcut, qualified, prov_class=None, **properties):
    """properties: attribute (local name in the prov namespace) -> PROV-O property (local name)."""
    return Relation(
        voprov_type, prov_type, shortcut, qualified,
        _prov(prov_class) if prov_class else None,
        dict((pc.PROV[attr], _prov(prop)) for attr, prop in properties.items()))


RELATIONS = [
    _relation(vc.VOPROV_USAGE, pc.PROV_USAGE, _prov('used'), _prov('qualifiedUsage'), 'Usage'),
    _relation(vc.VOPROV_GENERATION, pc.PROV_GENERATION, _prov('wasGeneratedBy'), _prov('qualifiedGeneration'),
              'Generation'),
    _relation(vc.VOPROV_START, pc.PROV_START, _prov('wasStartedBy'), _prov('qualifiedStart'), 'Start',
              trigger='entity', starter='hadActivity'),
    _relation(vc.VOPROV_END, pc.PROV_END, _prov('wasEndedBy'), _prov('qualifiedEnd'), 'End',
              trigger='entity', ender='hadActivity'),
    _relation(vc.VOPROV_INVALIDATION, pc.PROV_INVALIDATION, _prov('wasInvalidatedBy'),
              _prov('qualifiedInvalidation'), 'Invalidation'),
    _relation(vc.VOPROV_COMMUNICATION, pc.PROV_COMMUNICATION, _prov('wasInformedBy'),
              _prov('qualifiedCommunication'), 'Communication', informant='activity'),
    _relation(vc.VOPROV_ATTRIBUTION, pc.PROV_ATTRIBUTION, _prov('wasAttributedTo'), _prov('qualifiedAttribution'),
              'Attribution'),
    _relation(vc.VOPROV_ASSOCIATION, pc.PROV_ASSOCIATION, _prov('wasAssociatedWith'),
              _prov('qualifiedAssociation'), 'Association', plan='hadPlan'),
    _relation(vc.VOPROV_DELEGATION, pc.PROV_DELEGATION, _prov('actedOnBehalfOf'), _prov('qualifiedDelegation'),
              'Delegation', responsible='agent', activity='hadActivity'),
    _relation(vc.VOPROV_INFLUENCE, pc.PROV_INFLUENCE, _prov('wasInfluencedBy'), _prov('qualifiedInfluence'),
              'Influence'),
    _relation(vc.VOPROV_DERIVATION, pc.PROV_DERIVATION, _prov('wasDerivedFrom'), _prov('qualifiedDerivation'),
              'Derivation', usedEntity='entity', activity='hadActivity', generation='hadGeneration',
              usage='hadUsage'),
    # PROV-O does not qualify these ones: the qualified node uses voprov properties
    _relation(vc.VOPROV_SPECIALIZATION, pc.PROV_SPECIALIZATION, _prov('specializationOf'),
              _voprov('qualifiedSpecialization')),
    _relation(vc.VOPROV_ALTERNATE, pc.PROV_ALTERNATE, _prov('alternateOf'), _voprov('qualifiedAlternate')),
    _relation(vc.VOPROV_MENTION, pc.PROV_MENTION, _prov('mentionOf'), _voprov('qualifiedMention'),
              bundle='asInBundle'),
    _relation(vc.VOPROV_MEMBERSHIP, pc.PROV_MEMBERSHIP, _prov('hadMember'), _voprov('qualifiedMembership')),
    # VOProv relations
    _relation(vc.VOPROV_DESCRIPTION_RELATION, None, _voprov('isDescribedBy'), _voprov('qualifiedIsDescribedBy')),
    _relation(vc.VOPROV_RELATED_TO_RELATION, None, _voprov('isRelatedTo'), _voprov('qualifiedIsRelatedTo')),
    _relation(vc.VOPROV_CONFIGURATION_RELATION, None, _voprov('wasConfiguredBy'),
              _voprov('qualifiedWasConfiguredBy')),
    _relation(vc.VOPROV_REFERENCE_RELATION, None, _voprov('hadReference'), _voprov('qualifiedHadReference')),
]

RELATION_BY_TYPE = {}
for _rel in RELATIONS:
    RELATION_BY_TYPE[_rel.voprov_type] = _rel
    if _rel.prov_type is not None:
        RELATION_BY_TYPE[_rel.prov_type] = _rel
RELATION_BY_QUALIFIED = dict((rel.qualified, rel) for rel in RELATIONS)
#: predicates that link elements and relations, and are not attributes of the elements
STRUCTURAL_PREDICATES = set(rel.shortcut for rel in RELATIONS) | set(RELATION_BY_QUALIFIED)


def _graphs(dataset):
    """Graphs of a dataset (rdflib 7 renamed contexts() to graphs())."""
    return list(dataset.graphs()) if hasattr(dataset, 'graphs') else list(dataset.contexts())


def _default_graph(dataset):
    """Default graph of a dataset (rdflib 7 renamed default_context to default_graph)."""
    return dataset.default_graph if hasattr(dataset, 'default_graph') else dataset.default_context


def _formal_attributes(record_type):
    return prov.model.PROV_REC_CLS[record_type].FORMAL_ATTRIBUTES


class VOProvRDFSerializer(Serializer):
    """RDF serializer for :class:`~voprov.model.VOProvDocument`.

    The RDF is compatible with PROV-O, and a document written by this serializer is read back identical. The mapping
    is described in the documentation of the formats, and in the documentation of the module
    ``voprov.serializers.provrdf``.
    """

    def serialize(self, stream, rdf_format='trig', shortcuts=True, **kwargs):
        """
        Serializes a :class:`~voprov.model.VOProvDocument` to RDF.

        :param stream: Where to save the output.
        :param rdf_format: Format of the RDF, any format of rdflib that supports named graphs ('trig' by default,
            or 'nquads', 'json-ld'). The other formats ('turtle', 'xml', 'nt') merge the bundles in one graph.
        :param shortcuts: Write the PROV-O shortcut of each relation (``ex:run prov:used ex:data``) next to its
            qualified node (True by default). The shortcuts are the easiest to query, but redundant: the reader of
            prov, which expects a relation to be written in one way or the other, reads a document that has both
            with some of the relations twice. Use False to write the qualified nodes only (the relations that
            PROV-O does not qualify keep their shortcut).
        """
        dataset = Dataset()
        self._repeated = defaultdict(int)
        default = _default_graph(dataset)
        self._bind_namespaces(dataset, self.document)
        self._encode_container(self.document, default, shortcuts)
        for bundle in self.document.bundles:
            self._bind_namespaces(dataset, bundle)
            if bundle.identifier is None:
                continue
            node = URIRef(bundle.identifier.uri)
            default.add((node, RDF.type, _prov('Bundle')))
            self._encode_container(bundle, dataset.graph(node), shortcuts)
        if rdf_format not in ('trig', 'nquads', 'json-ld', 'hext') and self.document.has_bundles():
            logger.warning('The RDF format %s has no named graphs: the bundles are merged with the document.',
                           rdf_format)
            merged = Graph()
            for prefix, namespace in dataset.namespaces():
                merged.bind(prefix, namespace)
            for graph in _graphs(dataset):
                for triple in graph:
                    merged.add(triple)
            content = merged.serialize(format=rdf_format)
        else:
            content = dataset.serialize(format=rdf_format)
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        if isinstance(stream, io.TextIOBase):
            stream.write(content)
        else:
            stream.write(content.encode('utf-8'))

    def deserialize(self, stream, rdf_format='trig', relative_iri_base=None, **kwargs):
        """
        Deserializes RDF into a :class:`~voprov.model.VOProvDocument`.

        :param stream: Input data.
        :param rdf_format: Format of the RDF ('trig' by default).
        :param relative_iri_base: Base for the relative IRIs of the input.
        """
        from voprov.model import VOProvDocument

        content = stream.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        dataset = Dataset()
        dataset.parse(data=content, format=rdf_format, publicID=relative_iri_base)
        document = VOProvDocument()
        names = _Names(dataset, document)
        graphs = sorted(_graphs(dataset), key=lambda g: str(g.identifier))
        # the unnamed graph (the default graph, or a graph named with a blank node by rdflib 6) is the document,
        # the graphs named with an IRI are its bundles
        for graph in graphs:
            if graph.identifier == DATASET_DEFAULT_GRAPH_ID or isinstance(graph.identifier, BNode):
                self._decode_graph(graph, document, names)
        for graph in graphs:
            if isinstance(graph.identifier, URIRef) and graph.identifier != DATASET_DEFAULT_GRAPH_ID \
                    and len(graph) > 0:
                bundle = document.bundle(names.qname(graph.identifier))
                self._decode_graph(graph, bundle, names)
        return document

    # -- Encoding ---------------------------------------------------------------------------------------------------

    @staticmethod
    def _bind_namespaces(dataset, container):
        for namespace in container.namespaces:
            dataset.bind(namespace.prefix, URIRef(namespace.uri))
        for prefix in ('prov', 'voprov'):
            ns = pc.PROV if prefix == 'prov' else vc.VOPROV
            dataset.bind(prefix, URIRef(ns.uri))

    def _encode_container(self, container, graph, shortcuts):
        for record in container.records:
            if record.is_element():
                self._encode_element(record, graph)
            elif record.is_relation():
                self._encode_relation(record, graph, shortcuts)
            else:  # pragma: no cover
                logger.warning('RDF: the record %s is not written.', record)

    def _encode_element(self, record, graph):
        if record.identifier is None:  # pragma: no cover
            return
        node = URIRef(record.identifier.uri)
        record_type = record.get_type()
        prov_class = ELEMENT_CLASSES.get(record_type, _prov('Entity'))
        graph.add((node, RDF.type, prov_class))
        if URIRef(record_type.uri) != prov_class:
            graph.add((node, RDF.type, URIRef(record_type.uri)))
        for attr, value in record.attributes:
            for predicate, obj in self._attribute_triples(attr, value):
                graph.add((node, predicate, obj))

    def _encode_relation(self, record, graph, shortcuts):
        record_type = record.get_type()
        relation = RELATION_BY_TYPE.get(record_type)
        formal = [(attr, value) for attr, value in record.formal_attributes]
        if relation is None or not formal or formal[0][1] is None:
            logger.warning('RDF: the relation %s is not written.', record)
            return
        subject_attr, subject = formal[0]
        subject_node = URIRef(subject.uri)
        # what the qualified node says
        triples = []
        if relation.prov_class is not None:
            triples.append((RDF.type, relation.prov_class))
        if URIRef(record_type.uri) != relation.prov_class:
            triples.append((RDF.type, URIRef(record_type.uri)))
        for attr, value in record.attributes:
            if attr != subject_attr:
                triples.extend(self._attribute_triples(attr, value, relation.properties))
        if record.identifier is not None:
            node = URIRef(record.identifier.uri)
        else:
            node = self._anonymous_node(graph, subject_node, relation.qualified, triples)
        graph.add((subject_node, relation.qualified, node))
        for predicate, obj in triples:
            graph.add((node, predicate, obj))
        # a relation that PROV-O does not qualify (no prov class) has no other form than its shortcut
        if (shortcuts or relation.prov_class is None) and len(formal) > 1 \
                and isinstance(formal[1][1], QualifiedName):
            graph.add((subject_node, relation.shortcut, URIRef(formal[1][1].uri)))

    def _anonymous_node(self, graph, subject, predicate, triples):
        """Blank node of a relation without identifier, named after its content.

        The name does not depend on the order of the records, so the same document is always written the same way
        (which is useful to follow the changes of a file in a repository). Identical relations, which are
        interchangeable, are numbered. The graph is part of the name, as a blank node belongs to the whole file.
        """
        content = '|'.join([str(graph.identifier), subject.n3(), predicate.n3()]
                           + sorted(p.n3() + ' ' + o.n3() for p, o in triples))
        label = 'r' + hashlib.sha1(content.encode('utf-8')).hexdigest()[:12]
        self._repeated[label] += 1
        return BNode(label if self._repeated[label] == 1 else '%s_%d' % (label, self._repeated[label]))

    def _attribute_triples(self, attr, value, properties=None):
        """(predicate, object) pairs for an attribute of a record."""
        if attr == pc.PROV_TYPE and isinstance(value, QualifiedName):
            return [(RDF.type, URIRef(value.uri))]
        predicate = (properties or {}).get(attr) or ATTRIBUTE_TO_PROPERTY.get(attr) or URIRef(attr.uri)
        return [(predicate, self._to_rdf(value))]

    @staticmethod
    def _to_rdf(value):
        if isinstance(value, QualifiedName):
            return URIRef(value.uri)
        if isinstance(value, Identifier):
            return RDFLiteral(value.uri, datatype=XSD.anyURI)
        if isinstance(value, prov.model.Literal):
            datatype = URIRef(value.datatype.uri) if value.datatype is not None else None
            if value.langtag:
                return RDFLiteral(str(value.value), lang=value.langtag)
            return RDFLiteral(str(value.value), datatype=datatype)
        if isinstance(value, (bool, int, float, str)) or hasattr(value, 'isoformat'):  # bool, numbers, dates
            return RDFLiteral(value)
        return RDFLiteral(str(value))

    # -- Decoding ---------------------------------------------------------------------------------------------------

    def _decode_graph(self, graph, container, names):
        types = defaultdict(set)
        for subject, _, rdf_type in graph.triples((None, RDF.type, None)):
            if isinstance(rdf_type, URIRef):
                types[subject].add(rdf_type)
        # elements first, then the relations
        for subject in sorted(types, key=str):
            if isinstance(subject, URIRef):
                self._decode_element(graph, container, names, subject, types[subject])
        covered = set()  # (relation, subject, object) written with a qualified node
        for relation in RELATIONS:
            for subject, _, node in sorted(graph.triples((None, relation.qualified, None)), key=str):
                if isinstance(subject, URIRef):
                    covered.add(self._decode_qualified(graph, container, names, relation, subject, node, types))
        for relation in RELATIONS:
            for subject, _, obj in sorted(graph.triples((None, relation.shortcut, None)), key=str):
                if isinstance(subject, URIRef) and isinstance(obj, URIRef) \
                        and (relation.qualified, subject, obj) not in covered:
                    record_type = self._relation_type(relation, set(), has_node=False)
                    attrs = _formal_attributes(record_type)
                    container.new_record(record_type, None, [(attrs[0], names.qname(subject)),
                                                            (attrs[1], names.qname(obj))])

    @staticmethod
    def _relation_type(relation, node_types, has_node=True):
        """Record type of a relation: the VOProv one, unless the PROV-O class is the only one it is typed with."""
        if relation.prov_type is None:
            return relation.voprov_type
        if has_node and URIRef(relation.voprov_type.uri) in node_types:
            return relation.voprov_type
        return relation.prov_type  # plain PROV-O: a shortcut, or a node typed with the PROV-O class

    def _decode_element(self, graph, container, names, subject, node_types):
        record_type = next((t for t in VOPROV_ELEMENT_TYPES if URIRef(t.uri) in node_types), None)
        if record_type is None:
            record_type = next((PROV_ELEMENT_BY_CLASS[c] for c in PROV_ELEMENT_BY_CLASS if c in node_types), None)
        if record_type is None:
            return  # a bundle, or a resource that is only mentioned
        implied = (ELEMENT_CLASSES[record_type], URIRef(record_type.uri))
        attributes = [(pc.PROV_TYPE, names.qname(t)) for t in sorted(node_types, key=str) if t not in implied]
        for predicate, obj in sorted(graph.predicate_objects(subject), key=str):
            if predicate == RDF.type or predicate in STRUCTURAL_PREDICATES:
                continue
            attributes.append((PROPERTY_TO_ATTRIBUTE.get(predicate) or names.qname(predicate),
                               names.value(obj)))
        container.new_record(record_type, names.qname(subject), attributes)

    def _decode_qualified(self, graph, container, names, relation, subject, node, types):
        node_types = types.get(node, set())
        record_type = self._relation_type(relation, node_types)
        formal = _formal_attributes(record_type)
        inverse = dict((uri, attr) for attr, uri in relation.properties.items())
        attributes = [(formal[0], names.qname(subject))]
        implied = [URIRef(relation.voprov_type.uri), relation.prov_class,
                   URIRef(relation.prov_type.uri) if relation.prov_type is not None else None]
        for t in sorted(node_types, key=str):
            if t not in implied:
                attributes.append((pc.PROV_TYPE, names.qname(t)))
        obj = None
        for predicate, value in sorted(graph.predicate_objects(node), key=str):
            if predicate == RDF.type:
                continue
            attr = inverse.get(predicate) or PROPERTY_TO_ATTRIBUTE.get(predicate) or names.qname(predicate)
            if isinstance(value, BNode):
                continue  # a nested anonymous resource, which cannot be an attribute value
            attributes.append((attr, names.value(value)))
            if attr == formal[1] and isinstance(value, URIRef):
                obj = value
        identifier = names.qname(node) if isinstance(node, URIRef) else None
        container.new_record(record_type, identifier, attributes)
        return relation.qualified, subject, obj


class _Names(object):
    """Converts RDF terms to the names and values of prov, declaring the namespaces in the document."""

    def __init__(self, dataset, document):
        self.dataset = dataset
        self.document = document

    def qname(self, uri):
        uri = str(uri)
        best = None
        for namespace in self.document.namespaces:
            if uri.startswith(namespace.uri) and len(uri) > len(namespace.uri) \
                    and (best is None or len(namespace.uri) > len(best.uri)):
                best = namespace
        if best is None:
            cut = max(uri.rfind('#'), uri.rfind('/')) + 1
            if cut == 0 or cut == len(uri):
                cut = len(uri) - 1
            best = self.document.add_namespace(Namespace(self._prefix(uri[:cut]), uri[:cut]))
            return best[uri[cut:]]
        return best[uri[len(best.uri):]]

    def _prefix(self, namespace_uri):
        for prefix, uri in self.dataset.namespaces():
            if str(uri) == namespace_uri and prefix:
                return prefix
        used = set(ns.prefix for ns in self.document.namespaces)
        n = 1
        while 'ns%d' % n in used:
            n += 1
        return 'ns%d' % n

    def value(self, term):
        if isinstance(term, URIRef):
            return self.qname(term)
        if isinstance(term, BNode):
            return str(term)
        if term.language:
            return prov.model.Literal(str(term), langtag=term.language)
        if term.datatype == XSD.anyURI:
            return Identifier(str(term))
        python_value = term.toPython()
        if isinstance(python_value, RDFLiteral):  # a datatype that is not known
            return prov.model.Literal(str(term), datatype=self.qname(term.datatype))
        return python_value
