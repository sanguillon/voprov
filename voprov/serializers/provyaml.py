from voprov.model import VOProvEntity, VOProvAgent, VOProvActivity, VOProvAttribution, VOProvUsage, \
    VOProvGeneration, VOProvEntityDescription, VOProvActivityDescription, VOProvParameter
from voprov.model.records import VOProvWasConfiguredBy
from prov.serializers import Serializer
import yaml
import io


def _entry(sections, kind, identifier):
    """Dictionary describing an element, created if needed (elements without attributes are stored as None)."""
    section = sections.setdefault(kind, {})
    if section.get(identifier) is None:
        section[identifier] = {}
    return section[identifier]


def _append(entry, key, value):
    """Set entry[key] to value, or to a list of values if several are added."""
    if key not in entry:
        entry[key] = value
    elif isinstance(entry[key], list):
        entry[key].append(value)
    else:
        entry[key] = [entry[key], value]


class VOProvYAMLSerializer(Serializer):
    """Human readable YAML summary of a VOProvDocument (export only).

    Only the main records are kept (entities, agents, activities, their descriptions, usage, generation,
    attribution and parameters) in a compact layout, so the document cannot be rebuilt from it:
    use the JSON or XML format for a complete representation.
    """

    def serialize(self, stream, **kwargs):
        """
        Serialize a VOProvDocument into a YAML file.
        """
        pdoc = self.document.flattened()

        dict_record = {}
        list_records = pdoc.get_records()

        dict_all_agent = {}
        dict_all_activity = {}
        dict_all_entity = {}
        dict_all_entity_description = {}
        dict_all_activity_description = {}

        # elements first, then the relations that complete them
        for record in sorted(list_records, key=lambda r: r.is_relation()):
            if isinstance(record, VOProvEntity):
                dict_all_entity[record.identifier._str] = None
                if record.attributes:
                    dict_attributes = {}
                    for attr in record.attributes:
                        if 'location' in attr[0]._str:
                            dict_attributes['location'] = attr[1]
                        elif 'generatedAtTime' in attr[0]._str:
                            dict_attributes['generatedAtTime'] = attr[1]
                        elif 'name' in attr[0]._str:
                            dict_attributes['name'] = attr[1]
                        elif 'comment' in attr[0]._str:
                            dict_attributes['comment'] = attr[1]
                        elif 'description' in attr[0]._str:
                            dict_attributes['entity_description'] = attr[1]
                    dict_all_entity[record.identifier._str] = dict_attributes
                dict_record['entity'] = dict_all_entity

            elif isinstance(record, VOProvAgent):
                dict_all_agent[record.identifier._str] = None
                if record.attributes:
                    dict_attributes = {}
                    for attr in record.attributes:
                        if 'name' in attr[0]._str:
                            dict_attributes['name'] = attr[1]
                        elif 'type' in attr[0]._str:
                            dict_attributes['type'] = attr[1]
                        elif 'email' in attr[0]._str:
                            dict_attributes['email'] = attr[1]
                    dict_all_agent[record.identifier._str] = dict_attributes
                dict_record['agent'] = dict_all_agent

            elif isinstance(record, VOProvActivity):
                dict_all_activity[record.identifier._str] = None
                if record.attributes:
                    dict_attributes = {}
                    for attr in record.attributes:
                        if 'name' in attr[0]._str:
                            dict_attributes['name'] = attr[1]
                        elif 'start' in attr[0]._str:
                            dict_attributes['start'] = attr[1]
                        elif 'end' in attr[0]._str:
                            dict_attributes['end'] = attr[1]
                        elif 'description' in attr[0]._str:
                            dict_attributes['activity_description'] = attr[1]
                        dict_attributes['parameters'] = {}
                    dict_all_activity[record.identifier._str] = dict_attributes
                dict_record['activity'] = dict_all_activity

            elif isinstance(record, VOProvAttribution):
                dict_attribute = {record.attributes[1][1]._str: None}
                entity = record.attributes[0][1]._str
                if len(record.attributes) > 2:
                    dict_attribute[record.attributes[1][1]._str] = {'role': record.attributes[2][1]}
                _entry(dict_record, 'entity', entity).setdefault('attributed', {}).update(dict_attribute)

            elif isinstance(record, VOProvWasConfiguredBy):
                activity = record.attributes[0][1]._str
                for param in list_records:
                    if isinstance(param, VOProvParameter) and param.identifier._str == record.attributes[1][1]._str:
                        _entry(dict_record, 'activity', activity).setdefault('parameters', {})[
                            param.attributes[0][1]] = param.attributes[1][1]

            elif isinstance(record, VOProvUsage):
                activity = record.attributes[0][1]._str
                _append(_entry(dict_record, 'activity', activity), 'used', record.attributes[1][1]._str)

            elif isinstance(record, VOProvGeneration):
                activity = record.attributes[1][1]._str
                _append(_entry(dict_record, 'activity', activity), 'generated', record.attributes[0][1]._str)

            elif isinstance(record, VOProvEntityDescription):
                dict_all_entity_description[record.identifier._str] = None
                if record.attributes:
                    dict_attributes = {}
                    for attr in record.attributes:
                        if 'description' in attr[0]._str:
                            dict_attributes['description'] = attr[1]
                        elif 'type' in attr[0]._str:
                            dict_attributes['type'] = attr[1]
                        elif 'docurl' in attr[0]._str:
                            dict_attributes['docurl'] = attr[1]
                    dict_all_entity_description[record.identifier._str] = dict_attributes
                dict_record['entity_description'] = dict_all_entity_description

            elif isinstance(record, VOProvActivityDescription):
                dict_all_activity_description[record.identifier._str] = None
                if record.attributes:
                    dict_attributes = {}
                    for attr in record.attributes:
                        if 'description' in attr[0]._str:
                            dict_attributes['description'] = attr[1]
                        elif 'type' in attr[0]._str:
                            dict_attributes['type'] = attr[1]
                        elif 'docurl' in attr[0]._str:
                            dict_attributes['docurl'] = attr[1]
                    dict_all_activity_description[record.identifier._str] = dict_attributes
                dict_record['activity_description'] = dict_all_activity_description

        if isinstance(stream, io.TextIOBase):
            stream.write(yaml.dump(dict_record))
        else:
            stream.write(yaml.dump(dict_record, encoding="utf-8"))

    def deserialize(self, stream, **kwargs):
        """Not supported: the YAML export is a summary and does not contain the whole document."""
        raise NotImplementedError("The YAML format is an export only, it cannot be read back. "
                                  "Use the JSON or XML format to save a document.")


