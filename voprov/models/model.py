# -*- coding: ISO-8859-1 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import io
import itertools
import os
import shutil
import sys
import tempfile

from prov.model import (ProvException, ProvDocument, ProvBundle, ProvActivity,
                        ProvEntity, ProvUsage, ProvAgent,
                        PROV_REC_CLS, DEFAULT_NAMESPACES, NamespaceManager)
from six.moves.urllib.parse import urlparse

from voprov.models.constants import *
from voprov import serializers
from voprov.models.voprovDescriptions import *
from voprov.models.voprovRelations import *

__author__ = 'Jean-Francois Sornay'
__email__ = 'jean-francois.sornay@etu.umontpellier.fr'

DEFAULT_NAMESPACES.update({'voprov': VOPROV})


class VOProvEntity(ProvEntity):
    """Adaptation of prov Entity to VOProv Entity"""

    def set_name(self, name):
        """Set the name of this entity.

        :param name:                    A human-readable name for the entity.
        """
        self._attributes["voprov:name"] = {name}

    def set_location(self, location):
        """Set the location of this entity.

        :param location:                A path or spatial coordinates, e.g., a URL, latitude-longitude coordinates
                                        on Earth, the name of a place.
        """
        self._attributes["voprov:location"] = {location}

    def set_generatedAtTime(self, generatedAtTime):
        """Set the generated time of this entity.

        :param generatedAtTime:         Date and time at which the entity was created (e.g., timestamp of a file).
        """
        self._attributes["voprov:generatedAtTime"] = {generatedAtTime}

    def set_invalidatedAtTime(self, invalidatedAtTime):
        """Set the invalidated time of this entity.

        :param invalidatedAtTime:       Date and time of invalidation of the entity. After that date, the entity is
                                        no longer available for any use.
        """
        self._attributes["voprov:invalidatedAtTime"] = {invalidatedAtTime}

    def set_comment(self, comment):
        """Set a comment for this entity.

        :param comment:                 Text containing specific comments on the entity.
        """
        self._attributes["voprov:comment"] = {comment}


class VOProvValueEntity(VOProvEntity):
    """Class for VOProv Value Entity"""


class VOProvDataSetEntity(VOProvEntity):
    """Class for VOProv DataSet Entity"""


class VOProvActivity(ProvActivity):
    """Adaptation of prov Activity to VOProv Activity"""

    def set_name(self, name):
        """Set the name of this activity.

        :param name:                    A human-readable name for the activity.
        """
        self._attributes["voprov:name"] = {name}

    def set_comment(self, comment):
        """Set a comment for this activity.

        :param comment:                 Text containing specific comments on the activity.
        """
        self._attributes["voprov:comment"] = {comment}

    def isDescribedBy(self, activity_description, identifier=None):
        """Link an activity description to this activity

        :param activity_description:    Identifier for the activity description link to this activity.
        :param identifier:              Identifier of the description relation created.
        """
        return self._bundle.description(self, activity_description, identifier)


class VOProvAgent(ProvAgent):
    """"""

    def set_name(self, name):
        """Set the name of this activity.

        :param name:                    A human-readable name for the agent.
        """
        self._attributes["voprov:name"] = {name}

    def set_type(self, type):
        """Set the type of this agent.

        :param type:                    Type of the agent.
        """
        self._attributes["voprov:type"] = {type}

    def set_comment(self, comment):
        """Set a comment for this agent.

        :param comment:                 Text containing specific comments on the agent.
        """
        self._attributes["voprov:comment"] = {comment}

    def set_email(self, email):
        """Set an email address for this agent.

        :param email:                    Contact email of the agent.
        """
        self._attributes["voprov:email"] = {email}

    def set_affiliation(self, affiliation):
        """Set an affiliation for this agent.

        :param affiliation:              Affiliation of the agent.
        """
        self._attributes["voprov:affiliation"] = {affiliation}

    def set_phone(self, phone):
        """Set a phone number for this agent.

        :param phone:                   Phone number.
        """
        self._attributes["voprov:phone"] = {phone}

    def set_address(self, address):
        """Set an address for this agent.

        :param address:                  Address of the agent.
        """
        self._attributes["voprov:address"] = {address}

    def set_url(self, url):
        """Set an url for this agent.

        :param url:                      Reference URL to the agent.
        """
        self._attributes["voprov:url"] = {url}


class VOProvUsage(ProvUsage):
    """Adaptation of prov Used relation to VOProv Used relation"""

    def set_role(self, role):
        """Set the role of this usage.

        :param role:              Function of the entity with respect to the activity.
        """
        self._attributes["voprov:role"] = {role}

    def isDescribedBy(self, usage_description, identifier=None):
        """Link an usage description to this used relation.

        :param usage_description:       Identifier of the usage description link to this used relation.
        :param identifier:              Identifier of the description relation created.
        """
        return self._bundle.description(self, usage_description, identifier)


class VOProvNamespaceManager(NamespaceManager):
    """Manages namespaces for VOPROV documents and bundles."""

    def __init__(self, namespaces=None, default=None, parent=None):
        """
        Constructor.

        :param namespaces: Optional namespaces to add to the manager
            (default: None).
        :param default: Optional default namespace to use (default: None).
        :param parent: Optional parent :py:class:`NamespaceManager` to make this
            namespace manager a child of (default: None).
        """
        dict.__init__(self)
        self._default_namespaces = DEFAULT_NAMESPACES
        self._namespaces = {}

        if default is not None:
            self.set_default_namespace(default)
        else:
            self._default = None
        self.parent = parent
        #  TODO check if default is in the default namespaces
        self._anon_id_count = 0
        self._uri_map = dict()
        self._rename_map = dict()
        self._prefix_renamed_map = dict()
        for namespace in self._default_namespaces.values():
            self.add_namespace(namespace)
        self.add_namespaces(namespaces)


class VOProvBundle(ProvBundle):
    """Adaptation of prov bundle to VOProv Bundle"""

    def __init__(self, records=None, identifier=None, namespaces=None,
                 document=None):
        """
        Constructor.

        :param records: Optional iterable of records to add to the bundle
            (default: None).
        :param identifier: Optional identifier of the bundle (default: None).
        :param namespaces: Optional iterable of :py:class:`~prov.identifier.Namespace`s
            to set the document up with (default: None).
        :param document: Optional document to add to the bundle (default: None).
        """
        #  Initializing bundle-specific attributes
        super(VOProvBundle, self).__init__(records, identifier, namespaces, document)
        self._namespaces = VOProvNamespaceManager(
            namespaces,
            parent=(document._namespaces if document is not None else None)
        )
        if records:
            for record in records:
                self.add_record(record)

    def activity(self, identifier, name=None, startTime=None, endTime=None, comment=None,
                 other_attributes=None):
        """
        Creates a new activity.

        :param identifier:              Identifier for new activity.
        :param name:                    A human-readable name for the activity.
        :param startTime:               Optional start time for the activity (default: None).
                                        Either a :py:class:`datetime.datetime` object or a string that can be
                                        parsed by :py:func:`dateutil.parser`.
        :param endTime:                 Optional start time for the activity (default: None).
                                        Either a :py:class:`datetime.datetime` object or a string that can be
                                        parsed by :py:func:`dateutil.parser`.
        :param comment:                 Text containing specific comments on the activity.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if name is not None:
            other_attributes.update({'voprov:name': name})
        if comment is not None:
            other_attributes.update({'voprov:comment': comment})
        if len(other_attributes) is 0:
            other_attributes = None
        return super(VOProvBundle, self).activity(identifier, startTime, endTime, other_attributes)

    def entity(self, identifier, name=None, location=None, generatedAtTime=None, invalidatedAtTime=None,
               comment=None, other_attributes=None):
        """
        Creates a new entity.

        :param identifier:              Identifier for new entity.
        :param name:                    A human-readable name for the entity.
        :param location:                A path or spatial coordinates, e.g., a URL, latitude-longitude coordinates
                                        on Earth, the name of a place.
        :param generatedAtTime:         Date and time at which the entity was created (e.g., timestamp of a file).
        :param invalidatedAtTime:       Date and time of invalidation of the entity. After that date, the entity is
                                        no longer available for any use.
        :param comment:                 Text containing specific comments on the entity.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if name is not None:
            other_attributes.update({'voprov:name': name})
        if location is not None:
            other_attributes.update({'voprov:location': location})
        if generatedAtTime is not None:
            other_attributes.update({'voprov:generatedAtTime': generatedAtTime})
        if invalidatedAtTime is not None:
            other_attributes.update({'voprov:invalidatedAtTime': invalidatedAtTime})
        if comment is not None:
            other_attributes.update({'voprov:comment': comment})
        if len(other_attributes) is 0:
            other_attributes = None
        return super(VOProvBundle, self).entity(identifier, other_attributes)

    def agent(self, identifier, name, type=None, comment=None, email=None, affiliation=None, phone=None,
              address=None, url=None, other_attributes=None):
        """
        Creates a new agent.

        :param name:                    A human-readable name for the agent.
        :param type:                    Type of the agent.
        :param comment:                 Text containing specific comments on the entity.
        :param email:                   Contact email of the agent.
        :param affiliation:             Affiliation of the agent.
        :param phone:                   Phone number.
        :param address:                 Address of the agent.
        :param url:                     Reference URL to the agent.
        :param identifier:              Identifier for new agent.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if type is not None:
            other_attributes.update({'voprov:type': type})
        if comment is not None:
            other_attributes.update({'voprov:comment': comment})
        if email is not None:
            other_attributes.update({'voprov:email': email})
        if affiliation is not None:
            other_attributes.update({'voprov:affiliation': affiliation})
        if phone is not None:
            other_attributes.update({'voprov:phone': phone})
        if address is not None:
            other_attributes.update({'voprov:address': address})
        if url is not None:
            other_attributes.update({'voprov:url': url})

        other_attributes.update({'voprov:name': name})
        return super(VOProvBundle, self).agent(identifier, other_attributes)

    def usage(self, activity, entity=None, role=None, time=None, identifier=None,
              other_attributes=None):
        """
        Creates a new usage record for an activity.

        :param activity:                Activity or a string identifier for the entity.
        :param entity:                  Entity or string identifier of the entity involved in
                                        the usage relationship (default: None).
        :param role:                    Function of the entity with respect to the activity.
        :param time:                    Optional time for the usage (default: None).
                                        Either a :py:class:`datetime.datetime` object or a string that can be
                                        parsed by :py:func:`dateutil.parser`.
        :param identifier:              Identifier for new usage record.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if role is not None:
            other_attributes.update({'voprov:role': role})
        if len(other_attributes) is 0:
            other_attributes = None
        return super(VOProvBundle, self).usage(activity, entity, time, identifier, other_attributes)

    def generation(self, entity, activity=None, role=None, time=None, identifier=None,
                   other_attributes=None):
        """
        Creates a new generation record for an entity.

        :param role:                    Function of the entity with respect to the activity.
        :param entity:                  Entity or a string identifier for the entity.
        :param activity:                Activity or string identifier of the activity involved in
                                        the generation (default: None).
        :param time:                    Optional time for the generation (default: None).
                                        Either a :py:class:`datetime.datetime` object or a string that can be
                                        parsed by :py:func:`dateutil.parser`.
        :param identifier:              Identifier for new generation record.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if role is not None:
            other_attributes.update({'voprov:role': role})
        if len(other_attributes) is 0:
            other_attributes = None
        return super(VOProvBundle, self).generation(entity, activity, time, identifier, other_attributes)

    def attribution(self, entity, agent, role=None, identifier=None,
                    other_attributes=None):
        """
        Creates a new attribution record between an entity and an agent.

        :param role:                    Function of the agent with respect to the entity.
        :param entity:                  Entity or a string identifier for the entity (relationship
            source).
        :param agent:                   Agent or string identifier of the agent involved in the
                                        attribution (relationship destination).
        :param identifier:              Identifier for new attribution record.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if role is not None:
            other_attributes.update({'voprov:role': role})
        if len(other_attributes) is 0:
            other_attributes = None
        return super(VOProvBundle, self).attribution(entity, agent, identifier, other_attributes)

    def association(self, activity, agent=None, role=None, plan=None, identifier=None,
                    other_attributes=None):
        """
        Creates a new association record for an activity.

        :param role:                    Function of the agent with respect to the activity.
        :param activity:                Activity or a string identifier for the activity.
        :param agent:                   Agent or string identifier of the agent involved in the
                                        association (default: None).
        :param plan:                    Optionally extra entity to state qualified association through
                                        an internal plan (default: None).
        :param identifier:              Identifier for new association record.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if role is not None:
            other_attributes.update({'voprov:role': role})
        if len(other_attributes) is 0:
            other_attributes = None
        return super(VOProvBundle, self).association(activity, agent, plan, identifier, other_attributes)

    def activityDescription(self, identifier, name, version=None, description=None, docurl=None, type=None,
                            subtype=None, other_attributes=None):
        """
        Creates a new activity description.

        :param identifier:              Identifier for new activity description.
        :param name:                    Human readable name describing the activity.
        :param version:                 A version number, if applicable (e.g., for the code used)
        :param description:             Additional free text describing how the activity works internally.
        :param docurl:                  Link to further documentation on this activity, e.g., a paper, the source code
                                        in a version control system etc.
        :param type:                    Type of the activity.
        :param subtype:                 More specific subtype of the activity.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if version is not None:
            other_attributes.update({'voprov:version': version})
        if description is not None:
            other_attributes.update({'voprov:description': description})
        if docurl is not None:
            other_attributes.update({'voprov:docurl': docurl})
        if type is not None:
            other_attributes.update({'voprov:type': type})
        if subtype is not None:
            other_attributes.update({'voprov:subtype': subtype})
        if len(other_attributes) is 0:
            other_attributes = None
        return self.new_record(
            VOPROV_ACTIVITY_DESCRIPTION, identifier, {
                VOPROV_ATTR_NAME: name
            },
            other_attributes
        )

    def usageDescription(self, identifier, activity_description, role, description=None, type=None,
                         multiplicity=None, other_attributes=None):
        """
        Creates a new usage description.

        :param identifier:              Identifier for new activity description.
        :param activity_description:    Identifier or object of the activity description linked to the usage description.
        :param role:                    Function of the entity with respect to the activity.
        :param description:             A descriptive text for this kind of usage.
        :param type:                    Type of relation.
        :param multiplicity:            Number of expected input entities to be used with the given role.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if description is not None:
            other_attributes.update({'voprov:description': description})
        if type is not None:
            other_attributes.update({'voprov:type': type})
        if multiplicity is not None:
            other_attributes.update({'voprov:multiplicity': multiplicity})
        if len(other_attributes) is 0:
            other_attributes = None
        self.relate(identifier, activity_description)
        return self.new_record(
            VOPROV_USAGE_DESCRIPTION, identifier, {
                VOPROV_ATTR_ROLE: role
            },
            other_attributes
        )

    def generationDescription(self, identifier, activity_description, role, description=None, type=None,
                              multiplicity=None, other_attributes=None):
        """
        Creates a new usage description.

        :param identifier:              Identifier for new activity description.
        :param activity_description:    Identifier or object of the activity description linked to the usage description.
        :param role:                    Function of the entity with respect to the activity.
        :param description:             A descriptive text for this kind of usage.
        :param type:                    Type of relation.
        :param multiplicity:            Number of expected input entities to be used with the given role.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if description is not None:
            other_attributes.update({'voprov:description': description})
        if type is not None:
            other_attributes.update({'voprov:type': type})
        if multiplicity is not None:
            other_attributes.update({'voprov:multiplicity': multiplicity})
        if len(other_attributes) is 0:
            other_attributes = None
        self.relate(identifier, activity_description)
        return self.new_record(
            VOPROV_GENERATION_DESCRIPTION, identifier, {
                VOPROV_ATTR_ROLE: role
            },
            other_attributes
        )

    def description(self, described, descriptor, identifier=None):
        """
        Creates a new description relation record.

        :param described:               The described element (relationship destination).
        :param descriptor:              The describing element (relationship source).
        :param identifier:              Identifier for new isDescribedBy relation record.
        """
        return self.new_record(
            VOPROV_DESCRIPTION_RELATION, identifier, {
                VOPROV_ATTR_DESCRIBED: described,
                VOPROV_ATTR_DESCRIPTOR: descriptor
            },
            None
        )

    def relate(self, related, relator, identifier=None):
        """
        Creates a new relatedTo relation record.

        :param related:                 The related element (relationship destination).
        :param relator:                 The relator element (relationship source).
        :param identifier:              Identifier for new description record.
        """
        return self.new_record(
            VOPROV_RELATED_TO_RELATION, identifier, {
                VOPROV_ATTR_RELATED: related,
                VOPROV_ATTR_RELATOR: relator
            },
            None
        )

    # update alias of prov function
    wasGeneratedBy = generation
    used = usage
    wasAttributedTo = attribution
    wasAssociatedWith = association

    # alias for voprov's function
    isDescribedBy = description
    isRelatedTo = relate


class VOProvDocument(ProvDocument, VOProvBundle):
    """Adaptation of prov document to VOProvenance Document."""

    def __init__(self, records=None, namespaces=None):
        """
        Constructor.

        :param records: Optional records to add to the document (default: None).
        :param namespaces: Optional iterable of :py:class:`~prov.identifier.Namespace`s
            to set the document up with (default: None).
        """
        VOProvBundle.__init__(
            self, records=records, identifier=None, namespaces=namespaces
        )
        self._bundles = dict()

    def __repr__(self):
        return '<ProvDocument>'

    def __eq__(self, other):
        if not isinstance(other, ProvDocument):
            return False
        # Comparing the documents' content
        if not super(ProvDocument, self).__eq__(other):
            return False

        # Comparing the documents' bundles
        for b_id, bundle in self._bundles.items():
            if b_id not in other._bundles:
                return False
            other_bundle = other._bundles[b_id]
            if bundle != other_bundle:
                return False

        # Everything is the same
        return True

    def is_document(self):
        """
        `True` if the object is a document, `False` otherwise.

        :return: bool
        """
        return True

    def is_bundle(self):
        """
        `True` if the object is a bundle, `False` otherwise.

        :return: bool
        """
        return False

    def has_bundles(self):
        """
        `True` if the object has at least one bundle, `False` otherwise.

        :return: bool
        """
        return len(self._bundles) > 0

    @property
    def bundles(self):
        """
        Returns bundles contained in the document

        :return: Iterable of :py:class:`ProvBundle`.
        """
        return self._bundles.values()

    # Transformations
    def flattened(self):
        """
        Flattens the document by moving all the records in its bundles up
        to the document level.

        :returns: :py:class:`ProvDocument` -- the (new) flattened document.
        """
        if self._bundles:
            # Creating a new document for all the records
            new_doc = ProvDocument()
            bundled_records = itertools.chain(
                *[b.get_records() for b in self._bundles.values()]
            )
            for record in itertools.chain(self._records, bundled_records):
                new_doc.add_record(record)
            return new_doc
        else:
            # returning the same document
            return self

    def unified(self):
        """
        Returns a new document containing all records having same identifiers
        unified (including those inside bundles).

        :return: :py:class:`ProvDocument`
        """
        document = ProvDocument(self._unified_records())
        document._namespaces = self._namespaces
        for bundle in self.bundles:
            unified_bundle = bundle.unified()
            document.add_bundle(unified_bundle)
        return document

    def update(self, other):
        """
        Append all the records of the *other* document/bundle into this document.
        Bundles having same identifiers will be merged.

        :param other: The other document/bundle whose records to be appended.
        :type other: :py:class:`ProvDocument` or :py:class:`ProvBundle`
        :returns: None.
        """
        if isinstance(other, ProvBundle):
            for record in other.get_records():
                self.add_record(record)
            if other.has_bundles():
                for bundle in other.bundles:
                    if bundle.identifier in self._bundles:
                        self._bundles[bundle.identifier].update(bundle)
                    else:
                        new_bundle = self.bundle(bundle.identifier)
                        new_bundle.update(bundle)
        else:
            raise ProvException(
                'ProvDocument.update(): The other is not a ProvDocument or '
                'ProvBundle instance (%s)' % type(other)
            )

    # Bundle operations
    def add_bundle(self, bundle, identifier=None):
        """
        Add a bundle to the current document.

        :param bundle: The bundle to add to the document.
        :type bundle: :py:class:`ProvBundle`
        :param identifier: The (optional) identifier to use for the bundle
            (default: None). If none given, use the identifier from the bundle
            itself.
        """
        if not isinstance(bundle, ProvBundle):
            raise ProvException(
                'Only a ProvBundle instance can be added as a bundle in a '
                'ProvDocument.'
            )

        if bundle.is_document():
            if bundle.has_bundles():
                raise ProvException(
                    'Cannot add a document with nested bundles as a bundle.'
                )
            # Make it a new ProvBundle
            new_bundle = ProvBundle(namespaces=bundle.namespaces)
            new_bundle.update(bundle)
            bundle = new_bundle

        if identifier is None:
            identifier = bundle.identifier

        if not identifier:
            raise ProvException('The provided bundle has no identifier')

        # Link the bundle namespace manager to the document's
        bundle._namespaces.parent = self._namespaces

        valid_id = bundle.valid_qualified_name(identifier)
        # IMPORTANT: Rewriting the bundle identifier for consistency
        bundle._identifier = valid_id

        if valid_id in self._bundles:
            raise ProvException('A bundle with that identifier already exists')

        self._bundles[valid_id] = bundle
        bundle._document = self

    def bundle(self, identifier):
        """
        Returns a new bundle from the current document.

        :param identifier: The identifier to use for the bundle.
        :return: :py:class:`ProvBundle`
        """
        if identifier is None:
            raise ProvException(
                'An identifier is required. Cannot create an unnamed bundle.'
            )
        valid_id = self.valid_qualified_name(identifier)
        if valid_id is None:
            raise ProvException(
                'The provided identifier "%s" is not valid' % identifier
            )
        if valid_id in self._bundles:
            raise ProvException('A bundle with that identifier already exists')
        b = ProvBundle(identifier=valid_id, document=self)
        self._bundles[valid_id] = b
        return b

    # Serializing and deserializing
    def serialize(self, destination=None, format='json', **args):
        """
        Serialize the :py:class:`ProvDocument` to the destination.

        Available serializers can be queried by the value of
        `:py:attr:~prov.serializers.Registry.serializers` after loading them via
        `:py:func:~prov.serializers.Registry.load_serializers()`.

        :param destination: Stream object to serialize the output to. Default is
            `None`, which serializes as a string.
        :param format: Serialization format (default: 'json'), defaulting to
            PROV-JSON.
        :return: Serialization in a string if no destination was given,
            None otherwise.
        """
        serializer = serializers.get(format)(self)
        if destination is None:
            stream = io.StringIO()
            serializer.serialize(stream, **args)
            return stream.getvalue()
        if hasattr(destination, "write"):
            stream = destination
            serializer.serialize(stream, **args)
        else:
            location = destination
            scheme, netloc, path, params, _query, fragment = urlparse(location)
            if netloc != "":
                print("WARNING: not saving as location " +
                      "is not a local file reference")
                return
            fd, name = tempfile.mkstemp()
            stream = os.fdopen(fd, "wb")
            serializer.serialize(stream, **args)
            stream.close()
            if hasattr(shutil, "move"):
                shutil.move(name, path)
            else:
                shutil.copy(name, path)
                os.remove(name)

    @staticmethod
    def deserialize(source=None, content=None, format='json', **args):
        """
        Deserialize the :py:class:`ProvDocument` from source (a stream or a
        file path) or directly from a string content.

        Available serializers can be queried by the value of
        `:py:attr:~prov.serializers.Registry.serializers` after loading them via
        `:py:func:~prov.serializers.Registry.load_serializers()`.

        Note: Not all serializers support deserialization.

        :param source: Stream object to deserialize the PROV document from
            (default: None).
        :param content: String to deserialize the PROV document from
            (default: None).
        :param format: Serialization format (default: 'json'), defaulting to
            PROV-JSON.
        :return: :py:class:`ProvDocument`
        """
        serializer = serializers.get(format)()

        if content is not None:
            # io.StringIO only accepts unicode strings
            stream = io.StringIO(
                content if not isinstance(content, six.binary_type)
                else content.decode()
            )
            return serializer.deserialize(stream, **args)

        if source is not None:
            if hasattr(source, "read"):
                return serializer.deserialize(source, **args)
            else:
                with open(source) as f:
                    return serializer.deserialize(f, **args)


#  adding voprov class to the prov class mappings
PROV_REC_CLS.update({
    # link prov class to their voprov representation
    PROV_ENTITY: VOProvEntity,
    PROV_ACTIVITY: VOProvActivity,
    PROV_AGENT: VOProvAgent,
    PROV_USAGE: VOProvUsage,

    # voprov description
    VOPROV_ACTIVITY_DESCRIPTION: VOProvActivityDescription,
    VOPROV_USAGE_DESCRIPTION: VOProvUsageDescription,

    # voprov configuration

    # voprov relation
    VOPROV_DESCRIPTION_RELATION: VOProvIsDescribedBy,
    VOPROV_RELATED_TO_RELATION: VOProvIsRelatedTo,
})
