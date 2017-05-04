from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = 'Michele Sanguillon'
__email__ = 'Michele.Sanguillon@umontpellier.fr'

import pdb

import logging
logger = logging.getLogger('VOTable')

from prov.serializers import Serializer, Error
from prov.constants import * 
from prov.model import (Literal, Identifier, QualifiedName,
                        Namespace, ProvDocument, ProvBundle, first,
                        parse_xsd_datetime)

from xml.dom.minidom import Document, getDOMImplementation, parse, parseString


################################################################################
class ProvVOTableException(Error):
################################################################################
    pass

################################################################################
class ProvVOTableSerializer(Serializer):
################################################################################
    """
       PROV-VOTABLE serializer for :class:`~prov.model.ProvDocument`
    """

    #===========================================================================
    def serialize(self, stream, **kwargs):
    #===========================================================================
        """
        Serializes a :class:`~prov.model.ProvDocument` instance to
        `PROV-VOTABLE <http://www.ivoa.net/documents/VOTable/>`_.

        :param stream: Where to save the output.
        """

        #-----------------------------------------------------------------------
        # get arguments (provdoc.serialize(arguments))
        #-----------------------------------------------------------------------
        try:
            # type of the VOTable RESOURCE
            if 'type' in kwargs.keys():
                resType=kwargs['type']
            else:
                resType='provenance'
            # name of the VOTable RESOURCE
            if 'name' in kwargs.keys():
                resName=kwargs['name']
            else:
                resName=None
            # nb of spaces fot indentation
            if 'indent' in kwargs.keys():
                resIndent=int(kwargs['indent'])
            else:
                resIndent=0
        except:
            print("Exception getting arguments")

        #-----------------------------------------------------------------------
        # create VOTABLE
        #-----------------------------------------------------------------------
        try:
            # create VOTable document
            doc = VOTableDoc(self.document)

            # Level 1 : VOTABLE
            doc.open_VOTABLE()
            # Level 2 : RESOURCE
            doc.open_RESOURCE(resType, resName)
            # Level 3 : INFO
            doc.open_INFO('OK')

            #-------------------------------------------------------------------
            # level 3 : TABLE
            self.records = {}
            self.voprov_attr_ex = {}
            # stores the provenance information in a dictionary
            # self.record[ProvDM class][instance][attribute]=value
            self.record_analysis()
            # for each ProvDM class (Activity, Entity, ralation, ...
            for i in range(len(self.records)):
                classKey = self.records.keys()[i]
                # create an TABLE
                doc.open_TABLE(classKey)
                # add the attributes definition in each FIELD
                doc.append_FIELDS(classKey, self.voprov_attr_ex[classKey])
                # create a DATA block
                doc.open_DATA()
                # for each instance, create a TR block with the values
                # (each in a TD block)
                for tr in self.records[classKey].keys():
                    if tr != 'None':
		        doc.append_TR(classKey,tr,self.records[classKey][tr], self.voprov_attr_ex[classKey])
                # close tags
                doc.close('TABLEDATA','DATA')
                doc.close('DATA','TABLE')
                doc.close('TABLE','RESOURCE')
            doc.close('INFO','RESOURCE')
            doc.close('RESOURCE','VOTABLE')
            doc.close('VOTABLE','DOC')
  
            # write stream
            votable_content = unicode(doc.getDoc(resIndent))
            stream.write(votable_content)
        except:
            print("Exception creating VOTable document")

    #===========================================================================
    def deserialize(self, stream, **kwargs):
    #===========================================================================
        """
        Deserialize from `PROV-VOTABLE <http://www.ivoa.net/documents/VOTable/>`_
        representation to a :class:`~prov.model.ProvDocument` instance.

        :param stream: Input data.
        """
        raise NotImplementedError

    #===========================================================================
    def record_analysis(self):
    #===========================================================================
        """
        Record analysis :
          analyze the prov document and create a dictionary (self.records)
          containing the different records
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
                #---------------------------------------------------------------
                # get the record_key (Activity, Entity, wasGeneratedBy, ...)
                record_type = str(self.document.get_records()[rec].get_type())
                record_key = str(record_type.split(':')[1])
                #---------------------------------------------------------------
                # if it is a new key, 
                # - add this key in the dictionary with the value = a dictionary
                # - create the dictionary voprov_attr_ex which memorizes 
                #   if an attribute exists or not
                if record_key not in self.records:
                    self.records[record_key]={}
                    self.voprov_attr_ex[record_key]={}
                #---------------------------------------------------------------
                # get the sub_key = identifier of the item
                # item = an instance of an entity, activity, relation, ...
                # and create a dictionary for this instance
                record_sub_key = str(self.document.get_records()[rec].identifier)
                self.records[record_key][record_sub_key]={}
                #---------------------------------------------------------------
                # get the attributes for this instance and their value
                # the id is the name of the instance
                self.records[record_key][record_sub_key]['voprov:id']=record_sub_key
                self.voprov_attr_ex[record_key]['voprov:id']='YES'
                for att in range(len(self.document.records[rec].attributes)):
                    sub_sub_key = str(self.document.get_records()[rec].attributes[att][0])
                    self.records[record_key][record_sub_key][sub_sub_key] = str(self.document.get_records()[rec].attributes[att][1]) 
                    self.voprov_attr_ex[record_key][sub_sub_key]='YES'
        except:
            pass

###############################################################################
# VOTableDoc class
###############################################################################
class VOTableDoc:

    #==========================================================================
    def __init__(self, provdoc):
    #==========================================================================

        # 
        self.doc = Document()
        self.document=provdoc
        #-----------------------------------------------------------------------
        # Parameters for the header of the VOTable
        #-----------------------------------------------------------------------
        self.VOTable_Header = {
            'VOTABLE': {
                'version':'1.2',
                'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
                'xmlns':'http://www.ivoa.net/xml/VOTable/v1.2',
                'xsi:schemaLocation':'http://www.ivoa.net/xml/VOTable/v1.2 http://www.ivoa.net/xml/VOTable/VOTable-1.2.xsd' },
            'DESCRIPTION': 'Provenance VOTable'
        }
        #-----------------------------------------------------------------------
        # utype of each class
        #-----------------------------------------------------------------------
        self.VOTable_Table = {
            'Activity': {'utype':'voprov:Activity'},
            'Entity': {'utype':'voprov:Entity'},
            'Agent': {'utype':'voprov:Agent'},
            'Usage': {'utype':'voprov:used'},
            'Generation': {'utype':'voprov:wasGeneratedBy'},
            'Communication':{'utype':'voprov:wasInformedBy'},
            'Start':{'utype':'voprov:wasStartedBy'},
            'End':{'utype':'voprov:wasEndedBy'},
            'Invalidation':{'utype':'voprov:wasInvalidatedBy'},
            'Derivation':{'utype':'voprov:wasDerivedFrom'},
            'Attribution':{'utype':'voprov:wasAttributedTo'},
            'Association':{'utype':'voprov:wasAssociatedWith'},
            'Delegation':{'utype':'voprov:actedOnBehalfOf'},
            'Influence':{'utype':'voprov:wasInfluencedBy'},
            'Bundle':{'utype':'voprov:bundle'},
            'Alternate':{'utype':'voprov:alternateOf'},
            'Specialization':{'utype':'voprov:specializationOf'},
            'Mention':{'utype':'voprov:mentionOf'},
            'Membership':{'utype':'voprov:hadMember'},
            'Stepship':{'utype':'voprov:hadStep'}
        }
        #-----------------------------------------------------------------------
        # ordered fields (due to usage of dictionaries)
        #-----------------------------------------------------------------------
        self.VOTable_OrderedFields = {
            'Activity': ['voprov:id', 'voprov:name', 'voprov:startTime', \
                         'voprov:endTime', 'voprov:annotation', \
                        'voprov:desc_id', 'voprov:desc_name', 'voprov:desc_type', \
                        'voprov:desc_subtype', 'voprov:desc_annotation', 'voprov:desc_doculink'],
            'Entity' : ['voprov:id', 'voprov:name', 'voprov:type', 'voprov:annotation', \
                        'voprov:rights', 'voprov:desc_id', 'voprov:desc_name',\
                        'voprov:desc_annotation', 'voprov:desc_doculink'],
            'Agent': ['voprov:id', 'voprov:name', 'voprov:type'],
            'Usage': ['voprov:id', 'voprov:activity', 'voprov:entity', 'voprov:time', 'voprov:attributes'],
            'Generation': ['voprov:id', 'voprov:entity', 'voprov:activity'],
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
        #-----------------------------------------------------------------------
        # description of each attribute
        #-----------------------------------------------------------------------
        self.VOTable_Field = {
            'Activity': {
                'voprov:id' :{ 'name' : 'voprov:id', 'utype':'voprov:Activity.id', 'datatype':'char', 'arraysize':'*' , 'ucd':'meta.id'},
                'voprov:name':{ 'name' : 'voprov:name', 'utype':'voprov:Activity.name', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.title' },
                'voprov:startTime':{ 'name' : 'start', 'utype':'voprov:Activity.startTime', 'datatype':'char', 'arraysize':'*', 'ucd':'' },
                'voprov:endTime':{ 'name' : 'stop', 'utype':'voprov:Activity.endTime', 'datatype':'char', 'arraysize':'*' , 'ucd':''},
                'voprov:annotation':{ 'name' : 'annotation', 'utype':'voprov:Activity.annotation', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.description' },
                'voprov:desc_id':{ 'name' : 'desc_id', 'utype':'voprov:ActivityDescription.id', 'datatype':'char', 'arraysize':'*', 'ucd':'' },
                'voprov:desc_name':{ 'name' : 'desc_name', 'utype':'voprov:ActivityDescription.name', 'datatype':'char', 'arraysize':'*', 'ucd':'' },
                'voprov:desc_type':{ 'name' : 'desc_type', 'utype':'voprov:ActivityDescription.type', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.code.class' },
                'voprov:desc_subtype':{ 'name' : 'desc_subtype', 'utype':'voprov:ActivityDescription.subtype', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.code.class' },
                'voprov:desc_annotation':{ 'name' : 'desc_annotation', 'utype':'voprov:ActivityDescription.annotation', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.description' },
                'voprov:desc_doculink':{ 'name' : 'desc_doculink', 'utype':'voprov:ActivityDescription.doculink', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.ref.url' }
             },
            'Entity': {
                'voprov:id' :{ 'name' : 'voprov:id', 'utype':'voprov:Entity.id', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.id' },
                'voprov:name':{ 'name' : 'name', 'utype':'voprov:Entity.name', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.title' },
                'voprov:type':{ 'name' : 'type', 'utype':'voprov:Entity.type', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.code.class' },
                'voprov:annotation':{ 'name' : 'annotation', 'utype':'voprov:Entity.annotation', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.description' },
                'voprov:rights':{ 'name' : 'rights', 'utype':'voprov:Entity.rights', 'datatype':'char', 'arraysize':'*', 'ucd':'' },
                'voprov:desc_id':{ 'name' : 'desc_id', 'utype':'voprov:EntityDescription.id', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.id' },
                'voprov:desc_name':{ 'name' : 'desc_name', 'utype':'voprov:EntityDescription.name', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.title' },
                'voprov:desc_annotation':{ 'name' : 'desc_annotation', 'utype':'voprov:EntityDescription.annotation', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.description' },
                'voprov:desc_doculink':{ 'name' : 'desc_doculink', 'utype':'voprov:EntityDescription.doculink', 'datatype':'char', 'arraysize':'*', 'ucd':'imeta.ref.url' }
             },
            'Agent': {
                'voprov:id' :{ 'name' : 'voprov:id', 'utype':'voprov:Agent.id', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.id' },
                'voprov:name' :{ 'name' : 'name', 'utype':'voprov:Agent.name', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.title' },
                'voprov:type':{ 'name' : 'type', 'utype':'voprov:Agent.type', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.code.class' }
            },
            'Usage': {
                'voprov:id' :{ 'name' : 'voprov:id', 'utype':'voprov:Usage.id', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.id' },
                'voprov:activity' :{ 'name' : 'activity', 'utype':'voprov:Usage.activity', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.title' },
                'voprov:entity' :{ 'name' : 'entity', 'utype':'voprov:Usage.entity', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.title' },
                'voprov:time' :{ 'name' : 'time', 'utype':'voprov:Usage.time', 'datatype':'char', 'arraysize':'*', 'ucd':'' },
                'voprov:attributes' :{ 'name' : 'attributes', 'utype':'voprov:Usage.attributes', 'datatype':'char', 'arraysize':'*', 'ucd':'' },
            },
            'Generation': {
                'voprov:id' :{ 'name' : 'voprov:id', 'utype':'voprov:Generation.id', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.id' },
                'voprov:entity' :{ 'name' : 'entity', 'utype':'voprov:Generation.entity', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.title' },
                'voprov:activity' :{ 'name' : 'activity', 'utype':'voprov:Generation.activity', 'datatype':'char', 'arraysize':'*', 'ucd':'meta.title' },
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
        try:
            for i in range(len(self.document.get_registered_namespaces())):
                self.VOTable_Header['VOTABLE']['xmlns:'+self.document.get_registered_namespaces()[i].prefix]=self.document.get_registered_namespaces()[i].uri
            self.votable = self.doc.createElement( 'VOTABLE' )
            for k,v in self.VOTable_Header['VOTABLE'].items():
                self.votable.setAttribute( k, v )
        except:
            print("Exception open_VOTABLE")

    #---------------------------------------------------------------------------
    def open_RESOURCE(self, res_type=None, res_name=None):
        # Level 2 : RESOURCE
        try:
            self.resource = self.doc.createElement( 'RESOURCE' )
            if res_type:
                self.resource.setAttribute( 'type', res_type )
            if res_name:
                self.resource.setAttribute( 'name', res_name )

            # Level 3 : DESCRIPTION
            description = self.doc.createElement( 'DESCRIPTION' )
            text = self.doc.createTextNode( self.VOTable_Header['DESCRIPTION'] )
            description.appendChild(text)
            self.resource.appendChild(description)
        except:
            print("Exception open_RESOURCE")

    #---------------------------------------------------------------------------
    def open_INFO(self, value, msg=''):
        # Level 3 : INFO
        try:
            self.info = self.doc.createElement( 'INFO' )
            self.info.setAttribute( 'name', 'QUERY_STATUS')
            self.info.setAttribute( 'value', value)
            if value == 'ERROR':
                text = self.doc.createTextNode(msg)
                self.info.appendChild(text)
        except:
            print("Exception open_INFO")

    #---------------------------------------------------------------------------
    def open_TABLE(self, name=None):
        # Level 3 : TABLE
        try:
            self.table = self.doc.createElement( 'TABLE' )
            if name:
                self.table.setAttribute( 'name',  '%s' % str( name ) )
                if (name in self.VOTable_Table.keys()) and ('utype' in self.VOTable_Table[name].keys()):
                    self.table.setAttribute( 'utype', str(self.VOTable_Table[name]['utype']))
        except:
            print("Exception open_TABLE")

    #---------------------------------------------------------------------------
    def append_FIELDS(self, table, attributes):
        # Level 4 : FIELD 
        try:
            if table in self.VOTable_Field.keys():
                if len(self.VOTable_OrderedFields[table])!=0:
                    # For each attribute of a class (in a certain order)
                    for fieldLine in self.VOTable_OrderedFields[table]:
                        # test if this attribute has to be displayed
                        if fieldLine in attributes:
                            self.field = self.doc.createElement( 'FIELD')
                            for k in self.VOTable_Field[table][fieldLine].keys():
                                self.field.setAttribute(k, str(self.VOTable_Field[table][fieldLine][k]))
                            self.close('FIELD','TABLE')

        except:
            print("Exception append_FIELDS")
    #---------------------------------------------------------------------------
    def open_DATA(self):
        # Level 4 & 5: DATA & TABLEDATA
        try:
            self.data = self.doc.createElement( 'DATA' )
            self.tabledata = self.doc.createElement( 'TABLEDATA' )
        except:
            print("Exception open_DATA")

    #---------------------------------------------------------------------------
    def append_TR(self, classKey, name, dict_param, attributes):
        # Level 5 : TR
        try:
            self.tr = self.doc.createElement( 'TR' )
            td = self.doc.createElement( 'TD' )
            #td.appendChild(self.doc.createTextNode(name))
            #self.tr.appendChild(td)
            for param in self.VOTable_OrderedFields[classKey]:
                if param in attributes:
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
