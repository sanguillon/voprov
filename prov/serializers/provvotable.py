from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = 'Michele Sanguillon'
__email__ = 'Michele.Sanguillon@umontpellier.fr'

import datetime
import io
import pdb

import logging
logger = logging.getLogger('VOTable')

from prov.serializers import Serializer, Error
from prov.constants import * 
from prov.model import (Literal, Identifier, QualifiedName,
                        Namespace, ProvDocument, ProvBundle, first,
                        parse_xsd_datetime)

from xml.dom.minidom import Document, getDOMImplementation, parse, parseString


class ProvVOTableException(Error):
    pass

class ProvVOTableSerializer(Serializer):
    """
       PROV-VOTABLE serializer for :class:`~prov.model.ProvDocument`
    """
    def serialize(self, stream, **kwargs):
        """
        Serializes a :class:`~prov.model.ProvDocument` instance to
        `PROV-VOTABLE <http://www.ivoa.net/documents/VOTable/>`_.

        :param stream: Where to save the output.
        """

        # get arguments
        try:
            if 'type' in kwargs.keys():
                resType=kwargs['type']
            else:
                resType='provenance'
            if 'name' in kwargs.keys():
                resName=kwargs['name']
            else:
                resName=None
            if 'indent' in kwargs.keys():
                resIndent=int(kwargs['indent'])
            else:
                resIndent=0
        except:
            print("Exception getting arguments")

        try:
            # create VOTable document
            doc = VOTableDoc(self.document)

            # Level 1 : VOTABLE
            doc.open_VOTABLE()
            # Level 2 : RESOURCE
            doc.open_RESOURCE(resType, resName)
            # Level 3 : INFO
            doc.open_INFO('OK')

            # level 3 : TABLE
            self.records = {}
            self.record_analysis()
            for i in range(len(self.records)):
                classKey = self.records.keys()[i]
                doc.open_TABLE(classKey)
                doc.append_FIELDS(classKey)
                doc.open_DATA()
                for tr in self.records[classKey].keys():
                    if tr != 'None':
		        doc.append_TR(classKey,tr,self.records[classKey][tr])
                doc.close('TABLEDATA','DATA')
                doc.close('DATA','TABLE')
                doc.close('TABLE','RESOURCE')
            doc.close('INFO','RESOURCE')
            doc.close('RESOURCE','VOTABLE')
            doc.close('VOTABLE','DOC')
  
            votable_content = unicode(doc.getDoc(resIndent))
            stream.write(votable_content)
        except:
            print("Exception creating VOTable document")

    def deserialize(self, stream, **kwargs):
        """
        Deserialize from `PROV-VOTABLE <http://www.ivoa.net/documents/VOTable/>`_
        representation to a :class:`~prov.model.ProvDocument` instance.

        :param stream: Input data.
        """
        raise NotImplementedError

    def record_analysis(self):
        """
        Record analysis :
          fill the dictionary self.records
              with key = Activity, Entity, wasGeneratedBy, ...
              with value = dictionary 
                  with key = identifier of the item
                  with value = dictionary
                      with key = attribute name
                      with value = attribute value
        """
        try:
            # For each record
            for rec in range(len(self.document.get_records())):
                # get the record_type_key (Activity, Entity, wasGeneratedBy, ...)
                record_type = str(self.document.get_records()[rec].get_type())
                record_key = str(record_type.split(':')[1])
                # if a new key, create a sub dictionary which will contains all records of that type
                if record_key not in self.records:
                    self.records[record_key]={}
                # get the sub_key = identifier of the item
                record_sub_key = str(self.document.get_records()[rec].identifier)
               # get the attributes
                self.records[record_key][record_sub_key]={}
                for att in range(len(self.document.records[rec].attributes)):
                    sub_sub_key = str(self.document.get_records()[rec].attributes[att][0])
                    self.records[record_key][record_sub_key][sub_sub_key] = str(self.document.get_records()[rec].attributes[att][1]) 
        except:
            pass
#------------------------------------------------------------------------------
# VOTable class
#------------------------------------------------------------------------------
class VOTableDoc:

    #---------------------------------------------------------------------------
    def __init__(self, provdoc):

        # 
        self.doc = Document()
        self.document=provdoc
        # Parameters for the header
        self.dHeader = {
            'VOTABLE': {
                'version':'1.2',
                'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
                'xmlns':'http://www.ivoa.net/xml/VOTable/v1.1',
                'xsi:schemaLocation':'http://www.ivoa.net/xml/VOTable/v1.1 http://www.ivoa.net/xml/VOTable/VOTable-1.1.xsd' },
            'DESCRIPTION': 'Provenance VOTable'
        }
        self.VOTableParam = {
            'Activity': {'utype':'prov:activity'},
            'Entity': {'utype':'prov:entity'},
            'Agent': {'utype':'prov:agent'},
            'Usage': {'utype':'prov:used'},
            'Generation': {'utype':'prov:wasGeneratedBy'},
            'Communication':{'utype':'prov:wasInformedBy'},
            'Start':{'utype':'prov:wasStartedBy'},
            'End':{'utype':'prov:wasEndedBy'},
            'Invalidation':{'utype':'prov:wasInvalidatedBy'},
            'Derivation':{'utype':'prov:wasDerivedFrom'},
            'Attribution':{'utype':'prov:wasAttributedTo'},
            'Association':{'utype':'prov:wasAssociatedWith'},
            'Delegation':{'utype':'prov:actedOnBehalfOf'},
            'Influence':{'utype':'prov:wasInfluencedBy'},
            'Bundle':{'utype':'prov:bundle'},
            'Alternate':{'utype':'prov:alternateOf'},
            'Specialization':{'utype':'prov:specializationOf'},
            'Mention':{'utype':'prov:mentionOf'},
            'Membership':{'utype':'prov:hadMember'},
            'Stepship':{'utype':'voprov:hadStep'}
        }
        self.VOFieldParam_items = {
            'Activity': ['id', 'prov:startTime', 'prov:endTime', 'voprov:status', 'voprov:annotation', 'voprov:description'],
            'Entity': ['id', 'prov:label', 'prov:type', 'voprov:annotation', 'voprov:description'],
            'Agent': ['id', 'voprov:name', 'prov:type'],
            'Usage': [],
            'Generation': [],
            'Communication':[],
            'Start':[],
            'End':[],
            'Invalidation':[],
            'Derivation':[],
            'Attribution':[],
            'Association':[],
            'Delegation':[],
            'Influence':[],
            'Bundle':[],
            'Alternate':[],
            'Specialization':[],
            'Mention':[],
            'Membership':[],
            'Stepship':[]
        } 
        self.VOFieldParam = {
            'Activity': {
                'id' :{ 'name' : 'id', 'utype':'prov:activity.id', 'datatype':'char', 'arraysize':'*' },
                'prov:startTime':{ 'name' : 'start', 'utype':'prov:startTime', 'datatype':'char', 'arraysize':'*' },
                'prov:endTime':{ 'name' : 'stop', 'utype':'prov:endTime', 'datatype':'char', 'arraysize':'*' },
                'voprov:status':{ 'name' : 'status', 'utype':'voprov:status', 'datatype':'char', 'arraysize':'*' },
                'voprov:annotation':{ 'name' : 'annotation', 'utype':'voprov:annotation', 'datatype':'char', 'arraysize':'*' },
                'voprov:description':{ 'name' : 'description', 'utype':'voprov:description', 'datatype':'char', 'arraysize':'*' }
             },
            'Entity': {
                'id' :{ 'name' : 'id', 'utype':'prov:entity.id', 'datatype':'char', 'arraysize':'*' },
                'prov:label':{ 'name' : 'label', 'utype':'prov:label', 'datatype':'char', 'arraysize':'*' },
                'prov:type':{ 'name' : 'type', 'utype':'prov:type', 'datatype':'char', 'arraysize':'*' },
                'voprov:annotation':{ 'name' : 'annotation', 'utype':'voprov:annotation', 'datatype':'char', 'arraysize':'*' },
                'voprov:description':{ 'name' : 'description', 'utype':'voprov:description', 'datatype':'char', 'arraysize':'*' }
             },
            'Agent': {
                'id' :{ 'name' : 'id', 'utype':'prov:agent.id', 'datatype':'char', 'arraysize':'*' },
                'voprov:name' :{ 'name' : 'name', 'utype':'voprov:agent.name', 'datatype':'char', 'arraysize':'*' },
                'prov:type':{ 'name' : 'type', 'utype':'prov:type', 'datatype':'char', 'arraysize':'*' }
            },
            'Usage': {
            },
            'Generation': {
            },
            'Communication':{
            },
            'Start':{
            },
            'End':{
            },
            'Invalidation':{
            },
            'Derivation':{
            },
            'Attribution':{
            },
            'Association':{
            },
            'Delegation':{
            },
            'Influence':{
            },
            'Bundle':{
            },
            'Alternate':{
            },
            'Specialization':{
            },
            'Mention':{
            },
            'Membership':{
            },
            'Stepship':{
            }
        }

    #---------------------------------------------------------------------------
    def open_VOTABLE(self):
        # Level 1 : VOTABLE
        for i in range(len(self.document.get_registered_namespaces())):
            self.dHeader['VOTABLE']['xmlns:'+self.document.get_registered_namespaces()[i].prefix]=self.document.get_registered_namespaces()[i].uri
        self.votable = self.doc.createElement( 'VOTABLE' )
        for k,v in self.dHeader['VOTABLE'].items():
            self.votable.setAttribute( k, v )

    #---------------------------------------------------------------------------
    def open_RESOURCE(self, res_type=None, res_name=None):
        # Level 2 : RESOURCE
        self.resource = self.doc.createElement( 'RESOURCE' )
        if res_type:
            self.resource.setAttribute( 'type', res_type )
        if res_name:
            self.resource.setAttribute( 'name', res_name )

        # Level 3 : DESCRIPTION
        description = self.doc.createElement( 'DESCRIPTION' )
        text = self.doc.createTextNode( self.dHeader['DESCRIPTION'] )
        description.appendChild(text)
        self.resource.appendChild(description)

    #---------------------------------------------------------------------------
    def open_INFO(self, value, msg=''):
        # Level 3 : INFO
        self.info = self.doc.createElement( 'INFO' )
        self.info.setAttribute( 'name', 'QUERY_STATUS')
        self.info.setAttribute( 'value', value)
        if value == 'ERROR':
            text = self.doc.createTextNode(msg)
            self.info.appendChild(text)

    #---------------------------------------------------------------------------
    def open_TABLE(self, name=None):
        # Level 3 : TABLE
        self.table = self.doc.createElement( 'TABLE' )
        if name:
            self.table.setAttribute( 'name',  '%s' % str( name ) )
            if (name in self.VOTableParam.keys()) and ('utype' in self.VOTableParam[name].keys()):
                self.table.setAttribute( 'utype', str(self.VOTableParam[name]['utype']))

    #---------------------------------------------------------------------------
    def append_FIELDS(self, table):
        # Level 4 : FIELD 
        try:
            if table in self.VOFieldParam.keys():
                # For each field of the table
                if len(self.VOFieldParam_items[table])!=0:
                    for fieldLine in self.VOFieldParam_items[table]:
                        self.field = self.doc.createElement( 'FIELD')
                        for k in self.VOFieldParam[table][fieldLine].keys():
                            self.field.setAttribute(k, str(self.VOFieldParam[table][fieldLine][k]))
                        self.close('FIELD','TABLE')

        except:
            print("Exception append_FIELDS")
    #---------------------------------------------------------------------------
    def open_DATA(self):
        # Level 4 & 5: DATA & TABLEDATA
        self.data = self.doc.createElement( 'DATA' )
        self.tabledata = self.doc.createElement( 'TABLEDATA' )

    #---------------------------------------------------------------------------
    def append_TR(self, classKey, name, dict_param):
        # Level 5 : TR
        try:
            self.tr = self.doc.createElement( 'TR' )
            td = self.doc.createElement( 'TD' )
            td.appendChild(self.doc.createTextNode(name))
            self.tr.appendChild(td)
            for param in self.VOFieldParam_items[classKey]:
                if param != 'id':
                    td = self.doc.createElement( 'TD' )
                    if param in dict_param.keys():
                        td.appendChild(self.doc.createTextNode(dict_param[param]) )
                    else:
                        td.appendChild(self.doc.createTextNode(' '))
                    self.tr.appendChild(td)
            #
            self.close('TR','TABLEDATA')
        except:
            print("Exception append_TR")
    #---------------------------------------------------------------------------
    def close(self, tag1, tag2):
        if tag1 == 'INFO':
            item = self.info
        elif tag1 == 'RESOURCE':
            item = self.resource
        elif tag1 == 'VOTABLE':
            item = self.votable
        elif tag1 == 'inputPARAM':
            item = self.param
        elif tag1 == 'PARAM':
            item = self.param
        elif tag1 == 'TABLE':
            item = self.table
        elif tag1 == 'FIELD':
            item = self.field
        elif tag1 == 'DATA':
            item = self.data
        elif tag1 == 'TABLEDATA':
            item = self.tabledata
        elif tag1 == 'TR':
            item = self.tr
        if tag2 == 'INFO':
            container = self.info
        elif tag2 == 'RESOURCE':
            container = self.resource
        elif tag2 == 'VOTABLE':
            container = self.votable
        elif tag2 == 'DOC':
            container = self.doc
        elif tag2 == 'inputPARAM':
            container = self.param
        elif tag2 == 'PARAM':
            container = self.param
        elif tag2 == 'TABLE':
            container = self.table
        elif tag2 == 'FIELD':
            container = self.field
        elif tag2 == 'DATA':
            container = self.data
        elif tag2 == 'TABLEDATA':
            container = self.tabledata
        container.appendChild(item)

    #---------------------------------------------------------------------------
    def getDoc(self, indent):
        return self.doc.toprettyxml( encoding="UTF-8", indent=' '*indent )
