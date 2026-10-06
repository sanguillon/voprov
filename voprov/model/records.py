# -*- coding: utf-8 -*-
"""VOProv records: elements, relations, descriptions and configurations (extending prov.model records)."""
from prov.model import (ProvElement, ProvRelation, ProvBundle, ProvEntity, ProvActivity, ProvUsage, ProvAgent,
                        ProvGeneration, ProvAssociation, ProvCommunication, ProvStart, ProvEnd,
                        ProvInvalidation, ProvDerivation, ProvAttribution, ProvDelegation, ProvInfluence,
                        ProvSpecialization, ProvAlternate, ProvMention, ProvMembership, first)
from voprov.constants import *

__author__ = 'Jean-Francois Sornay'
__email__ = 'jeanfrancois.sornay@gmail.com'


class VOProvEntity(ProvEntity):
    """Adaptation of prov Entity to VOProv Entity"""

    _prov_type = VOPROV_ENTITY

    def set_name(self, name):
        """Set the name of this entity.

        :param name:                    A human-readable name for the entity.
        """
        self._attributes[VOPROV_ATTR_NAME] = {name}

    def set_location(self, location):
        """Set the location of this entity.

        :param location:                A path or spatial coordinates, e.g., a URL, latitude-longitude coordinates
                                        on Earth, the name of a place.
        """
        self._attributes[VOPROV['location']] = {location}

    def set_generatedAtTime(self, generatedAtTime):
        """Set the generated time of this entity.

        :param generatedAtTime:         Date and time at which the entity was created (e.g., timestamp of a file).
        """
        self._attributes[VOPROV['generatedAtTime']] = {generatedAtTime}

    def set_invalidatedAtTime(self, invalidatedAtTime):
        """Set the invalidated time of this entity.

        :param invalidatedAtTime:       Date and time of invalidation of the entity. After that date, the entity is
                                        no longer available for any use.
        """
        self._attributes[VOPROV['invalidatedAtTime']] = {invalidatedAtTime}

    def set_comment(self, comment):
        """Set a comment for this entity.

        :param comment:                 Text containing specific comments on the entity.
        """
        self._attributes[VOPROV['comment']] = {comment}

    def isDescribedBy(self, activityDescription, identifier=None):
        """Link an activity description to this activity
        :param activityDescription:     Identifier for the activity description link to this activity.
        :param identifier:              Identifier of the description relation created.
        """
        return self._bundle.description(self, activityDescription, identifier)

    def wasGeneratedBy(self, activity, time=None, attributes=None):
        """
        Creates a new generation record to this entity.

        :param activity: Activity or string identifier of the activity involved in
            the generation (default: None).
        :param time: Optional time for the generation (default: None).
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.generation(
            self, activity, time=time, other_attributes=attributes
        )
        return self

    def wasInvalidatedBy(self, activity, time=None, attributes=None):
        """
        Creates a new invalidation record for this entity.

        :param activity: Activity or string identifier of the activity involved in
            the invalidation (default: None).
        :param time: Optional time for the invalidation (default: None).
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.invalidation(
            self, activity, time=time, other_attributes=attributes
        )
        return self

    def wasDerivedFrom(self, usedEntity, activity=None, generation=None,
                       usage=None, attributes=None):
        """
        Creates a new derivation record for this entity from a used entity.

        :param usedEntity: Entity or a string identifier for the used entity.
        :param activity: Activity or string identifier of the activity involved in
            the derivation (default: None).
        :param generation: Optionally extra activity to state qualified derivation
            through an internal generation (default: None).
        :param usage: Optionally extra entity to state qualified derivation through
            an internal usage (default: None).
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.derivation(
            self, usedEntity, activity=activity, generation=generation, usage=usage,
            other_attributes=attributes
        )
        return self

    def wasAttributedTo(self, agent, attributes=None):
        """
        Creates a new attribution record between this entity and an agent.

        :param agent: Agent or string identifier of the agent involved in the
            attribution.
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.attribution(self, agent, other_attributes=attributes)
        return self

    def alternateOf(self, alternate2):
        """
        Creates a new alternate record between this and another entity.

        :param alternate2: Entity or a string identifier for the second entity.
        """
        self._bundle.alternate(self, alternate2)
        return self

    def specializationOf(self, generalEntity):
        """
        Creates a new specialisation record for this from a general entity.

        :param generalEntity: Entity or a string identifier for the general entity.
        """
        self._bundle.specialization(self, generalEntity)
        return self

    def hadMember(self, entity):
        """
        Creates a new membership record to an entity for a collection.

        :param entity: Entity to be added to the collection.
        """
        self._bundle.membership(self, entity)
        return self

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        entity = ProvEntity(bundle, self.identifier, self.attributes)
        entity.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        return bundle.add_record(entity)

    def add_agent(self, identifier, name=None, type=None, comment=None, email=None, affiliation=None, phone=None, address=None, url=None, other_attributes=None):
        """add an agent to an entity with the relation wasAttributedTo"""
        agent = self._bundle.agent(identifier, name, type, comment, email, affiliation, phone, address, url, other_attributes)
        self._bundle.wasAttributedTo(self, agent)
        self._bundle.unified()
        return agent

    def add_entity_description(self, description_id, name, description = None, docurl = None, type = None, other_attributes = None):
        ed = self._bundle.add_entity_description(self, description_id, name, description, docurl, type, other_attributes)
        return ed


class VOProvValueEntity(VOProvEntity):
    """Class for VOProv Value Entity"""
    _prov_type = VOPROV_VALUE_ENTITY

    def set_value(self, value):
        """Set a value for this entity.

        :param value:                 Text containing specific comments on the entity.
        """
        self._attributes[VOPROV['value']] = {value}


class VOProvDataSetEntity(VOProvEntity):
    """Class for VOProv DataSet Entity"""
    _prov_type = VOPROV_DATASET_ENTITY

    def add_dataset_description(self, description_id, name, contentType = None, description = None, docurl = None, type = None, other_attributes = None):
        ed = self._bundle.add_dataset_description(self, description_id, name, contentType, description, docurl, type, other_attributes)
        return ed


class VOProvActivity(ProvActivity):
    """Adaptation of prov Activity to VOProv Activity"""
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_STARTTIME, VOPROV_ATTR_ENDTIME)
    _prov_type = VOPROV_ACTIVITY

    def set_name(self, name):
        """Set the name of this activity.

        :param name:                    A human-readable name for the activity.
        """
        self._attributes[VOPROV_ATTR_NAME] = {name}

    def set_comment(self, comment):
        """Set a comment for this activity.

        :param comment:                 Text containing specific comments on the activity.
        """
        self._attributes[VOPROV['comment']] = {comment}

    def isDescribedBy(self, activityDescription, identifier=None):
        """Link an activity description to this activity

        :param activityDescription:     Identifier for the activity description link to this activity.
        :param identifier:              Identifier of the description relation created.
        """
        return self._bundle.description(self, activityDescription, identifier)

    def set_time(self, startTime=None, endTime=None):
        """
        Sets the time this activity took place.

        :param startTime: Start time for the activity.
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        :param endTime: Start time for the activity.
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        """
        if startTime is not None:
            self._attributes[VOPROV_ATTR_STARTTIME] = {startTime}
        if endTime is not None:
            self._attributes[VOPROV_ATTR_ENDTIME] = {endTime}

    def get_startTime(self):
        """
        Returns the time the activity started.

        :return: :py:class:`datetime.datetime`
        """
        values = self._attributes[VOPROV_ATTR_STARTTIME]
        return first(values) if values else None

    def get_endTime(self):
        """
        Returns the time the activity ended.

        :return: :py:class:`datetime.datetime`
        """
        values = self._attributes[VOPROV_ATTR_ENDTIME]
        return first(values) if values else None

    # Convenient assertions that take the current ProvActivity as the first
    # (formal) argument
    def used(self, entity, time=None, attributes=None):
        """
        Creates a new usage record for this activity.

        :param entity: Entity or string identifier of the entity involved in
            the usage relationship (default: None).
        :param time: Optional time for the usage (default: None).
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.usage(self, entity, time=time, other_attributes=attributes)
        return self

    def wasInformedBy(self, informant, attributes=None):
        """
        Creates a new communication record for this activity.

        :param informant: The informing activity (relationship source).
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.communication(
            self, informant, other_attributes=attributes
        )
        return self

    def wasStartedBy(self, trigger, starter=None, time=None, attributes=None):
        """
        Creates a new start record for this activity. The activity did not exist
        before the start by the trigger.

        :param trigger: Entity triggering the start of this activity.
        :param starter: Optionally extra activity to state a qualified start
            through which the trigger entity for the start is generated
            (default: None).
        :param time: Optional time for the start (default: None).
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.start(
            self, trigger, starter, time, other_attributes=attributes
        )
        return self

    def wasEndedBy(self, trigger, ender=None, time=None, attributes=None):
        """
        Creates a new end record for this activity.

        :param trigger: Entity triggering the end of this activity.
        :param ender: Optionally extra activity to state a qualified end through
            which the trigger entity for the end is generated (default: None).
        :param time: Optional time for the end (default: None).
            Either a :py:class:`datetime.datetime` object or a string that can be
            parsed by :py:func:`dateutil.parser`.
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.end(
            self, trigger, ender, time, other_attributes=attributes
        )
        return self

    def wasAssociatedWith(self, agent, plan=None, attributes=None):
        """
        Creates a new association record for this activity.

        :param agent: Agent or string identifier of the agent involved in the
            association (default: None).
        :param plan: Optionally extra entity to state qualified association through
            an internal plan (default: None).
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.association(
            self, agent=agent, plan=plan, other_attributes=attributes
        )
        return self

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        activity = ProvActivity(bundle, self.identifier, self.extra_attributes)
        activity.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvActivity, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        activity.add_attributes({super_formal: value})
                        break
        return bundle.add_record(activity)

    def add_parameter(self, idparam, nameparam, valueparam, parameterDescription=None, other_attributes=None):
        """Add a parameter to an activity with the relation wasConfiguredBy in a dedicated bundle"""
        bundle_config = self._bundle._dedicated_bundle('configuration', self.identifier._str)
        param = bundle_config.parameter(idparam, nameparam, valueparam, parameterDescription, other_attributes)
        self._bundle.wasConfiguredBy(self, param)
        self._bundle.unified_relations()
        return param

    def add_configFile(self, idfile, namefile, locationfile, comment=None, configFileDescription=None,
                       other_attributes=None):
        """add a configuration file to an activity with the relation wasConfiguredBy in a dedicated bundle"""
        bundle_config = self._bundle._dedicated_bundle('configuration', self.identifier._str)
        file = bundle_config.configFile(idfile, namefile, locationfile, comment, configFileDescription, other_attributes)
        self._bundle.wasConfiguredBy(self, file, 'ConfigFile')
        return file

    def add_agent(self, identifier, name=None, type=None, comment=None, email=None, affiliation=None, phone=None, address=None, url=None, other_attributes=None):
        """add an agent to an activity with the relation wasAssociatedWith"""
        agent = self._bundle.agent(identifier, name, type, comment, email, affiliation, phone, address, url, other_attributes)
        self._bundle.wasAssociatedWith(self, agent)
        self._bundle.unified()
        return agent

    def add_used_entity(self, identifier, name=None, location=None, generatedAtTime=None, invalidatedAtTime=None, comment=None, entityDescription=None, other_attributes=None, time=None, attributes=None):
        """add a entity to an activity with the relation used"""
        entity = self._bundle.entity(identifier, name, location, generatedAtTime, invalidatedAtTime,
               comment, entityDescription, other_attributes)
        self.used(entity, time, attributes)
        return entity

    def add_generated_entity(self, identifier, name=None, location=None, generatedAtTime=None, invalidatedAtTime=None,
               comment=None, entityDescription=None, other_attributes=None, time=None, attributes=None):
        """add a entity to an activity with the relation wasGeneratedBy"""
        entity = self._bundle.entity(identifier, name, location, generatedAtTime, invalidatedAtTime,
               comment, entityDescription, other_attributes)
        entity.wasGeneratedBy(self, time, attributes)
        return entity

    def add_activity_description(self, ad_id, name, version = None, description = None, docurl = None, type = None, subtype = None, other_attributes = None):
        ad = self._bundle.add_activity_description(ad_id, name, version, self.identifier, description, docurl, type, subtype, other_attributes)
        return ad


class VOProvAgent(ProvAgent):
    """Adaptation of Prov Agent class"""
    _prov_type = VOPROV_AGENT

    def set_name(self, name):
        """Set the name of this activity.

        :param name:                    A human-readable name for the agent.
        """
        self._attributes[VOPROV_ATTR_NAME] = {name}

    def set_type(self, type):
        """Set the type of this agent.

        :param type:                    Type of the agent.
        """
        self._attributes[VOPROV['type']] = {type}

    def set_comment(self, comment):
        """Set a comment for this agent.

        :param comment:                 Text containing specific comments on the agent.
        """
        self._attributes[VOPROV['comment']] = {comment}

    def set_email(self, email):
        """Set an email address for this agent.

        :param email:                    Contact email of the agent.
        """
        self._attributes[VOPROV['email']] = {email}

    def set_affiliation(self, affiliation):
        """Set an affiliation for this agent.

        :param affiliation:              Affiliation of the agent.
        """
        self._attributes[VOPROV['affiliation']] = {affiliation}

    def set_phone(self, phone):
        """Set a phone number for this agent.

        :param phone:                   Phone number.
        """
        self._attributes[VOPROV['phone']] = {phone}

    def set_address(self, address):
        """Set an address for this agent.

        :param address:                  Address of the agent.
        """
        self._attributes[VOPROV['address']] = {address}

    def set_url(self, url):
        """Set an url for this agent.

        :param url:                      Reference URL to the agent.
        """
        self._attributes[VOPROV['url']] = {url}

    def actedOnBehalfOf(self, responsible, activity=None, attributes=None):
        """
        Creates a new delegation record on behalf of this agent.

        :param responsible: Agent the responsibility is delegated to.
        :param activity: Optionally extra activity to state qualified delegation
            internally (default: None).
        :param attributes: Optional other attributes as a dictionary or list
            of tuples to be added to the record optionally (default: None).
        """
        self._bundle.delegation(
            self, responsible, activity, other_attributes=attributes
        )
        return self

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        agent = ProvAgent(bundle, self.identifier, self.attributes)
        agent.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        return bundle.add_record(agent)


class VOProvUsage(ProvUsage):
    """Adaptation of prov Used relation to VOProv Used relation"""
    _prov_type = VOPROV_USAGE
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ACTIVITY, VOPROV_ATTR_ENTITY, VOPROV_ATTR_TIME)

    def set_role(self, role):
        """Set the role of this usage.

        :param role:              Function of the entity with respect to the activity.
        """
        self._attributes[VOPROV_ATTR_ROLE] = {role}

    def isDescribedBy(self, usageDescription, identifier=None):
        """Link an usage description to this used relation.

        :param usageDescription:        Identifier of the usage description link to this used relation.
        :param identifier:              Identifier of the description relation created.
        """
        return self._bundle.description(self, usageDescription, identifier)

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        usage = ProvUsage(bundle, self.identifier, self.extra_attributes)
        usage.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvUsage, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        usage.add_attributes({super_formal: value})
                        break
        return bundle.add_record(usage)


class VOProvGeneration(ProvGeneration):
    """Adaptation of prov generation"""
    _prov_type = VOPROV_GENERATION
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ENTITY, VOPROV_ATTR_ACTIVITY, VOPROV_ATTR_TIME)

    def set_role(self, role):
        """Set the role of this generation.

        :param role: Function of the entity with respect to the activity.
        """
        self._attributes[VOPROV_ATTR_ROLE] = {role}

    def isDescribedBy(self, generationDescription, identifier=None):
        """Link a generation description to this used relation.

        :param generationDescription:   Identifier of the generation description link to this used relation.
        :param identifier:              Identifier of the description relation created.
        """
        return self._bundle.description(self, generationDescription, identifier)

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        generation = ProvGeneration(bundle, self.identifier, self.extra_attributes)
        generation.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvGeneration, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        generation.add_attributes({super_formal: value})
                        break
        return bundle.add_record(generation)


class VOProvCommunication(ProvCommunication):
    """Adaptation of prov Communication relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_INFORMED, VOPROV_ATTR_INFORMANT)

    _prov_type = VOPROV_COMMUNICATION

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        communication = ProvCommunication(bundle, self.identifier, self.extra_attributes)
        communication.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvCommunication, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        communication.add_attributes({super_formal: value})
                        break
        return bundle.add_record(communication)


class VOProvStart(ProvStart):
    """Adaptation of prov Start relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ACTIVITY, VOPROV_ATTR_TRIGGER,
                         VOPROV_ATTR_STARTER, VOPROV_ATTR_TIME)

    _prov_type = VOPROV_START

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        start = ProvStart(bundle, self.identifier, self.extra_attributes)
        start.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvStart, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        start.add_attributes({super_formal: value})
                        break
        return bundle.add_record(start)


class VOProvEnd(ProvEnd):
    """Adaptation of prov End relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ACTIVITY, VOPROV_ATTR_TRIGGER,
                         VOPROV_ATTR_ENDER, VOPROV_ATTR_TIME)

    _prov_type = VOPROV_END

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        end = ProvEnd(bundle, self.identifier, self.extra_attributes)
        end.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvEnd, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        end.add_attributes({super_formal: value})
                        break
        return bundle.add_record(end)


class VOProvInvalidation(ProvInvalidation):
    """Adaptation of prov Invalidation relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ENTITY, VOPROV_ATTR_ACTIVITY, VOPROV_ATTR_TIME)

    _prov_type = VOPROV_INVALIDATION

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        invalidation = ProvInvalidation(bundle, self.identifier, self.extra_attributes)
        invalidation.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvInvalidation, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        invalidation.add_attributes({super_formal: value})
                        break
        return bundle.add_record(invalidation)


class VOProvDerivation(ProvDerivation):
    """Adaptation of prov Derivation relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_GENERATED_ENTITY, VOPROV_ATTR_USED_ENTITY,
                         VOPROV_ATTR_ACTIVITY, VOPROV_ATTR_GENERATION,
                         VOPROV_ATTR_USAGE)

    _prov_type = VOPROV_DERIVATION

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        derivation = ProvDerivation(bundle, self.identifier, self.extra_attributes)
        derivation.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvDerivation, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        derivation.add_attributes({super_formal: value})
                        break
        return bundle.add_record(derivation)


class VOProvAttribution(ProvAttribution):
    """Adaptation of prov Attribution relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ENTITY, VOPROV_ATTR_AGENT)

    _prov_type = VOPROV_ATTRIBUTION

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        attribution = ProvAttribution(bundle, self.identifier, self.extra_attributes)
        attribution.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvAttribution, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        attribution.add_attributes({super_formal: value})
                        break
        return bundle.add_record(attribution)


class VOProvAssociation(ProvAssociation):
    """Adaptation of prov Association relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ACTIVITY, VOPROV_ATTR_AGENT, VOPROV_ATTR_PLAN)

    _prov_type = VOPROV_ASSOCIATION

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        association = ProvAssociation(bundle, self.identifier, self.extra_attributes)
        association.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvAssociation, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        association.add_attributes({super_formal: value})
                        break
        return bundle.add_record(association)


class VOProvDelegation(ProvDelegation):
    """Adaptation of prov Delegation relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_DELEGATE, VOPROV_ATTR_RESPONSIBLE, VOPROV_ATTR_ACTIVITY)

    _prov_type = VOPROV_DELEGATION

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        delegation = ProvDelegation(bundle, self.identifier, self.extra_attributes)
        delegation.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvDelegation, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        delegation.add_attributes({super_formal: value})
                        break
        return bundle.add_record(delegation)


class VOProvInfluence(ProvInfluence):
    """Adaptation of prov Influence relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_INFLUENCEE, VOPROV_ATTR_INFLUENCER)

    _prov_type = VOPROV_INFLUENCE

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        influence = ProvInfluence(bundle, self.identifier, self.extra_attributes)
        influence.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvInfluence, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        influence.add_attributes({super_formal: value})
                        break
        return bundle.add_record(influence)


class VOProvSpecialization(ProvSpecialization):
    """Adaptation of prov Specialization relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_SPECIFIC_ENTITY, VOPROV_ATTR_GENERAL_ENTITY)

    _prov_type = VOPROV_SPECIALIZATION

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        specialization = ProvSpecialization(bundle, self.identifier, self.extra_attributes)
        specialization.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvSpecialization, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        specialization.add_attributes({super_formal: value})
                        break
        return bundle.add_record(specialization)


class VOProvAlternate(ProvAlternate):
    """Adaptation of prov Alternate relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ALTERNATE1, VOPROV_ATTR_ALTERNATE2)

    _prov_type = VOPROV_ALTERNATE

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        alternate = ProvAlternate(bundle, self.identifier, self.extra_attributes)
        alternate.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvAlternate, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        alternate.add_attributes({super_formal: value})
                        break
        return bundle.add_record(alternate)


class VOProvMention(ProvMention, VOProvSpecialization):
    """Adaptation of prov Mention relationship (specific Specialization)."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_SPECIFIC_ENTITY, VOPROV_ATTR_GENERAL_ENTITY,
                         VOPROV_ATTR_BUNDLE)

    _prov_type = VOPROV_MENTION

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        mention = ProvMention(bundle, self.identifier, self.extra_attributes)
        mention.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvMention, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        mention.add_attributes({super_formal: value})
                        break
        return bundle.add_record(mention)


class VOProvMembership(ProvMembership):
    """Adaptation of prov Membership relationship."""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_COLLECTION, VOPROV_ATTR_ENTITY)

    _prov_type = VOPROV_MEMBERSHIP

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()

        membership = ProvMembership(bundle, self.identifier, self.extra_attributes)
        membership.add_asserted_type(self._prov_type)  # self.__class__.__name__)

        for formal in self.formal_attributes:
            local_part = formal[0].localpart
            value = formal[1]
            if value:
                for super_formal in super(VOProvMembership, self).FORMAL_ATTRIBUTES:
                    if local_part is super_formal.localpart:
                        membership.add_attributes({super_formal: value})
                        break
        return bundle.add_record(membership)


# VOProv descriptions

class VOProvDescription(ProvElement):
    """Base class for VOProvDescription classes"""
    FORMAL_ATTRIBUTES = None
    _prov_type = None

    def get_w3c(self, bundle=None):
        """get this element in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()
        w3c_record = ProvEntity(bundle, self.identifier, self.attributes)
        w3c_record.add_asserted_type(self._prov_type)  # self.__class__.__name__)
        return bundle.add_record(w3c_record)


class VOProvActivityDescription(VOProvDescription):
    """Class for VOProv activity description"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME,)
    _prov_type = VOPROV_ACTIVITY_DESCRIPTION

    def set_name(self, name):
        """Set the name of this activity description.

        :param name:                    A human-readable name for the agent.
        """
        self._attributes[VOPROV_ATTR_NAME] = {name}

    def set_version(self, version):
        """Set a version for this activity description.

        :param version:                 A version number, if applicable (e.g., for the code used).
        """
        self._attributes[VOPROV['version']] = {version}

    def set_description(self, description):
        """Set a description for this activity description.

        :param description:             Additional free text describing how the activity works internally.
        """
        self._attributes[VOPROV['description']] = {description}

    def set_docurl(self, docurl):
        """Set a docurl for this activity description.

        :param docurl:                  Link to further documentation on this activity, e.g., a paper, the source code
                                        in a version control system etc.
        """
        self._attributes[VOPROV['docurl']] = {docurl}

    def set_type(self, type):
        """Set the type of this activity description.

        :param type:                    Type of the activity.
        """
        self._attributes[VOPROV['type']] = {type}

    def set_subtype(self, subtype):
        """Set a subtype for this activity description.

        :param subtype:                 More specific subtype of the activity.
        """
        self._attributes[VOPROV['subtype']] = {subtype}

    def isDescriptorOf_activity(self, activity, identifier=None):
        """
        Creates a new relation between an activity and this activity description.

        :param activity:                Identifier or object of the activity described by this activity description.
        :param identifier:              Identifier for the relation between this activity description and the activity
                                        (default: None).
        """
        return self._bundle.description(activity, self, identifier)

    def usageDescription(self, identifier, role, description=None, type=None,
                         multiplicity=None, entityDescription=None, other_attributes=None):
        """
        Creates a new usage description.

        :param identifier:              Identifier for new usage description.
        :param role:                    Function of the entity with respect to the activity.
        :param description:             A descriptive text for this kind of usage (default: None).
        :param type:                    Type of relation (default: None).
        :param multiplicity:            Number of expected input entities to be used with the given role
                                        (default: None).
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        return self._bundle.usageDescription(identifier, self, role, description, type, multiplicity, entityDescription,
                                             other_attributes)

    def generationDescription(self, identifier, role, description=None, type=None,
                              multiplicity=None, entityDescription=None, other_attributes=None):
        """
        Creates a new generation description.

        :param identifier:              Identifier for new generation description.
        :param role:                    Function of the entity with respect to the activity.
        :param description:             A descriptive text for this kind of generation (default: None).
        :param type:                    Type of relation (default: None).
        :param multiplicity:            Number of expected input entities to be generated with the given role
                                        (default: None).
        :param other_attributes:        Optional other attributes as a dictionary or list
                                        of tuples to be added to the record optionally (default: None).
        """
        return self._bundle.generationDescription(identifier, self, role, description, type,
                                                  multiplicity, entityDescription, other_attributes)


class VOProvGenerationDescription(VOProvDescription):
    """Class for VOProv generation description"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ROLE,)
    _prov_type = VOPROV_GENERATION_DESCRIPTION

    def set_role(self, role):
        """Set the role of this generation description.

        :param role:                    Function of the entity with respect to the activity.
        """
        self._attributes[VOPROV_ATTR_ROLE] = {role}

    def set_description(self, description):
        """Set a description for this generation description.

        :param description:             A descriptive text for this kind of generation.
        """
        self._attributes[VOPROV['description']] = {description}

    def set_type(self, type):
        """Set the type of this generation description.

        :param type:                    Type of relation.
        """
        self._attributes[VOPROV['type']] = {type}

    def set_multiplicity(self, multiplicity):
        """Set a multiplicity for this generation description.

        :param multiplicity:            Number of expected input entities to be generated with the given role.
        """
        self._attributes[VOPROV['multiplicity']] = {multiplicity}

    def isRelatedTo_entityDescription(self, entity_description, identifier=None):
        """
        Creates a new relation between this generation description and a entity description.

        :param entity_description:      The entity description related to this generation description.
        :param identifier:              Identifier for new isRelatedTo relation record (default: None).
        """
        return self._bundle.relate(self, entity_description, identifier)


class VOProvUsageDescription(VOProvDescription):
    """Class for VOProv usage description"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ROLE,)
    _prov_type = VOPROV_USAGE_DESCRIPTION

    def set_role(self, role):
        """Set the role of this usage description.

        :param role:                    Function of the entity with respect to the activity.
        """
        self._attributes[VOPROV_ATTR_ROLE] = {role}

    def set_description(self, description):
        """Set a description for this usage description.

        :param description:             A descriptive text for this kind of usage.
        """
        self._attributes[VOPROV['description']] = {description}

    def set_type(self, type):
        """Set the type of this usage description.

        :param type:                    Type of relation.
        """
        self._attributes[VOPROV['type']] = {type}

    def set_multiplicity(self, multiplicity):
        """Set a multiplicity for this usage description.

        :param multiplicity:            Number of expected input entities to be used with the given role.
        """
        self._attributes[VOPROV['multiplicity']] = {multiplicity}

    def isRelatedTo_entityDescription(self, entity_description, identifier=None):
        """
        Creates a new relation between this usage description and an entity description.

        :param entity_description:      The entity description related to this usage description.
        :param identifier:              Identifier for new isRelatedTo relation record (default: None).
        """
        return self._bundle.relate(self, entity_description, identifier)


class VOProvEntityDescription(VOProvDescription):
    """Base class for VOProv entity description classes"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME,)
    _prov_type = VOPROV_ENTITY_DESCRIPTION

    def set_name(self, name):
        """Set the role of this usage description.

        :param name:                    A human-readable name for the entity description.
        """
        self._attributes[VOPROV_ATTR_NAME] = {name}

    def set_description(self, description):
        """Set a description for this entity description.

        :param description:             A descriptive text for this kind of entity.
        """
        self._attributes[VOPROV['description']] = {description}

    def set_docurl(self, docurl):
        """Set a docurl for this entity description.

        :param docurl:                  Link to more documentation.
        """
        self._attributes[VOPROV['docurl']] = {docurl}

    def set_type(self, type):
        """Set the type of this entity description.

        :param type:                    Type of the entity.
        """
        self._attributes[VOPROV['type']] = {type}

    def isDescriptorOf_entity(self, entity, identifier=None):
        """
        Creates a new relation between an entity and this entity description.

        :param entity:                  The entity described by this entity description.
        :param identifier:              Identifier for new isDescribedBy relation record (default: None).
        """
        return self._bundle.description(entity, self, identifier)

    def isRelatedTo_usageDescription(self, usage_description, identifier=None):
        """
        Creates a new relation between an usage description and this entity description.

        :param usage_description:       The usage description related to this entity description.
        :param identifier:              Identifier for new isRelatedTo relation record (default: None).
        """
        return self._bundle.relate(usage_description, self, identifier)

    def isRelatedTo_generationDescription(self, generation_description, identifier=None):
        """
        Creates a new relation between a generation description and this entity description.

        :param generation_description:  The generation description related to this entity description.
        :param identifier:              Identifier for new isRelatedTo relation record (default: None).
        """
        return self._bundle.relate(generation_description, self, identifier)


class VOProvValueDescription(VOProvEntityDescription):
    """Class for VOProv value entity description"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME, VOPROV_ATTR_VALUE_TYPE)
    _prov_type = VOPROV_VALUE_DESCRIPTION

    def set_valueType(self, valueType):
        """Set the value type of this value description.

        :param valueType:               Description of a value from a combination of datatype, arraysize and xtype
                                        following VOTable 1.3.
        """
        self._attributes[VOPROV_ATTR_VALUE_TYPE] = {valueType}

    def set_unit(self, unit):
        """Set the unit of this value description.

        :param unit:                    FVO unit, see C.1.1 and Derriere and Gray et al. (2014) for recommended unit
                                        representation.
        """
        self._attributes[VOPROV['unit']] = {unit}

    def set_ucd(self, ucd):
        """Set the ucd of this value description.

        :param ucd:                     Unified Content Descriptor, supplying a standardized classification of the
                                        physical quantity.
        """
        self._attributes[VOPROV['ucd']] = {ucd}

    def set_uType(self, uType):
        """Set the utype of this value description.

        :param uType:                   Utype, meant to express the role of the value in the context of an external
                                        data model.
        """
        self._attributes[VOPROV['uType']] = {uType}


class VOProvDataSetDescription(VOProvEntityDescription):
    """Class for VOProv data set entity description"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME, VOPROV_ATTR_CONTENT_TYPE)
    _prov_type = VOPROV_DATASET_DESCRIPTION

    def set_contentType(self, contentType):
        """Set the type of content of this dataset description.

        :param contentType:             Format of the dataset, MIME type when applicable.
        """
        self._attributes[VOPROV_ATTR_CONTENT_TYPE] = {contentType}


class VOProvConfigFileDescription(VOProvDescription):
    """Class for VOProv configuration file description"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME, VOPROV_ATTR_CONTENT_TYPE)
    _prov_type = VOPROV_CONFIG_FILE_DESCRIPTION


class VOProvParameterDescription(VOProvDescription):
    """Class for VOProv parameter description"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME, VOPROV_ATTR_VALUE_TYPE)
    _prov_type = VOPROV_PARAMETER_DESCRIPTION


# VOProv configurations

class VOProvConfig(ProvElement):
    FORMAL_ATTRIBUTES = None
    _prov_type = None

    def get_w3c(self, bundle=None):
        if bundle is None:
            bundle = ProvBundle()
        w3c_record = ProvEntity(bundle, self.identifier, self.attributes)
        w3c_record.add_asserted_type(self._prov_type)  # self.__class__.__name__)
        return bundle.add_record(w3c_record)


class VOProvConfigFile(VOProvConfig):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME, VOPROV_ATTR_LOCATION)
    _prov_type = VOPROV_CONFIGURATION_FILE


class VOProvParameter(VOProvConfig):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME, VOPROV_ATTR_VALUE)
    _prov_type = VOPROV_CONFIGURATION_PARAMETER


# VOProv relations

class VOProvRelation(ProvRelation):
    FORMAL_ATTRIBUTES = None
    _prov_type = None

    def get_w3c(self, bundle=None):
        """get this relation in the prov version which is an implementation of the W3C PROV-DM standard"""
        if bundle is None:
            bundle = ProvBundle()
        attribute = self.extra_attributes
        relation_formal_attribute = self.formal_attributes[0:2]

        w3c_record = ProvInfluence(bundle, self.identifier, attribute)
        namespaces = [list(i) for i in w3c_record.formal_attributes]
        for i in range(0, 2):
            namespaces[i][1] = relation_formal_attribute[i][1]
        w3c_record.add_attributes(namespaces)
        w3c_record.add_asserted_type(self._prov_type)  # self.__class__.__name__)
        return bundle.add_record(w3c_record)


class VOProvIsDescribedBy(VOProvRelation):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_DESCRIBED, VOPROV_ATTR_DESCRIPTOR)
    _prov_type = VOPROV_DESCRIPTION_RELATION


class VOProvIsRelatedTo(VOProvRelation):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_RELATED, VOPROV_ATTR_RELATOR)
    _prov_type = VOPROV_RELATED_TO_RELATION


class VOProvWasConfiguredBy(VOProvRelation):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_CONFIGURED, VOPROV_ATTR_CONFIGURATOR, VOPROV_ATTR_ARTEFACT_TYPE)
    _prov_type = VOPROV_CONFIGURATION_RELATION


class VOProvHadReference(VOProvRelation):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_REFERENCED, VOPROV_ATTR_REFERRER)
    _prov_type = VOPROV_REFERENCE_RELATION
