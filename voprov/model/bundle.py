# -*- coding: utf-8 -*-
import io
import itertools
import os
import logging
import shutil
import tempfile
import dateutil.parser
import requests
from prov.model import (ProvException, ProvDocument, ProvBundle, first)
from urllib.parse import urlparse

from voprov import serializers
from voprov.constants import *
from voprov.model.records import *
from voprov.model.namespaces import VOProvNamespaceManager

__author__ = 'Jean-Francois Sornay'
__email__ = 'jeanfrancois.sornay@gmail.com'

logger = logging.getLogger(__name__)


def _ensure_datetime(value):
    if isinstance(value, str):
        return dateutil.parser.parse(value)
    else:
        return value


class VOProvBundle(ProvBundle):
    """Adaptation of prov bundle to VOProv Bundle"""

    def __init__(self, records=None, identifier=None, namespaces=None,
                 document=None, label=""):
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
        if label:
            self.label = label
        else:
            self.label = identifier
        self._namespaces = VOProvNamespaceManager(
            namespaces,
            parent=(document._namespaces if document is not None else None)
        )

    def unified(self):
        """
        Unifies all records in the bundle that haves same identifiers

        :returns: :py:class:`VOProvBundle` -- the new unified bundle.
        """
        unified_records = self._unified_records()
        bundle = VOProvBundle(
            records=unified_records, identifier=self.identifier
        )
        return bundle

    def unified_relations(self):
        """
        Unifies all relations in the bundle that have same __repr__ (i.e. type, identifier if set, e1, e2)

        :returns: :py:class:`VOProvBundle` -- the new unified bundle.
        """
        hash_records = []
        if self.is_document():
            for bundle in self._bundles:
                self._bundles[bundle] = self._bundles[bundle].unified_relations()
        for record in self._records:
            if record.is_relation():
                hash_records.append(hash(str(record)))
            else:
                hash_records.append(hash(record))
        for hash_record in list(set(hash_records)):
            while hash_records.count(hash_record) > 1:
                rec_index = hash_records.index(hash_record)
                self._records.pop(rec_index)
                hash_records.pop(rec_index)
        return self

    def get_w3c(self, document=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if self.is_document():
            w3c_records = ProvDocument(namespaces=self.namespaces)
        else:
            w3c_records = ProvBundle(identifier=self.identifier, namespaces=self.namespaces, document=document)

        if self.is_document():
            for bundle in self.bundles:
                if isinstance(bundle, VOProvBundle):
                    w3c_records.add_bundle(bundle.get_w3c(document=w3c_records))
                else:
                    w3c_records.add_bundle(bundle)

        if self.records:
            for record in self.records:
                if hasattr(record, "get_w3c"):
                    record.get_w3c(w3c_records)
                else:
                    w3c_records.add_record(record)

        return w3c_records

    def activity(self, identifier, name=None, startTime=None, endTime=None, comment=None,
                 activityDescription=None, other_attributes=None):
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
        :param activityDescription:     Description object or identifier.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if name is not None:
            other_attributes.update({VOPROV_ATTR_NAME: name})
        if comment is not None:
            other_attributes.update({VOPROV['comment']: comment})
        if activityDescription is not None:
            self.description(identifier, activityDescription)
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_ACTIVITY, identifier, {
                VOPROV_ATTR_STARTTIME: startTime,
                VOPROV_ATTR_ENDTIME: endTime
            },
            other_attributes
        )

    def entity(self, identifier, name=None, location=None, generatedAtTime=None, invalidatedAtTime=None, comment=None, entityDescription=None, other_attributes=None):
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
        :param entityDescription:       Description object or identifier.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if name is not None:
            other_attributes.update({VOPROV_ATTR_NAME: name})
        if location is not None:
            other_attributes.update({VOPROV['location']: location})
        if generatedAtTime is not None:
            other_attributes.update({VOPROV['generatedAtTime']: generatedAtTime})
        if invalidatedAtTime is not None:
            other_attributes.update({VOPROV['invalidatedAtTime']: invalidatedAtTime})
        if comment is not None:
            other_attributes.update({VOPROV['comment']: comment})
        if entityDescription is not None:
            self.description(identifier, entityDescription)
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_ENTITY, identifier, None, other_attributes
        )

    def valueEntity(self, identifier, value, name=None, location=None, generatedAtTime=None, invalidatedAtTime=None, comment=None, valueDescription=None, other_attributes=None):
        """
        Creates a new value entity.

        :param identifier:              Identifier for new value entity.
        :param value:                   The value of the entity. If a corresponding ValueDescription.valueType
                                        attribute is set, the value string can be interpreted by this valueType.
        :param name:                    A human-readable name for the entity.
        :param location:                A path or spatial coordinates, e.g., a URL, latitude-longitude coordinates
                                        on Earth, the name of a place.
        :param generatedAtTime:         Date and time at which the entity was created (e.g., timestamp of a file).
        :param invalidatedAtTime:       Date and time of invalidation of the entity. After that date, the entity is
                                        no longer available for any use.
        :param comment:                 Text containing specific comments on the value entity.
        :param valueDescription:        Description object or identifier.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if name is not None:
            other_attributes.update({VOPROV_ATTR_NAME: name})
        if location is not None:
            other_attributes.update({VOPROV['location']: location})
        if generatedAtTime is not None:
            other_attributes.update({VOPROV['generatedAtTime']: generatedAtTime})
        if invalidatedAtTime is not None:
            other_attributes.update({VOPROV['invalidatedAtTime']: invalidatedAtTime})
        if comment is not None:
            other_attributes.update({VOPROV['comment']: comment})
        if value is not None:
            other_attributes.update({VOPROV['value']: value})
        if valueDescription is not None:
            self.description(identifier, valueDescription)
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(VOPROV_VALUE_ENTITY, identifier, None, other_attributes)

    def datasetEntity(self, identifier, name=None, location=None, generatedAtTime=None, invalidatedAtTime=None, comment=None, datasetDescription=None, other_attributes=None):
        """
        Creates a new data set entity.

        :param identifier:              Identifier for new data set entity.
        :param name:                    A human-readable name for the data set entity.
        :param location:                A path or spatial coordinates, e.g., a URL, latitude-longitude coordinates
                                        on Earth, the name of a place.
        :param generatedAtTime:         Date and time at which the entity was created (e.g., timestamp of a file).
        :param invalidatedAtTime:       Date and time of invalidation of the entity. After that date, the entity is
                                        no longer available for any use.
        :param comment:                 Text containing specific comments on the data set entity.
        :param datasetDescription:      Description object or identifier.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if name is not None:
            other_attributes.update({VOPROV_ATTR_NAME: name})
        if location is not None:
            other_attributes.update({VOPROV['location']: location})
        if generatedAtTime is not None:
            other_attributes.update({VOPROV['generatedAtTime']: generatedAtTime})
        if invalidatedAtTime is not None:
            other_attributes.update({VOPROV['invalidatedAtTime']: invalidatedAtTime})
        if comment is not None:
            other_attributes.update({VOPROV['comment']: comment})
        if datasetDescription is not None:
            self.description(identifier, datasetDescription)
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(VOPROV_DATASET_ENTITY, identifier, None, other_attributes)

    def configFile(self, identifier, name, location, comment=None, configFileDescription=None, other_attributes=None):
        """
        Creates a new config file.

        :param identifier:              Identifier for new config file.
        :param name:                    A human-readable name for the config file.
        :param location:                A path to the config file, e.g., a URL/URI.
        :param comment:                 Text containing comments on the config file.
        :param configFileDescription:   Description object or identifier.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if comment is not None:
            other_attributes.update({VOPROV['comment']: comment})
        if configFileDescription is not None:
            self.description(identifier, configFileDescription)
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(VOPROV_CONFIGURATION_FILE, identifier, {
            VOPROV_ATTR_NAME: name,
            VOPROV_ATTR_LOCATION: location
        }, other_attributes)

    def parameter(self, identifier, name, value, parameterDescription=None, other_attributes=None):
        """
        Creates a new parameter.

        :param identifier:              Identifier for new parameter.
        :param name:                    A human-readable name for the parameter.
        :param value:                   The value of the parameter. If a corresponding ParameterDescription.valueType
                                        attribute is set, the value string can be interpreted by this valueType.
        :param parameterDescription:    Description object or identifier.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        # TODO: idparam should be generated: act_id:param_name
        if parameterDescription is not None:
            self.description(identifier, parameterDescription)
        return self.new_record(VOPROV_CONFIGURATION_PARAMETER   , identifier, {
            VOPROV_ATTR_NAME: name,
            VOPROV_ATTR_VALUE: value,
            PROV_LABEL: name + " = " + str(value)
        }, other_attributes)

    def agent(self, identifier, name=None, type=None, comment=None, email=None, affiliation=None, phone=None,
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
        if name is not None:
            other_attributes.update({VOPROV_ATTR_NAME: name})
        if type is not None:
            other_attributes.update({VOPROV['type']: type})
        if comment is not None:
            other_attributes.update({VOPROV['comment']: comment})
        if email is not None:
            other_attributes.update({VOPROV['email']: email})
        if affiliation is not None:
            other_attributes.update({VOPROV['affiliation']: affiliation})
        if phone is not None:
            other_attributes.update({VOPROV['phone']: phone})
        if address is not None:
            other_attributes.update({VOPROV['address']: address})
        if url is not None:
            other_attributes.update({VOPROV['url']: url})
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(VOPROV_AGENT, identifier, None, other_attributes)

    def usage(self, activity, entity=None, usageDescription=None, role=None, time=None,
              identifier=None, other_attributes=None):
        """
        Creates a new usage record for an activity.

        :param activity:                Activity or a string identifier for the entity.
        :param entity:                  Entity or string identifier of the entity involved in
        :param usageDescription:        Identifier of the usage description which describe this usage.
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
            other_attributes.update({VOPROV_ATTR_ROLE: role})
        if usageDescription is not None:
            other_attributes.update({VOPROV['descriptor']: usageDescription})
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_USAGE, identifier, {
                VOPROV_ATTR_ACTIVITY: activity,
                VOPROV_ATTR_ENTITY: entity,
                VOPROV_ATTR_TIME: _ensure_datetime(time)},
            other_attributes
        )

    def generation(self, entity, activity=None, generationDescription=None, role=None, time=None,
                   identifier=None, other_attributes=None):
        """
        Creates a new generation record for an entity.

        :param entity:                  Entity or a string identifier for the entity.
        :param activity:                Activity or string identifier of the activity involved in
                                        the generation (default: None).
        :param generationDescription:   Identifier of the generation description which describe this generation.
        :param role:                    Function of the entity with respect to the activity.
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
            other_attributes.update({VOPROV_ATTR_ROLE: role})
        if generationDescription is not None:
            other_attributes.update({VOPROV['descriptor']: generationDescription})
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_GENERATION, identifier, {
                VOPROV_ATTR_ENTITY: entity,
                VOPROV_ATTR_ACTIVITY: activity,
                VOPROV_ATTR_TIME: _ensure_datetime(time)
            },
            other_attributes
        )

    def start(self, activity, trigger=None, starter=None, time=None,
              identifier=None, other_attributes=None):
        """
        Creates a new start record for an activity.

        :param activity: Activity or a string identifier for the entity.
        :param trigger: Entity triggering the start of this activity.
        :param starter: Optionally extra activity to state a qualified start
            through which the trigger entity for the start is generated
            (default: None).
        :param time: Optional time for the start (default: None).
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        :param identifier: Identifier for new start record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        return self.new_record(
            VOPROV_START, identifier, {
                VOPROV_ATTR_ACTIVITY: activity,
                VOPROV_ATTR_TRIGGER: trigger,
                VOPROV_ATTR_STARTER: starter,
                VOPROV_ATTR_TIME: _ensure_datetime(time)
            },
            other_attributes
        )

    def end(self, activity, trigger=None, ender=None, time=None,
            identifier=None, other_attributes=None):
        """
        Creates a new end record for an activity.

        :param activity: Activity or a string identifier for the entity.
        :param trigger: trigger: Entity triggering the end of this activity.
        :param ender: Optionally extra activity to state a qualified end
            through which the trigger entity for the end is generated
            (default: None).
        :param time: Optional time for the end (default: None).
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        :param identifier: Identifier for new end record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        return self.new_record(
            VOPROV_END, identifier, {
                VOPROV_ATTR_ACTIVITY: activity,
                VOPROV_ATTR_TRIGGER: trigger,
                VOPROV_ATTR_ENDER: ender,
                VOPROV_ATTR_TIME: _ensure_datetime(time)
            },
            other_attributes
        )

    def invalidation(self, entity, activity=None, time=None, identifier=None,
                     other_attributes=None):
        """
        Creates a new invalidation record for an entity.

        :param entity: Entity or a string identifier for the entity.
        :param activity: Activity or string identifier of the activity involved in
            the invalidation (default: None).
        :param time: Optional time for the invalidation (default: None).
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        :param identifier: Identifier for new invalidation record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        return self.new_record(
            VOPROV_INVALIDATION, identifier, {
                VOPROV_ATTR_ENTITY: entity,
                VOPROV_ATTR_ACTIVITY: activity,
                VOPROV_ATTR_TIME: _ensure_datetime(time)
            },
            other_attributes
        )

    def communication(self, informed, informant, identifier=None,
                      other_attributes=None):
        """
        Creates a new communication record for an entity.

        :param informed: The informed activity (relationship destination).
        :param informant: The informing activity (relationship source).
        :param identifier: Identifier for new communication record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        return self.new_record(
            VOPROV_COMMUNICATION, identifier, {
                VOPROV_ATTR_INFORMED: informed,
                VOPROV_ATTR_INFORMANT: informant
            },
            other_attributes
        )

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
            other_attributes.update({VOPROV_ATTR_ROLE: role})
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_ATTRIBUTION, identifier, {
                VOPROV_ATTR_ENTITY: entity,
                VOPROV_ATTR_AGENT: agent
            },
            other_attributes
        )

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
            other_attributes.update({VOPROV_ATTR_ROLE: role})
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_ASSOCIATION, identifier, {
                VOPROV_ATTR_ACTIVITY: activity,
                VOPROV_ATTR_AGENT: agent,
                VOPROV_ATTR_PLAN: plan
            },
            other_attributes
        )

    def delegation(self, delegate, responsible, activity=None, identifier=None,
                   other_attributes=None):
        """
        Creates a new delegation record on behalf of an agent.

        :param delegate: Agent delegating the responsibility (relationship source).
        :param responsible: Agent the responsibility is delegated to (relationship
            destination).
        :param activity: Optionally extra activity to state qualified delegation
            internally (default: None).
        :param identifier: Identifier for new association record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        return self.new_record(
            VOPROV_DELEGATION, identifier, {
                VOPROV_ATTR_DELEGATE: delegate,
                VOPROV_ATTR_RESPONSIBLE: responsible,
                VOPROV_ATTR_ACTIVITY: activity
            },
            other_attributes
        )

    def influence(self, influencee, influencer, identifier=None,
                  other_attributes=None):
        """
        Creates a new influence record between two entities, activities or agents.

        :param influencee: Influenced entity, activity or agent (relationship
            source).
        :param influencer: Influencing entity, activity or agent (relationship
            destination).
        :param identifier: Identifier for new influence record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        return self.new_record(
            VOPROV_INFLUENCE, identifier, {
                VOPROV_ATTR_INFLUENCEE: influencee,
                VOPROV_ATTR_INFLUENCER: influencer
            },
            other_attributes
        )

    def derivation(self, generatedEntity, usedEntity, activity=None,
                   generation=None, usage=None,
                   identifier=None, other_attributes=None):
        """
        Creates a new derivation record for a generated entity from a used entity.

        :param generatedEntity: Entity or a string identifier for the generated
            entity (relationship source).
        :param usedEntity: Entity or a string identifier for the used entity
            (relationship destination).
        :param activity: Activity or string identifier of the activity involved in
            the derivation (default: None).
        :param generation: Optionally extra activity to state qualified generation
            through a generation (default: None).
        :param usage: XXX (default: None).
        :param identifier: Identifier for new derivation record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        attributes = {VOPROV_ATTR_GENERATED_ENTITY: generatedEntity,
                      VOPROV_ATTR_USED_ENTITY: usedEntity,
                      VOPROV_ATTR_ACTIVITY: activity,
                      VOPROV_ATTR_GENERATION: generation,
                      VOPROV_ATTR_USAGE: usage}
        return self.new_record(
            VOPROV_DERIVATION, identifier, attributes, other_attributes
        )

    def revision(self, generatedEntity, usedEntity, activity=None,
                 generation=None, usage=None,
                 identifier=None, other_attributes=None):
        """
        Creates a new revision record for a generated entity from a used entity.

        :param generatedEntity: Entity or a string identifier for the generated
            entity (relationship source).
        :param usedEntity: Entity or a string identifier for the used entity
            (relationship destination).
        :param activity: Activity or string identifier of the activity involved in
            the revision (default: None).
        :param generation: Optionally to state qualified revision through a
            generation activity (default: None).
        :param usage: XXX (default: None).
        :param identifier: Identifier for new revision record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        record = self.derivation(
            generatedEntity, usedEntity, activity, generation, usage,
            identifier, other_attributes
        )
        record.add_asserted_type(VOPROV['Revision'])
        return record

    def quotation(self, generatedEntity, usedEntity, activity=None,
                  generation=None, usage=None,
                  identifier=None, other_attributes=None):
        """
        Creates a new quotation record for a generated entity from a used entity.

        :param generatedEntity: Entity or a string identifier for the generated
            entity (relationship source).
        :param usedEntity: Entity or a string identifier for the used entity
            (relationship destination).
        :param activity: Activity or string identifier of the activity involved in
            the quotation (default: None).
        :param generation: Optionally to state qualified quotation through a
            generation activity (default: None).
        :param usage: XXX (default: None).
        :param identifier: Identifier for new quotation record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        record = self.derivation(
            generatedEntity, usedEntity, activity, generation, usage,
            identifier, other_attributes
        )
        record.add_asserted_type(VOPROV['Quotation'])
        return record

    def primary_source(self, generatedEntity, usedEntity, activity=None,
                       generation=None, usage=None,
                       identifier=None, other_attributes=None):
        """
        Creates a new primary source record for a generated entity from a used
        entity.

        :param generatedEntity: Entity or a string identifier for the generated
            entity (relationship source).
        :param usedEntity: Entity or a string identifier for the used entity
            (relationship destination).
        :param activity: Activity or string identifier of the activity involved in
            the primary source (default: None).
        :param generation: Optionally to state qualified primary source through a
            generation activity (default: None).
        :param usage: XXX (default: None).
        :param identifier: Identifier for new primary source record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        record = self.derivation(
            generatedEntity, usedEntity, activity, generation, usage,
            identifier, other_attributes
        )
        record.add_asserted_type(VOPROV['PrimarySource'])
        return record

    def specialization(self, specificEntity, generalEntity):
        """
        Creates a new specialisation record for a specific from a general entity.

        :param specificEntity: Entity or a string identifier for the specific
            entity (relationship source).
        :param generalEntity: Entity or a string identifier for the general entity
            (relationship destination).
        """
        return self.new_record(
            VOPROV_SPECIALIZATION, None, {
                VOPROV_ATTR_SPECIFIC_ENTITY: specificEntity,
                VOPROV_ATTR_GENERAL_ENTITY: generalEntity
            }
        )

    def alternate(self, alternate1, alternate2):
        """
        Creates a new alternate record between two entities.

        :param alternate1: Entity or a string identifier for the first entity
            (relationship source).
        :param alternate2: Entity or a string identifier for the second entity
            (relationship destination).
        """
        return self.new_record(
            VOPROV_ALTERNATE, None, {
                VOPROV_ATTR_ALTERNATE1: alternate1,
                VOPROV_ATTR_ALTERNATE2: alternate2
            },
        )

    def mention(self, specificEntity, generalEntity, bundle):
        """
        Creates a new mention record for a specific from a general entity.

        :param specificEntity: Entity or a string identifier for the specific
            entity (relationship source).
        :param generalEntity: Entity or a string identifier for the general entity
            (relationship destination).
        :param bundle: XXX
        """
        return self.new_record(
            VOPROV_MENTION, None, {
                VOPROV_ATTR_SPECIFIC_ENTITY: specificEntity,
                VOPROV_ATTR_GENERAL_ENTITY: generalEntity,
                VOPROV_ATTR_BUNDLE: bundle
            }
        )

    def collection(self, identifier, other_attributes=None):
        """
        Creates a new collection record for a particular record.

        :param identifier: Identifier for new collection record.
        :param other_attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        record = self.new_record(
            VOPROV_ENTITY, identifier, None, other_attributes
        )
        record.add_asserted_type(VOPROV['Collection'])
        return record

    def membership(self, collection, entity):
        """
        Creates a new membership record for an entity to a collection.

        :param collection: Collection the entity is to be added to.
        :param entity: Entity to be added to the collection.
        """
        return self.new_record(
            VOPROV_MEMBERSHIP, None, {
                VOPROV_ATTR_COLLECTION: collection,
                VOPROV_ATTR_ENTITY: entity
            }
        )


    # DESCRIPTIONS functions

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
            other_attributes.update({VOPROV['version']: version})
        if description is not None:
            other_attributes.update({VOPROV['description']: description})
        if docurl is not None:
            other_attributes.update({VOPROV['docurl']: docurl})
        if type is not None:
            other_attributes.update({VOPROV['type']: type})
        if subtype is not None:
            other_attributes.update({VOPROV['subtype']: subtype})
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_ACTIVITY_DESCRIPTION, identifier, {
                VOPROV_ATTR_NAME: name
            },
            other_attributes
        )

    def entityDescription(self, identifier, name, description=None, docurl=None, type=None, other_attributes=None):
        """
        Creates a new activity description.

        :param identifier:              Identifier for new activity description.
        :param name:                    Human readable name describing the entity.
        :param description:             A descriptive text for this kind of entity.
        :param docurl:                  Link to more documentation.
        :param type:                    Type of the entity.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if description is not None:
            other_attributes.update({VOPROV['description']: description})
        if docurl is not None:
            other_attributes.update({VOPROV['docurl']: docurl})
        if type is not None:
            other_attributes.update({VOPROV['type']: type})
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_ENTITY_DESCRIPTION, identifier, {
                VOPROV_ATTR_NAME: name
            },
            other_attributes
        )

    def valueDescription(self, identifier, name, valueType, description=None, docurl=None, type=None,
                         unit=None, ucd=None, utype=None, other_attributes=None):
        """
        Creates a new activity description.

        :param identifier:              Identifier for new activity description.
        :param name:                    Human readable name describing the entity.
        :param valueType:               Description of a value from a combination of datatype, arraysize and xtype
                                        following VOTable 1.3.
        :param description:             A descriptive text for this kind of entity.
        :param docurl:                  Link to more documentation.
        :param type:                    Type of the entity.
        :param unit:                    VO unit, see C.1.1 and Derriere and Gray et al. (2014) for recommended unit
                                        representation.
        :param ucd:                     Unified Content Descriptor, supplying a standardized classification of the
                                        physical quantity.
        :param utype:                   Utype, meant to express the role of the value in the context of an external
                                        data model.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if description is not None:
            other_attributes.update({VOPROV['description']: description})
        if docurl is not None:
            other_attributes.update({VOPROV['docurl']: docurl})
        if type is not None:
            other_attributes.update({VOPROV['type']: type})
        if unit is not None:
            other_attributes.update({VOPROV['unit']: unit})
        if ucd is not None:
            other_attributes.update({VOPROV['ucd']: ucd})
        if utype is not None:
            other_attributes.update({VOPROV['utype']: utype})
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_VALUE_DESCRIPTION, identifier, {
                VOPROV_ATTR_NAME: name,
                VOPROV_ATTR_VALUE_TYPE: valueType
            },
            other_attributes
        )

    def datasetDescription(self, identifier, name, contentType, description=None, docurl=None, type=None, other_attributes=None):
        """
        Creates a new dataset description.

        :param identifier:              Identifier for new data set description.
        :param name:                    Human readable name describing the data set.
        :param contentType:             Format of the data set, MIME type when applicable.
        :param description:             A descriptive text for this kind of data set.
        :param docurl:                  Link to more documentation.
        :param type:                    Type of the data set.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if description is not None:
            other_attributes.update({VOPROV['description']: description})
        if docurl is not None:
            other_attributes.update({VOPROV['docurl']: docurl})
        if type is not None:
            other_attributes.update({VOPROV['type']: type})
        if len(other_attributes) == 0:
            other_attributes = None
        return self.new_record(
            VOPROV_DATASET_DESCRIPTION, identifier, {
                VOPROV_ATTR_NAME: name,
                VOPROV_ATTR_CONTENT_TYPE: contentType
            },
            other_attributes
        )

    def usageDescription(self, identifier, activityDescription, role, description=None, type=None,
                         multiplicity=None, entityDescription=None, other_attributes=None):
        """
        Creates a new usage description.

        :param identifier:              Identifier for new usage description.
        :param activityDescription:     Identifier or object of the activity description linked to the usage description.
        :param role:                    Function of the entity with respect to the activity.
        :param description:             A descriptive text for this kind of usage.
        :param type:                    Type of relation.
        :param multiplicity:            Number of expected input entities to be used with the given role.
        :param entityDescription:       Identifier(s) or object(s) of entity descriptions linked to the usage description
                                        (can be a list),
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if description is not None:
            other_attributes.update({VOPROV['description']: description})
        if type is not None:
            other_attributes.update({VOPROV['type']: type})
        if multiplicity is not None:
            other_attributes.update({VOPROV['multiplicity']: multiplicity})
        if len(other_attributes) == 0:
            other_attributes = None
        self.relate(identifier, activityDescription)
        if entityDescription:
            if not isinstance(entityDescription, list):
                entityDescription = [entityDescription]
            for ed_item in entityDescription:
                self.relate(ed_item, identifier)
        return self.new_record(
            VOPROV_USAGE_DESCRIPTION, identifier, {
                VOPROV_ATTR_ROLE: role
            },
            other_attributes
        )

    def generationDescription(self, identifier, activityDescription, role, description=None, type=None,
                              multiplicity=None, entityDescription=None, other_attributes=None):
        """
        Creates a new generation description.

        :param identifier:              Identifier for new generation description.
        :param activityDescription:     Identifier or object of the activity description linked to the generation
                                        description.
        :param role:                    Function of the entity with respect to the activity.
        :param description:             A descriptive text for this kind of generation.
        :param type:                    Type of relation.
        :param multiplicity:            Number of expected input entities to be generated with the given role.
        :param entityDescription:       Identifier(s) or object(s) of entity descriptions linked to the generation
                                        description (can be a list),
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if description is not None:
            other_attributes.update({VOPROV['description']: description})
        if type is not None:
            other_attributes.update({VOPROV['type']: type})
        if multiplicity is not None:
            other_attributes.update({VOPROV['multiplicity']: multiplicity})
        if len(other_attributes) == 0:
            other_attributes = None
        self.relate(identifier, activityDescription)
        if entityDescription:
            if not isinstance(entityDescription, list):
                entityDescription = [entityDescription]
            for ed_item in entityDescription:
                self.relate(ed_item, identifier)
        return self.new_record(
            VOPROV_GENERATION_DESCRIPTION, identifier, {
                VOPROV_ATTR_ROLE: role
            },
            other_attributes
        )

    def configFileDescription(self, identifier, activityDescription, name, contentType, description=None, other_attributes=None):
        """
        Creates a new config file description.

        :param identifier:              Identifier for new config file description.
        :param activityDescription:     Identifier or object of the activity description linked to the config file
                                        description.
        :param name:                    A human-readable name for the config file.
        :param contentType:             Format of the config file, MIME type when applicable.
        :param description:             A descriptive text for this config file.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if description is not None:
            other_attributes.update({VOPROV['description']: description})
        if len(other_attributes) == 0:
            other_attributes = None
        self.relate(identifier, activityDescription)
        return self.new_record(
            VOPROV_CONFIG_FILE_DESCRIPTION, identifier, {
                VOPROV_ATTR_NAME: name,
                VOPROV_ATTR_CONTENT_TYPE: contentType
            },
            other_attributes
        )

    def parameterDescription(self, identifier, activityDescription, name, valueType, description=None, unit=None,
                             ucd=None, utype=None, min=None, max=None, options=None, default=None,
                             other_attributes=None):
        """
        Creates a new parameter description.

        :param identifier:              Identifier for new generation description.
        :param activityDescription:     Identifier or object of the activity description linked to the generation
                                        description.
        :param name:                    Function of the entity with respect to the activity.
        :param valueType:               Description of a value from a combination of datatype, arraysize and xtype.
        :param description:             A descriptive text for this kind of generation.
        :param unit:                    VO unit, see C.1.1 and Derriere and Gray et al. (2014) for recommended unit
                                        representation.
        :param ucd:                     Unified Content Descriptor, supplying a standardized classification of
                                        the physical quantity.
        :param utype:                   Utype, meant to express the role of the parameter in the context of an external
                                        data model.
        :param min:                     Minimum value as a string whose value can be interpreted by the valueType
                                        attribute.
        :param max:                     Maximum value as a string whose value can be interpreted by the valueType
                                        attribute.
        :param options:                 Array of possible values.
        :param default:                 The default value of the parameter as a string whose value can be interpreted
                                        by the valueType attribute.
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        if other_attributes is None:
            other_attributes = {}
        if description is not None:
            other_attributes.update({VOPROV['description']: description})
        if unit is not None:
            other_attributes.update({VOPROV['unit']: unit})
        if ucd is not None:
            other_attributes.update({VOPROV['ucd']: ucd})
        if utype is not None:
            other_attributes.update({VOPROV['utype']: utype})
        if min is not None:
            other_attributes.update({VOPROV['min']: min})
        if max is not None:
            other_attributes.update({VOPROV['max']: max})
        if options is not None:
            other_attributes.update({VOPROV['options']: options})
        if default is not None:
            other_attributes.update({VOPROV['default']: default})
        if len(other_attributes) == 0:
            other_attributes = None
        self.relate(identifier, activityDescription)
        return self.new_record(
            VOPROV_PARAMETER_DESCRIPTION, identifier, {
                VOPROV_ATTR_NAME: name,
                VOPROV_ATTR_VALUE_TYPE: valueType
            },
            other_attributes
        )


    # RELATION functions

    def description(self, described, descriptor, identifier=None):
        """
        Creates a new description relation record.

        :param described:               The described element (relationship destination).
        :param descriptor:              The describing element (relationship source).
        :param identifier:              Identifier for new isDescribedBy relation record.
        """
        if isinstance(described, ProvRelation):
            described = described.identifier if described.identifier is not None else described.get_type().localpart

        return self.new_record(
            VOPROV_DESCRIPTION_RELATION, identifier, {
                VOPROV_ATTR_DESCRIBED: described,
                VOPROV_ATTR_DESCRIPTOR: descriptor
            },
            None
        )

    def configuration(self, configured, configurator, artefactType="Parameter", identifier=None):
        """
        Creates a new description relation record.

        :param configured:              The configured element (relationship destination).
        :param configurator:            The configuring element (relationship source).
        :param artefactType:            Literal that takes the value "Parameter" or "ConfigFile" to indicate the type
                                        of class pointed by the WasConfiguredBy instance.
        :param identifier:              Identifier for new wasConfiguredBy relation record.
        """

        return self.new_record(
            VOPROV_CONFIGURATION_RELATION, identifier, {
                VOPROV_ATTR_CONFIGURED: configured,
                VOPROV_ATTR_CONFIGURATOR: configurator,
                VOPROV_ATTR_ARTEFACT_TYPE: artefactType
            },
            None
        )

    def relate(self, related, relator, identifier=None):
        """
        Creates a new relatedTo relation record.

        :param related:                 The related element (relationship destination).
        :param relator:                 The relator element (relationship source).
        :param identifier:              Identifier for new relatedTo record.
        """
        return self.new_record(
            VOPROV_RELATED_TO_RELATION, identifier, {
                VOPROV_ATTR_RELATED: related,
                VOPROV_ATTR_RELATOR: relator
            },
            None
        )

    def reference(self, referenced, referrer, identifier=None):
        """
                Creates a new hadReference relation record.

                :param referenced:              The referenced element (relationship destination).
                :param referrer:                The referrer element (relationship source).
                :param identifier:              Identifier for new hadReference record.
                """
        return self.new_record(
            VOPROV_REFERENCE_RELATION, identifier, {
                VOPROV_ATTR_REFERENCED: referenced,
                VOPROV_ATTR_REFERRER: referrer
            },
            None
        )


    def _dedicated_bundle(self, kind, identifier):
        """Get (or create) the bundle dedicated to the descriptions or configuration of an element.

        :param kind:                    'description' or 'configuration'.
        :param identifier:              Identifier of the described/configured element.

        The bundle is named ``#<kind>#<identifier>``, a local name in the default namespace. If no default
        namespace is set (such a name is not valid), the ``voprov`` namespace is used explicitly.
        """
        idbundle = '#%s#%s' % (kind, str(identifier).replace(":", "#"))
        if self.valid_qualified_name(idbundle) is None:
            idbundle = 'voprov:' + idbundle
        valid_id = self.valid_qualified_name(idbundle)
        if valid_id in self._bundles:
            return self._bundles[valid_id]
        return self.bundle(idbundle)

    # ADD_ functions

    def add_activity_description(self, description_id, name, version = None, activity_id= None, description = None, docurl = None, type = None, subtype = None, other_attributes = None):
        """add a description to an activity in the dedicated bundle"""
        bundle_description = self._dedicated_bundle('description', description_id)
        ad = bundle_description.activityDescription(description_id, name, version, description, docurl, type, subtype, other_attributes)
        if activity_id:
            self.description(activity_id, description_id)
        return ad

    def add_entity_description(self, description_id, name, entity_id = None, description=None, docurl=None, type=None, other_attributes=None):
        """add a description to an entity"""
        ed = self.entityDescription(description_id, name, description, docurl, type, other_attributes)
        if entity_id:
            self.description(entity_id, description_id)
        return ed

    def add_dataset_description(self, description_id, name, contentType, entity_id = None, description=None, docurl=None, type=None, other_attributes=None):
        """add a description to a dataset entity"""
        ed = self.datasetDescription(description_id, name, contentType, description=description, docurl=docurl, type=type, other_attributes=other_attributes)
        if entity_id:
            self.description(entity_id, description_id)
        return ed

    def add_usage_description(self, identifier, activityDescription, role, description=None, type=None, multiplicity=None, entityDescription=None, other_attributes=None):
        """add a description to a usage in the dedicated bundle"""
        bundle_description = self._dedicated_bundle('description', activityDescription)
        return bundle_description.usageDescription(identifier, activityDescription, role, description, type, multiplicity, entityDescription, other_attributes)

    def add_generation_description(self, identifier, activityDescription, role, description=None, type=None, multiplicity=None, entityDescription=None, other_attributes=None):
        """add a description to a generation in the dedicated bundle"""
        bundle_description = self._dedicated_bundle('description', activityDescription)
        return bundle_description.generationDescription(identifier, activityDescription, role, description, type, multiplicity, entityDescription, other_attributes)

    def add_parameter_description(self, identifier, activityDescription, name, valueType, description=None, unit=None, ucd=None, utype=None, min=None, max=None, options=None, default=None, other_attributes=None):
        """add a description to a parameter in the dedicated bundle"""
        bundle_description = self._dedicated_bundle('description', activityDescription)
        return bundle_description.parameterDescription(identifier, activityDescription, name, valueType, description, unit, ucd, utype, min, max, options, default, other_attributes)


    def add_one_step(self, onestep):
        """builds provenance records from onestep dictionary"""

# onestep_1 = {
#     "product_id": "obs:image1b",
#     "product_name": None,
#     "product_location": None,
#     "product_generatedAtTime": None,
#     "product_comment": None,
#     "product_description": None,
#     "product_type": None,
#     "product_content_type": None,
#     "product_docurl": None,
#     "product_role": "bias-subtracted-image",
#     "contact_id": "staff:Emma",
#     "contact_name": None,
#     "contact_type": None,
#     "contact_email": None,
#     "step_id": "ps:2459",
#     "step_name": "ps:bias_subtraction",
#     "step_startTime": None,
#     "step_endTime": None,
#     "step_comment": None,
#     "step_parameters": {},
#     "step_description": "remove the readout noise of the detector from the input image by subtracting a bias image",
#     "step_type": None,
#     "step_docurl": None,
#     "step_software": {},
#     "used_ids": ["obs:image1", "obs:bias"],
#     "generated_ids": [],
#     "process_id": 7531,
#     "process_comment": None,
#     "workflow_name": "ImageCalibration",
#     "workflow_version": None,
#     "workflow_description": None,
#     "workflow_type": None,
#     "workflow_docurl": None,
#     "instrument_id": None,
#     "instrument_location": None,
#     "instrument_name": None,
#     "instrument_description": None,
#     "instrument_type": None,
#     "instrument_docurl": None,
#     "instrument_comment": None,
# }

        onestep_mandatory_keys = ["product_id", "step_id", "used_ids", "generated_ids"]
        for k in onestep_mandatory_keys:
            if not k in onestep:
                raise ProvException('the input dictionary must contain the key: ' + k)
        # Add product entity
        ent = self.datasetEntity(
            onestep["product_id"],
            name=onestep.get("product_name", None),
            location=onestep.get("product_location", None),
            generatedAtTime=onestep.get("product_generatedAtTime", None),
            invalidatedAtTime=onestep.get("product_invalidatedAtTime", None),
            comment=onestep.get("product_comment", None),
        )
        if onestep.get("product_content_type", None):
            ent.add_dataset_description(
                onestep["product_content_type"].replace("/", "_"),
                onestep["product_content_type"],
                onestep["product_content_type"],
            )
        # Add step activity and generation relation
        act = self.activity(
            onestep['step_id'],
            name=onestep.get("step_name", None),
            startTime=onestep.get("step_startTime", None),
            endTime=onestep.get("step_endTime", None),
            comment=onestep.get("step_comment", None),
        )
        gen_attributes = {}
        if onestep.get("product_role", None):
            gen_attributes = {'prov:role': onestep['product_role']}
        ent.wasGeneratedBy(onestep["step_id"], attributes=gen_attributes)
        # ActivityDescription
        if onestep.get("step_name", None):
            act.add_activity_description(
                onestep['step_name'],
                onestep['step_name'],
                version=onestep.get("step_version", None),
                description=onestep.get("step_description", None),
                docurl=onestep.get("step_docurl", None),
                type=onestep.get("step_type", None),
                subtype=onestep.get("step_subtype", None),
            )
        # Add used/generated entity ids
        if "used_ids" in onestep:
            for used_id in onestep["used_ids"]:
                act.add_used_entity(used_id)
        if "generated_ids" in onestep:
            for generated in onestep["generated_ids"]:
                act.add_generated_entity(generated)
        # Add contact
        if onestep.get("contact_name", None):
            ent.add_agent(
                onestep.get("contact_id", onestep["contact_name"]),  # TODO: remove blanks?
                name=onestep.get("contact_name", None),
                type=onestep.get("contact_type", "Person"),
                email=onestep.get("contact_email", None),
                comment=onestep.get("contact_comment", None),
            )
        # Add step parameters
        if onestep.get("step_parameters", None):
            for p,v in onestep['step_parameters'].items():
                act.add_parameter(onestep["step_id"]+":"+p, p, v)
        # add process
        if onestep.get("process_id", None):
            ps = self.activity(
                str(onestep['process_id']),
                name=onestep.get("workflow_name", None),
                comment=onestep.get("process_comment", None),
            )
            if onestep.get("workflow_name", None):
                ps.add_activity_description(
                    onestep['workflow_name'],
                    onestep['workflow_name'],
                    version=onestep.get("workflow_version", None),
                    description=onestep.get("workflow_description", None),
                    docurl=onestep.get("workflow_docurl", None),
                    type=onestep.get("workflow_type", None),
                    subtype=onestep.get("workflow_subtype", None),
                )
            if onestep.get("instrument_id", None):
                inst = self.entity(
                    onestep["instrument_id"],
                    name=onestep.get("instrument_name", None),
                    location=onestep.get("instrument_location", None),
                    comment=onestep.get("instrument_comment", None),
                )
                ps.used(onestep["instrument_id"], attributes={'prov:role': "instrument"})
            act.wasInformedBy(str(onestep['process_id']))
        self.unified_relations()
        return ent
        # END of onestep function

    def get_from_provsap(self, url):
        r = requests.get(url)
        return r.json()

    # update alias of prov function
    wasGeneratedBy = generation
    used = usage
    wasAttributedTo = attribution
    wasAssociatedWith = association
    wasStartedBy = start
    wasEndedBy = end
    wasInvalidatedBy = invalidation
    wasInformedBy = communication
    actedOnBehalfOf = delegation
    wasInfluencedBy = influence
    wasDerivedFrom = derivation
    wasRevisionOf = revision
    wasQuotedFrom = quotation
    hadPrimarySource = primary_source
    alternateOf = alternate
    specializationOf = specialization
    mentionOf = mention
    hadMember = membership

    # alias for voprov's function
    isDescribedBy = description
    isRelatedTo = relate
    wasConfiguredBy = configuration
    hadReference = reference




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
        return '<VOProvDocument>'

    def __eq__(self, other):
        if not isinstance(other, ProvDocument):
            return False
        # Comparing the documents' content
        if not super(VOProvDocument, self).__eq__(other):
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
            new_doc = VOProvDocument()
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
        document = VOProvDocument(self._unified_records())
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
            new_bundle = VOProvBundle(namespaces=bundle.namespaces)
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
        b = VOProvBundle(identifier=valid_id, document=self)
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
                content if not isinstance(content, bytes)
                else content.decode()
            )
            return serializer.deserialize(stream, **args)

        if source is not None:
            if hasattr(source, "read"):
                return serializer.deserialize(source, **args)
            else:
                with open(source) as f:
                    return serializer.deserialize(f, **args)
