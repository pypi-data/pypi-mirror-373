'''
 Pyecore MDB implements an BMI interface MDB with a pyecore in memory backend 
 
 This file is generated form: pyecoremdb.py.mako on 2025-08-29 10:24:46.964354 by calling E:/1_ILS/Projects/2025_IlsHackathon/Repos/hackathon/pyeoq/eoq3conceptsgen/generatefromconceptscli.py -i pyecoremdb.py.mako -o ../pyecoremdb.py -d pyecoremdb.prev.json.
 
 Bjoern Annighoefer 2023
'''

# ## EOQ imports
from eoq3.config import Config,EOQ_DEFAULT_CONFIG
from eoq3.logger import GetLoggerInstance
from eoq3.value import VAL, SIV, PRM, BOL, I64, U64, STR, QRY, NON, LST, InitValOrNon
from eoq3.mdb import Mdb
from eoq3.concepts import CONCEPT_PREFIX_LEN, CONCEPT_UNIQUE_LEN
from eoq3.concepts import CONCEPTS, MXMDB, MXELEMENT, MXCONSTRAINT, M2PRIMITIVES, M2PACKAGE, M2MODEL, M2ENUM, M2OPTIONOFENUM, M2CLASS, M2ATTRIBUTE, M2ASSOCIATION, M2COMPOSITION, M2INHERITANCE, M1MODEL, M1OBJECT, M1FEATURE, M1ATTRIBUTE, M1ASSOCIATION, M1COMPOSITION, FEATURE_MULTIVALUE_POSTFIX, IsConcept, IsMultivalueFeature, NormalizeFeatureName, IsNameFeature, GetConceptKeyString
from eoq3.query import Obj, Seg, SEG_TYPES, ObjId
from eoq3.error import EOQ_ERROR, EOQ_ERROR_INVALID_VALUE, EOQ_ERROR_INVALID_TYPE, EOQ_ERROR_UNSUPPORTED,\
                           EOQ_ERROR_DOES_NOT_EXIST, EOQ_ERROR_RUNTIME, EOQ_ERROR_UNKNOWN,\
                           EOQ_ERROR_INVALID_OPERATION

from eoq3pyecoreutils.genericstopyecore import IsEPrimitiveType, GenericPrimitiveTypeToEPrimitiveType,\
                            ConceptPrimitiveIdToPrimitiveType, ConceptPrimitiveTypeToPrimitiveId
from eoq3pyecoreutils.valuetopyecore import EValueToValue, ValueToEValue, ETypeToValueType
from eoq3pyecoreutils.crudforpyecore import UPDATE_MODES, GetUpdateModeAndAbsPosition, ValidateUpdatePosition,\
                            ClassIdToPackageAndName, ECORE_CLASSID_SEPERATOR
                            


# ## PYECORE imports
#ecore base types
from pyecore.ecore import EPackage, EObject, EClass, EAttribute, EReference, EEnum, EEnumLiteral, EAnnotation, EStructuralFeature, ENamedElement
#ecore primitives
from pyecore.ecore import EBoolean, EInt, ELong, EString, EFloat, EDouble, EDate
from pyecore.valuecontainer import BadValueError, EOrderedSet, EList

# ## OTHER imports
import types
import itertools #required for generator concatenation
from typing import Tuple, List, Dict, Union, Any, Collection, Callable #type checking


ECORE_FEATURE_MAX_LEN = -1

class EFEATURE_TYPES:
    ATTRIBUTE = 0
    ASSOCIATION = 1
    COMPOSITION = 2

ECORE_PACKAGE = EClass.eClass.eContainer().eClass    
ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES = next((f for f in EClass.eClass.eAllStructuralFeatures() if f.name == "eStructuralFeatures"), None)
ECORE_BASE_FEATURES_ECLASS_ESUPERTYPES = next((f for f in EClass.eClass.eAllStructuralFeatures() if f.name == "eSuperTypes"), None)
ECORE_BASE_FEATURES_EPACKAGE_ECLASSIFIERS = next((f for f in EPackage.eClass.eAllStructuralFeatures() if f.name == "eClassifiers"), None)
ECORE_BASE_FEATURES_EPACKAGE_ESUBPACKAGES = next((f for f in EPackage.eClass.eAllStructuralFeatures() if f.name == "eSubpackages"), None)
ECORE_BASE_FEATURES_EENUM_ELITERALS = next((f for f in EEnum.eClass.eAllStructuralFeatures() if f.name == "eLiterals"), None)
ECORE_BASE_FEATURES_ECLASS_EANNOTATIONS = next((f for f in EClass.eClass.eAllStructuralFeatures() if f.name == "eAnnotations"), None)
ECORE_BASE_FEATURES_ESTRUCTURALFEATURE_ETYPE = next((f for f in EStructuralFeature.eClass.eAllStructuralFeatures() if f.name == "eType"), None)


         
class EMxArtificialObject(EObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class EM2ArtificialObject(EObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class EM1ArtificialObject(EObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)



class EMxMdb(EMxArtificialObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._CON_orphans:Dict[EObject] = {}
        self._CON_m2Models:List[EPackage] = []
        self._CON_m1Models:List[EObject] = []

class EMxConstraint(EMxArtificialObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._CON_element:str = None
        self._CON_expression:str = None

class EM2Inheritance(EM2ArtificialObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._CON_subClass = None
        self._CON_superClass = None

class EM1Model(EM1ArtificialObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._CON_class:EPackage = None
        self._CON_name:EString = None
        self._CON_m1Objects:List[EObject] = []

class EM1Feature(EM1ArtificialObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class EM1Attribute(EM1Feature):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._CON_class:EAttribute = None
        self._CON_m1Object:EObject = None
        self._CON_pos:int = 0

class EM1Association(EM1Feature):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._CON_class:EReference = None
        self._CON_src:EObject = None
        self._CON_srcPos:int = 0
        self._CON_dst:EObject = None
        self._CON_dstPos:int = 0

class EM1Composition(EM1Feature):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._CON_class:EReference = None
        self._CON_parent:EObject = None
        self._CON_child:EObject = None
        self._CON_pos:EInt = 0

   

class EObjSeg(Seg):
    '''Specializes Obj, in order to store the reference to the eObj internally,
    such that faster encoding and decoding is possible
    '''
    def __init__(self, objId:U64, eObj=None):
        super().__init__(SEG_TYPES.OBJ,[objId])
        self._eObj = eObj



M2ATTRIBUTE_TYPES = [getattr(M2PRIMITIVES,k) for k in M2PRIMITIVES.__dict__ if not k.startswith('_')]



MXMDB_FEATURES = [getattr(MXMDB,k) for k in MXMDB.__dict__ if not k.startswith('_')]


class PyEcoreMdb(Mdb):
    ''' PYECORE BMI MDB
    '''
    def __init__(self, config:Config=EOQ_DEFAULT_CONFIG):
        self.config = config
        self.eMdb = EMxMdb()
        #internals
        self.logger = GetLoggerInstance(config)
        #handlers
        self.conceptsCreateHandlers = self.__InitConceptsCreateHandlerTable()
        self.conceptsReadHandlers = self.__InitConceptsReadHandlerTable()
        self.conceptsUpdateHandlers = self.__InitConceptsUpdateHandlerTable()
        self.conceptsDeleteHandlers = self.__InitConceptsDeleteHandlerTable()
        self.conceptsIsInstanceHandlers = self.__InitIsInstanceHandlers()
        #Initialize encoding
        self.idToObjectLUT:Dict[int,EObject] = {}
        self.lastId:int = 0
        #caching for fast look-up
        self.classNamesCache:Dict[str,Dict[EObject,Tuple[EObject,str,EObject]]] = {} #class name vs. class implementation. Stored is (Object, name, context) 
        self.createIdStrLut:Dict[str,EObject] = {} #stores IDs of M2 elements for speakable instantiation of M2 level
        #internal storages
        self.baseElements = {}
        self.artificialFeatures = {}
        self.artificialAttributesLut = {}
        self.anyM2Associations:Dict[EReference,EReference] = {} #stores all any M2 association, because they have no opposite 
        self.anyM2Composition:Dict[EReference,EReference] = {} #stores all any M2 composition, because they have no opposite 
        #Encoding all base elements (store the base elements to prevent that those are deleted)
        self.__RegisterBaseElements()
        #initialize base caches with base elements
        self.__CacheBaseElements()
        
    # PUBLIC METHODS
    
    # ###############################
    # CRUD+ INTERFACE               #
    # ###############################
    
    #@Override
    def Create(self, classId:Union[STR,Obj], createArgs:LST=LST([]), target:Obj=NON(), recoveryArgs:LST=LST([])) -> Tuple[Obj,EOQ_ERROR]:
        #input validation
        self.__ValidateTypes(classId, [STR,Obj], 'classId')
        self.__ValidateType(createArgs, LST, 'createArgs')
        self.__ValidateType(target, QRY, 'target',True)
        #create the new element
        res = NON()
        eClass = None
        conceptId = None
        if(STR == type(classId)):
            classIdStr = classId.GetVal()
            if(IsConcept(classIdStr)): #no class needed on M2 level. Create element directly
                conceptId = classIdStr
            else:
                eClass = self.__ValidateAndReturnUniqueClassId(classIdStr)
        elif(isinstance(classId,Obj)):
            eClass = self.__Dec(classId)
        else:
            raise EOQ_ERROR_INVALID_VALUE("Invalid class ID: %s"%(str(classId)))
        #create based on eClass
        if(conceptId):
            res = self.__CreateConcept(conceptId,createArgs,target,recoveryArgs)
        elif(isinstance(eClass, EClass)):# native access
            self.__StopIfConceptsOnlyMode()
            res = self.__CreateNative(eClass,createArgs,target,recoveryArgs)
        else:
            raise EOQ_ERROR_INVALID_VALUE('Cannot instantiate: %s'%(classId))
        #prepare return value
        return res, None #by default no post modification error is returned

    
    #@Override
    def Read(self, target:Obj, featureName:STR, context:Obj=NON()) -> VAL:
        value = None
        #input validation
        self.__ValidateType(target, QRY, 'target', True)
        self.__ValidateType(featureName, STR, 'featureNameStr')
        self.__ValidateType(context, QRY, 'context',True)
        featureNameStr = featureName.GetVal()
        #decode target
        eObj = self.__DecTarget(target,featureNameStr)
        #get feature properties
        isMultiValueFeature = IsMultivalueFeature(featureNameStr)      
        normalizedFeatureName = NormalizeFeatureName(featureNameStr) 
        if(IsConcept(featureNameStr)):
            handler = self.__GetConceptFeatureHandler(eObj, featureNameStr, self.conceptsReadHandlers)
            eContext = None if context.IsNone() else self.__Dec(context)
            value = handler(eObj,featureNameStr,eContext)
        #all other features
        else: #native access
            # self.__StopIfConceptsOnlyMode() native read is OK
            #validate target: prevent, that a meta-meta-element is changed
            self.__PreventMetaMetaAccess(target)
            value = self.__ReadNative(eObj,normalizedFeatureName)
            #sanity check of feature name and multiplicity
            isMultivalue = (isinstance(value,LST))
            self.__VaidateFeatureNameMultiplicity(isMultiValueFeature,isMultivalue,featureNameStr,normalizedFeatureName)
        return value
    
    #@Override
    def Update(self, target:Obj, featureName:STR, value:SIV, position:I64=I64(0)) -> Tuple[Obj,Obj,Obj,I64,EOQ_ERROR]:
        #validate input
        self.__ValidateType(target, QRY, 'target',True)
        self.__ValidateType(featureName, STR, 'featureName')
        self.__ValidateType(value, SIV, 'value',True)
        self.__ValidateType(position, I64, 'position')
        #validate target
        self.__PreventMetaMetaAccess(target)
        #convert values
        eFeatureName = featureName.GetVal()
        eObj = self.__DecTarget(target,eFeatureName)
        ePosition = position.GetVal()
        #init return values
        oldValue = NON() 
        oldOwner = NON() 
        oldComposition = NON()
        oldPosition = NON()
        if(IsConcept(eFeatureName)): #concepts feature update
            handler = self.__GetConceptFeatureHandler(eObj, eFeatureName, self.conceptsUpdateHandlers)
            (oldValue,oldOwner,oldComposition,oldPosition) = handler(eObj,value,ePosition)
        elif(isinstance(eObj,EObject)): #native update
            self.__StopIfConceptsOnlyMode()
            (oldValue,oldOwner,oldComposition,oldPosition) = self.__UpdateCustomFeature(eObj,eFeatureName,value,ePosition)
        else:
            raise EOQ_ERROR_INVALID_TYPE('Type error: target is no object, but %s.'%(eObj)) 
        #Update finished, return value
        return (oldValue, oldOwner, oldComposition, oldPosition, None) #no post modification error can occure
        
    #@Override             
    def Delete(self, target:Obj) -> Tuple[STR,LST,LST,EOQ_ERROR]:
        #is target legal?
        self.__ValidateType(target, QRY, 'target')
#         self.__PreventMetaMetaAccess(target,False)
        eObj = self.__Dec(target)
        # sanity checks can this element be deleted?
        deleteHandler = None
        concept = self.__GetConcept(eObj)
        if(concept):
            try:
                conceptKey = GetConceptKeyString(concept)
                deleteHandler = self.conceptsDeleteHandlers[conceptKey]
            except KeyError:
                raise EOQ_ERROR_INVALID_OPERATION("Cannot delete %s."%(concept))
        else:
            raise EOQ_ERROR_INVALID_OPERATION("Cannot delete element of unknown type.")
        # call delete handler
        (conceptId, createArgs,recoveryArgs) = deleteHandler(eObj)
        # clean up orphans
        if(eObj in self.eMdb._CON_orphans):
            del self.eMdb._CON_orphans[eObj]
        # clean up the object ID
        self.__EncLastTime(target)
        #return
        return (conceptId, createArgs, recoveryArgs, None)
    
    #@Override
    def FindElementByIdOrName(self, nameOrId:STR, context:Obj=NON(), restrictToConcept:STR=NON()) -> LST:
        #argument checks
        self.__ValidateType(nameOrId, STR, 'nameOrId', False)
        self.__ValidateType(context, Obj, 'context', True)
        self.__ValidateType(restrictToConcept, STR, 'restrictToConcept', True)
        #retrieve element
        eNameOrId = nameOrId.GetVal()
        eContext = self.__Dec(context)
        
        conceptFilter = None
        if(not restrictToConcept.IsNone()):
            eConceptId = restrictToConcept.GetVal()
            try:
                conceptFilter = self.conceptsIsInstanceHandlers[eConceptId]
            except KeyError:
                pass # this is expected
        elements = self.__FindElementeByIdOrNameRaw(eNameOrId,eContext,conceptFilter)
        return self.__EncCollection(elements)
    
    # # PROTECTED METHODS
    
    # #########################
    # Concept CREATE handlers #
    # #########################
    
    # MX
    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateMxMdb(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new MxMdb

        Args:
            createArgs: The list of create arguments, i.e.
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
        Returns:
            newElem: the new MxMdb
        """
        return self.mdb #mdb is a singelton, so return always the already registered mdb object

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateMxConstraint(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new MxConstraint

        Args:
            createArgs: The list of create arguments, i.e.
                element:MXELEMENT
                expression:STR
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                mxelementconstraintspos:U64
        Returns:
            newElem: the new MxConstraint
        """
        # validate createArgs
        element:Obj = None
        eElement:EObject = None
        eExpression:str = None
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.MXCONSTRAINT+' createArgs require target:Obj and expression:STR, but got %d arguments.'%(nArgs))
        #validate m2Model
        self.__ValidateType(createArgs[0], Obj, 'createArgs[0](element')
        element = createArgs[0]
        eElement = self.__Dec(element)
        if(not isinstance(eElement, EObject)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.MXCONSTRAINT+' m2Model must be a '+CONCEPTS.MXELEMENT+'. %s is no '+CONCEPTS.MXELEMENT)%(element))
        #validate expression
        self.__ValidateType(createArgs[1], STR, 'createArgs[1](expression)')
        eExpression = createArgs[1].GetVal()
        pos = -1 #append at the end
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.MXCONSTRAINT+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EMxConstraint()
        #create the class according to given arguments
        newElem = self.__InitAndEncNewElem(newEElem, target)
        newEElem._CON_element = eElement
        newEElem._CON_expression = eExpression
        self.__UpdateList(eElement._CON_constraints, (-pos-2), newEElem, ECORE_FEATURE_MAX_LEN)
        #eElement._CON_constraints.append(newEElem)
        return newElem

    # M2
    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM2Package(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M2Package

        Args:
            createArgs: The list of create arguments, i.e.
                name:STR
                superpackage:M2PACKAGE
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                mxmdbm2modelspos:U64
        Returns:
            newElem: the new M2Package
        """
        # validate createArgs
        name:STR = None
        superpackage:M2PACKAGE = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2PACKAGE+' createArgs require name:STR, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        #validate m2Model
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](superpackage')
        superpackage = createArgs[1]
        eSuperpackage = self.__Dec(superpackage)
        if(not isinstance(eSuperpackage, EPackage)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M2PACKAGE+' m2Model must be a '+CONCEPTS.M2PACKAGE+'. %s is no '+CONCEPTS.M2PACKAGE)%(superpackage))
        pos = -1 #append at the end
        # validate strId
        strId = eSuperpackage._CON_strId+self.config.strIdSeparator+name
        if(strId in self.createIdStrLut):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2PACKAGE+' strId must be unique. An element %s does already exist.'%(strId))
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2PACKAGE+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EPackage(name)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self.__UpdateMultiValueEFeature(eSuperpackage,ECORE_BASE_FEATURES_EPACKAGE_ESUBPACKAGES,(-pos-2),newEElem,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_m1Models",[])
        #update cache
        self.__UpdateElementNameCache(newEElem,name,eSuperpackage,None)
        newEElem._CON_strId = strId
        self.__UpdateCreateIdStrCache(newEElem,newEElem._CON_strId)
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM2Model(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M2Model

        Args:
            createArgs: The list of create arguments, i.e.
                name:STR
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                MxMdbM2ModelsPos: U64
        Returns:
            newElem: the new M2Model
        """
        #cargs = name:STR parent:OBJ -> m2model
        name:str = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=1):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2MODEL+' createArgs require name:STR, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        pos = -1 #append at the end
        # validate strId
        strId = name
        if(strId in self.createIdStrLut):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2MODEL+' strId must be unique. An element %s does already exist.'%(strId))
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2MODEL+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EPackage(name)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self.__UpdateList(self.eMdb._CON_m2Models, (-pos-2), newEElem, ECORE_FEATURE_MAX_LEN)
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_m1Models",[])
        #update cache
        self.__UpdateElementNameCache(newEElem,name,self.eMdb,None)
        newEElem._CON_strId = strId
        self.__UpdateCreateIdStrCache(newEElem,newEElem._CON_strId)
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM2Enum(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M2Enum

        Args:
            createArgs: The list of create arguments, i.e.
                name:STR
                m2package:M2PACKAGE
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                m2classenumspos:UNSPECIFIED
        Returns:
            newElem: the new M2Enum
        """
        #cargs = name:STR, m2Model:Obj
        name:str = None
        m2Model:Obj = None
        eM2Model:EPackage = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ENUM+' createArgs require name:STR and m2Model:Obj, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        #validate m2Model
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](m2Model')
        m2Model = createArgs[1]
        eM2Model = self.__Dec(m2Model)
        if(not isinstance(eM2Model, EPackage)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M2ENUM+' m2Model must be a '+CONCEPTS.M2MODEL+'. %s is no '+CONCEPTS.M2MODEL)%(m2Model))
        pos = -1 #append at the end
        # validate strId
        strId = eM2Model._CON_strId+self.config.strIdSeparator+name
        if(strId in self.createIdStrLut):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ENUM+' strId must be unique. An element %s does already exist.'%(strId))
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ENUM+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EEnum(name)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self.__UpdateMultiValueEFeature(eM2Model,ECORE_BASE_FEATURES_EPACKAGE_ECLASSIFIERS,(-pos-2),newEElem,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION,None)
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_m2Attributes",[])
        #update cache
        self.__UpdateElementNameCache(newEElem,name,eM2Model,None)
        newEElem._CON_strId = strId
        self.__UpdateCreateIdStrCache(newEElem,newEElem._CON_strId)
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM2OptionOfEnum(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M2OptionOfEnum

        Args:
            createArgs: The list of create arguments, i.e.
                name:STR
                value:U64
                enum:M2ENUM
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                optionsposofm2enum:U64
        Returns:
            newElem: the new M2OptionOfEnum
        """
        #cargs = name:STR, enum:Obj, value:U64
        name = None
        value = None
        enum = None
        eEnum = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=3):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2OPTIONOFENUM+' createArgs require name:STR, value:U64 and enum:Obj, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        #validate name
        self.__ValidateType(createArgs[1], U64, 'createArgs[1](value)')
        value = createArgs[1].GetVal()
        #validate m2Model
        self.__ValidateType(createArgs[2], Obj, 'createArgs[2](enum)')
        enum = createArgs[2]
        eEnum = self.__Dec(enum)
        if(not isinstance(eEnum, EEnum)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M2OPTIONOFENUM+' enum must be a '+CONCEPTS.M2ENUM+'. %s is no '+CONCEPTS.M2ENUM)%(enum))
        pos = -1 #append at the end
        # validate strId
        strId = eEnum._CON_strId+self.config.strIdSeparator+name
        if(strId in self.createIdStrLut):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2OPTIONOFENUM+' strId must be unique. An element %s does already exist.'%(strId))
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2OPTIONOFENUM+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EEnumLiteral(name,value=value)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self.__UpdateMultiValueEFeature(eEnum,ECORE_BASE_FEATURES_EENUM_ELITERALS,(-pos-2),newEElem,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        #update cache
        self.__UpdateElementNameCache(newEElem,name,eEnum,None)
        newEElem._CON_strId = strId
        self.__UpdateCreateIdStrCache(newEElem,newEElem._CON_strId)
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM2Class(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M2Class

        Args:
            createArgs: The list of create arguments, i.e.
                name:STR
                abstract:BOL
                m2package:M2PACKAGE
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                m2enumclassespos:U64
        Returns:
            newElem: the new M2Class
        """
        #cargs = name:STR m2model:OBJ -> class
        name:str = None
        stringId:str = None
        m2Model:Obj = None
        eM2Model:EPackage = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=3):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2CLASS+' createArgs require name:STR, abstract:BOL and m2Model:Obj, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        #validate name
        self.__ValidateType(createArgs[1], BOL, 'createArgs[0](abstract)')
        abstract = createArgs[1].GetVal()
        #validate m2Model
        self.__ValidateType(createArgs[2], Obj, 'createArgs[2](m2Model)')
        m2Model = createArgs[2]
        eM2Model = self.__Dec(m2Model)
        if(not isinstance(eM2Model, EPackage)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M2CLASS+' m2Model must be a '+CONCEPTS.M2MODEL+'. %s is no '+CONCEPTS.M2MODEL)%(m2Model))
        if(name in [c.name for c in eM2Model.eClassifiers]):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2CLASS+' name must be unique in m2 model.')
        pos = -1 #append at the end
        # validate strId
        strId = eM2Model._CON_strId+self.config.strIdSeparator+name
        if(strId in self.createIdStrLut):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2CLASS+' strId must be unique. An element %s does already exist.'%(strId))
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2CLASS+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EClass(name=name,abstract=abstract) #append super class to make sure it is instantiated
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self.__UpdateMultiValueEFeature(eM2Model,ECORE_BASE_FEATURES_EPACKAGE_ECLASSIFIERS,(-pos-2),newEElem,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_specializations",[])
        self.__SetAugmentedProperty(newEElem,"_CON_generalizations",[])
        #update cache
        self.__UpdateElementNameCache(newEElem,name,eM2Model,None)
        newEElem._CON_strId = strId
        self.__UpdateCreateIdStrCache(newEElem,newEElem._CON_strId)
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM2Attribute(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M2Attribute

        Args:
            createArgs: The list of create arguments, i.e.
                name:STR
                srcclass:M2CLASS
                primtype:STR
                mul:I64
                unit:STR
                enum:M2ENUM
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                m2classattributespos:U64
        Returns:
            newElem: the new M2Attribute
        """
        name:str = None
        srcClass:Obj = None
        eSrcClass:EClass = None
        primType:str = None
        mul:int = None
        unit:str = None
        enum:Obj = None
        eEnum:EEnum = None

        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=6):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ATTRIBUTE+' createArgs require name:STR, srcClass:OBJ, type:STR, mul:I64, unit:STR|NON and enum:OBJ|NON, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        if(IsNameFeature(name)):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ATTRIBUTE+' %s is not an allowed feature name.'%(name))
        #validate clazz
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](srcClass)')
        srcClass = createArgs[1]
        eSrcClass = self.__Dec(srcClass)
        if(not isinstance(eSrcClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ATTRIBUTE+' srcClass must be '+CONCEPTS.M2CLASS+'. %s is no class'%(srcClass))
        #validate mul
        self.__ValidateType(createArgs[2], STR, 'createArgs[3](primType)')
        primType = createArgs[2].GetVal()
        if(primType not in M2ATTRIBUTE_TYPES):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ATTRIBUTE+' type must be one of '+', '.join(M2ATTRIBUTE_TYPES)+', but got %s'%(primType))
        #TODO: validate acceptable prim types
        #validate mul
        self.__ValidateType(createArgs[3], I64, 'createArgs[3](mul)')
        mul = createArgs[3].GetVal()
        self.__ValidateMultiplicity(mul, 'createArgs[3](mul)')
        #validate unit
        self.__ValidateType(createArgs[4], STR, 'createArgs[4](unit)',True)
        unit = createArgs[4].GetVal()
        #validate enum
        ePrimType = None
        cPrimType = None
        if(M2PRIMITIVES.ENU == primType):
            self.__ValidateType(createArgs[5], Obj, 'createArgs[5](enum)')
            enum = createArgs[5]
            eEnum = self.__Dec(enum)
            if(not isinstance(eEnum, EEnum)):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ATTRIBUTE+' enum must be '+CONCEPTS.M2ENUM+'. %s is no enum'%(enum))
            ePrimType = eEnum
            cPrimType = STR
        else:
            self.__ValidateType(createArgs[5], NON, 'createArgs[5](enum)', True)
            ePrimType = GenericPrimitiveTypeToEPrimitiveType(primType)
            cPrimType = ConceptPrimitiveIdToPrimitiveType(primType)
        pos = -1 #append at the end
        # validate strId
        strId = eSrcClass._CON_strId+self.config.strIdSeparator+name
        if(strId in self.createIdStrLut):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ATTRIBUTE+' strId must be unique. An element %s does already exist.'%(strId))
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ATTRIBUTE+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EAttribute(name=name,eType=ePrimType,lower=0,upper=mul,unique=False) #unique shall be false by default
        newElem = self.__InitAndEncNewElem(newEElem, target)
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_type",cPrimType)
        self.__SetAugmentedProperty(newEElem,"_CON_unit",unit)
        self.__SetAugmentedProperty(newEElem,"_CON_incarnations",[])
        self.__UpdateMultiValueEFeature(eSrcClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,(-pos-2),newEElem,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        #update dependent augmented properties
        if(eEnum):
            self.__GetAugmentedProperty(eEnum, "_CON_m2Attributes", []).append(newEElem)
        #update cache
        self.__UpdateElementNameCache(newEElem,name,eSrcClass,None)
        newEElem._CON_strId = strId
        self.__UpdateCreateIdStrCache(newEElem,newEElem._CON_strId)
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM2Association(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M2Association
         __________                      __________
        |          | srcName    dstName |          |
        | srcClass |--------------------| dstClass |
        |__________| srcMul      dstMul |__________|


        Args:
            createArgs: The list of create arguments, i.e.
                srcname:STR
                srcclass:M2CLASS
                srcmul:I64
                dstname:STR
                dstclass:M2CLASS
                dstmul:I64
                anydst:BOL
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                m2classassociationspos:U64
        Returns:
            newElem: the new M2Association
        """
        srcName:str = None
        srcClass:Obj = None
        eSrcClass:EClass = None
        srcMul:int  = None
        dstName:str = None
        dstClass:Obj = None
        eDstClass:EClass = None
        dstMul:int = None
        anyDst:bool = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=7):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ASSOCIATION+' createArgs require arguments srcName:STR, srcClass:OBJ, srcMul:I64, dstName:STR, dstClass:OBJ, dstMul:I64 and anyDst:BOL, but got %d arguments.'%(nArgs))
        #validate srcName
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](srcName)')
        srcName = createArgs[0].GetVal()
        if (IsNameFeature(srcName)):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ASSOCIATION + ' %s is not an allowed feature name.' % (srcName))
        #validate srcClass
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](srcClass)')
        srcClass = createArgs[1]
        eSrcClass = self.__Dec(srcClass)
        if(not isinstance(eSrcClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ASSOCIATION+' srcClass must be a '+CONCEPTS.M2CLASS+'. %s is no '%(srcClass)+CONCEPTS.M2CLASS)
        #validate srcMul
        self.__ValidateType(createArgs[2], I64, 'createArgs[2](srcMul)')
        srcMul = createArgs[2].GetVal()
        self.__ValidateMultiplicity(srcMul, 'createArgs[2](srcMul)')
        #validate dstName
        self.__ValidateType(createArgs[3], STR, 'createArgs[3](dstName)')
        dstName = createArgs[3].GetVal()
        if (IsNameFeature(dstName)):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ASSOCIATION + ' %s is not an allowed feature name.' % (dstName))
        #validate dstMul
        self.__ValidateType(createArgs[5], I64, 'createArgs[5](dstMul)')
        dstMul = createArgs[5].GetVal()
        self.__ValidateMultiplicity(dstMul, 'createArgs[5](dstMul)')
        #validate anyDst
        self.__ValidateType(createArgs[6], BOL, 'createArgs[6](anyDst)')
        anyDst = createArgs[6].GetVal()
        #validate dstClass
        if(anyDst):
            self.__ValidateType(createArgs[4], NON, 'createArgs[4](dstClass)',True)
            eDstClass = EObject.eClass
        else:
            self.__ValidateType(createArgs[4], Obj, 'createArgs[4](dstClass)')
            dstClass = createArgs[4]
            eDstClass = self.__Dec(dstClass)
            if(not isinstance(eDstClass, EClass)):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ASSOCIATION+' dstClass must be a class. %s is no '%(dstClass)+CONCEPTS.M2CLASS)
        pos = -1 #append at the end
        # validate strId
        strId = eSrcClass._CON_strId+self.config.strIdSeparator+dstName
        if(strId in self.createIdStrLut):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ASSOCIATION+' strId must be unique. An element %s does already exist.'%(strId))
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2ASSOCIATION+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EReference(name=dstName,eType=eDstClass,containment=False,lower=0,upper=dstMul)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        newEElem._CON_srcName = srcName
        newEElem._CON_srcMul = srcMul
        self.__UpdateMultiValueEFeature(eSrcClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,(-pos-2),newEElem,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        #automatically create an opposite reference if it is not any dst
        if(anyDst):
            self.anyM2Associations[newEElem] = newEElem
        else:
            newEElemOpp = EReference(name=srcName,eType=eSrcClass,containment=False,lower=0,upper=srcMul,eOpposite=newEElem,volatile=True) #use derived to mark automatic opposite refs
            self.__InitAndEncNewElem(newEElemOpp) #no return required
            self.__SetAugmentedProperty(newEElemOpp,'_CON_isDst',True) #this is required for dstAssociations
            self.__UpdateMultiValueEFeature(eDstClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,-1,newEElemOpp,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        #augment properties
        self.__SetAugmentedProperty(newEElem,'_CON_isDst',False)
        self.__SetAugmentedProperty(newEElem,"_CON_incarnations",[])
        #update cache
        self.__UpdateElementNameCache(newEElem,dstName,eSrcClass,None)
        newEElem._CON_strId = strId
        self.__UpdateCreateIdStrCache(newEElem,newEElem._CON_strId)
        #return only the direct references
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM2Composition(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M2Composition
         __________                      __________
        |          |               name |          |
        | srcClass |<>------------------| dstClass |
        |__________|             dstMul |__________|


        Args:
            createArgs: The list of create arguments, i.e.
                name:STR
                parentclass:M2CLASS
                childclass:M2CLASS
                childmul:I64
                anychild:BOL
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                m2classcompositionspos:U64
        Returns:
            newElem: the new M2Composition
        """
        name:str = None
        srcClass:Obj = None
        eSrcClass:EClass = None
        dstClass:Obj = None
        eDstClass:EClass = None
        dstMul:int = None
        anyDst:bool = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=5):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2COMPOSITION+' createArgs require arguments name:STR, parentClass:OBJ, dstClass:OBJ and dstMul:I64, anychild:BOL, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        if (IsNameFeature(name)):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2COMPOSITION + ' %s is not an allowed feature name.' % (name))
        # validate src class
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](srcClass)')
        srcClass = createArgs[1]
        eSrcClass = self.__Dec(createArgs[1])
        if(not isinstance(eSrcClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M2COMPOSITION+' srcClass must be a '+CONCEPTS.M2CLASS+'. %s is no'+CONCEPTS.M2CLASS)%(srcClass))
        #validate dst mul
        self.__ValidateType(createArgs[3], I64, 'createArgs[3](dstMul)')
        dstMul = createArgs[3].GetVal()
        self.__ValidateMultiplicity(dstMul, 'createArgs[3](dstMul)')
        #validate anyDst
        self.__ValidateType(createArgs[4], BOL, 'createArgs[4](anyDst)')
        anyDst = createArgs[4].GetVal()
        #validate dstClass
        if(anyDst):
            self.__ValidateType(createArgs[2], NON, 'createArgs[2](dstClass)',True)
            eDstClass = EObject.eClass
        else:
            self.__ValidateType(createArgs[2], Obj, 'createArgs[2](dstClass)')
            dstClass = createArgs[2]
            eDstClass = self.__Dec(dstClass)
            if(not isinstance(eDstClass, EClass)):
                raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M2COMPOSITION+' dstClass must be a '+CONCEPTS.M2CLASS+'. %s is no'+CONCEPTS.M2CLASS)%(dstClass))
        pos = -1 #append at the end
        # validate strId
        strId = eSrcClass._CON_strId+self.config.strIdSeparator+name
        if(strId in self.createIdStrLut):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2COMPOSITION+' strId must be unique. An element %s does already exist.'%(strId))
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2COMPOSITION+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EReference(name=name,eType=eDstClass,containment=True,lower=0,upper=dstMul)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self.__UpdateMultiValueEFeature(eSrcClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,(-pos-2),newEElem,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        if(anyDst):
            self.anyM2Composition[newEElem] = newEElem
        else:
            oppName = "__parent_in_%s_of_%s"%(name,eSrcClass.name)
            newEElemOpp = EReference(name=oppName,eType=eSrcClass,containment=False,lower=0,upper=1,eOpposite=newEElem,volatile=True) #use derived to mark automatic opposite refs
            self.__InitAndEncNewElem(newEElemOpp) #only call it for encoding
            self.__UpdateMultiValueEFeature(eDstClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,-1,newEElemOpp,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_incarnations",[])
        #update cache
        self.__UpdateElementNameCache(newEElem,name,eSrcClass,None)
        newEElem._CON_strId = strId
        self.__UpdateCreateIdStrCache(newEElem,newEElem._CON_strId)
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM2Inheritance(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M2Inheritance

        Args:
            createArgs: The list of create arguments, i.e.
                subclass:M2CLASS
                superclass:M2CLASS
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                m2classsubinheritancespos:U64
                m2classsuperinheritancespos:U64
        Returns:
            newElem: the new M2Inheritance
        """
        #cargs = subClass:OBJ superClass:OBJ
        subClass:Obj = None
        eSubClass:EClass = None
        superClass:Obj = None
        eSuperClass:EClass = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2INHERITANCE+' createArgs require arguments subClass:OBJ and superClass:OBJ, but got %d arguments.'%(nArgs))
        #validate subClass
        self.__ValidateType(createArgs[0], Obj, 'createArgs[0](subClass)')
        subClass = createArgs[0]
        eSubClass = self.__Dec(subClass)
        if(not isinstance(eSubClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M2INHERITANCE+' subClass must be a '+CONCEPTS.M2CLASS+'. %s is no'+CONCEPTS.M2CLASS)%(subClass))
        #validate superClass
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](superClass)')
        superClass = createArgs[1]
        eSuperClass = self.__Dec(superClass)
        if(not isinstance(eSuperClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M2INHERITANCE+' superClass must be a '+CONCEPTS.M2CLASS+'. %s is no'+CONCEPTS.M2CLASS)%(superClass))
        subPos = -1
        superPos = -1
        # validate strId
        strId = eSubClass._CON_strId+self.config.strIdSeparator+eSuperClass.name
        if(strId in self.createIdStrLut):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2INHERITANCE+' strId must be unique. An element %s does already exist.'%(strId))
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(2 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M2INHERITANCE+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            subPos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
            superPos = self.__ValidateType(recoveryArgs[1], U64, 'recoveryArgs[1](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EM2Inheritance()
        newElem = self.__InitAndEncNewElem(newEElem, target)
        newEElem._CON_subClass = eSubClass
        newEElem._CON_superClass = eSuperClass
        self.__UpdateMultiValueEFeature(eSubClass,ECORE_BASE_FEATURES_ECLASS_ESUPERTYPES,(-superPos-2),eSuperClass,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.ASSOCIATION)
        #augment properties
        self.__UpdateList(self.__GetAugmentedProperty(eSubClass,"_CON_generalizations",[]), (-subPos-2), newEElem, ECORE_FEATURE_MAX_LEN)
        self.__UpdateList(self.__GetAugmentedProperty(eSuperClass,"_CON_specializations",[]), (-superPos-2), newEElem, ECORE_FEATURE_MAX_LEN)
        #update cache
        newEElem._CON_strId = strId
        self.__UpdateCreateIdStrCache(newEElem,newEElem._CON_strId)
        return newElem

    # M1
    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM1Model(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M1Model

        Args:
            createArgs: The list of create arguments, i.e.
                class:M2MODEL
                name:STR
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                MxMdbM1ModelsPos:U64
        Returns:
            newElem: the new M1Model
        """
        eM2Model:EPackage = None
        name:str = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1MODEL+' createArgs requires arguments m2Model::M2MODEL and name:STR but got %d arguments.'%(nArgs))
        #validate m2Model
        m2Model = self.__ValidateTypes(createArgs[0], [STR,Obj], 'createArgs[0](m2Model)')
        eM2Model = None
        if(STR==type(m2Model)):
            eM2Model = self.__ValidateAndReturnUniqueClassId(m2Model.GetVal(),CONCEPTS.M2MODEL,None,self._IsM2Model)
        else: #must be obj now, because of type check before
            eM2Model = self.__Dec(m2Model)
            if(not isinstance(eM2Model, EPackage)):
                raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1MODEL+' m2Model must be a '+CONCEPTS.M2MODEL+'. %s is no'+CONCEPTS.M2MODEL)%(m2Model))
        #validate name
        name = self.__ValidateType(createArgs[1], STR, 'createArgs[1](name)',True).GetVal()
        pos = -1 #append at the end
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1MODEL+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EM1Model()
        newElem = self.__InitAndEncNewElem(newEElem, target)
        newEElem._CON_class = eM2Model
        newEElem._CON_name = name
        self.eMdb._CON_m1Models.append(newEElem)
        # augmented properties
        self.__UpdateList(self.__GetAugmentedProperty(eM2Model,"_CON_m1Models",[]), (-pos-2), newEElem, ECORE_FEATURE_MAX_LEN)
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM1Object(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M1Object

        Args:
            createArgs: The list of create arguments, i.e.
                m2class:M2CLASS
                m1model:M1MODEL
                name:STR
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                m1modelobjectspos:U64
        Returns:
            newElem: the new M1Object
        """
        # validate createArgs
        m2Class:M2CLASS = None
        eM2Class:EClass = None
        m1Model:M1MODEL = None
        eM1Model:EM1Model = None
        name:str = None
        nArgs = len(createArgs)
        if(nArgs!=3):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1OBJECT+' createArgs require m2Class:M2CLASS, m1Model:M1MODEL and name:STR, but got %d arguments.'%(nArgs))
        #validate m2Class
        m2Class = self.__ValidateTypes(createArgs[0], [STR,Obj], 'createArgs[0](m2Class)')
        if(STR==type(m2Class)):
            eM2Class = self.__ValidateAndReturnUniqueClassId(m2Class.GetVal(),CONCEPTS.M2CLASS,None,self._IsM2Class)
        else: #must be obj now, because of type check before
            eM2Class = self.__Dec(m2Class)
            if(not self._IsM2Class(eM2Class)):
                raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1OBJECT+' m2Class must be a '+CONCEPTS.M2CLASS+'. %s is no '+CONCEPTS.M2CLASS)%(m2Class))
        #validate m1Model
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](m1Model)')
        m1Model = createArgs[1]
        eM1Model = self.__Dec(m1Model)
        if(not self._IsM1Model(eM1Model)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1OBJECT+' m1Model must be a '+CONCEPTS.M1MODEL+'. %s is no '+CONCEPTS.M2CLASS)%(m1Model))
        #validate name
        self.__ValidateType(createArgs[2], STR, 'createArgs[2](name)',True)
        name = createArgs[2].GetVal()
        #validate EM2CLASS
        if(eM2Class.abstract):
            raise EOQ_ERROR_INVALID_VALUE('Cannot instantiate abstract class')
        pos = -1 #append at the end
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1OBJECT+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = eM2Class()
        newElem = self.__InitAndEncNewElem(newEElem, target)
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_m1Model",eM1Model)
        self.__SetAugmentedProperty(newEElem,"_CON_name",name)
        self.__SetAugmentedProperty(newEElem,"_CON_attributes",[])
        self.__SetAugmentedProperty(newEElem,"_CON_srcAssociations",[])
        self.__SetAugmentedProperty(newEElem,"_CON_dstAssociations",[])
        self.__SetAugmentedProperty(newEElem,"_CON_parentCompositions",[])
        self.__SetAugmentedProperty(newEElem,"_CON_childComposition",None)
        self.__SetAugmentedProperty(newEElem,"_CON_isM1Obj",True) #this is necessary, because a distingtion by class is not possible
        self.__UpdateList(eM1Model._CON_m1Objects, (-pos-2), newEElem, ECORE_FEATURE_MAX_LEN)
        self.__UpdateChildStateAndCache(newEElem) #update explicitly, because the containment in the M1 model is artificial for ecore
        # return new element
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM1Attribute(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M1Attribute

        Args:
            createArgs: The list of create arguments, i.e.
                m2attribute:M2ATTRIBUTE
                object:M1OBJECT
                value:PRM
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                pos:U64
        Returns:
            newElem: the new M1Attribute
        """
        m2Attribute:Obj = None
        eM2Attribute:EStructuralFeature = None
        m1Object:Obj = None
        eM1Object:EObject = None
        # validate createArgs
        nArgs = len(createArgs)
        if(nArgs!=3):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ATTRIBUTE+' createArgs require m2Attribute:M1Attribute, m1Object:M1OBJECT and value:PRM, but got %d arguments.'%(nArgs))
        #get m1OBject
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](m1Object)')
        m1Object = createArgs[1]
        eM1Object = self.__Dec(m1Object)
        #validate m2Attribute (out of order, since m1 object is necessary before)
        m2Attribute = self.__ValidateTypes(createArgs[0], [STR,Obj], 'createArgs[0](m2Attribute)')
        if(STR==type(m2Attribute)):
            eM2Attribute = self.__ValidateAndReturnUniqueClassId(m2Attribute.GetVal(),CONCEPTS.M2ATTRIBUTE,eM1Object.eClass,self._IsM2Attribute)
        else: #must be obj now, because of type check before
            eM2Attribute = self.__Dec(m2Attribute)
            if(not self._IsM2Attribute(eM2Attribute)):
                raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1ATTRIBUTE+' m2Attribute must be a '+CONCEPTS.M2ATTRIBUTE+'. %s is no'+CONCEPTS.M2ATTRIBUTE)%(m2Attribute))
        #validate m1OBject
        if(not self._IsM1Object(eM1Object)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1ATTRIBUTE+' m1object must be a '+CONCEPTS.M1OBJECT+'. %s is no'+CONCEPTS.M1OBJECT)%(m1Object))
        if(not eM2Attribute in eM1Object.eClass.eAllStructuralFeatures()):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ATTRIBUTE+' %s is no attribute of %s.'%(eM2Attribute.name,eM1Object.eClass.name))
        #validate value
        self.__ValidateType(createArgs[2], PRM, 'createArgs[2](value)')
        value = createArgs[2]
        eValue = value.GetVal()
        #test existing feature length
        many = eM2Attribute.many
        nExistingElem = -1
        if(many):
            nExistingElem = len(eM1Object.eGet(eM2Attribute.name))
        else: #single attributes cannot be checked if set already
            nExistingElem = len([a for a in eM1Object._CON_attributes if a._CON_class==eM2Attribute])
        if(eM2Attribute.upperBound > -1 and eM2Attribute.upperBound <= nExistingElem):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ATTRIBUTE+' maximum number of %d element(s) reached for %s'%(eM2Attribute.upperBound,eM2Attribute.name))
        pos = nExistingElem
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ATTRIBUTE+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EM1Attribute()
        try: #test if the value matches
            self.__UpdateEFeature(eM1Object, eM2Attribute, (-pos-2), eValue, eM2Attribute.upperBound, EFEATURE_TYPES.ATTRIBUTE, newEElem)
        except Exception as e:
            #make sure no memory leak is created
            newEElem.delete()
            del newEElem
            raise e
        newElem = self.__InitAndEncNewElem(newEElem, target)
        #set values after encoding, to keep side effect small in case of failure
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_class",eM2Attribute)
        self.__SetAugmentedProperty(newEElem,"_CON_m1Object",eM1Object)
        self.__SetAugmentedProperty(newEElem,"_CON_pos",pos)
        #relate to others
        self.__GetAugmentedProperty(eM1Object,"_CON_attributes",[]).append(newEElem)
        self.__GetAugmentedProperty(eM2Attribute,"_CON_incarnations",[]).append(newEElem)
        # return new element
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM1Association(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M1Association

         _____                    __________                    ______
        |     | srcAssociations:*|         |              dst:1|     |
        | src |------------------| M1Assoc |-------------------| dst |
        |_____|src:1             |_________|dstAssociations:*  |_____|

        Args:
            createArgs: The list of create arguments, i.e.
                m2association:M2ASSOCIATION
                src:M1OBJECT
                dst:MXELEMENT
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                srcpos:U64
                dstpos:U64
        Returns:
            newElem: the new M1Association
        """
        m2Association:Obj = None
        eM2Association:EStructuralFeature = None
        src:Obj = None
        eSrc:EObject = None
        dst:Obj = None
        eDst:EObject = None
        eOpposite = None
        # validate createArgs
        nArgs = len(createArgs)
        if(nArgs!=3):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ASSOCIATION+' createArgs require m2Association:M2Association, src:M1Object and dst:M1Object, but got %d arguments.'%(nArgs))
        #get src
        src = self.__ValidateType(createArgs[1], Obj, 'createArgs[1](src)')
        eSrc = self.__Dec(src)
        #validate m2Association (out of order, since m1 object is necessary before)
        m2Association = self.__ValidateTypes(createArgs[0], [STR,Obj], 'createArgs[0](m2Association)')
        if(STR==type(m2Association)):
            eM2Association = self.__ValidateAndReturnUniqueClassId(m2Association.GetVal(),CONCEPTS.M2ASSOCIATION,eSrc.eClass,self._IsM2Association)
        else: #must be obj now, because of type check before
            eM2Association = self.__Dec(m2Association)
            if(not self._IsM2Association(eM2Association)):
                raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1ASSOCIATION+' m2Association must be a '+CONCEPTS.M2ASSOCIATION+'. %s is no '+CONCEPTS.M2ASSOCIATION)%(m2Association))
        eOpposite = eM2Association.eOpposite
        #validate src
        if(not self._IsM1Object(eSrc)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1ASSOCIATION+' src must be a '+CONCEPTS.M1OBJECT+'. %s is no '+CONCEPTS.M1OBJECT)%(src))
        if(not eM2Association in eSrc.eClass.eAllStructuralFeatures()):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ASSOCIATION+' %s is no src association of %s.'%(eM2Association.name,eSrc.eClass.name))
        #validate dst
        dst = self.__ValidateType(createArgs[2], Obj, 'createArgs[2](dst)')
        eDst = self.__Dec(dst)
        if(not self._IsM1Object(eDst)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1ASSOCIATION+' dst must be a '+CONCEPTS.M1OBJECT+'. %s is no '+CONCEPTS.M1OBJECT)%(dst))
        #test existing feature length
        many = eM2Association.many
        nDstEleme = -1
        if(many):
            nDstEleme = len(eSrc.eGet(eM2Association))
        else:
            nDstEleme = len([a for a in eSrc._CON_srcAssociations if a._CON_class==eM2Association])
        if(eM2Association.upperBound > -1 and eM2Association.upperBound <= nDstEleme):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ASSOCIATION+' maximum number of %d dst element(s) reached for %s'%(eM2Association.upperBound,eM2Association.name))
        nSrcEleme = -1
        # TODO: opposite necessary? can use associates cache instead?
        if(eOpposite and eOpposite.many):
            nSrcEleme = len(eDst.eGet(eOpposite.name))
        else:
            nSrcEleme = len([a for a in eDst._CON_dstAssociations if a._CON_class==eM2Association])
        if(eM2Association._CON_srcMul > -1 and eM2Association._CON_srcMul <= nSrcEleme):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ASSOCIATION+' maximum number of %d src element(s) reached for %s'%(eM2Association._CON_srcMul,eM2Association.name))
        #test existing feature content
        if(many and eDst in eSrc.eGet(eM2Association.name)):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ASSOCIATION+' dst association %s -> %s is duplicated.'%(eSrc,eDst))
        srcPos = nDstEleme
        dstPos = nSrcEleme
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(2 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1ASSOCIATION+' recoveryArgs require srcPos:U64 and dstPos:U64, but got %d arguments.'%(nRecovArgs))
            srcPos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](srcPos)').GetVal() #overwrite with old position of element
            dstPos = self.__ValidateType(recoveryArgs[1], U64, 'recoveryArgs[1](dstPos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EM1Association()
        try: #test if the value matches
            self.__UpdateEFeature(eSrc, eM2Association, (-srcPos-2), eDst, eM2Association.upperBound, EFEATURE_TYPES.ASSOCIATION, newEElem)
            #must not set for eDst, because it is an opposite reference
        except:
            #make sure no memory leak is created
            newEElem.delete()
            del newEElem
            raise
        newElem = self.__InitAndEncNewElem(newEElem, target)
        #set values after encoding, to keep side effect small in case of failure
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_class",eM2Association)
        self.__SetAugmentedProperty(newEElem,"_CON_src",eSrc)
        self.__SetAugmentedProperty(newEElem,"_CON_srcPos",srcPos)
        self.__SetAugmentedProperty(newEElem,"_CON_dst",eDst)
        self.__SetAugmentedProperty(newEElem,"_CON_dstPos",dstPos)
        #relate to others
        self.__GetAugmentedProperty(eSrc,"_CON_srcAssociations",[]).append(newEElem)
        self.__GetAugmentedProperty(eDst,"_CON_dstAssociations",[]).append(newEElem)
        self.__GetAugmentedProperty(eM2Association,"_CON_incarnations",[]).append(newEElem)
        # return new element
        return newElem

    #@generate head no
    #@generate comment no
    #@generate body no
    def _CreateM1Composition(self, createArgs:LST, target:Obj, recoveryArgs:LST) -> Obj:
        """Create a new M1Composition

         ________                            __________                          ________
        |        | _CON_parentCompositions:*|         |                  child:1|       |
        | parent |--------------------------| M1Compo |-------------------------| child |
        |________|parent:1                  |_________|_CON_childComposition:1  |_______|


        Args:
            createArgs: The list of create arguments, i.e.
                m2composition:M2COMPOSITION
                parent:M1OBJECT
                child:MXELEMENT
            target:Obj the object ID of a deleted element
            recoveryArgs: LST the args necessary for recovery
                pos:U64
        Returns:
            newElem: the new M1Composition
        """
        m2Composition:Obj = None
        eM2Composition:EStructuralFeature = None
        parent:Obj = None
        eParent:EObject = None
        child:Obj = None
        eChild:EObject = None
        # validate createArgs
        nArgs = len(createArgs)
        if(nArgs!=3):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1COMPOSITION+' createArgs require parent:M1Object and child:M1Object, but got %d arguments.'%(nArgs))
        #get parent
        parent = self.__ValidateType(createArgs[1], Obj, 'createArgs[1](parent)')
        eParent = self.__Dec(parent)
        #validate m2Composition (out of order, since m1 object is necessary before)
        m2Composition = self.__ValidateTypes(createArgs[0], [STR,Obj], 'createArgs[0](m2Composition)')
        if(STR==type(m2Composition)):
            # eM2Composition = self.__GetM1ClassByLocalName(eParent, m2Composition.GetVal())
            # if(None==eM2Composition):
            eM2Composition = self.__ValidateAndReturnUniqueClassId(m2Composition.GetVal(),CONCEPTS.M2COMPOSITION,eParent.eClass,self._IsM2Composition)
        else: #must be obj now, because of type check before
            eM2Composition = self.__Dec(m2Composition)
            if(not self._IsM2Composition(eM2Composition)):
                raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1COMPOSITION+' m2Composition must be a '+CONCEPTS.M2COMPOSITION+'. %s is no'+CONCEPTS.M2COMPOSITION)%(m2Composition))
        #validate parent
        if(not self._IsM1Object(eParent)):
            raise EOQ_ERROR_INVALID_VALUE((CONCEPTS.M1COMPOSITION+' child must be a '+CONCEPTS.M1OBJECT+'. %s is no'+CONCEPTS.M1OBJECT)%(parent))
        if(not eM2Composition in eParent.eClass.eAllStructuralFeatures()):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1COMPOSITION+' %s is no child of %s.'%(eM2Composition.name,eParent.eClass.name))
        #validate parent
        child = self.__ValidateType(createArgs[2], Obj, 'createArgs[2](child)')
        eChild = self.__Dec(child)
        if(not isinstance(eChild, EObject)):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1COMPOSITION+' parent must be a '+MXELEMENT+', but got: %s'%(child))
        #test existing feature length
        many = eM2Composition.many
        nChildElem = -1
        if(many):
            nChildElem = len(eParent.eGet(eM2Composition))
        else:
            nChildElem = len([a for a in eParent._CON_parentCompositions if a._CON_class==eM2Composition])
        if(eM2Composition.upperBound > -1 and eM2Composition.upperBound <= nChildElem):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1COMPOSITION+' maximum number of %d children reached for %s'%(eM2Composition.upperBound,eM2Composition.name))
        nParentEleme = 1 if eChild.eContainer() else 0
        if(1 <= nParentEleme):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1COMPOSITION+' %s already has a parent.'%(child))
        #test existing feature content
        if(many and eChild in eParent.eGet(eM2Composition.name)):
            raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1COMPOSITION+' child %s is duplicated.'%(child))
        pos = nChildElem
        # check if a recovery is intended and if there are recovery appropriate args
        if(None != target):
            nRecovArgs = len(recoveryArgs)
            if(1 != nRecovArgs):
                raise EOQ_ERROR_INVALID_VALUE(CONCEPTS.M1COMPOSITION+' recoveryArgs require pos:U64, but got %d arguments.'%(nRecovArgs))
            pos = self.__ValidateType(recoveryArgs[0], U64, 'recoveryArgs[0](pos)').GetVal() #overwrite with old position of element
        # create new element
        newEElem = EM1Composition()
        try: #test if the value matches
            self.__UpdateEFeature(eParent, eM2Composition, (-pos-2), eChild, eM2Composition.upperBound, EFEATURE_TYPES.COMPOSITION, newEElem)
        except:
            #make sure no memory leak is created
            newEElem.delete()
            del newEElem
            raise
        newElem = self.__InitAndEncNewElem(newEElem, target)
        #set values after encoding, to keep side effect small in case of failure
        #augment properties
        self.__SetAugmentedProperty(newEElem,"_CON_class",eM2Composition)
        self.__SetAugmentedProperty(newEElem,"_CON_parent",eParent)
        self.__SetAugmentedProperty(newEElem,"_CON_child",eChild)
        self.__SetAugmentedProperty(newEElem,"_CON_pos",pos)
        #relate to others
        self.__GetAugmentedProperty(eParent,"_CON_parentCompositions",[]).append(newEElem)
        self.__SetAugmentedProperty(eChild,"_CON_childComposition",newEElem)
        self.__GetAugmentedProperty(eM2Composition,"_CON_incarnations",[]).append(newEElem)
        # return new element
        return newElem


    # #########################
    # Concept READ handlers #
    # #########################
    
    # MX
    # MXMDB
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxMdbConcept(self, eObj:EMxMdb, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Concept from MxMdb

        Args:
            eObj:EMxMdb The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = STR(CONCEPTS.MXMDB)
        return value
        #end _ReadMxMdbConcept  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxMdbM2Models(self, eObj:EMxMdb, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property M2Models from MxMdb

        Args:
            eObj:EMxMdb The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.eMdb._CON_m2Models)
        return value
        #end _ReadMxMdbM2Models  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxMdbM1Models(self, eObj:EMxMdb, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property M1Models from MxMdb

        Args:
            eObj:EMxMdb The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.eMdb._CON_m1Models)
        return value
        #end _ReadMxMdbM1Models  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxMdbMdb(self, eObj:EMxMdb, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Mdb from MxMdb

        Args:
            eObj:EMxMdb The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:MXMDB
        """
        return self.__Enc(self.eMdb)
        #end _ReadMxMdbMdb  

    # MXELEMENT
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxElementConcept(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Concept from MxElement

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = NON()
        concept = self.__GetConcept(eObj)
        if(concept):
            value = STR(concept)
        # TODO: retrieve value from eObj
        return value
        #end _ReadMxElementConcept  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxElementStrId(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property StrId from MxElement

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = InitValOrNon(eObj._CON_strId,STR)
        return value
        #end _ReadMxElementStrId  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxElementDocumentation(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Documentation from MxElement

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = InitValOrNon(eObj._CON_documentation,STR)
        return value
        #end _ReadMxElementDocumentation  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxElementOwner(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Owner from MxElement

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = InitValOrNon(eObj._CON_owner,STR)
        return value
        #end _ReadMxElementOwner  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxElementGroup(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Group from MxElement

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = InitValOrNon(eObj._CON_group,STR)
        return value
        #end _ReadMxElementGroup  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxElementPermissions(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Permissions from MxElement

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        elems = eObj._CON_permissions
        value = LST([STR(s) for s in elems])
        return value
        #end _ReadMxElementPermissions  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxElementHash(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> I64:
        """Read the property Hash from MxElement

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:I64
        """
        value = NON()
        # TODO: retrieve value from eObj
        return value
        #end _ReadMxElementHash  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxElementConstraints(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Constraints from MxElement

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(eObj._CON_constraints)
        return value
        #end _ReadMxElementConstraints  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxElementMdb(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Mdb from MxElement

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:MXMDB
        """
        return self.__Enc(self.eMdb)
        #end _ReadMxElementMdb  

    # MXCONSTRAINT
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxConstraintElement(self, eObj:EMxConstraint, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Element from MxConstraint

        Args:
            eObj:EMxConstraint The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:MXELEMENT
        """
        value = self.__Enc(eObj._CON_element)
        return value
        #end _ReadMxConstraintElement  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadMxConstraintExpression(self, eObj:EMxConstraint, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Expression from MxConstraint

        Args:
            eObj:EMxConstraint The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = STR(eObj._CON_expression)
        return value
        #end _ReadMxConstraintExpression  

    # M2
    # M2PRIMITIVES
    # M2PACKAGE
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2PackageName(self, eObj:EPackage, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Name from M2Package

        Args:
            eObj:EPackage The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        return STR(eObj.name) #cannot be None
        #end _ReadM2PackageName  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2PackageSuperpackage(self, eObj:EPackage, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Superpackage from M2Package

        Args:
            eObj:EPackage The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2PACKAGE
        """
        eSuperpackage = eObj.eSuperPackage
        superpackage = NON()
        if(None!=eSuperpackage):
            superpackage = self.__Enc(eSuperpackage)
        # TODO: retrieve value from eObj
        return superpackage
        #end _ReadM2PackageSuperpackage  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2PackageSubpackages(self, eObj:EPackage, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Subpackages from M2Package

        Args:
            eObj:EPackage The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        return self.__EncCollection(eObj.eSubpackages)
        #end _ReadM2PackageSubpackages  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2PackageClasses(self, eObj:EPackage, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Classes from M2Package

        Args:
            eObj:EPackage The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        mask = lambda e: isinstance(e,EClass)
        return self.__EncCollection(eObj.eClassifiers,mask)
        #end _ReadM2PackageClasses  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2PackageEnums(self, eObj:EPackage, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Enums from M2Package

        Args:
            eObj:EPackage The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        mask = lambda e: isinstance(e,EEnum)
        return self.__EncCollection(eObj.eClassifiers,mask)
        #end _ReadM2PackageEnums  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2PackageM1Models(self, eObj:EPackage, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property M1Models from M2Package

        Args:
            eObj:EPackage The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.eMdb._CON_m1Models, lambda e: self.__GetAugmentedProperty(e,"_CON_class",None) == eObj)
        return value
        #end _ReadM2PackageM1Models  

    # M2MODEL
    # M2ENUM
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2EnumName(self, eObj:EEnum, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Name from M2Enum

        Args:
            eObj:EEnum The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        return STR(eObj.name) #cannot be None  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2EnumPackage(self, eObj:EEnum, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Package from M2Enum

        Args:
            eObj:EEnum The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2PACKAGE
        """
        return self.__Enc(eObj.ePackage)
        #end _ReadM2EnumPackage  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2EnumOptions(self, eObj:EEnum, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Options from M2Enum

        Args:
            eObj:EEnum The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        return self.__EncCollection(eObj.eLiterals)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2EnumAttributes(self, eObj:EEnum, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Attributes from M2Enum

        Args:
            eObj:EEnum The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__GetAugmentedProperty(eObj, "_CON_m2Attributes", [])
        return self.__EncCollection(value)
        #end _ReadM2EnumAttributes  

    # M2OPTIONOFENUM
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2OptionOfEnumName(self, eObj:EEnumLiteral, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Name from M2OptionOfEnum

        Args:
            eObj:EEnumLiteral The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = STR(eObj.name)
        # TODO: retrieve value from eObj
        return value
        #end _ReadM2EnumOptionName  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2OptionOfEnumValue(self, eObj:EEnumLiteral, featureName:str=None, eContext:EObject=None) -> U64:
        """Read the property Value from M2OptionOfEnum

        Args:
            eObj:EEnumLiteral The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:U64
        """
        return U64(eObj.value)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2OptionOfEnumEnum(self, eObj:EEnumLiteral, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Enum from M2OptionOfEnum

        Args:
            eObj:EEnumLiteral The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2ENUM
        """
        value = self.__Enc(eObj.eEnum)
        return value
        #end _ReadM2OptionOfEnumEnum  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2OptionOfEnumM1AttributesUsingOption(self, eObj:EEnumLiteral, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property M1AttributesUsingOption from M2OptionOfEnum

        Args:
            eObj:EEnumLiteral The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        eEnum = eObj.eEnum
        allM2Attributes = self.__GetAugmentedProperty(eEnum,"_CON_m2Attributes",[])
        allM1Attributes = [x for y in allM2Attributes for x in self.__GetAugmentedProperty(y, "_CON_incarnations", [])]
        return self.__EncCollection(allM1Attributes, lambda x : eObj.name == self._ReadM1AttributeValue(x).GetVal())
        #end _ReadM2EnumOptionAllM1AttributesUsingOption  

    # M2CLASS
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassName(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Name from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        return STR(eObj.name) #cannot be None  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassIsAbstract(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> BOL:
        """Read the property IsAbstract from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:BOL
        """
        value = BOL(eObj.abstract)
        return value
        #end _ReadM2ClassIsAbstract  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassPackage(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Package from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2PACKAGE
        """
        return self.__Enc(eObj.ePackage)
        #end _ReadM2ClassPackage  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassInstances(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Instances from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        instances = []
        if(None==eContext or eContext==self.eMdb):
            instances = self.__ReadClassInstancesRawFromContexts(eObj,self.eMdb._CON_orphans.values()) #self._CON_root is included in orphans
        else:
            instances = self.__ReadClassInstancesRawFromContexts(eObj,[eContext])
        return self.__EncCollection(instances)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassMyInstances(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MyInstances from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        incarnations = []
        if(None==eContext or eContext==self.eMdb):
            incarnations = self.__ReadClassIncarnationsRawFromContexts(eObj,self.eMdb._CON_orphans) #self._CON_root is included in orphans
        else:
            incarnations = self.__ReadClassIncarnationsRawFromContexts(eObj,[eContext])
        return self.__EncCollection(incarnations)
        #end _ReadM2ClassMyInstances  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassMyAttributes(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MyAttributes from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        return self.__EncCollection(eObj.eAttributes)
        #end _ReadM2ClassMyAttributes  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassAttributes(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Attributes from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        sorter = lambda e: ObjId(e) #sorted by obj ID. Sorting seems necessary, since otherwise the order is not was observed to be not deterministic
        return self.__EncCollection(eObj.eAllAttributes(),sorter=sorter)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassMySrcAssociations(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MySrcAssociations from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        mask = lambda e: e.containment == False and self.__EReferenceContainerFix(e)==False and not self.__GetAugmentedProperty(e, "_CON_isDst", False)
        return self.__EncCollection(eObj.eReferences, mask)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassSrcAssociations(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property SrcAssociations from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        sorter = lambda e: ObjId(e) #sorted by obj ID. Sorting seems necessary, since otherwise the order is not was observed to be not deterministic
        return self.__EncCollection(self.__ReadM2ClassSrcAssociationsRaw(eObj,eContext),sorter=sorter)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassMyDstAssociations(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MyDstAssociations from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        typedDstItems = (e.eOpposite for e in eObj.eReferences if e.containment == False and self.__GetAugmentedProperty(e, "_CON_isDst", False))
        value = self.__EncCollection(typedDstItems)
        return value
        #end _ReadM2ClassMyDstAssociations  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassDstAssociations(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property DstAssociations from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        sorter = lambda e: ObjId(e) #sorted by obj ID. Sorting seems necessary, since otherwise the order is not was observed to be not deterministic
        value = self.__EncCollection(self.__ReadM2ClassDstAssociationsRaw(eObj,eContext),sorter=sorter)
        return value
        #end _ReadM2ClassDstAssociations  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassMyParentCompositions(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MyParentCompositions from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        mask = lambda e: e.containment
        return self.__EncCollection(eObj.eReferences, mask)
        #end _ReadM2ClassMyParentCompositions  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassParentCompositions(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property ParentCompositions from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        sorter = lambda e: ObjId(e) #sorted by obj ID. Sorting seems necessary, since otherwise the order is not was observed to be not deterministic
        return self.__EncCollection(self.__ReadM2ClassParentCompositionsRaw(eObj,eContext),sorter=sorter)
        #end _ReadM2ClassParentCompositions  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassMyChildCompositions(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MyChildCompositions from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        typedDstItems = (e.eOpposite for e in eObj.eReferences if e.container and None!=e.eOpposite)
        value = self.__EncCollection(typedDstItems)
        return value
        #end _ReadM2ClassMyChildCompositions  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassChildCompositions(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property ChildCompositions from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        sorter = lambda e: ObjId(e) #sorted by obj ID. Sorting seems necessary, since otherwise the order is not was observed to be not deterministic
        value = self.__EncCollection(self.__ReadM2ClassChildCompositionsRaw(eObj,eContext),sorter=sorter)
        return value
        #end _ReadM2ClassChildCompositions  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassMySpecializations(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MySpecializations from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.__GetAugmentedProperty(eObj,"_CON_specializations",[]))
        return value
        #end _ReadM2ClassMySpecializations  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassSpecializations(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Specializations from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.__ReadM2ClassSpecializationsRaw(eObj))
        return value
        #end _ReadM2ClassSpecializations  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassMyGeneralizations(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MyGeneralizations from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.__GetAugmentedProperty(eObj,"_CON_generalizations",[]))
        return value
        #end _ReadM2ClassMyGeneralizations  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2ClassGeneralizations(self, eObj:EClass, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Generalizations from M2Class

        Args:
            eObj:EClass The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.__ReadM2ClassGeneralizationsRaw(eObj))
        return value
        #end _ReadM2ClassGeneralizations  

    # M2ATTRIBUTE
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AttributeName(self, eObj:EAttribute, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Name from M2Attribute

        Args:
            eObj:EAttribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        return STR(eObj.name) #cannot be None  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AttributeClass(self, eObj:EAttribute, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Class from M2Attribute

        Args:
            eObj:EAttribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2CLASS
        """
        value = self.__Enc(eObj.eContainingClass)
        return value
        #end _ReadM2AttributeClass  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AttributePrimType(self, eObj:EAttribute, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property PrimType from M2Attribute

        Args:
            eObj:EAttribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = None
        if(isinstance(eObj.eType,EEnum)):
            value = STR(M2PRIMITIVES.ENU)
        else:
            value = STR(ConceptPrimitiveTypeToPrimitiveId(eObj._CON_type))
        return value
        #end _ReadM2AttributePrimType  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AttributeMul(self, eObj:EAttribute, featureName:str=None, eContext:EObject=None) -> I64:
        """Read the property Mul from M2Attribute

        Args:
            eObj:EAttribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:I64
        """
        return I64(eObj.upperBound)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AttributeUnit(self, eObj:EAttribute, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Unit from M2Attribute

        Args:
            eObj:EAttribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        return InitValOrNon(eObj._CON_unit,STR)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AttributeEnum(self, eObj:EAttribute, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Enum from M2Attribute

        Args:
            eObj:EAttribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2ENUM
        """
        value = None
        if(isinstance(eObj.eType,EEnum)):
            value = self.__Enc(eObj.eType)
        else:
            value = NON()
        return value
        #end _ReadM2AttributeEnum  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AttributeMyInstances(self, eObj:EAttribute, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MyInstances from M2Attribute

        Args:
            eObj:EAttribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.__GetAugmentedProperty(eObj, "_CON_incarnations", []))
        return value
        #end _ReadM2AttributeMyInstances  

    # M2ASSOCIATION
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AssociationSrcName(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property SrcName from M2Association

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = STR(eObj._CON_srcName)
        return value  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AssociationSrcClass(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property SrcClass from M2Association

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2CLASS
        """
        value = self.__Enc(eObj.eContainingClass)
        return value  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AssociationSrcMul(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> I64:
        """Read the property SrcMul from M2Association

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:I64
        """
        value = I64(eObj._CON_srcMul)
        return value  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AssociationDstName(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property DstName from M2Association

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = STR(eObj.name)
        return value  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AssociationDstClass(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property DstClass from M2Association

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2CLASS
        """
        value = None
        if(EObject.eClass == eObj.eType):
            value = NON()
        else:
            value = self.__Enc(eObj.eType)
        return value  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AssociationDstMul(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> I64:
        """Read the property DstMul from M2Association

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:I64
        """
        value = I64(eObj.upperBound)
        return value  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AssociationAnyDst(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> BOL:
        """Read the property AnyDst from M2Association

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:BOL
        """
        value = None
        if(EObject.eClass == eObj.eType):
            value = BOL(True)
        else:
            value = BOL(False)
        return value
        #end _ReadM2AssociationAnyDst  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2AssociationMyInstances(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MyInstances from M2Association

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.__GetAugmentedProperty(eObj, "_CON_incarnations", []))
        return value
        #end _ReadM2AssociationMyInstances  

    # M2COMPOSITION
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2CompositionName(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Name from M2Composition

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        return STR(eObj.name) #cannot be None  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2CompositionParentClass(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property ParentClass from M2Composition

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2CLASS
        """
        value = self.__Enc(eObj.eContainingClass)
        return value
        #end _ReadM2CompositionParentClass  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2CompositionChildClass(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property ChildClass from M2Composition

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2CLASS
        """
        value = None
        if(EObject.eClass == eObj.eType):
            value = NON()
        else:
            value = self.__Enc(eObj.eType)
        return value
        #end _ReadM2CompositionChildClass  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2CompositionMulChild(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> I64:
        """Read the property MulChild from M2Composition

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:I64
        """
        value = I64(eObj.upperBound)
        return value
        #end _ReadM2CompositionMulChild  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2CompositionAnyChild(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> BOL:
        """Read the property AnyChild from M2Composition

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:BOL
        """
        value = None
        if(EObject.eClass == eObj.eType):
            value = BOL(True)
        else:
            value = BOL(False)
        return value
        #end _ReadM2CompositionAnyChild  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2CompositionMyInstances(self, eObj:EReference, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property MyInstances from M2Composition

        Args:
            eObj:EReference The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(self.__GetAugmentedProperty(eObj, "_CON_incarnations", []))
        return value
        #end _ReadM2CompositionMyInstances  

    # M2INHERITANCE
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2InheritanceSubclass(self, eObj:EM2Inheritance, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Subclass from M2Inheritance

        Args:
            eObj:EM2Inheritance The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2CLASS
        """
        value = self.__Enc(eObj._CON_subClass)
        return value
        #end _ReadM2InheritanceSubclass  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2InheritanceSuperclass(self, eObj:EM2Inheritance, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Superclass from M2Inheritance

        Args:
            eObj:EM2Inheritance The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2CLASS
        """
        value = self.__Enc(eObj._CON_superClass)
        return value
        #end _ReadM2InheritanceSuperclass  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2InheritanceM1AttributesByInheritance(self, eObj:EM2Inheritance, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property M1AttributesByInheritance from M2Inheritance

        Args:
            eObj:EM2Inheritance The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        eSubCLass = eObj._CON_subClass
        eSuperClass = eObj._CON_superClass
        allSuperFeatures = eSuperClass.eAllAttributes()
        allSubFeatures = eSubCLass.eAllAttributes()
        #the following is not 100% correct, because more than one inheritance for the same class could exists indirectly
        allInheritFeatures = [e for e in allSuperFeatures if e in allSubFeatures] #union
        allClassInstances = self.__ReadClassInstancesRawFromContexts(eSubCLass,self.eMdb._CON_orphans.values())
        allFeatureIncarnations = [e for a in allInheritFeatures for e in a._CON_incarnations]
        allFeatureIncarnationsBySub = [e for e in allFeatureIncarnations if e._CON_m1Object in allClassInstances]
        value = self.__EncCollection(allFeatureIncarnationsBySub)
        return value
        #end _ReadM2InheritanceM1AttributesByInheritance  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2InheritanceM1AssociationsByInheritance(self, eObj:EM2Inheritance, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property M1AssociationsByInheritance from M2Inheritance

        Args:
            eObj:EM2Inheritance The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        eSubCLass = eObj._CON_subClass
        eSuperClass = eObj._CON_superClass
        allSuperFeatures = itertools.chain(self.__ReadM2ClassDstAssociationsRaw(eSuperClass),self.__ReadM2ClassSrcAssociationsRaw(eSuperClass))
        allSubFeatures = itertools.chain(self.__ReadM2ClassDstAssociationsRaw(eSubCLass),self.__ReadM2ClassSrcAssociationsRaw(eSubCLass))
        #the following is not 100% correct, because more than one inheritance for the same class could exist indirectly
        allInheritFeatures = [e for e in allSuperFeatures if e in allSubFeatures] #union
        allClassInstances = self.__ReadClassInstancesRawFromContexts(eSubCLass,self.eMdb._CON_orphans.values())
        allFeatureIncarnations = [e for a in allInheritFeatures for e in a._CON_incarnations]
        allFeatureIncarnationsBySub = [e for e in allFeatureIncarnations if e._CON_src in allClassInstances or e._CON_dst in allClassInstances]
        value = self.__EncCollection(allFeatureIncarnationsBySub)
        return value
        #end _ReadM2InheritanceM1AssociationsByInheritance  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM2InheritanceM1CompositionsByInheritance(self, eObj:EM2Inheritance, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property M1CompositionsByInheritance from M2Inheritance

        Args:
            eObj:EM2Inheritance The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        eSubCLass = eObj._CON_subClass
        eSuperClass = eObj._CON_superClass
        allSuperFeatures = itertools.chain(self.__ReadM2ClassParentCompositionsRaw(eSuperClass),self.__ReadM2ClassChildCompositionsRaw(eSuperClass))
        allSubFeatures = itertools.chain(self.__ReadM2ClassParentCompositionsRaw(eSubCLass),self.__ReadM2ClassChildCompositionsRaw(eSubCLass))
        #the following is not 100% correct, because more than one inheritance for the same class could exists indirectly
        allInheritFeatures = [e for e in allSuperFeatures if e in allSubFeatures] #union
        allClassInstances = self.__ReadClassInstancesRawFromContexts(eSubCLass,self.eMdb._CON_orphans.values())
        allFeatureIncarnations = [e for a in allInheritFeatures for e in a._CON_incarnations]
        allFeatureIncarnationsBySub = [e for e in allFeatureIncarnations if e._CON_parent in allClassInstances or e._CON_child in allClassInstances]
        value = self.__EncCollection(allFeatureIncarnationsBySub)
        return value
        #end _ReadM2InheritanceM1CompositionsByInheritance  

    # M1
    # M1MODEL
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ModelM2Model(self, eObj:EM1Model, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Class from M1Model

        Args:
            eObj:EM1Model The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2MODEL
        """
        value = self.__Enc(eObj._CON_class)
        return value
        #end _ReadM1ModelM2Model  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ModelName(self, eObj:EM1Model, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Name from M1Model

        Args:
            eObj:EM1Model The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = InitValOrNon(eObj._CON_name,STR)
        return value
        #end _ReadM1ModelName  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ModelObjects(self, eObj:EM1Model, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Objects from M1Model

        Args:
            eObj:EM1Model The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(eObj._CON_m1Objects)
        return value
        #end _ReadM1ModelObjects  

    # M1OBJECT
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectM2Class(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property M2Class from M1Object

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2CLASS
        """
        return self.__Enc(eObj.eClass)
        #end _ReadM1ObjectM2Class  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectModel(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Model from M1Object

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M1MODEL
        """
        value = self.__Enc(eObj._CON_m1Model)
        return value
        #end _ReadM1ObjectModel  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectName(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> STR:
        """Read the property Name from M1Object

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:STR
        """
        value = InitValOrNon(eObj._CON_name,STR)
        # TODO: retrieve value from eObj
        return value
        #end _ReadM1ObjectName  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectAttributes(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property Attributes from M1Object

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(eObj._CON_attributes)
        return value
        #end _ReadM1ObjectAttributes  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectSrcAssociations(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property SrcAssociations from M1Object

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(eObj._CON_srcAssociations)
        return value
        #end _ReadM1ObjectSrcAssociations  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectDstAssociations(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property DstAssociations from M1Object

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(eObj._CON_dstAssociations)
        return value
        #end _ReadM1ObjectDstAssociations  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectParentCompositions(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> LST:
        """Read the property ParentCompositions from M1Object

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        value = self.__EncCollection(eObj._CON_parentCompositions)
        return value
        #end _ReadM1ObjectParentCompositions  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectChildComposition(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property ChildComposition from M1Object

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M1COMPOSITION
        """
        value = self.__Enc(eObj._CON_childComposition)
        return value
        #end _ReadM1ObjectChildComposition  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectFeatureValues(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> VAL:
        """Read the property FeatureValues from M1Object

        Args:
            eObj:EObject The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:VAL
        """
        realFeatureName = featureName[(CONCEPT_PREFIX_LEN+CONCEPT_UNIQUE_LEN):] #remove the prefix
        normFeatureName = NormalizeFeatureName(realFeatureName) #remove the prefix
        if(0<len(normFeatureName)):
            value = self.__ReadNative(eObj,normFeatureName)
        else: #featureName == "" is a special case that shall return all values
            value = NON() #TODO: This is only necessary for unit tests. Is there a better solution?
        return value
        #end _ReadM1ObjectFeatureValues  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1ObjectFeatureInstances(self, eObj:EObject, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read all M1 feature instances for a given name

        Args:
            eObj:EObject The object from which it is read
            feature:str The feature name proceeded by
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:LST
        """
        featureInstances = []
        realFeatureName = featureName[(CONCEPT_PREFIX_LEN+CONCEPT_UNIQUE_LEN):] #remove the prefix
        normFeatureName = NormalizeFeatureName(realFeatureName) #remove the prefix
        if(0<len(normFeatureName)):
            eFeatures = self.__FindElementeByIdOrNameRaw(normFeatureName, eObj.eClass, None)
            if(1 != len(eFeatures)):
                raise EOQ_ERROR_INVALID_VALUE("%s is not a known feature"%(realFeatureName))
            eFeature = eFeatures[0]
            #check mul
            if(IsMultivalueFeature(realFeatureName) and not eFeature.many):
                self.logger.Warn("%s indicates multi value feature, but is single."%(featureName))
            elif(not IsMultivalueFeature(realFeatureName) and eFeature.many):
                self.logger.Warn("%s indicates single  feature, but is multi."%(featureName))
            #get featureInstances

            if(self._IsM2Attribute(eFeature)):
                featureInstances = [e for e in eObj._CON_attributes if e._CON_class == eFeature]
            elif(self._IsM2Association(eFeature)):
                if(self.__GetAugmentedProperty(eFeature,'_CON_isDst',False)):
                    featureInstances = [e for e in eObj._CON_dstAssociations if e._CON_class == eFeature]
                else:
                    featureInstances = [e for e in eObj._CON_srcAssociations if e._CON_class == eFeature]
            elif(self._IsM2Composition(eFeature)):
                featureInstances = [e for e in eObj._CON_parentCompositions if e._CON_class == eFeature]
        else: #featureName == "" is a special case that shall return all instances
            featureInstances = itertools.chain(eObj._CON_attributes,eObj._CON_srcAssociations,eObj._CON_dstAssociations,eObj._CON_parentCompositions)
        value = self.__EncCollection(featureInstances)
        return value
        #end _ReadM1ObjectChildComposition  

    # M1FEATURE
    # M1ATTRIBUTE
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1AttributeM2Attribute(self, eObj:EM1Attribute, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property M2Attribute from M1Attribute

        Args:
            eObj:EM1Attribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2ATTRIBUTE
        """
        value = self.__Enc(eObj._CON_class)
        return value
        #end _ReadM1AttributeM2Attribute  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1AttributeObject(self, eObj:EM1Attribute, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Object from M1Attribute

        Args:
            eObj:EM1Attribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M1OBJECT
        """
        value = self.__Enc(eObj._CON_m1Object)
        return value
        #end _ReadM1AttributeObject  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1AttributeValue(self, eObj:EM1Attribute, featureName:str=None, eContext:EObject=None) -> PRM:
        """Read the property Value from M1Attribute

        Args:
            eObj:EM1Attribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:PRM
        """
        eValue = eObj._CON_m1Object.eGet(eObj._CON_class)
        if(eObj._CON_class.many):
            eValue = eValue[eObj._CON_pos]
        value = eObj._CON_class._CON_type(eValue)
        return value
        #end _ReadM1AttributeValue  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1AttributePos(self, eObj:EM1Attribute, featureName:str=None, eContext:EObject=None) -> U64:
        """Read the property Pos from M1Attribute

        Args:
            eObj:EM1Attribute The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:U64
        """
        value = U64(eObj._CON_pos)
        return value
        #end _ReadM1AttributePos  

    # M1ASSOCIATION
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1AssociationM2Association(self, eObj:EM1Association, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property M2Association from M1Association

        Args:
            eObj:EM1Association The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2ASSOCIATION
        """
        value = self.__Enc(eObj._CON_class)
        return value
        #end _ReadM1AssociationM2Association  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1AssociationSrc(self, eObj:EM1Association, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Src from M1Association

        Args:
            eObj:EM1Association The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M1OBJECT
        """
        value = self.__Enc(eObj._CON_src)
        return value
        #end _ReadM1AssociationSrc  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1AssociationSrcPos(self, eObj:EM1Association, featureName:str=None, eContext:EObject=None) -> U64:
        """Read the property SrcPos from M1Association

        Args:
            eObj:EM1Association The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:U64
        """
        value = U64(eObj._CON_srcPos)
        return value
        #end _ReadM1AssociationPos  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1AssociationDst(self, eObj:EM1Association, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Dst from M1Association

        Args:
            eObj:EM1Association The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:MXELEMENT
        """
        value = self.__Enc(eObj._CON_dst)
        return value
        #end _ReadM1AssociationDst  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1AssociationDstPos(self, eObj:EM1Association, featureName:str=None, eContext:EObject=None) -> U64:
        """Read the property DstPos from M1Association

        Args:
            eObj:EM1Association The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:U64
        """
        value = U64(eObj._CON_dstPos)
        return value
        #end _ReadM1AssociationPos  

    # M1COMPOSITION
    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1CompositionM2Composition(self, eObj:EM1Composition, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property M2Composition from M1Composition

        Args:
            eObj:EM1Composition The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M2COMPOSITION
        """
        value = self.__Enc(eObj._CON_class)
        return value
        #end _ReadM1CompositionM2Composition  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1CompositionParent(self, eObj:EM1Composition, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Parent from M1Composition

        Args:
            eObj:EM1Composition The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:M1OBJECT
        """
        value = self.__Enc(eObj._CON_parent)
        return value
        #end _ReadM1CompositionParent  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1CompositionChild(self, eObj:EM1Composition, featureName:str=None, eContext:EObject=None) -> Obj:
        """Read the property Child from M1Composition

        Args:
            eObj:EM1Composition The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:MXELEMENT
        """
        value = self.__Enc(eObj._CON_child)
        return value
        #end _ReadM1CompositionChild  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _ReadM1CompositionPos(self, eObj:EM1Composition, featureName:str=None, eContext:EObject=None) -> U64:
        """Read the property Pos from M1Composition

        Args:
            eObj:EM1Composition The object from which it is read
            eContext:EObject (optional) the context for the read operation. This works only for a few properties.
        Returns:
            value:U64
        """
        value = U64(eObj._CON_pos)
        return value
        #end _ReadM1CompositionPos  


    # #########################
    # Concept UPDATE handlers #
    # #########################
    
    # MX
    # MXMDB
    # MXELEMENT
    #@generate head no
    #@generate comment no
    #@generate body no
    def _UpdateMxElementStrId(self, eObj:EObject, value:STR, ePosition:int) -> (STR,NON,NON,NON):
        """Update the property StrId of MxElement

        Args:
            eObj:EObject The object whose property is updated
            value:STR The new value
        Returns:
            oldValue:STR the old value
            oldOwner:Obj (optional) the old owner of an object element
            oldComposition:Obj (optional) the old composition of an object element
            oldPosition:U64 (optional) the old position of the element in an composition

        """
        raise NotImplementedError("_UpdateMxElementStrId")
        oldValue = None
        # TODO: update value
        return (oldValue,NON(),NON(),NON())
        #end _UpdateMxElementStrId  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _UpdateMxElementDocumentation(self, eObj:EObject, value:STR, ePosition:int) -> (STR,NON,NON,NON):
        """Update the property Documentation of MxElement

        Args:
            eObj:EObject The object whose property is updated
            value:STR The new value
        Returns:
            oldValue:STR the old value
            oldOwner:Obj (optional) the old owner of an object element
            oldComposition:Obj (optional) the old composition of an object element
            oldPosition:U64 (optional) the old position of the element in an composition

        """
        eValue = self.__ValidateType(value, STR, MXELEMENT.DOCUMENTATION, True).GetVal()
        eOldValue = eObj._CON_documentation
        eObj._CON_documentation = eValue
        oldValue = InitValOrNon(eOldValue,STR)
        return (oldValue,NON(),NON(),NON())
        #end _UpdateMxElementDocumentation  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _UpdateMxElementOwner(self, eObj:EObject, value:STR, ePosition:int) -> (STR,NON,NON,NON):
        """Update the property Owner of MxElement

        Args:
            eObj:EObject The object whose property is updated
            value:STR The new value
        Returns:
            oldValue:STR the old value
            oldOwner:Obj (optional) the old owner of an object element
            oldComposition:Obj (optional) the old composition of an object element
            oldPosition:U64 (optional) the old position of the element in an composition

        """
        eValue = self.__ValidateType(value, STR, MXELEMENT.OWNER, True).GetVal()
        eOldValue = eObj._CON_owner
        eObj._CON_owner = eValue
        oldValue = InitValOrNon(eOldValue,STR)
        return (oldValue,NON(),NON(),NON())
        #end _UpdateMxElementOwner  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _UpdateMxElementGroup(self, eObj:EObject, value:STR, ePosition:int) -> (STR,NON,NON,NON):
        """Update the property Group of MxElement

        Args:
            eObj:EObject The object whose property is updated
            value:STR The new value
        Returns:
            oldValue:STR the old value
            oldOwner:Obj (optional) the old owner of an object element
            oldComposition:Obj (optional) the old composition of an object element
            oldPosition:U64 (optional) the old position of the element in an composition

        """
        eValue = self.__ValidateType(value, STR, MXELEMENT.GROUP, True).GetVal()
        eOldValue = eObj._CON_group
        eObj._CON_group = eValue
        oldValue = InitValOrNon(eOldValue,STR)
        return (oldValue,NON(),NON(),NON())
        #end _UpdateMxElementGroup  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _UpdateMxElementPermissions(self, eObj:EObject, value:STR, ePosition:int) -> (STR,NON,NON,NON):
        """Update the property Permissions of MxElement

        Args:
            eObj:EObject The object whose property is updated
            value:STR The new value
        Returns:
            oldValue:STR the old value
            oldOwner:Obj (optional) the old owner of an object element
            oldComposition:Obj (optional) the old composition of an object element
            oldPosition:U64 (optional) the old position of the element in an composition

        """
        eValue = self.__ValidateType(value, STR, MXELEMENT.PERMISSIONS, True).GetVal()
        eOldValue = self.__UpdateList(eObj._CON_permissions,ePosition,eValue,ECORE_FEATURE_MAX_LEN)
        oldValue = InitValOrNon(eOldValue,STR)
        return (oldValue,NON(),NON(),NON())
        #end _UpdateMxElementPermissions  

    # MXCONSTRAINT
    # M2
    # M2PRIMITIVES
    # M2PACKAGE
    # M2MODEL
    # M2ENUM
    # M2OPTIONOFENUM
    # M2CLASS
    # M2ATTRIBUTE
    # M2ASSOCIATION
    # M2COMPOSITION
    # M2INHERITANCE
    # M1
    # M1MODEL
    # M1OBJECT
    # M1FEATURE
    # M1ATTRIBUTE
    #@generate head no
    #@generate comment no
    #@generate body no
    def _UpdateM1AttributeValue(self, eObj:EM1Attribute, value:PRM, ePosition:int) -> (PRM,NON,NON,NON):
        """Update the property Value of M1Attribute

        Args:
            eObj:EM1Attribute The object whose property is updated
            value:PRM The new value
        Returns:
            oldValue:PRM the old value
            oldOwner:Obj (optional) the old owner of an object element
            oldComposition:Obj (optional) the old composition of an object element
            oldPosition:U64 (optional) the old position of the element in an composition

        """
        eValue = self.__ValidateType(value, eObj._CON_class._CON_type, eObj._CON_class.name).GetVal()
        eOldValue = self.__UpdateEFeature(eObj._CON_m1Object, eObj._CON_class, eObj._CON_pos, eValue, eObj._CON_class.upper, EFEATURE_TYPES.ATTRIBUTE, eObj)
        oldValue = eObj._CON_class._CON_type(eOldValue)
        return (oldValue,NON(),NON(),NON())
        #end _UpdateM1AttributeValue  

    # M1ASSOCIATION
    # M1COMPOSITION


    # ##########################
    # Concept DELETE handlers #
    # ##########################
    
    # MX
    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteMxConstraint(self, eObj:EMxConstraint)->Tuple[STR,LST,LST]:
        """Delete an MxConstraint instance

        Cannot be deleted if the following properties are set :
        native:
        artificial: DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EMxConstraint The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                element:MXELEMENT
                expression:STR
            recoveryArgs: LST the args that are required to restore the element
                mxelementconstraintspos:U64
        """
        # check if element is deletable
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete MXCONSTRAINT if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete MXCONSTRAINT if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete MXCONSTRAINT if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete MXCONSTRAINT if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete MXCONSTRAINT if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.MXCONSTRAINT)
        # get the create args
        eElement = eObj._CON_element
        element = self.__Enc(eElement)
        eExpression = eObj._CON_expression
        expression = STR(eExpression)
        createArgs = LST([element, expression])
        # get recovery args
        pos = eElement._CON_constraints.index(eObj)
        recoveryArgs = LST([U64(pos)])
        # clean up
        eObj._CON_element = None
        eObj._CON_expression = None
        eElement._CON_constraints.remove(eObj)
        # get rid of the EObject
        eObj.delete()
        del eObj
        # return
        return (conceptId, createArgs, recoveryArgs)  

    # M2
    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM2Package(self, eObj:EPackage)->Tuple[STR,LST,LST]:
        """Delete an M2Package instance

        Cannot be deleted if the following properties are set :
        native: SUBPACKAGES, CLASSES, ENUMS
        artificial: M1MODELS, DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EPackage The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                name:STR
                superpackage:M2PACKAGE
            recoveryArgs: LST the args that are required to restore the element
                m2packagesubpackagespos:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM2PackageSubpackages(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2PACKAGE if SUBPACKAGES is not empty.")
        if(0<len(self._ReadM2PackageClasses(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2PACKAGE if CLASSES is not empty.")
        if(0<len(self._ReadM2PackageEnums(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2PACKAGE if ENUMS is not empty.")
        if(0<len(self._ReadM2PackageM1Models(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2PACKAGE if M1MODELS is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2PACKAGE if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2PACKAGE if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2PACKAGE if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2PACKAGE if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2PACKAGE if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M2PACKAGE)
        # get create args
        name = self._ReadM2PackageName(eObj)
        eSuperpackage = eObj.eSuperPackage
        superpackage = self.__Enc(eSuperpackage)
        createArgs = LST([name, superpackage])
        # get recovery args
        pos = eSuperpackage.eSubpackages.index(eObj)
        recoveryArgs = LST([U64(pos)])
        # clean up
        self.__UpdateMultiValueEFeature(eSuperpackage,ECORE_BASE_FEATURES_EPACKAGE_ESUBPACKAGES,pos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        # clean up cache
        self.__UpdateElementNameCache(eObj, None, eObj.name, None)
        self.__UpdateCreateIdStrCache(None,None,eObj._CON_strId)
        # get rid of the EObject
        eObj.delete()
        del eObj
        # return
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM2Model(self, eObj:EPackage)->Tuple[STR,LST,LST]:
        """Delete an M2Model instance

        Cannot be deleted if the following properties are set :
        native: SUBPACKAGES, CLASSES, ENUMS
        artificial: M1MODELS, DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EPackage The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                name:STR
            recoveryArgs: LST the args that are required to restore the element
                mxmdbm2modelspos:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM2PackageSubpackages(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2MODEL if SUBPACKAGES is not empty.")
        if(0<len(self._ReadM2PackageClasses(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2MODEL if CLASSES is not empty.")
        if(0<len(self._ReadM2PackageEnums(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2MODEL if ENUMS is not empty.")
        if(0<len(self._ReadM2PackageM1Models(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2MODEL if M1MODELS is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2MODEL if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2MODEL if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2MODEL if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2MODEL if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2MODEL if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M2MODEL)
        # get create args
        name = STR(eObj.name)
        createArgs = LST([name])
        # get recovery args
        pos = self.eMdb._CON_m2Models.index(eObj)
        recoveryArgs = LST([U64(pos)])
        # clean up
        self.eMdb._CON_m2Models.pop(pos)
        # clean up cache
        self.__UpdateElementNameCache(eObj, None, eObj.name, None)
        self.__UpdateCreateIdStrCache(None,None,eObj._CON_strId)
        # get rid of the EObject
        eObj.delete()
        del eObj
        # return
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM2Enum(self, eObj:EEnum)->Tuple[STR,LST,LST]:
        """Delete an M2Enum instance

        Cannot be deleted if the following properties are set :
        native: OPTIONS
        artificial: DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EEnum The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                name:STR
                m2package:M2PACKAGE
            recoveryArgs: LST the args that are required to restore the element
                m2classenumspos:UNSPECIFIED
        """
        # check if element is deletable
        if(0<len(self._ReadM2EnumOptions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ENUM if OPTIONS is not empty.")
        if(0<len(self._ReadM2EnumAttributes(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ENUM if M2ATTRIBUTES is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ENUM if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ENUM if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ENUM if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ENUM if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ENUM if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M2ENUM)
        # get create args
        name = STR(eObj.name)
        eM2Model = eObj.ePackage
        m2Model = self.__Enc(eM2Model)
        createArgs = LST([name, m2Model])
        # get recovery args
        pos = eM2Model.eClassifiers.index(eObj)
        recoveryArgs = LST([U64(pos)])
        # clean up
        self.__UpdateMultiValueEFeature(eM2Model,ECORE_BASE_FEATURES_EPACKAGE_ECLASSIFIERS,pos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        # clean up cache
        self.__UpdateElementNameCache(eObj, None, eObj.name, None)
        self.__UpdateCreateIdStrCache(None,None,eObj._CON_strId)
        # get rid of the EObject
        eObj.delete()
        del eObj
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM2OptionOfEnum(self, eObj:EEnumLiteral)->Tuple[STR,LST,LST]:
        """Delete an M2OptionOfEnum instance

        Cannot be deleted if the following properties are set :
        native: M1ATTRIBUTESUSINGOPTION
        artificial: DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EEnumLiteral The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                name:STR
                value:U64
                enum:M2ENUM
            recoveryArgs: LST the args that are required to restore the element
                optionsposofm2enum:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM2OptionOfEnumM1AttributesUsingOption(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2OPTIONOFENUM if M1ATTRIBUTESUSINGOPTION is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2OPTIONOFENUM if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2OPTIONOFENUM if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2OPTIONOFENUM if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2OPTIONOFENUM if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2OPTIONOFENUM if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M2OPTIONOFENUM)
        # get create args
        name = STR(eObj.name)
        value = U64(eObj.value)
        eEnum = eObj.eEnum
        enum = self.__Enc(eEnum)
        createArgs = LST([name, value, enum])
        # get recovery args
        pos = eEnum.eLiterals.index(eObj)
        recoveryArgs = LST([U64(pos)])
        # clean up
        self.__UpdateMultiValueEFeature(eEnum,ECORE_BASE_FEATURES_EENUM_ELITERALS,pos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        # clean up cache
        self.__UpdateElementNameCache(eObj, None, eObj.name, None)
        self.__UpdateCreateIdStrCache(None,None,eObj._CON_strId)
        # get rid of the EObject
        eObj.delete()
        del eObj
        # return
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM2Class(self, eObj:EClass)->Tuple[STR,LST,LST]:
        """Delete an M2Class instance

        Cannot be deleted if the following properties are set :
        native: MYINSTANCES, MYATTRIBUTES, MYSRCASSOCIATIONS, MYDSTASSOCIATIONS, MYPARENTCOMPOSITIONS, MYCHILDCOMPOSITIONS
        artificial: MYSPECIALIZATIONS, MYGENERALIZATIONS, DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EClass The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                name:STR
                abstract:BOL
                m2package:M2PACKAGE
            recoveryArgs: LST the args that are required to restore the element
                m2enumclassespos:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM2ClassMyInstances(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if MYINSTANCES is not empty.")
        if(0<len(self._ReadM2ClassMyAttributes(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if MYATTRIBUTES is not empty.")
        if(0<len(self._ReadM2ClassMySrcAssociations(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if MYSRCASSOCIATIONS is not empty.")
        if(0<len(self._ReadM2ClassMyDstAssociations(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if MYDSTASSOCIATIONS is not empty.")
        if(0<len(self._ReadM2ClassMyParentCompositions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if MYPARENTCOMPOSITIONS is not empty.")
        if(0<len(self._ReadM2ClassMyChildCompositions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if MYCHILDCOMPOSITIONS is not empty.")
        if(0<len(self._ReadM2ClassMySpecializations(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if MYSPECIALIZATIONS is not empty.")
        if(0<len(self._ReadM2ClassMyGeneralizations(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if MYGENERALIZATIONS is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2CLASS if CONSTRAINTS is not empty.")
        # get concept ID
        conceptId = STR(CONCEPTS.M2CLASS)
        # get create args
        name = STR(eObj.name)
        abstract = BOL(eObj.abstract)
        eM2Model = eObj.ePackage
        m2Model = self.__Enc(eM2Model)
        createArgs = LST([name, abstract, m2Model])
        # get recovery args
        pos = eM2Model.eClassifiers.index(eObj)
        recoveryArgs = LST([U64(pos)])
        # clean up
        self.__UpdateMultiValueEFeature(eM2Model,ECORE_BASE_FEATURES_EPACKAGE_ECLASSIFIERS,pos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        # clean up cache
        self.__UpdateElementNameCache(eObj, None, eObj.name, None)
        self.__UpdateCreateIdStrCache(None,None,eObj._CON_strId)
        # get rid of the EObject
        eObj.delete()
        del eObj
        # return
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM2Attribute(self, eObj:EAttribute)->Tuple[STR,LST,LST]:
        """Delete an M2Attribute instance

        Cannot be deleted if the following properties are set :
        native:
        artificial: MYINSTANCES, DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EAttribute The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                name:STR
                srcclass:M2CLASS
                primtype:STR
                mul:I64
                unit:STR
                enum:M2ENUM
            recoveryArgs: LST the args that are required to restore the element
                m2classattributespos:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM2AttributeMyInstances(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ATTRIBUTE if MYINSTANCES is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ATTRIBUTE if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ATTRIBUTE if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ATTRIBUTE if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ATTRIBUTE if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ATTRIBUTE if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M2ATTRIBUTE)
        # get create args
        eName = eObj.name
        name = STR(eName)
        eSrcClass = eObj.eContainingClass #internal
        srcClass = self.__Enc(eSrcClass)
        primType = self._ReadM2AttributePrimType(eObj)
        enum = self._ReadM2AttributeEnum(eObj)
        mul = I64(eObj.upperBound)
        unit = InitValOrNon(eObj._CON_unit,STR)
        createArgs = LST([name, srcClass, primType, mul, unit, enum])
        # get recovery args
        srcPos = eSrcClass.eStructuralFeatures.index(eObj)
        recoveryArgs = LST([U64(srcPos)])
        # clean up
        self.__UpdateMultiValueEFeature(eSrcClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,srcPos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        if(enum):
            eEnum = eObj.eType
            self.__GetAugmentedProperty(eEnum, "_CON_m2Attributes", []).remove(eObj)
        # clean up cache
        self.__UpdateElementNameCache(eObj, None, eObj.name, None)
        self.__UpdateCreateIdStrCache(None,None,eObj._CON_strId)
        # get rid of the EObject
        eObj.delete()
        del eObj
        # FIX: pyecore will not remove features on existing instances,
        # but only set the feature type to None, which will cause failures in
        # deletion. So do remove entries manually
        m1SrcInstances = self.__ReadClassInstancesRawFromContexts(eSrcClass,self.eMdb._CON_orphans.values())
        for e in m1SrcInstances:
            if hasattr(e, eName):
                delattr(e,eName)
        # return
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM2Association(self, eObj:EReference)->Tuple[STR,LST,LST]:
        """Delete an M2Association instance

        Cannot be deleted if the following properties are set :
        native:
        artificial: MYINSTANCES, DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EReference The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                srcname:STR
                srcclass:M2CLASS
                srcmul:I64
                dstname:STR
                dstclass:M2CLASS
                dstmul:I64
                anydst:BOL
            recoveryArgs: LST the args that are required to restore the element
                m2classassociationspos:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM2AssociationMyInstances(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ASSOCIATION if MYINSTANCES is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ASSOCIATION if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ASSOCIATION if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ASSOCIATION if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ASSOCIATION if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2ASSOCIATION if CONSTRAINTS is not empty.")
        # get concept ID
        conceptId = STR(CONCEPTS.M2ASSOCIATION)
        # get create args
        eSrcName = eObj._CON_srcName
        srcName = STR(eSrcName)
        eSrcClass = eObj.eContainingClass #internal
        srcClass = self.__Enc(eSrcClass)
        srcMul = I64(eObj._CON_srcMul)
        eDstName = eObj.name
        dstName = STR(eDstName)
        eDstClass = eObj.eType #internal
        dstMul = I64(eObj.upperBound)
        dstClass = self._ReadM2AssociationDstClass(eObj)
        anyDst = self._ReadM2AssociationAnyDst(eObj)
        createArgs = LST([srcName, srcClass, srcMul, dstName, dstClass, dstMul, anyDst])
        # get recovery args
        srcPos = eSrcClass.eStructuralFeatures.index(eObj)
        recoveryArgs = LST([U64(srcPos)])
        # clean up
        self.__UpdateMultiValueEFeature(eSrcClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,srcPos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        eOpposite = None
        if(anyDst):
            del self.anyM2Associations[eObj]
        else:
            eOpposite = eObj.eOpposite
            dstPos = eDstClass.eStructuralFeatures.index(eOpposite)
            self.__UpdateMultiValueEFeature(eDstClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,dstPos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
            eObj.eOpposite = None #clear the link
        # clean up cache
        self.__UpdateElementNameCache(eObj, None, eObj.name, None)
        self.__UpdateCreateIdStrCache(None,None,eObj._CON_strId)
        # get rid of the EObject
        eObj.delete()
        del eObj
        if(eOpposite):
            if(eOpposite in self.eMdb._CON_orphans):
                del self.eMdb._CON_orphans[eOpposite]
            eOpposite.delete()
            self.__EncLastTime(self.__Enc(eOpposite)) #because this is later not removed from the ids
            del eOpposite
        # FIX: pyecore will not remove features on existing instances,
        # but only set the feature type to None, which will cause failures in
        # deletion. So do remove entries manually
        m1SrcInstances = self.__ReadClassInstancesRawFromContexts(eSrcClass,self.eMdb._CON_orphans.values())
        for e in m1SrcInstances:
            if hasattr(e, eDstName):
                delattr(e,eDstName)
        if(not dstClass.IsNone()):
            m1DstInstances = self.__ReadClassInstancesRawFromContexts(eDstClass,self.eMdb._CON_orphans.values())
            for e in m1DstInstances:
                if hasattr(e, eSrcName):
                    delattr(e,eSrcName)
        # return
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM2Composition(self, eObj:EReference)->Tuple[STR,LST,LST]:
        """Delete an M2Composition instance

        Cannot be deleted if the following properties are set :
        native:
        artificial: MYINSTANCES, DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EReference The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                name:STR
                parentclass:M2CLASS
                childclass:M2CLASS
                childmul:I64
                anychild:BOL
            recoveryArgs: LST the args that are required to restore the element
                m2classcompositionspos:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM2CompositionMyInstances(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2COMPOSITION if MYINSTANCES is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2COMPOSITION if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2COMPOSITION if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2COMPOSITION if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2COMPOSITION if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2COMPOSITION if CONSTRAINTS is not empty.")
        # get conceptId
        conceptId = STR(CONCEPTS.M2COMPOSITION)
        #get create args
        eName = eObj.name
        name = STR(eName)
        eSrcClass = eObj.eContainingClass #internal
        srcClass = self.__Enc(eSrcClass)
        eDstClass = eObj.eType #internal
        dstMul = I64(eObj.upperBound)
        #eDstClass is special because it belongs to anyDST
        dstClass = self._ReadM2CompositionChildClass(eObj)
        anyDst = self._ReadM2CompositionAnyChild(eObj)
        createArgs = LST([name, srcClass, dstClass, dstMul, anyDst])
        # get recovery args
        pos = eSrcClass.eStructuralFeatures.index(eObj)
        recoveryArgs = LST([U64(pos)])
        # clean up
        self.__UpdateMultiValueEFeature(eSrcClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,pos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        eOpposite = eObj.eOpposite
        eOppName = None
        if(anyDst):
            del self.anyM2Composition[eObj]
        elif(eOpposite):
            eOppName = eOpposite.name
            dstPos = eDstClass.eStructuralFeatures.index(eOpposite)
            self.__UpdateMultiValueEFeature(eDstClass,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,dstPos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
            eObj.eOpposite = None #clear the link
        # clean up cache
        self.__UpdateElementNameCache(eObj, None, eObj.name, None)
        self.__UpdateCreateIdStrCache(None,None,eObj._CON_strId)
        # get rid of the EObject
        eObj.delete()
        del eObj
        if(eOpposite):
            if(eOpposite in self.eMdb._CON_orphans):
                del self.eMdb._CON_orphans[eOpposite]
            eOpposite.delete()
            self.__EncLastTime(self.__Enc(eOpposite)) #because this is later not removed from the ids
            del eOpposite
        # FIX: pyecore will not remove features on existing instances,
        # but only set the feature type to None, which will cause failures in
        # deletion. So do remove entries manually
        m1SrcInstances = self.__ReadClassInstancesRawFromContexts(eSrcClass,self.eMdb._CON_orphans.values())
        for e in m1SrcInstances:
            if hasattr(e, eName):
                delattr(e,eName)
        if(not dstClass.IsNone()):
            m1DstInstances = self.__ReadClassInstancesRawFromContexts(eDstClass,self.eMdb._CON_orphans.values())
            for e in m1DstInstances:
                if hasattr(e, eOppName):
                    delattr(e,eOppName)
        # return
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM2Inheritance(self, eObj:EM2Inheritance)->Tuple[STR,LST,LST]:
        """Delete an M2Inheritance instance

        Cannot be deleted if the following properties are set :
        native: ALLM1ATTRIBUTESBYINHERITANCE, ALLM1ASSOCIATIONSBYINHERITANCE, ALLM1COMPOSITIONSBYINHERITANCE
        artificial: DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EM2Inheritance The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                subclass:M2CLASS
                superclass:M2CLASS
            recoveryArgs: LST the args that are required to restore the element
                m2classsubinheritancespos:U64
                m2classsuperinheritancespos:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM2InheritanceM1AttributesByInheritance(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2INHERITANCE if ALLM1ATTRIBUTESBYINHERITANCE is not empty.")
        if(0<len(self._ReadM2InheritanceM1AssociationsByInheritance(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2INHERITANCE if ALLM1ASSOCIATIONSBYINHERITANCE is not empty.")
        if(0<len(self._ReadM2InheritanceM1CompositionsByInheritance(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2INHERITANCE if ALLM1COMPOSITIONSBYINHERITANCE is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2INHERITANCE if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2INHERITANCE if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2INHERITANCE if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2INHERITANCE if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M2INHERITANCE if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M2INHERITANCE)
        # get create args
        eSubClass = eObj._CON_subClass
        subclass = self.__Enc(eSubClass)
        eSuperClass = eObj._CON_superClass
        superclass = self.__Enc(eSuperClass)
        createArgs = LST([subclass, superclass])
        # get recovery args
        superPos = eSubClass.eSuperTypes.index(eSuperClass)
        subPos = eSubClass._CON_generalizations.index(eObj)
        recoveryArgs = LST([U64(subPos),U64(superPos)])
        # clean up
        self.__UpdateMultiValueEFeature(eSubClass,ECORE_BASE_FEATURES_ECLASS_ESUPERTYPES,superPos,None,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.ASSOCIATION)
        eObj._CON_subClass = None
        eObj._CON_superClass = None
        eSuperClass._CON_specializations.remove(eObj)
        eSubClass._CON_generalizations.remove(eObj)
        # clean up cache
        self.__UpdateCreateIdStrCache(None,None,eObj._CON_strId)
        # get rid of the EObject
        eObj.delete()
        del eObj
        # return
        return (conceptId, createArgs, recoveryArgs)  

    # M1
    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM1Model(self, eObj:EM1Model)->Tuple[STR,LST,LST]:
        """Delete an M1Model instance

        Cannot be deleted if the following properties are set :
        native:
        artificial: OBJECTS, DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EM1Model The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                class:M2MODEL
                name:STR
            recoveryArgs: LST the args that are required to restore the element
                mxmdbm1modelspos:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM1ModelObjects(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1MODEL if M1OBJECTS is not empty.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1MODEL if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1MODEL if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1MODEL if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1MODEL if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1MODEL if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M1MODEL)
        # get create args
        m2Model = self.__Enc(eObj._CON_class)
        name = self._ReadM1ModelName(eObj)
        createArgs = LST([m2Model,name])
        # get recoveryArgs
        pos = self.eMdb._CON_m1Models.index(eObj)
        recoveryArgs = LST([U64(pos)])
        # clean up
        eObj._CON_class = None
        self.eMdb._CON_m1Models.remove(eObj)
        # get rid of the EObject
        eObj.delete()
        del eObj
        # return
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM1Object(self, eObj:EObject)->Tuple[STR,LST,LST]:
        """Delete an M1Object instance

        Cannot be deleted if the following properties are set :
        native:
        artificial: ATTRIBUTES, SRCASSOCIATIONS, DSTASSOCIATIONS, PARENTCOMPOSITIONS, CHILDCOMPOSITION, DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EObject The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                m2class:M2CLASS
                m1model:M1MODEL
                name:STR
            recoveryArgs: LST the args that are required to restore the element
                m1modelobjectspos:U64
        """
        # check if element is deletable
        if(0<len(self._ReadM1ObjectAttributes(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if ATTRIBUTES is not empty.")
        if(0<len(self._ReadM1ObjectSrcAssociations(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if SRCASSOCIATIONS is not empty.")
        if(0<len(self._ReadM1ObjectDstAssociations(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if DSTASSOCIATIONS is not empty.")
        if(0<len(self._ReadM1ObjectParentCompositions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if PARENTCOMPOSITIONS is not empty.")
        if(not self._ReadM1ObjectChildComposition(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if CHILDCOMPOSITION is set.")
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1OBJECT if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M1OBJECT)
        # get create args
        eM2Class = eObj.eClass
        m2Class = self.__Enc(eM2Class)
        eM1Model = eObj._CON_m1Model #TODO: can be zero. Need default M1Model and M2 Model
        m1model = self.__Enc(eM1Model)
        name = self._ReadM1ObjectName(eObj)
        createArgs = LST([m2Class, m1model, name])
        # get recoveryArgs
        pos = eM1Model._CON_m1Objects.index(eObj)
        recoveryArgs = LST([U64(pos)])
        # clean up
        eM1Model._CON_m1Objects.remove(eObj)
        eM1Model._CON_m1Model = None
        # artificially update the child cache
        del eM1Model._eoqChildrenByClassCache[eM2Class][eObj]
        #eObj._eoqOldParent = eM1Model #this is just a fake to make the next command work
        #self.__UpdateChildStateAndCache(eObj)
        #eObj._eoqOldParent = None
        # get rid of the EObject
        eObj.delete()
        del eObj
        # return
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM1Attribute(self, eObj:EM1Attribute)->Tuple[STR,LST,LST]:
        """Delete an M1Attribute instance

        Cannot be deleted if the following properties are set :
        native:
        artificial: DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EM1Attribute The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                m2attribute:M2ATTRIBUTE
                object:M1OBJECT
                value:PRM
            recoveryArgs: LST the args that are required to restore the element
                pos:U64
        """
        # check if element is deletable
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ATTRIBUTE if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ATTRIBUTE if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ATTRIBUTE if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ATTRIBUTE if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ATTRIBUTE if CONSTRAINTS is not empty.")
        #get concept ID
        conceptId = STR(CONCEPTS.M1ATTRIBUTE)
        # get create arguments
        eFeature = eObj._CON_class
        feature = self.__Enc(eFeature)
        value = self._ReadM1AttributeValue(eObj)
        eM1Obj = eObj._CON_m1Object
        m1Obj = self.__Enc(eM1Obj)
        createArgs = LST([feature, m1Obj, value])
        # get recovery args
        recoveryArgs = LST([U64(eObj._CON_pos)])
        # clean up the eFeature (opposite is cleaned automatically)
        self.__UpdateEFeature(eM1Obj, eFeature, eObj._CON_pos, None, eFeature.upperBound, EFEATURE_TYPES.ATTRIBUTE, eObj)
        # delete of eObject is not necessary, because the element is removed with the above feature update
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM1Association(self, eObj:EM1Association)->Tuple[STR,LST,LST]:
        """Delete an M1Association instance

        Cannot be deleted if the following properties are set :
        native:
        artificial: DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EM1Association The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                m2association:M2ASSOCIATION
                src:M1OBJECT
                dst:MXELEMENT
            recoveryArgs: LST the args that are required to restore the element
                srcpos:U64
                dstpos:U64
        """
        # check if element is deletable
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ASSOCIATION if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ASSOCIATION if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ASSOCIATION if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ASSOCIATION if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1ASSOCIATION if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M1ASSOCIATION)
        # get create args
        eFeature = eObj._CON_class
        feature = self.__Enc(eFeature)
        eSrc = eObj._CON_src
        src = self.__Enc(eSrc)
        eDst = eObj._CON_dst
        dst = self.__Enc(eDst)
        createArgs = LST([feature, src, dst])
        # get recovery args
        recoveryArgs = LST([U64(eObj._CON_srcPos),U64(eObj._CON_dstPos)])
        # clean up the eFeature (opposite is cleaned automatically)
        self.__UpdateEFeature(eSrc, eFeature, eObj._CON_srcPos, None, eFeature.upperBound, EFEATURE_TYPES.ASSOCIATION, eObj)
        # delete of eObject is not necessary, because the element is removed with the above feature update
        return (conceptId, createArgs, recoveryArgs)  

    #@generate head no
    #@generate comment no
    #@generate body no
    def _DeleteM1Composition(self, eObj:EM1Composition)->Tuple[STR,LST,LST]:
        """Delete an M1Composition instance

        Cannot be deleted if the following properties are set :
        native:
        artificial: DOCUMENTATION, OWNER, GROUP, PERMISSIONS, CONSTRAINTS

        Args:
            eObj: EM1Composition The object to be deleted
        Returns:
            classId: STR or Obj the class Id necessary to create the element
            createArgs: LST the list of create arguments necessary to create the same element
                m2composition:M2COMPOSITION
                parent:M1OBJECT
                child:MXELEMENT
            recoveryArgs: LST the args that are required to restore the element
                pos:U64
        """
        # check if element is deletable
        if(not self._ReadMxElementDocumentation(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1COMPOSITION if DOCUMENTATION is set.")
        if(not self._ReadMxElementOwner(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1COMPOSITION if OWNER is set.")
        if(not self._ReadMxElementGroup(eObj).IsNone()): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1COMPOSITION if GROUP is set.")
        if(0<len(self._ReadMxElementPermissions(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1COMPOSITION if PERMISSIONS is not empty.")
        if(0<len(self._ReadMxElementConstraints(eObj))): raise EOQ_ERROR_INVALID_OPERATION("Cannot delete M1COMPOSITION if CONSTRAINTS is not empty.")
        # get the concept ID
        conceptId = STR(CONCEPTS.M1COMPOSITION)
        # get the create args
        eFeature = eObj._CON_class
        feature = self.__Enc(eFeature)
        eParent = eObj._CON_parent
        parent = self.__Enc(eParent)
        eChild = eObj._CON_child
        child = self.__Enc(eChild)
        createArgs = LST([feature, parent, child])
        # get recovery args
        recoveryArgs = LST([U64(eObj._CON_pos)])
        # clean up
        self.__UpdateEFeature(eParent, eFeature, eObj._CON_pos, None, eFeature.upperBound, EFEATURE_TYPES.COMPOSITION, eObj)
        # delete of eObject is not necessary, because the element is removed with the above feature update
        return (conceptId, createArgs, recoveryArgs)  


    # #################################
    # Concept IS handlers #
    # #################################
    
    # MX
    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsInMxLayer(self, elem:Any) -> bool:
        """Check if an element is in Mx

        Args:
            element: The element to be checked
        Returns:
            bool: true, if the element is in
        """
        return isinstance(elem,EMxArtificialObject)
    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsMxMdb(self, elem:Any) -> bool:
        """Check if an element is a MxMdb

        Args:
            element: The element to be checked for being an MxMdb
        Returns:
            bool: true, if the element is an MxMdb
        """
        return isinstance(elem,EMxMdb)

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsMxConstraint(self, elem:Any) -> bool:
        """Check if an element is a MxConstraint

        Args:
            element: The element to be checked for being an MxConstraint
        Returns:
            bool: true, if the element is an MxConstraint
        """
        return isinstance(elem,EMxConstraint)

    # M2
    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsInM2Layer(self, elem:Any) -> bool:
        """Check if an element is in M2

        Args:
            element: The element to be checked
        Returns:
            bool: true, if the element is in
        """
        return isinstance(elem,ENamedElement) or isinstance(elem,EM2ArtificialObject)
    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM2Package(self, elem:Any) -> bool:
        """Check if an element is a M2Package

        Args:
            element: The element to be checked for being an M2Package
        Returns:
            bool: true, if the element is an M2Package
        """
        return isinstance(elem,EPackage) and None != elem.eSuperPackage

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM2Model(self, elem:Any) -> bool:
        """Check if an element is a M2Model

        Args:
            element: The element to be checked for being an M2Model
        Returns:
            bool: true, if the element is an M2Model
        """
        return isinstance(elem,EPackage) and None == elem.eSuperPackage

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM2Enum(self, elem:Any) -> bool:
        """Check if an element is a M2Enum

        Args:
            element: The element to be checked for being an M2Enum
        Returns:
            bool: true, if the element is an M2Enum
        """
        return isinstance(elem,EEnum)

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM2OptionOfEnum(self, elem:Any) -> bool:
        """Check if an element is a M2OptionOfEnum

        Args:
            element: The element to be checked for being an M2OptionOfEnum
        Returns:
            bool: true, if the element is an M2OptionOfEnum
        """
        return isinstance(elem,EEnumLiteral)

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM2Class(self, elem:Any) -> bool:
        """Check if an element is a M2Class

        Args:
            element: The element to be checked for being an M2Class
        Returns:
            bool: true, if the element is an M2Class
        """
        return isinstance(elem,EClass)

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM2Attribute(self, elem:Any) -> bool:
        """Check if an element is a M2Attribute

        Args:
            element: The element to be checked for being an M2Attribute
        Returns:
            bool: true, if the element is an M2Attribute
        """
        return isinstance(elem,EAttribute)

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM2Association(self, elem:Any) -> bool:
        """Check if an element is a M2Association

        Args:
            element: The element to be checked for being an M2Association
        Returns:
            bool: true, if the element is an M2Association
        """
        return isinstance(elem,EReference) and elem.containment == False and self.__EReferenceContainerFix(elem)==False

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM2Composition(self, elem:Any) -> bool:
        """Check if an element is a M2Composition

        Args:
            element: The element to be checked for being an M2Composition
        Returns:
            bool: true, if the element is an M2Composition
        """
        return isinstance(elem,EReference) and elem.containment == True

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM2Inheritance(self, elem:Any) -> bool:
        """Check if an element is a M2Inheritance

        Args:
            element: The element to be checked for being an M2Inheritance
        Returns:
            bool: true, if the element is an M2Inheritance
        """
        return isinstance(elem,EM2Inheritance)

    # M1
    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsInM1Layer(self, elem:Any) -> bool:
        """Check if an element is in M1

        Args:
            element: The element to be checked
        Returns:
            bool: true, if the element is in
        """
        return isinstance(elem,EM1ArtificialObject) or self._IsM1Object(elem)
    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM1Model(self, elem:Any) -> bool:
        """Check if an element is a M1Model

        Args:
            element: The element to be checked for being an M1Model
        Returns:
            bool: true, if the element is an M1Model
        """
        return isinstance(elem,EM1Model)

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM1Object(self, elem:Any) -> bool:
        """Check if an element is a M1Object

        Args:
            element: The element to be checked for being an M1Object
        Returns:
            bool: true, if the element is an M1Object
        """
        return isinstance(elem,EObject) and self.__GetAugmentedProperty(elem, "_CON_isM1Obj", False)

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM1Attribute(self, elem:Any) -> bool:
        """Check if an element is a M1Attribute

        Args:
            element: The element to be checked for being an M1Attribute
        Returns:
            bool: true, if the element is an M1Attribute
        """
        return isinstance(elem,EM1Attribute)

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM1Association(self, elem:Any) -> bool:
        """Check if an element is a M1Association

        Args:
            element: The element to be checked for being an M1Association
        Returns:
            bool: true, if the element is an M1Association
        """
        return isinstance(elem,EM1Association)

    #@generate head no
    #@generate comment no
    #@generate body no
    def _IsM1Composition(self, elem:Any) -> bool:
        """Check if an element is a M1Composition

        Args:
            element: The element to be checked for being an M1Composition
        Returns:
            bool: true, if the element is an M1Composition
        """
        return isinstance(elem,EM1Composition)


    
    # # PRIVATE METHODS 
    
    # ###############################
    # CRUD support functions        #
    # ###############################
    
    # generic support functions
    def __GetConcept(self,elem):
        '''Returns the concept ID or None
        '''
        concept = None
        if(self._IsInM1Layer(elem)):
            if(self._IsM1Composition(elem)): concept = CONCEPTS.M1COMPOSITION
            if(self._IsM1Association(elem)): concept = CONCEPTS.M1ASSOCIATION
            if(self._IsM1Attribute(elem)): concept = CONCEPTS.M1ATTRIBUTE
            if(self._IsM1Object(elem)): concept = CONCEPTS.M1OBJECT
            if(self._IsM1Model(elem)): concept = CONCEPTS.M1MODEL
        elif(self._IsInM2Layer(elem)):
            if(self._IsM2Inheritance(elem)): concept = CONCEPTS.M2INHERITANCE
            if(self._IsM2Composition(elem)): concept = CONCEPTS.M2COMPOSITION
            if(self._IsM2Association(elem)): concept = CONCEPTS.M2ASSOCIATION
            if(self._IsM2Attribute(elem)): concept = CONCEPTS.M2ATTRIBUTE
            if(self._IsM2Class(elem)): concept = CONCEPTS.M2CLASS
            if(self._IsM2OptionOfEnum(elem)): concept = CONCEPTS.M2OPTIONOFENUM
            if(self._IsM2Enum(elem)): concept = CONCEPTS.M2ENUM
            if(self._IsM2Model(elem)): concept = CONCEPTS.M2MODEL
            if(self._IsM2Package(elem)): concept = CONCEPTS.M2PACKAGE
        elif(self._IsInMxLayer(elem)):
            if(self._IsMxConstraint(elem)): concept = CONCEPTS.MXCONSTRAINT
            if(self._IsMxMdb(elem)): concept = CONCEPTS.MXMDB
        return concept
    
    
    def __GetConceptFeatureHandler(self,eObj,featureName,handlerTable):
        concept = self.__GetConcept(eObj)
        try: 
            conceptKey = GetConceptKeyString(concept)
            featureKey = GetConceptKeyString(featureName)
            return handlerTable[conceptKey][featureKey]
        except KeyError: #no handler for EObjects matches or is registered
            raise EOQ_ERROR_DOES_NOT_EXIST("%s has no feature %s"%(concept,featureName))
    
    # support create
    
    def __InitAndEncNewElem(self, newElem:EObject, target:Obj=NON())->Obj:
        #add secret properties
        self.__SetAugmentedProperty(newElem,"_CON_strId",None)
        self.__SetAugmentedProperty(newElem,"_CON_documentation",None)
        self.__SetAugmentedProperty(newElem,"_CON_owner",None)
        self.__SetAugmentedProperty(newElem,"_CON_group",None)
        self.__SetAugmentedProperty(newElem,"_CON_permissions",[])
        self.__SetAugmentedProperty(newElem,"_CON_constraints",[])
        #init caching
        self.__InitCaching(newElem)
        self.__UpdateChildStateAndCache(newElem)
        res = self.__EncFirstTime(newElem,target)
        return res
    
    def __CreateConcept(self, conceptId:str, createArgs:LST, target:Obj, recoveryArgs:LST) -> Tuple[object,object]:
        #create a generic element
        res = None
        try:
            conceptKey = GetConceptKeyString(conceptId)
            createHandler = self.conceptsCreateHandlers[conceptKey][0]
            res = createHandler(createArgs, target, recoveryArgs)
        except KeyError:
            raise EOQ_ERROR_INVALID_VALUE('Cannot create %s. Generic identifier is unknown'%(conceptId))  
        return res
    
    def __CreateNative(self, clazz:EClass, createArgs:LST, target:Obj, recoveryArgs:LST) -> Tuple[object,object]:
        cArgs = self.__DecCollection(createArgs)
        try:
            newElem = clazz(*cArgs)
        except Exception as e:
            raise EOQ_ERROR_UNKNOWN('Failed to instantiate class. Wrong create args?: %s'%(str(e)))
        res = self.__InitAndEncNewElem(newElem, target)    
        return res
    
    def __ReadNative(self,eObj:EObject,normalizedFeatureName:str)->Any:
        eFeature = eObj.eClass.findEStructuralFeature(normalizedFeatureName)
        try:
            try:
                # Performance Hack?
                eValue = eObj.__dict__[normalizedFeatureName]._get() #is this quicker than eGet? Works for most attributes, but not all
            except KeyError:
                eValue = getattr(eObj, normalizedFeatureName) #is the same as eGet() :(
            #check if this was not a value but a method.
            if(isinstance(eValue,types.MethodType)):
                self.__StopIfConceptsOnlyMode() #no call of e... operations
                eValue =  eValue() #call the method to get the values
        except Exception as e:
            raise EOQ_ERROR_DOES_NOT_EXIST('%s has no feature %s'%(eObj.eClass.name,normalizedFeatureName))
        return self.__EncValue(eValue,eFeature.eType,eFeature.many)
    
    # support read
    
    def __ReadM2ClassSrcAssociationsRaw(self, eObj:EClass, eContext:EObject=None) -> Collection[EReference]:
        mask = lambda e: e.containment==False and self.__EReferenceContainerFix(e)==False and not self.__GetAugmentedProperty(e, "_CON_isDst", False)
        return [e for e in eObj.eAllReferences() if mask(e)]
        
    def __ReadM2ClassDstAssociationsRaw(self, eObj:EClass, eContext:EObject=None) -> Collection[EReference]:
        typedDstItems = (e.eOpposite for e in eObj.eAllReferences() if e.containment == False and self.__GetAugmentedProperty(e, "_CON_isDst", False))
        anyDstItems = self.anyM2Associations.values()
        allDstItems = itertools.chain(typedDstItems, anyDstItems)
        return allDstItems
     
    def __ReadM2ClassParentCompositionsRaw(self, eObj:EClass, eContext:EObject=None) -> Collection:
        mask = lambda e: e.containment
        return [e for e in eObj.eAllReferences() if mask(e)]
        
    def __ReadM2ClassChildCompositionsRaw(self, eObj:EClass, eContext:EObject=None) -> Collection:
        typedDstItems = (e.eOpposite for e in eObj.eAllReferences() if e.container and None!=e.eOpposite)
        anyDstItems = self.anyM2Composition.values()
        allDstItems = itertools.chain(typedDstItems, anyDstItems)
        return allDstItems
    
    def __ReadM2ClassSpecializationsRaw(self, eObj:EClass) -> List[EObject]:
        """Recursively read all super inheritances
        """
        ownItems = self.__GetAugmentedProperty(eObj,"_CON_specializations",[])
        inheritItems = []
        for i in ownItems:
            inheritItems += self.__ReadM2ClassSpecializationsRaw(i._CON_subClass)
        return ownItems + inheritItems
    
    def __ReadM2ClassGeneralizationsRaw(self, eObj:EClass) -> List[EObject]:
        """Recursively read all super inheritances
        """
        ownItems = eObj._CON_generalizations
        inheritItems = []
        for i in ownItems:
            inheritItems += self.__ReadM2ClassGeneralizationsRaw(i._CON_superClass)
        return ownItems + inheritItems
        
    def __ReadAssociationNameRaw(self, eObj:EStructuralFeature, eContext:EObject)->str:
        if(eObj.upperBound == 1):
            return eObj.name #cannot be None
        elif(eObj.name.endswith(FEATURE_MULTIVALUE_POSTFIX)): #name and safe name are identical, e.g. for generic features
            return eObj.name
        else:
            return eObj.name + FEATURE_MULTIVALUE_POSTFIX
    
    def __ReadElementAssociatesRaw(self, eObj:EObject, eContext:EObject):
        if(None != eContext):
            return [a for a in eObj._eoqAssociatesCache.values() if a[0] == eContext or a[0] in eContext.eAllContents()] 
        else: 
            return [a for a in eObj._eoqAssociatesCache.values()]
    
    def __ReadClassAllSubtypesRaw(self, eObj:EClass, eContext:EObject)->List[EClass]:
        return [c for c in EClass.eClass.allInstances() if eObj in c.eAllSuperTypes()] #TODO: faster method by eSubTypes?
    
    def __ReadClassInstancesRawFromContexts(self, eObj:EClass, eContexts:list)->List[EObject]:
        instances = []
        if(EObject.eClass!=eObj):
            subtypes = [eObj]+self.__ReadClassAllSubtypesRaw(eObj,None)
            for c in eContexts:
                for t in subtypes:
                    try:
                        instances = itertools.chain(instances,[e for e in c._eoqChildrenByClassCache[t].values()])
                        #instances = instances + [e for e in c._eoqChildrenByClassCache[t].values()] #itertools.chain solution seems to be much faster, bad to debug
                    except KeyError:
                        pass #add nothing to the list
                if isinstance(c,eObj):
                    instances = itertools.chain([c],instances)
                    #instances = [c] +instances
        else:
            for c in eContexts:
                instances = itertools.filterfalse(lambda e: isinstance(e,EAnnotation),itertools.chain(instances,[c],c.eAllContents()) )
                #instances = instances + [c] + [e for e in c.eAllContents()]
        return instances
    
    def __ReadClassIncarnationsRawFromContexts(self, eObj:EClass, eContexts:list)->List[EObject]:
        incarnations = []
        for c in eContexts:
            try:
                incarnations = itertools.chain(incarnations,[e for e in c._eoqChildrenByClassCache[eObj].values()])
            except KeyError:
                pass #add nothing to the list
            if(c.eClass == eObj):
                incarnations = itertools.chain([c],incarnations)
        return incarnations
    
    # support update
    
    def __UpdateCustomFeature(self, eObj:EObject, eFeatureName:str, value:VAL, ePosition:int):
        oldOwner = NON() 
        oldComposition = NON()
        oldPosition = NON()
        isMultiValueFeature = IsMultivalueFeature(eFeatureName)
        #validate the feature
        if(not eObj.eClass): #if the object has no class it cannot have any feature
            raise EOQ_ERROR_INVALID_VALUE('Target has no class. Cannot add anything.') 
        normalizedFeatureName = NormalizeFeatureName(eFeatureName)
        eFeature = eObj.eClass.findEStructuralFeature(normalizedFeatureName)
        if not eFeature:
            raise EOQ_ERROR_DOES_NOT_EXIST('%s has no feature %s'%(eObj.eClass.name,normalizedFeatureName))
        #validate the value type
        eType = eFeature.eType
        if(None == eType):
            raise EOQ_ERROR_RUNTIME('%s.%s has not type.'%(eObj.eClass.name,normalizedFeatureName))
        if(eFeature.derived):
            raise EOQ_ERROR_RUNTIME('%s.%s is readonly.'%(eObj.eClass.name,normalizedFeatureName))
        featureType = None
        if isinstance(eFeature,EAttribute): #Attribute
            #validate value 
            expectedType = STR if isinstance(eType,EEnum) else ETypeToValueType(eType) #Enum is a special case
            self.__ValidateType(value,expectedType,eFeatureName,True)
            eValue = ValueToEValue(value)
            #get feature type
            featureType = EFEATURE_TYPES.ATTRIBUTE 
        else: #Association or composition
            #decode value (only objects are allowed here)
            eValue = self.__Dec(value)
            #validate value
            #if(eValue):
            self.__ValidateType(eValue,eType,eFeatureName,True)
            #safe old value
            (oldOwner,oldComposition,oldPosition) = self.__GetEObjectUpdateRecoveryInfo(eValue)
            #get feature type
            if eFeature.containment:
                featureType = EFEATURE_TYPES.COMPOSITION
            else:
                featureType = EFEATURE_TYPES.ASSOCIATION
        #update the feature value
        try:
            if(eFeature.many):
                self.__VaidateFeatureNameMultiplicity(isMultiValueFeature,True,eFeatureName,normalizedFeatureName)
                eOldValue = self.__UpdateMultiValueEFeature(eObj,eFeature,ePosition,eValue,eFeature.upperBound,featureType)
            else: #single value feature
                self.__VaidateFeatureNameMultiplicity(isMultiValueFeature,False,eFeatureName,normalizedFeatureName)
                eOldValue = self.__UpdateSingleValueEFeature(eObj,eFeature,ePosition,eValue,featureType)
        except BadValueError:
            raise EOQ_ERROR_INVALID_VALUE("%s.%s is of type %s, but got %s"%(eObj.eClass.name,eFeature.name,eFeature.eType.name,type(eValue).__name__))
        #convert the old value back to an VAL
        oldValue = self.__EncValue(eOldValue, eType, False)
        #Check special cases which require cache updates
        if(EClass == type(eObj) and 'name' == normalizedFeatureName):
            self.__UpdateElementNameCache(eObj, eOldValue)
        elif(EPackage == type(eObj) and 'nsURI' == normalizedFeatureName):
            self.__UpdatePackagesCache(eObj, eOldValue)
        return (oldValue,oldOwner,oldComposition,oldPosition)
    
    # support find class by name or id
    
    def __FindElementeByIdOrNameRaw(self, eNameOrId:str, eContext:EObject, conceptFilterFunc:Callable[[EObject],bool]) -> list:
        #search all matching elements
        elements = []
        if(eNameOrId in self.createIdStrLut):
            elements.append(self.createIdStrLut[eNameOrId])
        else:
            if eNameOrId in self.classNamesCache:
                for c in self.classNamesCache[eNameOrId].values():
                    cachedEObj = c[0]
                    cachedContext = c[2]
                    if(self._IsM2Class(eContext)): #eClass need special context handling because of inheritance
                        if((None==eContext or cachedContext==eContext or (cachedContext in eContext.eAllSuperTypes())) and (None==conceptFilterFunc or conceptFilterFunc(cachedEObj))):
                            elements.append(cachedEObj)
                    else: #no EClass
                        if((None==eContext or cachedContext==eContext) and (None==conceptFilterFunc or conceptFilterFunc(cachedEObj))):
                            elements.append(cachedEObj)
        return elements
      
    # ###############################
    # Object encoding / decoding    #
    # ############################### 
    
    def __EncFirstTime(self,eObj,target:Obj=NON()):
        """
        Converts EObjects to EOQ Obj
        """
        #no none check necessary, because it is only called after the creation of objects 
        # that never creates none objects.
        idNb = None
        if(not target.IsNone()):
            #if target is given, try to reuse the ID
            idNb = target.v[0].v[0].GetVal()
            if(idNb in self.idToObjectLUT):
                raise EOQ_ERROR_INVALID_VALUE('Cannot use %d as create target, because it is already in use.')
        else:
            #if no target is given, create a new object ID
            idNb = self.lastId
            self.lastId += 1 #root id starts now at 0 like all other indexes
        self.idToObjectLUT[idNb] = eObj
        eObj._eoqId = idNb
        objId = U64(idNb)
        newSeg = EObjSeg(objId,eObj)
        eObj._eoqObj = newSeg
        newObj = Obj(newSeg)
        return newObj
    
    def __EncLastTime(self,elem : Obj):
        """
        Removes a deleted element from the and removes all internal references of that objects
        Afterwards this element cannot be used in the MDB any more, 
        except for a Create target
        """
        idNb = elem.v[0].v[0].GetVal()  
        eObj = self.idToObjectLUT[idNb]
        # remove any hidden caching entries
        self.__DeinitCaching(eObj)
        # there should be only one existing ObjSeg with a reference to the eObj
        # lets remove that.        
        del eObj._eoqObj._eObj
        del self.idToObjectLUT[idNb]
        return elem


    def __Enc(self,eObj : EObject or None):
        ''' Converts EObjects to Obj queries (and none references)
        '''
        if(isinstance(eObj,EObject)):
            obj = eObj._eoqObj
            return Obj(obj)
        else:
            return NON()
        
    
    def __EncCollection(self,collection,mask=lambda e:True,sorter=None):
        ''' Encodes every element in a collection to a list of encoded values. 
        Assumes that the collection only contains EObjects.
        E.g. a list of EObjects or an eSet of EObjects.
        '''
        if(sorter):
            return LST(sorted([self.__Enc(e) for e in collection if mask(e)],key=sorter))
        else:
            return LST([self.__Enc(e) for e in collection if mask(e)])
    
                
    def __EncValue(self,eValue,eType,many):
        if(IsEPrimitiveType(eType)): #Primitives
            if(many):
                return LST([EValueToValue(v,eType) for v in eValue])
            else:
                return EValueToValue(eValue,eType) 
        elif(isinstance(eType,EEnum)): #enum literals shall only be returned as string
            if(many):
                return LST([STR(v.name) if type(v)==EEnumLiteral else STR(v) for v in eValue]) #sometimes the value is already string
            else:
                return STR(eValue.name) if type(eValue)==EEnumLiteral else STR(eValue)
        else: #EObjects
            if(many):
                return LST([self.__Enc(v) for v in eValue])
            else:
                return self.__Enc(eValue)

        
    def __Dec(self,elem):
        """
        Converts EOQ Obj to EObjects
        """
        if(elem.IsNone()):
            return None
        eObj = None
        try: 
            eObj = elem.v[0]._eObj #access the query segment inside the Obj query
            if(None == eObj):
                #restore the binding
                try:
                    eoqId = elem.v[0].v[0].GetVal()
                    eObj = self.idToObjectLUT[eoqId]
                    elem.v[0]._eObj = eObj
                except KeyError: 
                    raise EOQ_ERROR_DOES_NOT_EXIST('Element #%s is not part of this MDB.'%(eoqId))
        except AttributeError: #is no EObjSeg
            try:
                eoqId = elem.v[0].v[0].GetVal()
                eObj = self.idToObjectLUT[eoqId]
            except KeyError:
                    raise EOQ_ERROR_DOES_NOT_EXIST('Element #%s is not known.'%(eoqId))
        return eObj
    
    def __DecCollection(self,collection:LST) -> List[Any]:
        res = []
        for e in collection:
            if(LST == type(e)):
                res.append(self.__DecCollection(e))
            elif(isinstance(e,Obj)):
                res.append(self.__Dec(e))
            else:
                res.append(e.GetVal())
        return res
    
    def __DecTarget(self,target:Obj,featureNameStr:str)->EObject:
        """ Special decode function that allows NON targets
        and returns eMdb in case of MDB features.
        """
        if(target.IsNone()):
            if(featureNameStr in MXMDB_FEATURES):
                return self.eMdb
            else:
                raise EOQ_ERROR_DOES_NOT_EXIST("NON has no feature %s"%(featureNameStr))
        else:
            return self.__Dec(target)
    
    
    # #################################
    # Update Eset helpers             #
    # #################################
    
    def __UpdateEFeature(self, eObj:EObject, eFeature:EStructuralFeature, position:int, eValue, featureLength:int, featureType:int, m1Feature:EObject=None):
        if(eFeature.many):
            return self.__UpdateMultiValueEFeature(eObj,eFeature,position,eValue,featureLength,featureType,m1Feature)
        else:
            return self.__UpdateSingleValueEFeature(eObj,eFeature,position,eValue,featureType,m1Feature)
        
    #inserts a value at a fixed position of an eSet. Use -1 for adding at the last position.
    def __UpdateSingleValueEFeature(self, eObj:EObject, eFeature:EStructuralFeature, position:int, eValue, featureType:int, m1Feature:EObject=None):
        featureLength = 1
        eOldValue = eObj.eGet(eFeature)
        nElements = 0 if (None==eOldValue or (EFEATURE_TYPES.ATTRIBUTE==featureType and eFeature.default_value==eOldValue)) else 1
        # determine mode and absolute position from the index
        (mode,absPos) = GetUpdateModeAndAbsPosition(nElements,position,eValue)
        # position sanity checks
        ValidateUpdatePosition(mode,nElements,featureLength,absPos)
        # set operation
        eObj.eSet(eFeature,eValue)
        if(EFEATURE_TYPES.ATTRIBUTE == featureType):
            if(UPDATE_MODES.REMOVE == mode):
                if(m1Feature): self.__DelM1Attr(m1Feature)
            elif(UPDATE_MODES.REPLACE == mode):
                pass #replace needs no removal, because the m1 feature can be reused. 
#                 removedM1Feature = self.__GetM1AttrByPos(eObj, eFeature, 0)
#                 if(removedM1Feature): self.__DelM1Attr(m1Feature,True)
        elif(EFEATURE_TYPES.ASSOCIATION == featureType):
            if isinstance(eValue, EObject): self.__AddToAssociateCache(eValue, eObj, eFeature, 0, m1Feature)    
            if isinstance(eOldValue, EObject): self.__RemoveFromAssociateCache(eOldValue, eObj, eFeature)
            if(UPDATE_MODES.REMOVE == mode):
                if(m1Feature): self.__DelM1Assoc(m1Feature)
            elif(UPDATE_MODES.REPLACE == mode):
                pass #replace needs no removal, because the m1 feature can be reused. 
#                 removedM1Feature = self.__GetM1AssocByPos(eObj, eFeature, 0)
#                 if(removedM1Feature): self.__DelM1Assoc(m1Feature,True)
        elif(EFEATURE_TYPES.COMPOSITION == featureType):
            if isinstance(eValue, EObject): self.__UpdateChildStateAndCache(eValue)
            if isinstance(eOldValue, EObject): self.__UpdateChildStateAndCache(eOldValue)
            if(UPDATE_MODES.REMOVE == mode):
                if(m1Feature): self.__DelM1Compo(m1Feature)
            elif(UPDATE_MODES.REPLACE == mode):
                pass #replace needs no removal, because the m1 feature can be reused. 
#                 removedM1Feature = self.__GetM1CompoByPos(eObj, eFeature, 0)
#                 if(removedM1Feature): self.__DelM1Compo(m1Feature,True)
        return eOldValue

        
    #inserts a value at a fixed position of an eSet. Use -1 for adding at the last position.
    def __UpdateMultiValueEFeature(self, eObj:EObject, eFeature:EStructuralFeature, position:int, eValue, featureLength:int, featureType:int, m1Feature:EObject=None):
        eSet = eObj.eGet(eFeature)
        nElements = len(eSet)
        nFilteredElements = nElements
        eOldValue = None
        
        (mode,absPos) = GetUpdateModeAndAbsPosition(nFilteredElements,position,eValue)
        
        # position sanity checks
        ValidateUpdatePosition(mode,nFilteredElements,featureLength,absPos)
        
        # catch the special case that the value is already in the feature, the feature is a containment, 
        # and its position is before the current position. In that case pyecore will not re-add or move the feature
        # so it needs to be removed before: 
        # TODO: How to improve performance here?
        if(isinstance(eSet,EOrderedSet)): #is only valid for unique StructuralFeatures, which return ESet
            try: 
                currentPosition = eSet.index(eValue)
                if(currentPosition < absPos):
                    eSet.remove(eValue)
                    absPos -= 1 #reduce by one since the element is now missing
            except KeyError:
                pass
        # in some cases the last parent must be preserved to update the positions of remaining children
        eFormerParent = None
        eFormerFeature = None
        eFormerPos = 0
        if(isinstance(eValue,EObject)):
            (eFormerParent,eFormerFeature,eFormerPos) = self.__ReadEObjectParentInfoRaw(eValue,None)
        # regular update operation starts here    
        if(nFilteredElements == absPos):
            if(None != eValue): #ADD to END
                eSet.append(eValue)
                if(EFEATURE_TYPES.COMPOSITION == featureType):
                    self.__UpdateChildStateAndCache(eValue)
                    self.__UpdateFormerCompositionSiblingPositions(eFormerParent,eFormerFeature,eFormerPos)
                elif(EFEATURE_TYPES.ASSOCIATION == featureType):
                    self.__AddToAssociateCache(eValue, eObj, eFeature, nElements, m1Feature)
            else:
                raise EOQ_ERROR_INVALID_VALUE("Cannot add none value to feature. If delete was intended, index is wrong.")
        else: # it is not the last element that is added
            # here the update takes place
            successors = self.__InsertReplaceOrRemoveInESet(eSet, absPos, mode, eValue)
            if(UPDATE_MODES.REPLACE == mode or UPDATE_MODES.REMOVE == mode):
                eOldValue = successors[len(successors)-1] #last element
            else:
                eOldValue = None #no old value in case of insert, because the old ones are persistent
            #feature type specific operations
            posWithoutFilter = nElements-len(successors)
            if(EFEATURE_TYPES.ATTRIBUTE == featureType):
                if(UPDATE_MODES.INSERT == mode):
                    j = 0 #positive counting
                    for i in range(len(successors)-2,-1,-1):
                        prePos = posWithoutFilter+j
                        newPos = prePos+1
                        successorM1Feature = self.__GetM1AttrByPos(eObj, eFeature, prePos)
                        if(successorM1Feature):
                            successorM1Feature._CON_pos = newPos
                        j += 1
                elif(UPDATE_MODES.REMOVE == mode):
                    j = 0 #positive counting
                    for i in range(len(successors)-2,-1,-1):
                        prePos = posWithoutFilter+j+1
                        newPos = prePos-1
                        successorM1Feature = self.__GetM1AttrByPos(eObj, eFeature, prePos)
                        if(successorM1Feature):
                            successorM1Feature._CON_pos = newPos
                        j += 1
                    if(m1Feature): self.__DelM1Attr(m1Feature)
                elif(UPDATE_MODES.REPLACE == mode):
                    pass #replace needs no removal, because the m1 feature can be reused. 
#                     removedM1Feature = self.__GetM1AttrByPos(eObj, eFeature, absPos)
#                     if(removedM1Feature): self.__DelM1Attr(m1Feature,True)
            elif(EFEATURE_TYPES.ASSOCIATION == featureType):
                if(UPDATE_MODES.INSERT == mode):
                    self.__AddToAssociateCache(eValue, eObj, eFeature, posWithoutFilter, m1Feature)
                    j = 0 #positive counting
                    for i in range(len(successors)-2,-1,-1):
                        prePos = posWithoutFilter+j
                        newPos = prePos+1
                        successorM1Feature = self.__GetM1AssocBySrcPos(eObj, eFeature, prePos)
                        self.__RemoveFromAssociateCache(successors[i], eObj, eFeature) #old position
                        self.__AddToAssociateCache(successors[i], eObj, eFeature, newPos, successorM1Feature) #new position  
                        j += 1
                elif(UPDATE_MODES.REMOVE == mode):
                    self.__RemoveFromAssociateCache(eOldValue, eObj, eFeature) #old position
                    j = 0 #positive counting
                    for i in range(len(successors)-2,-1,-1):
                        prePos = posWithoutFilter+j+1
                        newPos = prePos-1
                        successorM1Feature = self.__GetM1AssocBySrcPos(eObj, eFeature, prePos)
                        self.__RemoveFromAssociateCache(successors[i], eObj, eFeature) #old position
                        self.__AddToAssociateCache(successors[i], eObj, eFeature, newPos, successorM1Feature) #new position  
                        j += 1
                    if(m1Feature): self.__DelM1Assoc(m1Feature)
                elif(UPDATE_MODES.REPLACE == mode):
                    self.__AddToAssociateCache(eValue, eObj, eFeature, posWithoutFilter, m1Feature)
                    #replace needs no removal, because the m1 feature can be reused. 
#                     removedM1Feature = self.__GetM1AssocByPos(eObj, eFeature, absPos)
#                     if(removedM1Feature): self.__DelM1Assoc(m1Feature,True)
            elif(EFEATURE_TYPES.COMPOSITION == featureType):
                if(UPDATE_MODES.INSERT == mode):
                    j = 0 #positive counting
                    for i in range(len(successors)-2,-1,-1):
                        prePos = posWithoutFilter+j
                        newPos = prePos+1
                        successorM1Feature = self.__GetM1CompoByParentPos(eObj, eFeature, prePos)
                        if(successorM1Feature):
                            successorM1Feature._CON_pos = newPos
                        j += 1
                    self.__UpdateFormerCompositionSiblingPositions(eFormerParent,eFormerFeature,eFormerPos)
                elif(UPDATE_MODES.REMOVE == mode):
                    self.__UpdateChildStateAndCache(eOldValue)
                    j = 0 #positive counting
                    for i in range(len(successors)-2,-1,-1):
                        prePos = posWithoutFilter+j+1
                        newPos = prePos-1
                        successorM1Feature = self.__GetM1CompoByParentPos(eObj, eFeature, prePos)
                        if(successorM1Feature):
                            successorM1Feature._CON_pos = newPos
                        j += 1
                    if(m1Feature): self.__DelM1Compo(m1Feature)
                elif(UPDATE_MODES.REPLACE == mode):
                    self.__UpdateChildStateAndCache(eValue) 
                    self.__UpdateChildStateAndCache(eOldValue)
                    self.__UpdateFormerCompositionSiblingPositions(eFormerParent,eFormerFeature,eFormerPos)
                    #replace needs no removal, because the m1 feature can be reused. 
#                     removedM1Feature = self.__GetM1CompoByPos(eObj, eFeature, absPos)
#                     if(removedM1Feature): self.__DelM1Compo(m1Feature,True)
        return eOldValue
    
    def __UpdateFormerCompositionSiblingPositions(self,eFormerParent:EObject,eFormerFeature:EStructuralFeature,eFormerPos:int):
        '''Updates the position of all follwoing siblings,
        if an elmement is removed from a former composition
        '''
        if(eFormerParent and eFormerFeature.many):
            eSiblingM1Compositions = [c for c in self.__GetAugmentedProperty(eFormerParent, "_CON_parentCompositions", []) if eFormerFeature == self.__GetAugmentedProperty(c,"_CON_class",None)]
            for p in range(eFormerPos,len(eSiblingM1Compositions)):
                eSiblingM1Compositions[p]._CON_pos -=1
    
    #inserts a value at a fixed position of an eSet. Use -1 for adding at the last position.
    def __UpdateList(self, l:list, position:int, eValue, featureLength:int):
        '''Updates and python list with the same index as an feature update
        '''
        nElements = len(l)
        eOldValue = None
        (mode,absPos) = GetUpdateModeAndAbsPosition(nElements,position,eValue)
        # position sanity checks
        ValidateUpdatePosition(mode,nElements,featureLength,absPos)
        # regular update operation starts here    
        if(nElements == absPos):
            if(None != eValue): #ADD to END
                l.append(eValue)
            else:
                raise EOQ_ERROR_INVALID_VALUE("Cannot add none value to feature. If delete was intended, index is wrong.")
        else: #it is not the last element that is added
            if(UPDATE_MODES.REPLACE == mode):
                eOldValue = l[absPos]
                l[absPos] = eValue
            elif(UPDATE_MODES.REMOVE == mode):
                eOldValue = l[absPos]
                l.pop(absPos)
            elif(UPDATE_MODES.INSERT == mode):
                l.insert(absPos,eValue)    
        return eOldValue
    
    def __GetM1AttrByPos(self, eObj:EObject, eFeature:EStructuralFeature, pos:int):
        m1Feature = None
        if(self._IsM1Object(eObj)):
            for m1f in eObj._CON_attributes:
                if m1f._CON_class == eFeature and m1f._CON_pos == pos:
                    m1Feature = m1f
                    break
        return m1Feature
    
    def __GetM1AssocBySrcPos(self, eObj:EObject, eFeature:EStructuralFeature, srcPos:int):
        m1Feature = None
        if(self._IsM1Object(eObj)):
            for m1f in eObj._CON_srcAssociations:
                if m1f._CON_class == eFeature and m1f._CON_srcPos == srcPos:
                    m1Feature = m1f
                    break
        return m1Feature
    
    def __GetM1CompoByParentPos(self, eObj:EObject, eFeature:EStructuralFeature, pos:int):
        m1Feature = None
        if(self._IsM1Object(eObj)):
            for m1f in eObj._CON_parentCompositions:
                if m1f._CON_class == eFeature and m1f._CON_pos == pos:
                    m1Feature = m1f
                    break
        return m1Feature
    
    def __DelM1Attr(self, eM1Feature:EM1ArtificialObject, encLastTime:bool=False):
        eM1Object = eM1Feature._CON_m1Object
        eM2Attribute = eM1Feature._CON_class
        eM1Feature._CON_class = None
        eM1Feature._CON_m1Object = None
        eM1Object._CON_attributes.remove(eM1Feature)
        eM2Attribute._CON_incarnations.remove(eM1Feature)
        eM1Feature.delete()
        if(encLastTime): 
            self.__EncLastTime(self.__Dec(eM1Feature))
        del eM1Feature
        
        
    def __DelM1Assoc(self, eM1Feature:EM1ArtificialObject, encLastTime:bool=False):
        eSrc = eM1Feature._CON_src
        eDst = eM1Feature._CON_dst
        eM2Association = eM1Feature._CON_class 
        eM1Feature._CON_class = None
        eM1Feature._CON_src = None
        eM1Feature._CON_dst = None
        eSrc._CON_srcAssociations.remove(eM1Feature)
        eDst._CON_dstAssociations.remove(eM1Feature)
        eM2Association._CON_incarnations.remove(eM1Feature)
        eM1Feature.delete()
        if(encLastTime): 
            self.__EncLastTime(self.__Dec(eM1Feature))
        del eM1Feature
        
    def __DelM1Compo(self, eM1Feature:EM1ArtificialObject, encLastTime:bool=False):
        eParent = eM1Feature._CON_parent
        eChild = eM1Feature._CON_child
        eM2Composition = eM1Feature._CON_class 
        eM1Feature._CON_class = None
        eM1Feature._CON_parent = None
        eM1Feature._CON_child = None
        eParent._CON_parentCompositions.remove(eM1Feature)
        eChild._CON_childComposition = None
        eM2Composition._CON_incarnations.remove(eM1Feature)
        eM1Feature.delete()
        if(encLastTime): 
            self.__EncLastTime(self.__Dec(eM1Feature))
        del eM1Feature
    
    def __UpdateSingleValueEFeatureValidatePosition(self,position,oldValue,eValue):
        featureLength = 1
        nElements = 0 if (oldValue==None) else 1
        (mode,absPos) = GetUpdateModeAndAbsPosition(nElements,position,eValue)
        ValidateUpdatePosition(mode,nElements,featureLength,position)
          
    def __InsertReplaceOrRemoveInESet(self,eSet:Union[EOrderedSet,EList], pos:int, mode:int, value:Any):
        #find all elements passing the mask after the element desired    
        elements = [e for e in eSet]
        sucessors = list(reversed(elements[pos:]))
        if(isinstance(eSet,EOrderedSet)):
        #EOrderedSets cannot be inserted at any position, so remove all elements after the desired position first ...
            for s in sucessors:
                eSet.remove(s)
            #... then eventually (replace or insert) add a new element ...
            if (mode == UPDATE_MODES.REPLACE or 
                mode == UPDATE_MODES.INSERT):
                eSet.append(value)
            #... and finally re-add the successors, either all (insert) or one less (remove, replace)
            sucessorReaddStart = len(sucessors)-1 
            if (mode == UPDATE_MODES.REPLACE or 
                mode == UPDATE_MODES.REMOVE):
                sucessorReaddStart = len(sucessors)-2     
            for i in range(sucessorReaddStart,-1,-1):
                eSet.append(sucessors[i])
        elif(isinstance(eSet,EList)):
        #ELists can be modified by native functions
            if(mode == UPDATE_MODES.REPLACE):
                eSet[pos] = value
            elif(mode == UPDATE_MODES.INSERT):
                eSet.insert(pos,value)
            elif(mode == UPDATE_MODES.REMOVE):
                eSet.pop(pos)
        else:
            raise EOQ_ERROR_RUNTIME("Unsupported multi-element feature data type: %s"%(type(eSet).__name__))
        return sucessors
    
    def __UpdateChildStateAndCache(self,eObj):
        '''Updates the orphans variable as well as all internal caches that are related to the child state of the object''' 
        eAnchestors = self.__GetEAnchastors(eObj)
        eParent = self.__GetEParent(eObj)
        eOldParent = eObj._eoqOldParent
        #Update the orphans array if the object has no parent any more
        if(None == eParent and not eObj in self.eMdb._CON_orphans):
            self.eMdb._CON_orphans[eObj] = eObj
        elif(None != eParent ): 
            if None == eOldParent: #eObj in self.eMdb._CON_orphans: #only update the orphans, if the old parent is None, i.e. this was an orphan before
                self.eMdb._CON_orphans.pop(eObj)
            #update type child caches
            eClass = eObj.eClass
            for a in eAnchestors:
                #put the object itself to the type cache
                if(eClass not in a._eoqChildrenByClassCache):
                    a._eoqChildrenByClassCache[eClass] = {}
                a._eoqChildrenByClassCache[eClass][eObj] = eObj
                #add the own type cache to the parent
                for k,v in eObj._eoqChildrenByClassCache.items():
                    if(k not in a._eoqChildrenByClassCache):
                        a._eoqChildrenByClassCache[k] = {}
                    for c in v.values():
                        a._eoqChildrenByClassCache[k][c] = c
        #if the object had a parent before, remove it from the old parents typed child cache
        if(None!=eOldParent):
            eClass = eObj.eClass
            eOldAnchestors = [eOldParent] + self.__GetEAnchastors(eOldParent)
            for a in eOldAnchestors:
                if(a in eAnchestors):
                    break #no need to delete further entries, because the elements share the same root
                del a._eoqChildrenByClassCache[eClass][eObj]
                #remove the old type cache from the parent
                for k,v in eObj._eoqChildrenByClassCache.items():
                    for c in v.values():
                        del a._eoqChildrenByClassCache[k][c]
        eObj._eoqOldParent = eParent
        
    def __InitCaching(self,eObj):
        '''Enables the caching of associates, typed children and more by adding internal 
        variables to the eObjects
        '''
        eObj._eoqAssociatesCache = {}
        eObj._eoqChildrenByClassCache = {}
        eObj._eoqOldParent = None # safe the old parent for a short moment after an update operation
        
    def __DeinitCaching(self,eObj:EObject):
        '''Removes any dangling references caused by caching
        '''
        del eObj._eoqAssociatesCache
        del eObj._eoqChildrenByClassCache
        del eObj._eoqOldParent

    def __GetEParent(self,eObj:EObject):
        '''Returns the parent of an object if it is contained in a composition
        If it has no parent, but is contained in an EM1Model, this is returned.
        '''
        eParent = None
        if(eObj.eContainer()):
            eParent = eObj.eContainer()
        elif(hasattr(eObj,"_CON_m1Model") and None != eObj._CON_m1Model):
            eParent = eObj._CON_m1Model
        return eParent
        
    def __GetEAnchastors(self,eObj):
        '''Returns all parents in a row
        '''
        eAnchestors = []
        eParent = self.__GetEParent(eObj)
        while None != eParent:
            eAnchestors.append(eParent)
            eParent = self.__GetEParent(eParent)
        return eAnchestors
        
    def __AddToAssociateCache(self, eObj:EObject, eAssociate:EObject, eFeature:EReference, position:int, m1Feature:EObject=None):
        key = (eAssociate,eFeature)
        fName = self.__ReadAssociationNameRaw(eFeature,None)
        eObj._eoqAssociatesCache[key] = [eAssociate,eFeature,position,fName,m1Feature]
        if(m1Feature):
            m1Feature._CON_dstPos = position
        #do not forget to update the opposite cache
        eOpposite = eFeature.eOpposite
        if(eOpposite):
            opPosition = 0
            if(eOpposite.many):
                opPosition = eObj.eGet(eOpposite).index(eAssociate)
            opKey = (eObj,eOpposite)
            opFName = self.__ReadAssociationNameRaw(eOpposite,None)
            eAssociate._eoqAssociatesCache[opKey] = [eObj,eOpposite,opPosition,opFName,m1Feature]
            if(m1Feature):
                m1Feature._CON_srcPos = position
        
    def __RemoveFromAssociateCache(self, eObj:EObject, eAssociate:EObject, eFeature:EReference):
        key = (eAssociate,eFeature)
        try:
            del eObj._eoqAssociatesCache[key]
        except KeyError as e:
            print(e)
        #do not forget to update the opposite cache
        eOpposite = eFeature.eOpposite
        if(eOpposite):
            #search and find entry in opposite associations
            opKey = (eObj,eOpposite)
            del eAssociate._eoqAssociatesCache[opKey]
            if(eOpposite.many):
                #reindex all siblings
                i = 0
                for s in eObj.eGet(eOpposite):
                    if( s != eAssociate):
                        #opKey = (eObj,eOpposite)
                        entry = s._eoqAssociatesCache[opKey]
                        entry[2] = i #update index
                        m1assoc = entry[4]
                        if(m1assoc):
                            m1assoc._CON_dstPos = i
                        i += 1

            
            
    def __UpdateElementNameCache(self, eObj:EObject, name:str, context:EObject, oldName:str=None):
        if(name):
            # names cache
            namesChacheEntry = {}
            if(name in self.classNamesCache):
                namesChacheEntry = self.classNamesCache[name]
            else:
                self.classNamesCache[name] = namesChacheEntry
            namesChacheEntry[eObj] = (eObj,name,context) #this is not useless but updates the dict in the previous dict
        if(oldName):
            if (oldName in self.classNamesCache) and (eObj in self.classNamesCache[oldName]):
                oldCacheEntry = self.classNamesCache[oldName]
                del oldCacheEntry[eObj]
                if(0 == len(oldCacheEntry)):
                    del self.classNamesCache[oldName]
                
    def __UpdateCreateIdStrCache(self,eObj:EObject,key:str,oldKey=None):
        if(eObj and key):
            self.createIdStrLut[key] = eObj
        if(oldKey):
            if(oldKey in self.createIdStrLut):
                del self.createIdStrLut[oldKey]

    # #########################
    # INIT FUNCTIONS          #
    # #########################

    def __RegisterBaseElements(self)->None:
        '''Assignes IDs to all generic elements as well a to elements from the ecore meta model
        
        '''
        self.mdb = self.__EncFirstTime(self.eMdb)
        #Encode ECORE meta model
        self.baseElements[self.__EncFirstTime(ECORE_PACKAGE)] = ECORE_PACKAGE #the ecore package
        #encode classes
        self.baseElements[self.__EncFirstTime(EObject.eClass)] = EObject.eClass
        self.baseElements[self.__EncFirstTime(EPackage.eClass)] = EPackage.eClass
        self.baseElements[self.__EncFirstTime(EClass.eClass)] = EClass.eClass
        self.baseElements[self.__EncFirstTime(EAttribute.eClass)] = EAttribute.eClass
        self.baseElements[self.__EncFirstTime(EReference.eClass)] = EReference.eClass
        self.baseElements[self.__EncFirstTime(EEnum.eClass)] = EEnum.eClass
        self.baseElements[self.__EncFirstTime(EEnumLiteral.eClass)] = EEnumLiteral.eClass
        #encode base attributes and references
        for eReference in EReference.eClass.allInstances():
            self.baseElements[self.__EncFirstTime(eReference)] = eReference
        #encode ecore primitive types
        self.baseElements[self.__EncFirstTime(EBoolean)] = EBoolean
        self.baseElements[self.__EncFirstTime(EInt)] = EInt
        self.baseElements[self.__EncFirstTime(ELong)] = ELong
        self.baseElements[self.__EncFirstTime(EFloat)] = EFloat
        self.baseElements[self.__EncFirstTime(EDouble)] = EDouble
        self.baseElements[self.__EncFirstTime(EString)] = EString
        self.baseElements[self.__EncFirstTime(EDate)] = EDate
        
    def __CacheBaseElements(self)->None:    
        self.__InitCaching(EObject.eClass)
        self.__InitCaching(EClass.eClass)
        self.__InitCaching(EPackage.eClass)
        self.__InitCaching(EEnum.eClass)
        self.__InitCaching(EAttribute.eClass)
        self.__InitCaching(EReference.eClass)
        self.__InitCaching(EBoolean)
        self.__InitCaching(EInt)
        self.__InitCaching(ELong)
        self.__InitCaching(EFloat)
        self.__InitCaching(EDouble)
        self.__InitCaching(EString)
        self.__InitCaching(EDate)
        #Ecore Create Ids Cache caches
        self.__UpdateCreateIdStrCache(ECORE_PACKAGE, ECORE_PACKAGE.nsURI)
        self.__UpdateCreateIdStrCache(EPackage.eClass, ECORE_PACKAGE.nsURI+self.config.strIdSeparator+'EPackage')
        self.__UpdateCreateIdStrCache(EClass.eClass, ECORE_PACKAGE.nsURI+self.config.strIdSeparator+'EClass')
        self.__UpdateCreateIdStrCache(EEnum.eClass, ECORE_PACKAGE.nsURI+self.config.strIdSeparator+'EEnum')
        self.__UpdateCreateIdStrCache(EEnumLiteral.eClass, ECORE_PACKAGE.nsURI+self.config.strIdSeparator+'EEnumLiteral')
        self.__UpdateCreateIdStrCache(EAttribute.eClass, ECORE_PACKAGE.nsURI+self.config.strIdSeparator+'EAttribute')
        self.__UpdateCreateIdStrCache(EReference.eClass, ECORE_PACKAGE.nsURI+self.config.strIdSeparator+'EReference')
        
        self.__UpdateElementNameCache(EObject.eClass, 'EObject', None, None)
        self.__UpdateElementNameCache(EPackage.eClass, 'EPackage', None, None)
        self.__UpdateElementNameCache(EClass.eClass, 'EClass', None, None)
        self.__UpdateElementNameCache(EEnum.eClass, 'EEnum', None, None)
        self.__UpdateElementNameCache(EEnumLiteral.eClass, 'EEnumLiteral', None, None)
        self.__UpdateElementNameCache(EAttribute.eClass, 'EAttribute', None, None)


    # ##########################################
    # Init concept CRUD handlers (generated)   #
    # ##########################################   
    
    #@generated
    def __InitConceptsCreateHandlerTable(self):
        handlerTable = {}
        # MX
        handlerTable[GetConceptKeyString(CONCEPTS.MXMDB)] = (self._CreateMxMdb,0,[])
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)] = (self._CreateMxConstraint,2,['Element', 'Expression'])
        # M2
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)] = (self._CreateM2Package,2,['Name', 'Superpackage'])
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)] = (self._CreateM2Model,0,[])
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)] = (self._CreateM2Enum,2,['Name', 'Package'])
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)] = (self._CreateM2OptionOfEnum,3,['Name', 'Value', 'Enum'])
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)] = (self._CreateM2Class,3,['Name', 'IsAbstract', 'Package'])
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)] = (self._CreateM2Attribute,6,['Name', 'Class', 'PrimType', 'Mul', 'Unit', 'Enum'])
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)] = (self._CreateM2Association,7,['SrcName', 'SrcClass', 'SrcMul', 'DstName', 'DstClass', 'DstMul', 'AnyDst'])
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)] = (self._CreateM2Composition,5,['Name', 'ParentClass', 'ChildClass', 'MulChild', 'AnyChild'])
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)] = (self._CreateM2Inheritance,2,['Subclass', 'Superclass'])
        # M1
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)] = (self._CreateM1Model,2,['M2Model', 'Name'])
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)] = (self._CreateM1Object,3,['M2Class', 'Model', 'Name'])
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)] = (self._CreateM1Attribute,3,['M2Attribute', 'Object', 'Value'])
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)] = (self._CreateM1Association,3,['M2Association', 'Src', 'Dst'])
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)] = (self._CreateM1Composition,3,['M2Composition', 'Parent', 'Child'])
        return handlerTable
    
    #@generated
    def __InitConceptsReadHandlerTable(self):
        handlerTable = {}
        # MX
        handlerTable[GetConceptKeyString(CONCEPTS.MXMDB)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.MXMDB)][GetConceptKeyString(MXMDB.CONCEPT)] = self._ReadMxMdbConcept
        handlerTable[GetConceptKeyString(CONCEPTS.MXMDB)][GetConceptKeyString(MXMDB.M2MODELS)] = self._ReadMxMdbM2Models
        handlerTable[GetConceptKeyString(CONCEPTS.MXMDB)][GetConceptKeyString(MXMDB.M1MODELS)] = self._ReadMxMdbM1Models
        handlerTable[GetConceptKeyString(CONCEPTS.MXMDB)][GetConceptKeyString(MXMDB.MDB)] = self._ReadMxMdbMdb
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXCONSTRAINT.ELEMENT)] = self._ReadMxConstraintElement
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXCONSTRAINT.EXPRESSION)] = self._ReadMxConstraintExpression
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        # M2
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(M2PACKAGE.NAME)] = self._ReadM2PackageName
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(M2PACKAGE.SUPERPACKAGE)] = self._ReadM2PackageSuperpackage
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(M2PACKAGE.SUBPACKAGES)] = self._ReadM2PackageSubpackages
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(M2PACKAGE.CLASSES)] = self._ReadM2PackageClasses
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(M2PACKAGE.ENUMS)] = self._ReadM2PackageEnums
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(M2PACKAGE.M1MODELS)] = self._ReadM2PackageM1Models
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(M2PACKAGE.NAME)] = self._ReadM2PackageName
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(M2PACKAGE.SUPERPACKAGE)] = self._ReadM2PackageSuperpackage
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(M2PACKAGE.SUBPACKAGES)] = self._ReadM2PackageSubpackages
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(M2PACKAGE.CLASSES)] = self._ReadM2PackageClasses
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(M2PACKAGE.ENUMS)] = self._ReadM2PackageEnums
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(M2PACKAGE.M1MODELS)] = self._ReadM2PackageM1Models
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(M2ENUM.NAME)] = self._ReadM2EnumName
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(M2ENUM.PACKAGE)] = self._ReadM2EnumPackage
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(M2ENUM.OPTIONS)] = self._ReadM2EnumOptions
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(M2ENUM.ATTRIBUTES)] = self._ReadM2EnumAttributes
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(M2OPTIONOFENUM.NAME)] = self._ReadM2OptionOfEnumName
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(M2OPTIONOFENUM.VALUE)] = self._ReadM2OptionOfEnumValue
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(M2OPTIONOFENUM.ENUM)] = self._ReadM2OptionOfEnumEnum
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(M2OPTIONOFENUM.M1ATTRIBUTESUSINGOPTION)] = self._ReadM2OptionOfEnumM1AttributesUsingOption
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.NAME)] = self._ReadM2ClassName
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.ISABSTRACT)] = self._ReadM2ClassIsAbstract
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.PACKAGE)] = self._ReadM2ClassPackage
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.INSTANCES)] = self._ReadM2ClassInstances
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.MYINSTANCES)] = self._ReadM2ClassMyInstances
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.MYATTRIBUTES)] = self._ReadM2ClassMyAttributes
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.ATTRIBUTES)] = self._ReadM2ClassAttributes
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.MYSRCASSOCIATIONS)] = self._ReadM2ClassMySrcAssociations
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.SRCASSOCIATIONS)] = self._ReadM2ClassSrcAssociations
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.MYDSTASSOCIATIONS)] = self._ReadM2ClassMyDstAssociations
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.DSTASSOCIATIONS)] = self._ReadM2ClassDstAssociations
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.MYPARENTCOMPOSITIONS)] = self._ReadM2ClassMyParentCompositions
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.PARENTCOMPOSITIONS)] = self._ReadM2ClassParentCompositions
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.MYCHILDCOMPOSITIONS)] = self._ReadM2ClassMyChildCompositions
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.CHILDCOMPOSITIONS)] = self._ReadM2ClassChildCompositions
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.MYSPECIALIZATIONS)] = self._ReadM2ClassMySpecializations
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.SPECIALIZATIONS)] = self._ReadM2ClassSpecializations
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.MYGENERALIZATIONS)] = self._ReadM2ClassMyGeneralizations
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(M2CLASS.GENERALIZATIONS)] = self._ReadM2ClassGeneralizations
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(M2ATTRIBUTE.NAME)] = self._ReadM2AttributeName
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(M2ATTRIBUTE.CLASS)] = self._ReadM2AttributeClass
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(M2ATTRIBUTE.PRIMTYPE)] = self._ReadM2AttributePrimType
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(M2ATTRIBUTE.MUL)] = self._ReadM2AttributeMul
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(M2ATTRIBUTE.UNIT)] = self._ReadM2AttributeUnit
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(M2ATTRIBUTE.ENUM)] = self._ReadM2AttributeEnum
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(M2ATTRIBUTE.MYINSTANCES)] = self._ReadM2AttributeMyInstances
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(M2ASSOCIATION.SRCNAME)] = self._ReadM2AssociationSrcName
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(M2ASSOCIATION.SRCCLASS)] = self._ReadM2AssociationSrcClass
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(M2ASSOCIATION.SRCMUL)] = self._ReadM2AssociationSrcMul
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(M2ASSOCIATION.DSTNAME)] = self._ReadM2AssociationDstName
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(M2ASSOCIATION.DSTCLASS)] = self._ReadM2AssociationDstClass
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(M2ASSOCIATION.DSTMUL)] = self._ReadM2AssociationDstMul
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(M2ASSOCIATION.ANYDST)] = self._ReadM2AssociationAnyDst
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(M2ASSOCIATION.MYINSTANCES)] = self._ReadM2AssociationMyInstances
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(M2COMPOSITION.NAME)] = self._ReadM2CompositionName
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(M2COMPOSITION.PARENTCLASS)] = self._ReadM2CompositionParentClass
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(M2COMPOSITION.CHILDCLASS)] = self._ReadM2CompositionChildClass
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(M2COMPOSITION.MULCHILD)] = self._ReadM2CompositionMulChild
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(M2COMPOSITION.ANYCHILD)] = self._ReadM2CompositionAnyChild
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(M2COMPOSITION.MYINSTANCES)] = self._ReadM2CompositionMyInstances
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(M2INHERITANCE.SUBCLASS)] = self._ReadM2InheritanceSubclass
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(M2INHERITANCE.SUPERCLASS)] = self._ReadM2InheritanceSuperclass
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(M2INHERITANCE.M1ATTRIBUTESBYINHERITANCE)] = self._ReadM2InheritanceM1AttributesByInheritance
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(M2INHERITANCE.M1ASSOCIATIONSBYINHERITANCE)] = self._ReadM2InheritanceM1AssociationsByInheritance
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(M2INHERITANCE.M1COMPOSITIONSBYINHERITANCE)] = self._ReadM2InheritanceM1CompositionsByInheritance
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        # M1
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(M1MODEL.M2MODEL)] = self._ReadM1ModelM2Model
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(M1MODEL.NAME)] = self._ReadM1ModelName
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(M1MODEL.OBJECTS)] = self._ReadM1ModelObjects
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.M2CLASS)] = self._ReadM1ObjectM2Class
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.MODEL)] = self._ReadM1ObjectModel
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.NAME)] = self._ReadM1ObjectName
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.ATTRIBUTES)] = self._ReadM1ObjectAttributes
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.SRCASSOCIATIONS)] = self._ReadM1ObjectSrcAssociations
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.DSTASSOCIATIONS)] = self._ReadM1ObjectDstAssociations
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.PARENTCOMPOSITIONS)] = self._ReadM1ObjectParentCompositions
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.CHILDCOMPOSITION)] = self._ReadM1ObjectChildComposition
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.FEATUREVALUES)] = self._ReadM1ObjectFeatureValues
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(M1OBJECT.FEATUREINSTANCES)] = self._ReadM1ObjectFeatureInstances
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(M1ATTRIBUTE.M2ATTRIBUTE)] = self._ReadM1AttributeM2Attribute
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(M1ATTRIBUTE.OBJECT)] = self._ReadM1AttributeObject
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(M1ATTRIBUTE.VALUE)] = self._ReadM1AttributeValue
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(M1ATTRIBUTE.POS)] = self._ReadM1AttributePos
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(M1ASSOCIATION.M2ASSOCIATION)] = self._ReadM1AssociationM2Association
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(M1ASSOCIATION.SRC)] = self._ReadM1AssociationSrc
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(M1ASSOCIATION.SRCPOS)] = self._ReadM1AssociationSrcPos
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(M1ASSOCIATION.DST)] = self._ReadM1AssociationDst
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(M1ASSOCIATION.DSTPOS)] = self._ReadM1AssociationDstPos
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(M1COMPOSITION.M2COMPOSITION)] = self._ReadM1CompositionM2Composition
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(M1COMPOSITION.PARENT)] = self._ReadM1CompositionParent
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(M1COMPOSITION.CHILD)] = self._ReadM1CompositionChild
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(M1COMPOSITION.POS)] = self._ReadM1CompositionPos
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.CONCEPT)] = self._ReadMxElementConcept
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.STRID)] = self._ReadMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._ReadMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.OWNER)] = self._ReadMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.GROUP)] = self._ReadMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._ReadMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.HASH)] = self._ReadMxElementHash
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.CONSTRAINTS)] = self._ReadMxElementConstraints
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.MDB)] = self._ReadMxElementMdb
        return handlerTable
    
    #@generated
    def __InitConceptsUpdateHandlerTable(self):
        handlerTable = {}
        # MX
        handlerTable[GetConceptKeyString(CONCEPTS.MXMDB)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        # M2
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        # M1
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(M1ATTRIBUTE.VALUE)] = self._UpdateM1AttributeValue
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)] = {}
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.STRID)] = self._UpdateMxElementStrId
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.DOCUMENTATION)] = self._UpdateMxElementDocumentation
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.OWNER)] = self._UpdateMxElementOwner
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.GROUP)] = self._UpdateMxElementGroup
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)][GetConceptKeyString(MXELEMENT.PERMISSIONS)] = self._UpdateMxElementPermissions
        return handlerTable
    
    #@generated
    def __InitConceptsDeleteHandlerTable(self):
        handlerTable = {}
        # MX
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)] = self._DeleteMxConstraint
        # M2
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)] = self._DeleteM2Package
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)] = self._DeleteM2Model
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)] = self._DeleteM2Enum
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)] = self._DeleteM2OptionOfEnum
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)] = self._DeleteM2Class
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)] = self._DeleteM2Attribute
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)] = self._DeleteM2Association
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)] = self._DeleteM2Composition
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)] = self._DeleteM2Inheritance
        # M1
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)] = self._DeleteM1Model
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)] = self._DeleteM1Object
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)] = self._DeleteM1Attribute
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)] = self._DeleteM1Association
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)] = self._DeleteM1Composition
        return handlerTable

    #@generated
    def __InitIsInstanceHandlers(self):
        handlerTable = {}
        # MX
        handlerTable[GetConceptKeyString(CONCEPTS.MXCONSTRAINT)] = self._IsMxConstraint
        # M2
        handlerTable[GetConceptKeyString(CONCEPTS.M2PACKAGE)] = self._IsM2Package
        handlerTable[GetConceptKeyString(CONCEPTS.M2MODEL)] = self._IsM2Model
        handlerTable[GetConceptKeyString(CONCEPTS.M2ENUM)] = self._IsM2Enum
        handlerTable[GetConceptKeyString(CONCEPTS.M2OPTIONOFENUM)] = self._IsM2OptionOfEnum
        handlerTable[GetConceptKeyString(CONCEPTS.M2CLASS)] = self._IsM2Class
        handlerTable[GetConceptKeyString(CONCEPTS.M2ATTRIBUTE)] = self._IsM2Attribute
        handlerTable[GetConceptKeyString(CONCEPTS.M2ASSOCIATION)] = self._IsM2Association
        handlerTable[GetConceptKeyString(CONCEPTS.M2COMPOSITION)] = self._IsM2Composition
        handlerTable[GetConceptKeyString(CONCEPTS.M2INHERITANCE)] = self._IsM2Inheritance
        # M1
        handlerTable[GetConceptKeyString(CONCEPTS.M1MODEL)] = self._IsM1Model
        handlerTable[GetConceptKeyString(CONCEPTS.M1OBJECT)] = self._IsM1Object
        handlerTable[GetConceptKeyString(CONCEPTS.M1ATTRIBUTE)] = self._IsM1Attribute
        handlerTable[GetConceptKeyString(CONCEPTS.M1ASSOCIATION)] = self._IsM1Association
        handlerTable[GetConceptKeyString(CONCEPTS.M1COMPOSITION)] = self._IsM1Composition
        return handlerTable
    
    # #########################
    # Validation functions    #
    # #########################
            
    def __VaidateFeatureNameMultiplicity(self,isNameMultivalue,isFeatureMultivalue,featureName,normalizedFeatureName):
        if(isNameMultivalue and not isFeatureMultivalue):
            self.logger.Warn('Warning: Feature name %s indicates multi value feature, but it is a single value feature. Use %s to prevent this warning.'%(featureName,normalizedFeatureName))
        elif(not isNameMultivalue and isFeatureMultivalue):
            self.logger.Warn('Feature name %s indicates single value feature, but it is a multi value feature. Use %s%s to prevent this warning.'%(featureName,featureName,FEATURE_MULTIVALUE_POSTFIX))
            
    def __ValidateType(self, value:Any, expectedType, varname:str, isNoneOk=False)->Any:
        if(None == expectedType and None != value):
            raise EOQ_ERROR_INVALID_VALUE("%s: Expected None but got %s."%(varname,type(value).__name__))
        if(isinstance(value,expectedType)):
            if(not isNoneOk and NON == type(value)):
                raise EOQ_ERROR_INVALID_VALUE("%s: Expected %s but got %s (NON is not allowed)."%(varname,expectedType.__name__,type(value).__name__))
        else:
            if(isNoneOk and None == value):
                pass #is allowed
            else:
                raise EOQ_ERROR_INVALID_VALUE("%s: Expected %s but got %s"%(varname,expectedType.__name__,type(value).__name__))
        return value 
            
    def __ValidateMultiplicity(self,mul:int,varname:str="multiplicity"):
        if(mul == -1 or mul > 0):
            return
        #else error
        raise EOQ_ERROR_INVALID_VALUE("%s: Expected positive value or -1 but got %s"%(varname,mul))
            
    def __ValidateTypes(self, value, expectedTypes:List[Any], varname:str):
        for t in expectedTypes:
            if(isinstance(value,t)):
                return value
        #if we get here, no type matched.
        raise EOQ_ERROR_INVALID_VALUE("%s: Expected %s but got %s"%(varname,[t.__name__ for t in expectedTypes],type(value).__name__))
    
    def __ValidateAndReturnUniqueClassId(self, classIdStr:str, typeName:str="Class", context:EObject=None, conceptFilterFun:Callable[[EObject],bool]=None) -> EClass:
        classes = self.__FindElementeByIdOrNameRaw(classIdStr,context,conceptFilterFun)
        nClasses = len(classes)
        if(1 == nClasses):
            return classes[0]
        elif(0 == nClasses):
            raise EOQ_ERROR_INVALID_VALUE('%s with id %s does not exist.'%(typeName,classIdStr))
        else:
            raise EOQ_ERROR_INVALID_VALUE('%s with id %s is ambiguous. Found %d options.'%(typeName,classIdStr,nClasses))
    
    def __PreventMetaMetaAccess(self,target:Obj,isRootOk=True)->None:
        #check if a base element is given, which is not allowed to be deleted.
        if(target and (target in self.baseElements or (not isRootOk and target == self.eMdb))):
            raise EOQ_ERROR_UNSUPPORTED('Invalid target %s: meta-meta content of meta-meta elements is not accessible'%(target))
    
    def __GetEObjectUpdateRecoveryInfo(self, eObj:EObject)->Tuple[Obj,Obj,I64]:
        if(None==eObj):
            return (NON(),NON(),NON())
        else:
            parentInfo = self.__ReadEObjectParentInfo(eObj, None)
            return parentInfo
        
    def __ReadEObjectParentInfoRaw(self, eObj:EObject, eContext:EObject) -> Tuple[EObject,EStructuralFeature,int]:  
        eParent = eObj.eContainer()
        eFeature = eObj.eContainmentFeature()
        if(eParent and isinstance(eParent,EObject) and eFeature and isinstance(eFeature,EStructuralFeature)):
            ePosition = 0 #already correct for single value features
            if(eFeature.many):
                #ePosition must be determined by backwards search
                #this backward search seems not optimal
                i = 0 #Eoq indicies start at 0
                for sibling in eParent.eGet(eFeature):
                    if(sibling==eObj):
                        ePosition = i
                        break;
                    i += 1
            return (eParent,eFeature,ePosition)
        else:
            return (None,None,None)

    def __ReadEObjectParentInfo(self,eObj : EObject,eContext : EObject) -> Tuple[Obj,Obj,I64]:  
        (eParent,eFeature,ePosition) = self.__ReadEObjectParentInfoRaw(eObj,eContext)
        return (self.__Enc(eParent),self.__Enc(eFeature),InitValOrNon(ePosition, I64)) 
    
    def __SetAugmentedProperty(self, eObj:EObject, name:str, val:Any) -> Any:
        '''Creates a new attribute and sets the value. The new attribute is returned.
        '''
        setattr(eObj, name, val)
        return val
    
    def __GetAugmentedProperty(self, eObj:EObject, name:str, defaultVal:Any) -> Any:
        '''Tries to get the value attribute from an object. 
        If the attribute is not existing, it is created with the defaultVal
        and the Default value is returned.
        '''
        res = defaultVal
        try:
            res = getattr(eObj, name)
        except AttributeError:
            setattr(eObj, name, defaultVal)
        return res
    
    def __EReferenceContainerFix(self,eRef:EReference)->bool:
        return None != eRef._eopposite and eRef._eopposite.containment

    def __StopIfConceptsOnlyMode(self):
        if(self.config.conceptsOnly):
            raise EOQ_ERROR_UNSUPPORTED('Native model access is not allowed in concepts only mode. Set config.conceptsOnly to False to enable native model access.')
        
        
    

