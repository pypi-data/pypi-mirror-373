'''
 Bjoern Annighoefer 2021
'''

## EOQ imports
from eoq3.config import Config,EOQ_DEFAULT_CONFIG
from eoq3.value import VAL, PRM, I64, U64, STR, QRY, NON, LST, InitValOrNon, ValidateVal
from eoq3.mdb import Mdb
from eoq3.generics import IsGenericFeature, NormalizeFeatureName, IsMultivalueFeature, IsGenericClass, \
                          GENERIC_ATTRIBUTE_FEATURES, GENERIC_CLASS_FEATURES, GENERIC_PACKAGE_FEATURES, \
                          GENERIC_MDB_FEATURES, GENERIC_COMPOSITION_FEATURES, GENERIC_ELEMENT_FEATURES,  \
                          GENERIC_ELEMENTS, GENERIC_ENUM_FEATURES, GENERIC_ENUMOPTION_FEATURES, \
                          GENERIC_ASSOCIATION_FEATURES, FEATURE_MULTIVALUE_POSTFIX, GENERIC_FEATURES_FOR_META_CLASSES
from eoq3.query import Obj, Seg, SEG_TYPES
from eoq3.error import EOQ_ERROR, EOQ_ERROR_INVALID_VALUE, EOQ_ERROR_INVALID_TYPE, EOQ_ERROR_UNSUPPORTED,\
                           EOQ_ERROR_DOES_NOT_EXIST, EOQ_ERROR_RUNTIME, EOQ_ERROR_UNKNOWN

from eoq3pyecoreutils.genericstopyecore import IsEPrimitiveType,  \
                            GenericPrimitiveTypeToEPrimitiveType, EPrimitiveTypeToGenericPrimitiveType, \
                            EANNOTATION_SOURCES, EANNOTATION_KEYS
from eoq3pyecoreutils.valuetopyecore import EValueToValue, ValueToEValue, ETypeToValueType
from eoq3pyecoreutils.crudforpyecore import UPDATE_MODES, GetUpdateModeAndAbsPosition, ValidateUpdatePosition, \
                            GetAllEAnnotations, UpdateMultiValueEAnnotation, GetEAnnotation, \
                            UpdateSingleValueEAnnotation, ClassIdToPackageAndName, \
                            ECORE_CLASSID_SEPERATOR


## PYECORE imports
#ecore base types
from pyecore.ecore import EPackage, EObject, EClass, EAttribute, EReference, EEnum, EEnumLiteral, EAnnotation, EStructuralFeature
#ecore primitives
from pyecore.ecore import EBoolean, EInt, ELong, EString, EFloat, EDouble, EDate

## OTHER imports
import types
import itertools #required for generator concatenation
#type checking
from typing import Tuple, List, Union, Any
from pyecore.valuecontainer import BadValueError

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

'''
EREFERENCE AMBIGUITY HACK
'''

nsURI = 'EOQ_EReference_Ambiguity_Resolve_Extension' #must be here, because this is read while deleting

class EAssociation(EReference):
    def __init__(self, name=None, eType=None, containment=False,
                 eOpposite=None, isOpposite=False, **kwargs):
        super().__init__(name, eType, containment, eOpposite, **kwargs)
        self.isOpposite = isOpposite

class EComposition(EReference):
    def __init__(self, name=None, eType=None, containment=True,
                 eOpposite=None, **kwargs):
        super().__init__(name, eType, containment, eOpposite, **kwargs)
        
        
'''
GENERICS AUGMENTATION
'''
class EInheritance(EObject):
    def __init__(self, subClass, superClass):
        super().__init__(name, eType, containment, eOpposite, **kwargs)
        self.isOpposite = isOpposite
        

'''
SPECIALIZATION OF OBJSEG
'''

class EObjSeg(Seg):
    def __init__(self,objId,eObj=None):
        super().__init__(SEG_TYPES.OBJ,[objId])
        self._eObj = eObj
        
        
# class EObjectLotRecord:
#     def __init__(self,eObj : EObject):
#         self.eObj = eObj
#         self.objSegs = WeakSet()

''' 
PYECORE MDBACESSOR 
'''

class PyEcoreMdb(Mdb):
    def __init__(self, config:Config=EOQ_DEFAULT_CONFIG):
        self.config = config
        self.root = None
        self.orphans = {} #manages objects without parents such that they cannot get lost
        #handlers
        self.genericCreateHandlers = self.__InitGenericCreateHandlerTable()
        self.genericReadHandlers = self.__InitGenericReadHandlerTable()
        self.genericUpdateHandlers = self.__InitGenericUpdateHandlerTable()
        
            
        #Initialize encoding
        self.idToObjectLUT = {}
        self.lastId = 0
        #internal storages
        self.baseElements = {}
        self.artificialFeatures = {}
        self.artificialAttributesLut = {}
        #Encoding all base elements (store the base elements to prevent that those are deleted)
        self.__RegisterBaseElements()
        #initialize base caches with base elements
        self.__CacheBaseElements()
        #initialize artificial features
        self.__InitArtificialFeatures()
        
    # BASIC METHODS
    
    #@Override
    def Create(self, classId:Union[STR,Obj], createArgs:LST=LST([]), target:Obj=NON()) -> Tuple[Obj,EOQ_ERROR]:
        #input validation
        self.__ValidateTypes(classId, [STR,Obj], 'classId')
        self.__ValidateType(createArgs, LST, 'createArgs')
        self.__ValidateType(target, QRY, 'target',True)
        #create the new element
        res = NON()
        if(STR == type(classId)):
            classIdStr = classId.GetVal()
            if(IsGenericClass(classIdStr)):
                res = self.__CreateGenericElement(classIdStr,createArgs,target)  
            else:
                #create native class
                c = self.__ValidateAndReturnUniqueClassId(classIdStr)
                res = self.__CreateNativeElement(c,createArgs,target)  
        elif(isinstance(classId,Obj)):
            c = self.__Dec(classId)
            if(not isinstance(c, EClass)):
                raise EOQ_ERROR_INVALID_VALUE('%s is no class. Cannot instantiate.'%(classId))
            res = self.__CreateNativeElement(c,createArgs,target)
            
        #prepare return value
        return res, None #by default no post modification error is returned
    
    def __InitAndEncNewElem(self,newElem:EObject,target:Obj)->Obj:
        self.__InitCaching(newElem)
        self.__UpdateChildStateAndCache(newElem)
        res = self.__EncFirstTime(newElem,target)
        return res
    
    def __CreateGenericElement(self, classIdStr:str, createArgs:LST, target:Obj) -> Tuple[object,object]:
        #create a generic element
        res = None
        try:
            createHandler = self.genericCreateHandlers[classIdStr]
            res = createHandler(createArgs,target)
        except KeyError:
            raise EOQ_ERROR_INVALID_VALUE('Cannot create %s. Generic identifier is unknown'%(classIdStr))  
        return res
    
    def __CreateNativeElement(self, clazz:EClass, createArgs:LST, target:Obj) -> Tuple[object,object]:
        cArgs = self.__DecCollection(createArgs)
        try:
            newElem = clazz(*cArgs)
        except Exception as e:
            raise EOQ_ERROR_UNKNOWN('Failed to instantiate class. Wrong create args?: %s'%(str(e)))
        res = self.__InitAndEncNewElem(newElem, target)    
        return res
    
    def _CreateM2Model(self, createArgs:LST, target:Obj) -> Obj:
        #cargs = name:STR parent:OBJ -> m2model
        name:str = None
        parentM2Model:Obj = None 
        eParentM2Model:Obj = None 
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.M2MODEL+' createArgs require name:STR and parentM2Model:Obj, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        if(name in self.packageIdCache):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.M2MODEL+' names must be unique. A '+GENERIC_ELEMENTS.M2MODEL+' with name %s does already exist.'%(name))
        #validate parentM2Model package
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](parentM2Model)',True)
        if(not createArgs[1].IsNone()): #non parents are allowed.
            parentM2Model = createArgs[1]
            eParentM2Model = self.__Dec(parentM2Model)
            if(not isinstance(eParentM2Model, EPackage)):
                raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.M2MODEL+' parentM2Model must be '+GENERIC_ELEMENTS.M2MODEL+'. %s'+ 'is no '+GENERIC_ELEMENTS.M2MODEL)%(parentM2Model))
        #create the package according to given arguments
        newEElem = EPackage(name)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        if(parentM2Model):
            self._UpdatePackageSubpackages(eParentM2Model, newElem, -1)
        return newElem
            
    def _CreateM2Class(self, createArgs:LST, target:Obj) -> Obj:
        #cargs = name:STR m2model:OBJ -> class
        name:str = None
        m2Model:Obj = None 
        eM2Model:EPackage = None 
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.CLASS+' createArgs require name:STR and m2Model:Obj, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        #validate m2Model
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](m2Model')
        m2Model = createArgs[1]
        eM2Model = self.__Dec(m2Model)
        if(not isinstance(eM2Model, EPackage)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.CLASS+' m2Model must be a '+GENERIC_ELEMENTS.M2MODEL+'. %s is no '+GENERIC_ELEMENTS.M2MODEL)%(m2Model))
        #create the class according to given arguments
        newEElem = EClass(name)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self._UpdatePackageClasses(eM2Model, newElem, -1)
        self.__UpdateClassNameCache(newEElem)
        return newElem
    
    def _CreateM2Attribute(self, createArgs:LST, target:Obj) -> Obj:
        #cargs = name:STR clazz:OBJ primType:STR mul:I64 unit:STR -> attrib
        name:str = None
        clazz:Obj = None 
        eClazz:EClass = None
        datatype:Union[Obj,STR] = None
        mul:I64 = None
        unit:STR = None
        
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=5):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.ATTRIBUTE+' createArgs require name:STR, clazz:OBJ, primType:STR, mul:I64 and unit:STR, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        #validate clazz
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](clazz)')
        clazz = createArgs[1]
        eClazz = self.__Dec(clazz)
        if(not isinstance(eClazz, EClass)):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.ATTRIBUTE+' clazz must be '+GENERIC_ELEMENTS.CLASS+'. %s is no class'%(clazz))
        #validate mul
        datatype = createArgs[2]
        self.__ValidateTypes(datatype, [STR,Obj], 'createArgs[3](primType)')
        #TODO: validate acceptable prim types
        #validate mul
        mul = createArgs[3]
        self.__ValidateType(mul, I64, 'createArgs[3](mul)')
        self.__ValidateMultiplicity(mul, 'createArgs[3](mul)')
        #validate unit
        unit = createArgs[4]
        self.__ValidateType(unit, STR, 'createArgs[4](unit)')
        #create the attribute according to given arguments
        newEElem = EAttribute(name)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self._UpdateAttributeType(newEElem,datatype,0)
        self._UpdateAttributeLen(newEElem,mul,0)
        self._UpdateAttributeUnit(newEElem,unit,0)
        self._UpdateClassAttributes(eClazz, newElem, -1)
        return newElem
    
    def _CreateM2Association(self, createArgs:LST, target:Obj) -> Obj:
        '''cargs = srcName:STR srcClass:OBJ srcMul:I64 dstName:STR dstClass:OBJ dstMul:I64   
         __________                      __________
        |          | srcName    dstName |          |
        | srcClass |--------------------| dstClass |
        |__________| srcMul      dstMul |__________|
        
        '''
        name:str = None
        srcClass:Obj = None 
        srcEClass:EClass = None
        srcMul: I64 = None
        dstClass:Obj = None
        dstEClass:EClass = None
        dstMul:I64 = None
        
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=6):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.ASSOCIATION+' createArgs require arguments srcName:STR, srcClass:OBJ, srcMul:I64, dstName:STR, dstClass:OBJ and dstMul:I64, but got %d arguments.'%(nArgs))
        #validate srcName
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](srcName)')
        srcName = createArgs[0].GetVal()
        #validate srcClass
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](srcClass)')
        srcClass = createArgs[1]
        srcEClass = self.__Dec(srcClass)
        if(not isinstance(srcEClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.ASSOCIATION+'srcClass must be a '+GENERIC_ELEMENTS.CLASS+'. %s is no '%(srcClass)+GENERIC_ELEMENTS.CLASS)
        #validate srcMul
        srcMul = createArgs[2]
        self.__ValidateType(srcMul, I64, 'createArgs[2](srcMul)')
        self.__ValidateMultiplicity(srcMul, 'createArgs[2](srcMul)')
        #validate dstName
        self.__ValidateType(createArgs[3], STR, 'createArgs[3](dstName)')
        dstName = createArgs[3].GetVal()
        #validate dstClass
        self.__ValidateType(createArgs[4], Obj, 'createArgs[5](dstClass)')
        dstClass = createArgs[4]
        dstEClass = self.__Dec(dstClass)
        if(not isinstance(dstEClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.ASSOCIATION+' dstClass must be a class. %s is no '%(dstClass)+GENERIC_ELEMENTS.CLASS)
        #validate dstMul
        dstMul = createArgs[5]
        self.__ValidateType(dstMul, I64, 'createArgs[5](dstMul)')
        self.__ValidateMultiplicity(dstMul, 'createArgs[5](dstMul)')
        #create the association according to given arguments
        newEElem = EAssociation(dstName,containment=False,isOpposite=False)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self._UpdateAssociationDstType(newEElem,dstClass,0)
        self._UpdateAssociationDstMul(newEElem,dstMul,0)
        self._UpdateClassAssociations(srcEClass, newElem, -1)
        
        #automatically create an opposite reference
        newEElemOpp = EAssociation(srcName,containment=False,isOpposite=True)
        newEElemOpp.eOpposite = newEElem
        newElemOpp = self.__InitAndEncNewElem(newEElemOpp, target)
        self._UpdateAssociationSrcType(newEElemOpp,srcClass,0)
        self._UpdateAssociationSrcMul(newEElemOpp,srcMul,0)
        self._UpdateClassAssociations(dstEClass, newElemOpp, -1)
        
        #return only the direct references
        return newElem
    
    
    def _CreateM2Composition(self, createArgs:LST, target:Obj) -> Obj:
        #cargs = name:STR srcClass:OBJ dstClass:OBJ dstMul:I64 
        name:str = None
        srcClass:Obj = None
        srcEClass:EClass = None 
        dstClass:Obj = None
        dstEClass:EClass = None
        dstMul:I64 = None
        
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=4):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.COMPOSITION+' createArgs require arguments name:STR, parrentClass:OBJ, dstClass:OBJ and dstMul:I64, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        # validate src class
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](srcClass)')
        srcClass = createArgs[1]
        srcEClass = self.__Dec(createArgs[1])
        if(not isinstance(srcEClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.COMPOSITION+' srcClass must be a '+GENERIC_ELEMENTS.CLASS+'. %s is no'+GENERIC_ELEMENTS.CLASS)%(srcClass))
        #validate dst class
        self.__ValidateType(createArgs[2], Obj, 'createArgs[2](dstClass)')
        dstClass = createArgs[2]
        dstEClass = self.__Dec(createArgs[2])
        if(not isinstance(dstEClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.COMPOSITION+' dstClass must be a '+GENERIC_ELEMENTS.CLASS+'. %s is no'+GENERIC_ELEMENTS.CLASS)%(dstClass))
        #validate dst mul
        dstMul = createArgs[3]
        self.__ValidateType(dstMul, I64, 'createArgs[3](dstMul)')
        #create the association according to given arguments
        newEElem = EComposition(name,containment=True)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self._UpdateCompositionType(newEElem,dstClass,0)
        self._UpdateCompositionLen(newEElem,dstMul,0)
        self._UpdateClassCompositions(srcEClass, newElem, -1)
        return newElem
    
    def _CreateM2Inheritance(self, createArgs:LST, target:Obj) -> Obj:
        #cargs = subClass:OBJ superClass:OBJ
        subClass:Obj = None 
        subEClass:EClass = None
        superClass:Obj = None
        superEClass:EClass = None
        
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.INHERITANCE+' createArgs require arguments subClass:OBJ and superClass:OBJ, but got %d arguments.'%(nArgs))
        #validate subClass
        self.__ValidateType(createArgs[0], Obj, 'createArgs[0](subClass)')
        subClass = createArgs[0]
        subEClass = self.__Dec(subClass)
        if(not isinstance(subEClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.COMPOSITION+' subClass must be a '+GENERIC_ELEMENTS.CLASS+'. %s is no'+GENERIC_ELEMENTS.CLASS)%(subClass))
        #validate superClass
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](superClass)')
        superClass = createArgs[1]
        superEClass = self.__Dec(superClass)
        if(not isinstance(superEClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.COMPOSITION+' superClass must be a '+GENERIC_ELEMENTS.CLASS+'. %s is no'+GENERIC_ELEMENTS.CLASS)%(superClass))
        #create the association according to given arguments
        self._UpdateClassSupertypes(subEClass, superClass, -1)
        return subClass
    
    def _CreateConstraint(self, createArgs:LST, target:Obj) -> Obj:
        #cargs = context:Obj, constraint:STR
        context:Obj = None 
        eContext:EObject = None 
        constraint:STR = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.CONSTRAINT+' createArgs require target:Obj and constraint:STR, but got %d arguments.'%(nArgs))
        #validate target
        self.__ValidateType(createArgs[0], Obj, 'createArgs[0](context)')
        context = createArgs[0]
        eContext = self.__Dec(context)
        if(not isinstance(eContext, EObject)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.CONSTRAINT+' m2Model must be a '+GENERIC_ELEMENTS.ELEMENT+'. %s is no '+GENERIC_ELEMENTS.ELEMENT)%(context))
        #validate constraint
        self.__ValidateType(createArgs[1], STR, 'createArgs[1](constraint)')
        constraint = createArgs[1]
        #add a constraint to the element
        self._UpdateElementConstraints(eContext,constraint,-1)
        return context
    
    def _CreateM2Enum(self, createArgs:LST, target:Obj) -> Obj:
        #cargs = name:STR, m2Model:Obj
        name:str = None
        m2Model:Obj = None 
        eM2Model:EPackage = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.ENUM+' createArgs require name:STR and m2Model:Obj, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        #validate m2Model
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](m2Model')
        m2Model = createArgs[1]
        eM2Model = self.__Dec(m2Model)
        if(not isinstance(eM2Model, EPackage)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.ENUM+' m2Model must be a '+GENERIC_ELEMENTS.M2MODEL+'. %s is no '+GENERIC_ELEMENTS.M2MODEL)%(m2Model))
        #create the class according to given arguments
        newEElem = EEnum(name)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self._UpdatePackageEnums(eM2Model, newElem, -1)
        return newElem
    
    def _CreateM2EnumOption(self, createArgs:LST, target:Obj) -> Obj:
        #cargs = name:STR, enum:Obj, value:U64
        enum = None
        eEnum = None
        name = None
        value = None
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=3):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.ENUMOPTION+' createArgs require enum:Obj, name:STR and value:U64, but got %d arguments.'%(nArgs))
        #validate name
        self.__ValidateType(createArgs[0], STR, 'createArgs[0](name)')
        name = createArgs[0].GetVal()
        #validate m2Model
        self.__ValidateType(createArgs[1], Obj, 'createArgs[1](m2Model)')
        enum = createArgs[1]
        eEnum = self.__Dec(enum)
        if(not isinstance(eEnum, EEnum)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.ENUMOPTION+' enum must be a '+GENERIC_ELEMENTS.ENUM+'. %s is no '+GENERIC_ELEMENTS.ENUM)%(enum))
        #validate value
        self.__ValidateType(createArgs[2], U64, 'createArgs[2](name)')
        value = createArgs[2]
        
        #create the class according to given arguments
        newEElem = EEnumLiteral(name)
        newElem = self.__InitAndEncNewElem(newEElem, target)
        self._UpdateEnumoptionValue(newEElem, value, 0)
        self._UpdateEnumOptions(eEnum, newElem, -1)
        return newElem
    
    def _CreateM1Model(self, createArgs:LST, target:Obj) -> Obj:
        #cargs = m2Model:Obj, m1RootClass:Obj
        name:str = None
        m2Model:Obj = None 
        eM2Model:EPackage = None 
        m1RootClass:Obj = None 
        m1RootEClass:EClass = None
        
        #validate create args
        nArgs = len(createArgs)
        if(nArgs!=2):
            raise EOQ_ERROR_INVALID_VALUE(GENERIC_ELEMENTS.M1MODEL+' createArgs require m2Model:Obj and m1RootClass, but got %d arguments.'%(nArgs))
        #validate m2Model
        self.__ValidateType(createArgs[0], Obj, 'createArgs[0](m2Model')
        m2Model = createArgs[0]
        eM2Model = self.__Dec(m2Model)
        if(not isinstance(eM2Model, EPackage)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.M1MODEL+' m2Model must be a '+GENERIC_ELEMENTS.M2MODEL+'. %s is no '+GENERIC_ELEMENTS.M2MODEL)%(m2Model))
        #validate m1RootClass
        self.__ValidateType(createArgs[0], Obj, 'createArgs[0](m1RootClass')
        m1RootClass = createArgs[1]
        m1RootEClass = self.__Dec(m1RootClass)
        if(not isinstance(m1RootEClass, EClass)):
            raise EOQ_ERROR_INVALID_VALUE((GENERIC_ELEMENTS.M1MODEL+' m1RootClass must be a '+GENERIC_ELEMENTS.CLASS+'. %s is no '+GENERIC_ELEMENTS.CLASS)%(m2Model))
        #create the class according to given arguments
        #assume the first class in the model 
        classes = self._ReadPackageClasses(eM2Model, NON())
        if(m1RootClass not in classes):
            raise EOQ_ERROR_INVALID_VALUE(' m1RootClass is no class of given m2Model.')
        newElem = self.__CreateNativeElement(m1RootEClass, LST([]), NON())
        return newElem
    
    #@Override
    def Read(self, target:Obj, featureName:STR, context:Obj=NON()) -> VAL:
        value = None
        #input validation
        self.__ValidateType(target, QRY, 'target')
        self.__ValidateType(featureName, STR, 'featureNameStr')
        self.__ValidateType(context, QRY, 'context',True)
        #decode target
        eObj = self.__Dec(target)
        #generic feature names
        featureNameStr = featureName.GetVal()
        isMultiValueFeature = IsMultivalueFeature(featureNameStr)      
        normalizedFeatureName = NormalizeFeatureName(featureNameStr) 
        if(IsGenericFeature(featureNameStr)):
            handler = self.__GetGenericFeatureHandler(eObj, featureNameStr, self.genericReadHandlers)
            if(featureNameStr not in GENERIC_FEATURES_FOR_META_CLASSES):
                self.__PreventMetaMetaAccess(target)
            eContext = None if context.IsNone() else self.__Dec(context)
            value = handler(eObj,eContext)
        #all other features
        else:
            #validate target: prevent, that a meta-meta-element is changed
            self.__PreventMetaMetaAccess(target)
            eFeature = eObj.eClass.findEStructuralFeature(normalizedFeatureName)
            try:
                #traditional variant
#                 eValue = eObj.eGet(normalizedFeatureName)
#                 eValue = getattr(eObj, normalizedFeatureName) #is the same as eGet() :(
                #Performance Hack?
                try: 
                    eValue = eObj.__dict__[normalizedFeatureName]._get() #is this quicker than eGet? Works for most attributes, but not all
                except KeyError:
                    eValue = getattr(eObj, normalizedFeatureName) #is the same as eGet() :(
                #check if this was not a value but a method.
                if(isinstance(eValue,types.MethodType)): 
                    eValue =  eValue()#call the method to get the values
            except Exception as e:
                raise EOQ_ERROR_DOES_NOT_EXIST('%s is no valid feature: %s'%(featureNameStr,str(e)))
            value = self.__EncValue(eValue,eFeature.eType,eFeature.many)
            #sanity check of feature name an multiplicity
            isMultivalue = (isinstance(value,LST))
            self.__VaidateFeatureNameMultiplicity(isMultiValueFeature,isMultivalue,featureNameStr,normalizedFeatureName)
        return value
    
    #@Override
    def Update(self, target:Obj, featureName:STR, value:PRM, position:I64=I64(0)) -> Tuple[Obj,Obj,Obj,I64,EOQ_ERROR]:
        #validate input
        self.__ValidateType(target, QRY, 'target')
        self.__ValidateType(featureName, STR, 'featureName')
        self.__ValidateType(value, PRM, 'value',True)
        self.__ValidateType(position, I64, 'position')
        #validate target
        self.__PreventMetaMetaAccess(target)
        #convert values
        eObj = self.__Dec(target)
        eFeatureName = featureName.GetVal()
        ePosition = position.GetVal()
        #init return values
        oldValue = NON() 
        oldOwner = NON() 
        oldComposition = NON()
        oldPosition = NON()
        #update generic features
        if(IsGenericFeature(eFeatureName)): #translate generic features
            handler = self.__GetGenericFeatureHandler(eObj, eFeatureName, self.genericUpdateHandlers)
            (oldValue,oldOwner,oldComposition,oldPosition) = handler(eObj,value,ePosition)
        # update normal features
        elif(isinstance(eObj,EObject)): 
            (oldValue,oldOwner,oldComposition,oldPosition) = self.__UpdateCustomFeature(eObj,eFeatureName,value,ePosition)
        else:
            raise EOQ_ERROR_INVALID_TYPE('Type error: target is no object, but %s.'%(eObj)) 
        #Update finished, return value
        return (oldValue, oldOwner, oldComposition, oldPosition, None) #no post modification error can occure
    
    def __UpdateCustomFeature(self,eObj : EObject,eFeatureName : str, value : VAL, ePosition : int):
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
            raise EOQ_ERROR_DOES_NOT_EXIST('%s has no feature %s.'%(eObj.eClass.name,normalizedFeatureName))
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
            (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
            #get feature type
            if eFeature.containment:
                featureType = EFEATURE_TYPES.COMPOSITION
            else:
                featureType = EFEATURE_TYPES.ASSOCIATION
        #update the feature value
        try:
            if(eFeature.many):
                self.__VaidateFeatureNameMultiplicity(isMultiValueFeature,True,eFeatureName,normalizedFeatureName)
                oldEValue = self.__UpdateMultiValueEFeature(eObj,eFeature,ePosition,eValue,eFeature.upperBound,featureType)
            else: #single value feature
                self.__VaidateFeatureNameMultiplicity(isMultiValueFeature,False,eFeatureName,normalizedFeatureName)
                oldEValue = self.__UpdateSingleValueEFeature(eObj,eFeature,ePosition,eValue,featureType)
        except BadValueError as e:
            raise EOQ_ERROR_INVALID_VALUE("%s.%s is of type %s, but got %s"%(eObj.eClass.name,eFeature.name,eFeature.eType.name,type(eValue).__name__))
        #convert the old value back to an VAL
        oldValue = self.__EncValue(oldEValue, eType, False)
        #Check special cases which require cache updates
        if(EClass == type(eObj) and 'name' == normalizedFeatureName):
            self.__UpdateClassNameCache(eObj, oldEValue)
        elif(EPackage == type(eObj) and 'nsURI' == normalizedFeatureName):
            self.__UpdatePackagesCache(eObj, oldEValue)
        return (oldValue,oldOwner,oldComposition,oldPosition)
        
    #@Override             
    def Delete(self, target:Obj) -> Tuple[STR,List[STR],List[VAL],EOQ_ERROR]:
        #is target legal?
        self.__ValidateType(target, QRY, 'target')
        self.__PreventMetaMetaAccess(target,False)
        eObj = self.__Dec(target)
        # sanity checks can this element be deleted?

        eParent = self.__ReadElementParentRaw(eObj,None)
        if(eParent[0] != None):
            raise EOQ_ERROR_RUNTIME('Cannot delete element that has a parent.')
        eAssociates = self.__ReadElementAssociatesRaw(eObj,None)
        nAssociates = len(eAssociates)
        if(0 < nAssociates):
            raise EOQ_ERROR_RUNTIME('Cannot delete element that is associated with other elements. Found %d active associations.'%(nAssociates))
        classId = self._ReadClassId(eObj.eClass,None)
        #preserve recovery information
        featureNames = [self._ReadFeatureSafeName(f,None) for f in eObj.eClass.eAllStructuralFeatures()]
        featureValues = [self.Read(target,f) for f in featureNames]
        #delete the element
        self._DeleteElement(eObj)
        #consider special cases:
        if(self.root == eObj): 
            self.root = None
        if(eObj in self.orphans):
            del self.orphans[eObj]
        #finally clean-up the element reference
        self.__EncLastTime(target)
        return (classId,featureNames,featureValues,None) #no post modification error can happen
        
    
    def __FindClassByIdOrNameRaw(self,classNameOrId : str) -> list:
        #search all matching classes
        classes = []
        if(ECORE_CLASSID_SEPERATOR in classNameOrId):
            (packageId,className) = ClassIdToPackageAndName(classNameOrId)
            if(packageId in self.packageIdCache):
                ePackage = self.packageIdCache[packageId]
                for c in ePackage.eClassifiers:
                    if(className == c.name):
                        classes.append(c)
                        break 
#             if classNameOrId in self.classIdCache:
#                 classes.append(self.classIdCache[classNameOrId])
        else:
            if classNameOrId in self.classNamesCache:
                for c in self.classNamesCache[classNameOrId]:
                    classes.append(c)
        return classes
    
    #@Override
    def FindClassByIdOrName(self,classNameOrIdVal : STR) -> LST:
        classNameOrId = classNameOrIdVal.GetVal()
        classes = self.__FindClassByIdOrNameRaw(classNameOrId)
        return self.__EncCollection(classes)
    
    ### PROTECTED METHODS
    
    ### BEGIN READ HANDLERS ###
    ## READ
    # UNIVERSAL
    def _ReadM2ModelName(self,eObj : EObject,eContext : EObject) -> STR:
        return STR(eObj.name) #cannot be None
    
    def _ReadM2EnumName(self,eObj : EObject,eContext : EObject) -> STR:
        return STR(eObj.name) #cannot be None
    
    def _ReadM2ClassName(self,eObj : EObject,eContext : EObject) -> STR:
        return STR(eObj.name) #cannot be None
    
    def _ReadM2AttributeName(self,eObj : EObject,eContext : EObject) -> STR:
        return STR(eObj.name) #cannot be None
    
    def _ReadM2AssociationName(self,eObj : EObject,eContext : EObject) -> STR:
        return STR(eObj.name) #cannot be None
    
    def _ReadM2CompositionName(self,eObj : EObject,eContext : EObject) -> STR:
        return STR(eObj.name) #cannot be None
    
    def _ReadFeatureSafeName(self,eObj : EStructuralFeature,eContext : EObject) -> STR:
        return STR(self._ReadFeatureSafeNameRaw(eObj, eContext))
        
    def _ReadFeatureSafeNameRaw(self,eObj : EStructuralFeature,eContext : EObject) -> str:
        if(eObj.upperBound == 1):
            return eObj.name #cannot be None
        elif(eObj.name.endswith(FEATURE_MULTIVALUE_POSTFIX)): #name and safe name are identical, e.g. for generic features
            return eObj.name
        else:
            return eObj.name + FEATURE_MULTIVALUE_POSTFIX
    
    # ROOT
    def _ReadMdbRoot(self,eObj : EObject,eContext : EObject) -> Obj:
        return self.__Enc(self.root)
    
    def _ReadMdbOrphans(self,eObj : EObject,eContext : EObject):
        return LST([self.__Enc(m) for m in self.orphans])
    
    # ELEMENT
    def _ReadM1ObjectClass(self,eObj : EObject,eContext : EObject) -> Obj:
        return self.__Enc(eObj.eClass)
    
    def __ReadElementParentRaw(self,eObj : EObject,eContext : EObject) -> list:  
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
            return [eParent,eFeature,ePosition]
        else:
            return [None,None,None]
    
    def _ReadM2ClassM2Model(self,eObj : EObject,eContext : EObject) -> LST:  
        [eParent,eFeature,ePosition] = self.__ReadElementParentRaw(eObj,eContext)
        return LST([self.__Enc(eParent),self.__Enc(eFeature),InitValOrNon(ePosition, I64)]) #is [None, None, None]
    
    def __ReadElementAssociatesRaw(self,eObj : EObject,eContext : EObject):
        if(None != eContext):
            return [a for a in eObj._eoqAssociatesCache.values() if a[0] == eContext or a[0] in eContext.eAllContents()] 
        else: 
            return [a for a in eObj._eoqAssociatesCache.values()]
    
    def _ReadElementAssociates(self,eObj : EObject,eContext : EObject):
        associates = self.__ReadElementAssociatesRaw(eObj, eContext)         
        return LST([ LST([self.__Enc(a[0]), self.__Enc(a[1]), I64(a[2]), STR(a[3])]) for a in associates ])

    def _ReadElementDocumentation(self,eObj : EObject,eContext : EObject) -> STR:
        return InitValOrNon(GetEAnnotation(eObj, EANNOTATION_SOURCES.DOCUMENTATION, EANNOTATION_KEYS.DOCUMENTATION),STR)
    
    def _ReadElementConstraints(self,eObj : EObject,eContext : EObject):
        eConstraints = GetAllEAnnotations(eObj, EANNOTATION_SOURCES.CONSTRAINTS )
        return LST([STR(s) for s in eConstraints])
    
    def _ReadElementOwner(self,eObj : EObject,eContext : EObject) -> STR:
        return InitValOrNon(GetEAnnotation(eObj, EANNOTATION_SOURCES.OWNER, EANNOTATION_KEYS.OWNER),STR)
    
    def _ReadElementGroup(self,eObj : EObject,eContext : EObject) -> STR:
        return InitValOrNon(GetEAnnotation(eObj, EANNOTATION_SOURCES.GROUP, EANNOTATION_KEYS.GROUP),STR)
    
    def _ReadElementPermissions(self,eObj : EObject,eContext : EObject):
        eConstraints = GetAllEAnnotations(eObj, EANNOTATION_SOURCES.PERMISSIONS )
        return LST([STR(s) for s in eConstraints])
    
    def _ReadElementChildren(self,eObj : EObject,eContext : EObject) -> LST:
        return self.__EncCollection(eObj.eContents)
    
    def _ReadElementAllChildren(self,eObj : EObject,eContext : EObject) -> LST:
        return self.__EncCollection(eObj.eAllContents())
            
    #CLASS
    def _ReadClassId(self,eObj : EClass,eContext : EObject) -> STR:
        if(None == eObj.name or None == eObj.eContainer() or None == eObj.eContainer().nsURI):
            raise EOQ_ERROR_INVALID_VALUE('No class ID available. Class name, package or package ID are not set.')
        return STR(eObj.eContainer().nsURI + ECORE_CLASSID_SEPERATOR + eObj.name)

    def _ReadM2ClassAttributes(self,eObj : EClass,eContext : EObject)  -> LST:
        mask = lambda e: EAttribute==type(e)
        return self.__EncCollection(eObj.eStructuralFeatures, mask)
    
    def _ReadM2ClassAllAttributes(self,eObj : EClass,eContext : EObject) -> LST:
        artificialAttribtues = self.__GetAllArtificialAttributesForEClass(eObj)
        return LST([self.__Enc(x) for x in eObj.eAllAttributes()] + artificialAttribtues)
    
    def _ReadM2ClassSrcAssociations(self,eObj : EClass,eContext : EObject)  -> LST:
        mask = lambda e: isinstance(e,EReference) and not e.containment
        return self.__EncCollection(eObj.eStructuralFeatures, mask)
    
    def _ReadM2ClassAllSrcAssociations(self,eObj : EClass,eContext : EObject)  -> LST:
        return  LST([self.__Enc(x) for x in eObj.eAllReferences() if not x.containment])
    
    def _ReadM2ClassSrcCompositions(self,eObj : EClass,eContext : EObject)  -> LST:
        mask = lambda e: isinstance(e,EReference) and e.containment
        return self.__EncCollection(eObj.eStructuralFeatures, mask)
    
    def _ReadM2ClassAllSrcCompositions(self,eObj : EClass,eContext : EObject)  -> LST:
        return  LST([self.__Enc(x) for x in eObj.eAllReferences() if x.containment])
    
    def _ReadM2ClassSupertypes(self,eObj : EClass,eContext : EObject)  -> LST:
        return self.__EncCollection(eObj.eSuperTypes)
    
    def _ReadM2ClassAllSupertypes(self,eObj : EClass,eContext : EObject)  -> LST:
        return self.__EncCollection(eObj.eAllSuperTypes())
    
    def _ReadM2ClassSubtypes(self,eObj : EClass,eContext : EObject)  -> LST:
        return self.__EncCollection([c for c in EClass.eClass.allInstances() if eObj in c.eSuperTypes])
    
    def __ReadClassAllSubtypesRaw(self,eObj : EClass,eContext : EObject)  -> list:
        return [c for c in EClass.eClass.allInstances() if eObj in c.eAllSuperTypes()]
            
    def _ReadM2ClassAllSubtypes(self,eObj : EClass,eContext : EObject)  -> LST:
        return self.__EncCollection(self.__ReadClassAllSubtypesRaw(eObj, eContext))
    
    def __ReadClassInstancesRawFromContexts(self,eObj : EClass, eContexts : list)  -> list:
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
    
    def _ReadM2ClassInstances(self,eObj : EClass, eContext : EObject)  -> LST:
        instances = []
        if(None==eContext or eContext==self.root):
            instances = self.__ReadClassInstancesRawFromContexts(eObj,self.orphans.values()) #self.root is included in orphans
        else:
            instances = self.__ReadClassInstancesRawFromContexts(eObj,[eContext])
        return self.__EncCollection(instances)
    
    def __ReadClassIncarnationsRawFromContexts(self,eObj : EClass, eContexts : list)  -> list:
        incarnations = []
        for c in eContexts:
            try:
                incarnations = itertools.chain(incarnations,[e for e in c._eoqChildrenByClassCache[eObj].values()])
            except KeyError:
                pass #add nothing to the list
            if(c.eClass == eObj):
                incarnations = itertools.chain([c],incarnations)
        return incarnations
    
    def _ReadClassIncarnations(self,eObj : EClass, eContext : EObject)  -> LST:
        incarnations = []
        if(None==eContext or eContext==self.root):
            incarnations = self.__ReadClassIncarnationsRawFromContexts(eObj,self.orphans) #self.root is included in orphans
        else:
            incarnations = self.__ReadClassIncarnationsRawFromContexts(eObj,[eContext])
        return self.__EncCollection(incarnations)
    
    def _ReadClassAssociationsForMe(self,eObj : EClass, eContext : EObject)  -> LST:
        allReferences = []
        if(None==eContext or eContext==self.root):
            allReferences = self.__ReadClassInstancesRawFromContexts(EReference.eClass,self.orphans.values()) #self.root is included in orphans
        else:
            allReferences = self.__ReadClassInstancesRawFromContexts(EReference.eClass,[eContext])
        #assoc = [r for r in allReferences if not r.containment]
        associationsForMe = [r for r in allReferences if not r.containment and self.__IsSubType(eObj,r.eType)]
        return self.__EncCollection(associationsForMe)
    
    def _ReadClassCompositionsForMe(self,eObj : EClass, eContext : EObject)  -> LST:
        allReferences = []
        if(None==eContext or eContext==self.root):
            allReferences = self.__ReadClassInstancesRawFromContexts(EReference.eClass,self.orphans.values()) #self.root is included in orphans
        else:
            allReferences = self.__ReadClassInstancesRawFromContexts(EReference.eClass,[eContext])
        compositionsForMe = [r for r in allReferences if r.containment and self.__IsSubType(eObj,r.eType)]
        return self.__EncCollection(compositionsForMe)
    
    def __IsSubType(self,eClass:EClass,eType:EClass)->bool:
        if(eClass==eType):
            return True
        elif(eType == EObject.eClass):
            return True
        else:
            return eType in eClass.eAllSuperTypes()
        
    ## PACKAGE
    def _ReadM2ModelId(self,eObj : EPackage, eContext : EObject)  -> STR:
        return InitValOrNon(eObj.nsURI,STR) #because that can also be None
    
    def _ReadM2ModelClasses(self,eObj : EPackage, eContext : EObject)  -> LST:
        mask = lambda e: EClass == type(e)
        return self.__EncCollection(eObj.eClassifiers,mask)
    
    def _ReadM2ModelEnums(self,eObj : EPackage, eContext : EObject)  -> LST:
        mask = lambda e: EEnum == type(e)
        return self.__EncCollection(eObj.eClassifiers,mask)
    
    def _ReadPackageSubpackages(self,eObj : EPackage, eContext : EObject)  -> LST:
        return self.__EncCollection(eObj.eSubpackages)
    
    ## ATTRIBUTE
    def _ReadM2AttributeType(self,eObj: EAttribute, eContext : EObject)  -> Obj or STR:
        eType = eObj.eType
        if(isinstance(eType,EEnum)):
            return self.__Enc(eType)
        elif(None == eType):
            return NON()
        else:
            return STR(EPrimitiveTypeToGenericPrimitiveType(eType))
        
    def _ReadM2AttributeMul(self,eObj: EAttribute, eContext : EObject)  -> I64:
        return I64(eObj.upperBound)
    
    def _ReadM2AttributeUnit(self,eObj : EObject,eContext : EObject) -> STR:
        return InitValOrNon(GetEAnnotation(eObj, EANNOTATION_SOURCES.UNIT, EANNOTATION_KEYS.UNIT),STR)
    
    ## ASSOCIATION
    def _ReadM2AssociationSrcName(self,eObj: EReference, eContext : EObject)  -> I64:
        if(eObj.isOpposite):
            return STR(eObj.name)
        elif(eObj.eOpposite):
            return STR(eObj.eOpposite.name)
        else:
            return NON()
        
    def _ReadM2AssociationDstName(self,eObj: EReference, eContext : EObject)  -> I64:
        if(not eObj.isOpposite):
            return STR(eObj.name)
        else:
            return STR(eObj.eOpposite.name)
        
    def _ReadM2AssociationSrcSafeName(self,eObj: EReference, eContext : EObject)  -> I64:
        if(eObj.isOpposite):
            return self._ReadFeatureSafeName(eObj, eContext)
        elif(eObj.eOpposite):
            return self._ReadFeatureSafeName(eObj.eOpposite, eContext)
        else:
            return NON()
        
    def _ReadM2AssociationDstSafeName(self,eObj: EReference, eContext : EObject)  -> I64:
        if(not eObj.isOpposite):
            return self._ReadFeatureSafeName(eObj, eContext)
        else:
            return self._ReadFeatureSafeName(eObj.eOpposite, eContext)
    
    def _ReadM2AssociationSrcClass(self,eObj: EReference, eContext : EObject)  -> Obj:
        if(eObj.isOpposite):
            return self.__Enc(eObj.eType)
        elif(eObj.eOpposite):
            return self.__Enc(eObj.eOpposite.eType)
        else:
            return NON()
    
    def _ReadM2AssociationDstClass(self,eObj: EReference, eContext : EObject)  -> Obj:
        eType = None
        if(not eObj.isOpposite):
            eType = eObj.eType
        elif(eObj.eOpposite):
            eType = eObj.eOpposite.eType
        else:
            eType = NON()
        return self.__Enc(eType)
        
    def _ReadM2AssociationSrcMul(self,eObj: EReference, eContext : EObject)  -> I64:
        if(eObj.isOpposite):
            return I64(eObj.upperBound)
        elif(eObj.eOpposite):
            return I64(eObj.eOpposite.upperBound)
        else:
            return NON()
        
    def _ReadM2AssociationDstMul(self,eObj: EReference, eContext : EObject)  -> I64:
        if(not eObj.isOpposite):
            return I64(eObj.upperBound)
        else:
            return I64(eObj.eOpposite.upperBound)    
        
        
    ## COMPOSITION
    def _ReadM2CompositionDstClass(self,eObj: EReference, eContext : EObject)  -> Obj:
        eType = eObj.eType
        return self.__Enc(eType)
        
    def _ReadM2CompositionDstMul(self,eObj: EReference, eContext : EObject)  -> I64:
        return I64(eObj.upperBound)
        
    ## ENUM
    def _ReadM2EnumOptions(self,eObj: EEnum, eContext : EObject)  -> LST:
        return self.__EncCollection(eObj.eLiterals)

    ## ENUMOPTION
    def _ReadM2EnumOptionValue(self,eObj : EEnumLiteral,eContext : EObject) -> I64:
        return I64(eObj.value)
    
    ### END READ HANDLERS ###
    
    ### BEGIN UPDATE HANDLERS ###
    
    def _UpdateAnyName(self,eObj : EObject,value : STR, ePosition : int) -> (STR,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, STR, GENERIC_ASSOCIATION_FEATURES.SRCNAME, True)
        oldValue = InitValOrNon(eObj.name,STR)
        self.__UpdateSingleValueEFeatureValidatePosition(ePosition,oldValue,eValue)
        #check uniqueness of new name
        [eParent,composition,ePosition] = self.__ReadElementParentRaw(eObj,None)
        if(eValue and eParent and composition.many):
            self.__ValidateValueUniqueness(eValue,eParent.eGet(composition.name),'name',eObj)
        #set new value
        eObj.name = eValue
        return (oldValue,NON(),NON(),NON())
        
    ## ELEMENT
    def _UpdateElementDocumentation(self,eObj : EObject,value : STR, ePosition : int) -> (STR,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, STR, GENERIC_ELEMENT_FEATURES.DOCUMENTATION, True)
        oldEValue = UpdateSingleValueEAnnotation(eObj, EANNOTATION_SOURCES.DOCUMENTATION, EANNOTATION_KEYS.DOCUMENTATION,eValue, self.__RegisterNewEAnnotation)
        oldValue = InitValOrNon(oldEValue,STR)
        return (oldValue,NON(),NON(),NON())
    
    def _UpdateElementConstraints(self,eObj : EObject,value : STR, ePosition : int) -> (STR,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, STR, GENERIC_ELEMENT_FEATURES.DOCUMENTATION, True)
        oldEValue = UpdateMultiValueEAnnotation(eObj, EANNOTATION_SOURCES.CONSTRAINTS, eValue, ePosition, self.__RegisterNewEAnnotation)
        oldValue = InitValOrNon(oldEValue,STR)
        return (oldValue,NON(),NON(),NON())
    
    def _UpdateElementOwner(self,eObj : EObject,value : STR, ePosition : int) -> (STR,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, STR, GENERIC_ELEMENT_FEATURES.OWNER, True)
        oldEValue = UpdateSingleValueEAnnotation(eObj, EANNOTATION_SOURCES.OWNER, EANNOTATION_KEYS.OWNER, eValue,self.__RegisterNewEAnnotation)
        oldValue = InitValOrNon(oldEValue,STR)
        return (oldValue,NON(),NON(),NON())
    
    def _UpdateElementGroup(self,eObj : EObject,value : STR, ePosition : int) -> (STR,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, STR, GENERIC_ELEMENT_FEATURES.GROUP, True)
        oldEValue = UpdateSingleValueEAnnotation(eObj, EANNOTATION_SOURCES.GROUP, EANNOTATION_KEYS.GROUP, eValue,self.__RegisterNewEAnnotation)
        oldValue = InitValOrNon(oldEValue,STR)
        return (oldValue,NON(),NON(),NON())
    
    def _UpdateElementPermissions(self,eObj : EObject,value : STR, ePosition : int) -> (STR,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, STR, GENERIC_ELEMENT_FEATURES.PERMISSIONS, True)
        oldEValue = UpdateMultiValueEAnnotation(eObj, EANNOTATION_SOURCES.PERMISSIONS, eValue, ePosition, self.__RegisterNewEAnnotation)
        oldValue = InitValOrNon(oldEValue,STR)
        return (oldValue,NON(),NON(),NON())
    
    ## CLASS
    def _UpdateClassName(self,eObj : EClass,value : STR, ePosition : int) -> (STR,NON,NON,NON):
        (oldValue,oldOwner,oldComposition,oldPosition) = self._UpdateAnyName(eObj,value,ePosition)
        self.__UpdateClassNameCache(eObj,oldValue.GetVal())
        return (oldValue,oldOwner,oldComposition,oldPosition)
    
    
    def _UpdateClassAttributes(self,eObj : EClass,value : Obj, ePosition : int) -> (Obj,Obj,Obj,I64):
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EAttribute,GENERIC_CLASS_FEATURES.ASSOCIATIONS,True)
        (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
        mask = lambda e: EAttribute == type(e)
        oldEValue = self.__UpdateMultiValueEFeature(eObj,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,ePosition,eValue,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.ATTRIBUTE,mask)
        oldValue = self.__Enc(oldEValue)
        return (oldValue,oldOwner,oldComposition,oldPosition)
    
    def _UpdateClassAssociations(self,eObj : EClass,value : Obj, ePosition : int) -> (Obj,Obj,Obj,I64):
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EAssociation,GENERIC_CLASS_FEATURES.ASSOCIATIONS,True)
        (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
        mask = lambda e: EAssociation == type(e)# and not e.containment
        oldEValue = self.__UpdateMultiValueEFeature(eObj,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,ePosition,eValue,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.ASSOCIATION,mask)
        oldValue = self.__Enc(oldEValue)
        return (oldValue,oldOwner,oldComposition,oldPosition)
       
    def _UpdateClassCompositions(self,eObj : EClass,value : Obj, ePosition : int) -> (Obj,Obj,Obj,I64):
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EComposition,GENERIC_CLASS_FEATURES.COMPOSITIONS,True)
        (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
        mask = lambda e: EComposition == type(e) #and e.containment
        oldEValue = self.__UpdateMultiValueEFeature(eObj,ECORE_BASE_FEATURES_ECLASS_ESTRUCTURALFEATURES,ePosition,eValue,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION,mask)
        oldValue = self.__Enc(oldEValue)
        return (oldValue,oldOwner,oldComposition,oldPosition)
  
    def _UpdateClassSupertypes(self,eObj : EClass,value : Obj, ePosition : int) -> (Obj,Obj,Obj,I64):
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EClass,GENERIC_CLASS_FEATURES.SUPERTYPES,True)
        (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
        oldEValue = self.__UpdateMultiValueEFeature(eObj,ECORE_BASE_FEATURES_ECLASS_ESUPERTYPES,ePosition,eValue,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.ASSOCIATION)
        oldValue = self.__Enc(oldEValue)
        eValue = self.__Dec(value)
        return (oldValue,oldOwner,oldComposition,oldPosition)
    
    ## PACKAGE
    
    def _UpdatePackageId(self,eObj : EPackage,value : str, ePosition : int) -> (STR,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, STR, GENERIC_PACKAGE_FEATURES.ID, True)
        if(eValue in self.packageIdCache and not eObj != self.packageIdCache[eValue]):
            raise EOQ_ERROR_INVALID_VALUE('Package names must be unique. A package with name %s does already exist'%(eValue))
        oldEValue = eObj.nsURI
        eObj.nsURI = eValue
        self.__UpdatePackagesCache(eObj, oldEValue)
        oldValue = InitValOrNon(oldEValue,STR)
        return (oldValue,NON(),NON(),NON())
    
    def _UpdatePackageClasses(self,eObj : EPackage,value : Obj, ePosition : int) -> (Obj,Obj,Obj,I64):
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EClass,GENERIC_PACKAGE_FEATURES.CLASSES,True)
        (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
        if(eValue): self.__ValidateValueUniqueness(eValue.name,eObj.eClassifiers,'name',None)
        mask = lambda e: type(e) == EClass
        oldEValue = self.__UpdateMultiValueEFeature(eObj,ECORE_BASE_FEATURES_EPACKAGE_ECLASSIFIERS,ePosition,eValue,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION,mask)
        oldValue = self.__Enc(oldEValue)
        return (oldValue,oldOwner,oldComposition,oldPosition)
        
    def _UpdatePackageEnums(self,eObj : EPackage,value : Obj, ePosition : int) -> (Obj,Obj,Obj,I64):
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EEnum,GENERIC_PACKAGE_FEATURES.ENUMS,True)
        (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
        mask = lambda e: type(e) == EEnum
        oldEValue = self.__UpdateMultiValueEFeature(eObj,ECORE_BASE_FEATURES_EPACKAGE_ECLASSIFIERS,ePosition,eValue,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION,mask)
        oldValue = self.__Enc(oldEValue)
        return (oldValue,oldOwner,oldComposition,oldPosition)
        
    def _UpdatePackageSubpackages(self,eObj : EPackage,value : Obj, ePosition : int) -> (Obj,Obj,Obj,I64):
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EPackage,GENERIC_PACKAGE_FEATURES.SUBPACKAGES,True)
        (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
        oldEValue = self.__UpdateMultiValueEFeature(eObj,ECORE_BASE_FEATURES_EPACKAGE_ESUBPACKAGES,ePosition,eValue,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        oldValue = self.__Enc(oldEValue)
        return (oldValue,oldOwner,oldComposition,oldPosition)
    
    ## ATTRIBUTE
    def _UpdateAttributeType(self,eObj : EAttribute,value : STR or Obj, ePosition : int) -> (STR or Obj,NON,NON,NON):
        if(isinstance(value,STR)):
            eValue = value.GetVal()
            oldEValue = self.__UpdateSingleValueEFeature(eObj, ECORE_BASE_FEATURES_ESTRUCTURALFEATURE_ETYPE, ePosition, GenericPrimitiveTypeToEPrimitiveType(eValue), EFEATURE_TYPES.ASSOCIATION)
            oldValue = InitValOrNon(EPrimitiveTypeToGenericPrimitiveType(oldEValue),STR)
            return (oldValue,NON(),NON(),NON())
        elif(isinstance(value,Obj)):
            eValue = self.__Dec(value)
            self.__ValidateType(eValue,EEnum,GENERIC_ATTRIBUTE_FEATURES.TYPE)
            #(oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue) # not needed because the enum is not owned by 
            oldEValue = self.__UpdateSingleValueEFeature(eObj, ECORE_BASE_FEATURES_ESTRUCTURALFEATURE_ETYPE, ePosition, eValue, EFEATURE_TYPES.ASSOCIATION)
            oldValue = self.__Enc(eValue) 
            return (oldValue,NON(),NON(),NON())
        else:
            raise EOQ_ERROR_INVALID_TYPE('Attribute type must be STR or Obj but got %s.'%(type(value).__name__))
        
    
    def _UpdateAttributeLen(self,eObj : EAttribute,value : I64, ePosition : int) -> (I64,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, I64, GENERIC_ATTRIBUTE_FEATURES.MUL)
        oldValue = InitValOrNon(eObj.upperBound,I64)
        eObj.upperBound = eValue
        return (oldValue,NON(),NON(),NON())
    
    def _UpdateAttributeUnit(self,eObj : EObject,value : STR, ePosition : int) -> (STR,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, STR, GENERIC_ATTRIBUTE_FEATURES.UNIT, True)
        oldEValue = UpdateSingleValueEAnnotation(eObj, EANNOTATION_SOURCES.UNIT, EANNOTATION_KEYS.UNIT,eValue,self.__RegisterNewEAnnotation)
        oldValue = InitValOrNon(oldEValue,STR)
        return (oldValue,NON(),NON(),NON())
    
    ## ASSOCIATION
    def _UpdateAssociationSrcName(self,eObj : EReference,value : Obj, ePosition : int) -> (Obj,NON,NON,NON):
        if(eObj.isOpposite):
            return self._UpdateAnyName(eObj, value, ePosition)
        else:
            return self._UpdateAnyName(eObj.eOpposite, value, ePosition)
        
    def _UpdateAssociationDstName(self,eObj : EReference,value : Obj, ePosition : int) -> (Obj,NON,NON,NON):
        if(not eObj.isOpposite):
            return self._UpdateAnyName(eObj, value, ePosition)
        else:
            return self._UpdateAnyName(eObj.eOpposite, value, ePosition)
    
    
    def _UpdateAssociationType(self,eObj : EReference,value : Obj, ePosition : int, featureName : str) -> (Obj,NON,NON,NON):
        ValidateVal(value,[Obj,NON],featureName)
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EClass,featureName,True)
        oldEValue = self.__UpdateSingleValueEFeature(eObj, ECORE_BASE_FEATURES_ESTRUCTURALFEATURE_ETYPE, ePosition, eValue, EFEATURE_TYPES.ASSOCIATION)
        oldValue = self.__Enc(oldEValue)
        return (oldValue,NON(),NON(),NON())
    
    def _UpdateAssociationSrcType(self,eObj : EReference,value : Obj, ePosition : int) -> (Obj,NON,NON,NON):
        if(eObj.isOpposite):
            return self._UpdateAssociationType(eObj, value, ePosition, GENERIC_ASSOCIATION_FEATURES.SRCTYPE)
        else:
            return self._UpdateAssociationType(eObj, value, ePosition, GENERIC_ASSOCIATION_FEATURES.SRCTYPE)
        
    def _UpdateAssociationDstType(self,eObj : EReference,value : Obj, ePosition : int) -> (Obj,NON,NON,NON):
        if(not eObj.isOpposite):
            return self._UpdateAssociationType(eObj, value, ePosition, GENERIC_ASSOCIATION_FEATURES.DSTTYPE)
        else:
            return self._UpdateAssociationType(eObj, value, ePosition, GENERIC_ASSOCIATION_FEATURES.DSTTYPE)
    
    def _UpdateAssociationMul(self,eObj : EReference,value : I64, ePosition : int, featureName : str) -> (I64,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, I64,featureName)
        oldValue = InitValOrNon(eObj.upperBound,I64)
        eObj.upperBound = eValue
        return (oldValue,NON(),NON(),NON())
    
    def _UpdateAssociationSrcMul(self,eObj : EReference,value : Obj, ePosition : int) -> (Obj,NON,NON,NON):
        if(eObj.isOpposite):
            return self._UpdateAssociationMul(eObj, value, ePosition, GENERIC_ASSOCIATION_FEATURES.SRCMUL)
        else:
            return self._UpdateAssociationMul(eObj.eOpposite, value, ePosition, GENERIC_ASSOCIATION_FEATURES.SRCMUL)
    
    def _UpdateAssociationDstMul(self,eObj : EReference,value : Obj, ePosition : int) -> (Obj,NON,NON,NON):
        if(not eObj.isOpposite):
            return self._UpdateAssociationMul(eObj, value, ePosition, GENERIC_ASSOCIATION_FEATURES.DSTMUL)
        else:
            return self._UpdateAssociationMul(eObj.eOpposite, value, ePosition, GENERIC_ASSOCIATION_FEATURES.DSTMUL)


    ## COMPOSITION
    def _UpdateCompositionType(self,eObj : EReference,value : Obj, ePosition : int) -> (Obj,NON,NON,NON):
        ValidateVal(value,[Obj,NON],"value")
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EClass,GENERIC_COMPOSITION_FEATURES.TYPE,True)
        oldEValue = self.__UpdateSingleValueEFeature(eObj, ECORE_BASE_FEATURES_ESTRUCTURALFEATURE_ETYPE, ePosition, eValue, EFEATURE_TYPES.ASSOCIATION)
        oldValue = self.__Enc(oldEValue)
        return (oldValue,NON(),NON(),NON())
        
    def _UpdateCompositionLen(self,eObj : EReference,value : I64, ePosition : int) -> (I64,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, I64, GENERIC_COMPOSITION_FEATURES.MUL)
        oldValue = InitValOrNon(eObj.upperBound,I64)
        eObj.upperBound = eValue
        return (oldValue,NON(),NON(),NON())
    
    
    ## ENUM
    def _UpdateEnumOptions(self,eObj : EEnum,value : Obj, ePosition : int) -> (Obj,Obj,Obj,I64):
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EEnumLiteral,GENERIC_ENUM_FEATURES.OPTIONS,True)
        (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
        oldEValue = self.__UpdateMultiValueEFeature(eObj,ECORE_BASE_FEATURES_EENUM_ELITERALS,ePosition,eValue,ECORE_FEATURE_MAX_LEN,EFEATURE_TYPES.COMPOSITION)
        oldValue = self.__Enc(oldEValue)
        return (oldValue,oldOwner,oldComposition,oldPosition)
    
    ## ENUMOPTION
    def _UpdateEnumoptionValue(self,eObj : EEnumLiteral,value : U64, ePosition : int) -> (I64,NON,NON,NON):
        eValue = self.__ValidateValueTypeAndGet(value, U64, GENERIC_ENUMOPTION_FEATURES.VALUE)
        oldValue = InitValOrNon(eObj.value,U64)
        eObj.value = eValue
        return (oldValue,NON(),NON(),NON())
    

    ## ROOT
    def _UpdateRootRoot(self,eObj : EObject,value : Obj, ePosition : int) -> (Obj,Obj,Obj,I64):
        eValue = self.__Dec(value)
        self.__ValidateType(eValue,EObject,GENERIC_MDB_FEATURES.ROOT,True)
        (oldOwner,oldComposition,oldPosition) = self.__GetUpdateRecoveryInfo(eValue)
        oldValue = self.__Enc(self.root)
        self.root = eValue
        return (oldValue,oldOwner,oldComposition,oldPosition)
    
    
    ### END UPDATE HANDLERS ###
    
    ## DELETE
    # Element
    
    def _DeleteElement(self,eObj : EObject):
        #remove all children and associated elements        
        for r in eObj.eClass.eAllReferences():
            if(r.containment):
                if(r.many):
                    n = len([e for e in eObj.eGet(r)])
                    for i in range(n-1,-1,-1):
                        self.__UpdateMultiValueEFeature(eObj, r, i, None, ECORE_FEATURE_MAX_LEN, EFEATURE_TYPES.COMPOSITION)
                else:
                    self.__UpdateSingleValueEFeature(eObj, r, 0, None, EFEATURE_TYPES.COMPOSITION)
            elif(not r.eOpposite and not r.derived): #make sure no other element thinks it the deleted element is an associate
                # skip opposites since they are removed anyhow by deleting the containments or associates
                if(r.many):
                    n = len([e for e in eObj.eGet(r)])
                    for i in range(n-1,-1,-1):
                        self.__UpdateMultiValueEFeature(eObj, r, i, None, ECORE_FEATURE_MAX_LEN, EFEATURE_TYPES.ASSOCIATION)
                else:
                    self.__UpdateSingleValueEFeature(eObj, r, 0, None, EFEATURE_TYPES.ASSOCIATION)
        #handle special case and delete from cache
        if(EClass == type(eObj)):
            self.__UpdateClassNameCache(eObj, eObj.name)
        elif(EPackage == type(eObj) and eObj.nsURI):
            self.__UpdatePackagesCache(eObj, eObj.nsURI)
        elif(EAssociation == type(eObj) and None != eObj.eOpposite):
            eObj.eOpposite.delete();
        eObj.delete(True) #clean up pyecore
      
    ### PRIVATE METHODS 
    
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
        newSeg = EObjSeg(idNb,eObj)
        eObj._eoqObj = newSeg
        newObj = Obj(newSeg)
        return newObj
    
    def __EncLastTime(self,elem : Obj):
        """
        Removes a deleted element from the and removes all internal references of that objects
        Afterwards this element can not be used in the MDB any more, 
        except for a Create target
        """
        idNb = elem.v[0].v[0].GetVal()  
        eObj = self.idToObjectLUT[idNb]
        # there should be only one existing ObjSeg with a reference to the eObj
        # lets remove that.        
        eObj._eoqObj._eObj = None
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
        
    
    def __EncCollection(self,collection,mask=lambda e:True):
        ''' Encodes every element in a collection to a list of encoded values. 
        Assumes that the collection only contains EObjects.
        E.g. a list of EObjects or an eSet of EObjects.
        '''
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
        
    #inserts a value at a fixed position of an eSet. Use -1 for adding at the last position.
    def __UpdateSingleValueEFeature(self,eObj,eFeature,position,eValue,featureType):
        featureLength = 1
        eOldValue = eObj.eGet(eFeature)
        nElements = 0 if (None==eOldValue) else 1
        # determine mode and absolute position from the index
        (mode,absPos) = GetUpdateModeAndAbsPosition(nElements,position,eValue)
        # position sanity checks
        ValidateUpdatePosition(mode,nElements,featureLength,absPos)
        # set operation
        eObj.eSet(eFeature,eValue)
        if(EFEATURE_TYPES.COMPOSITION == featureType):
            if isinstance(eValue, EObject): self.__UpdateChildStateAndCache(eValue)
            if isinstance(eOldValue, EObject): self.__UpdateChildStateAndCache(eOldValue) 
        elif(EFEATURE_TYPES.ASSOCIATION == featureType):
            if isinstance(eValue, EObject): self.__AddToAssociateCache(eValue, eObj, eFeature, 0)    
            if isinstance(eOldValue, EObject): self.__RemoveFromAssociateCache(eOldValue, eObj, eFeature, 0)  
        return eOldValue

        
    #inserts a value at a fixed position of an eSet. Use -1 for adding at the last position.
    def __UpdateMultiValueEFeature(self,eObj : EObject,eFeature,position,eValue,featureLength,featureType,mask=lambda e:True):
        eSet = eObj.eGet(eFeature)
        nElements = len(eSet)
        maskedElements = [e for e in eSet if mask(e)]
        nFilteredElements = len(maskedElements)
        eOldValue = None
        
        (mode,absPos) = GetUpdateModeAndAbsPosition(nFilteredElements,position,eValue)
        
        # position sanity checks
        ValidateUpdatePosition(mode,nFilteredElements,featureLength,absPos)
        
        # catch the special case that the value is already in the feature, the feature is a containment, 
        # and its position is before the current position. In that case pyecore will not re-add or move the feature
        # so it needs to be removed before: 
        # TODO: How to improve performance here?
        try: 
            currentPosition = eSet.index(eValue)
            if(currentPosition < absPos):
                eSet.remove(eValue)
                absPos -= 1 #reduce by one since the element is now missing
        except KeyError:
            pass
#         except ValueError:
#             raise EOQ_ERROR_UNSUPPORTED("Trying to write a read-only feature") #some instances of eSet used in pyecore seem to return a ValueError instead of a KeyError
        
        # regular update operation starts here    
        if(nFilteredElements == absPos): 
            eSet.add(eValue)
            if(EFEATURE_TYPES.COMPOSITION == featureType):
                self.__UpdateChildStateAndCache(eValue)
            elif(EFEATURE_TYPES.ASSOCIATION == featureType):
                self.__AddToAssociateCache(eValue, eObj, eFeature, nElements)  
        else: #it is not the last element that is added
            elementToInsertBefore = maskedElements[absPos]
            successors = self.__InsertReplaceOrRemoveInESet(eSet, elementToInsertBefore, mode, eValue)
            if(UPDATE_MODES.REPLACE == mode or UPDATE_MODES.REMOVE == mode):
                eOldValue = successors[len(successors)-1] #last element
            else:
                eOldValue = None #no old value in case of insert, because the old ones are persistent
            if(EFEATURE_TYPES.COMPOSITION == featureType):
                if(UPDATE_MODES.REPLACE == mode):
                    self.__UpdateChildStateAndCache(eValue) 
                    self.__UpdateChildStateAndCache(eOldValue)
                elif(UPDATE_MODES.REMOVE == mode):
                    self.__UpdateChildStateAndCache(eOldValue)
            elif(EFEATURE_TYPES.ASSOCIATION == featureType):
                posWithoutFilter = nElements-len(successors)
                if(UPDATE_MODES.INSERT == mode or UPDATE_MODES.REPLACE == mode):
                    self.__AddToAssociateCache(eValue, eObj, eFeature, posWithoutFilter)
                elif(UPDATE_MODES.REMOVE == mode):
                    self.__RemoveFromAssociateCache(eOldValue, eObj, eFeature, posWithoutFilter) #old position
                #also update the associates position of all elements after the new or removed one
                j = 0 #positive counting
                if(UPDATE_MODES.INSERT == mode):
                    for i in range(len(successors)-2,-1,-1):
                        self.__RemoveFromAssociateCache(successors[i], eObj, eFeature, posWithoutFilter+j) #old position
                        self.__AddToAssociateCache(successors[i], eObj, eFeature, posWithoutFilter+j+1) #new position  
                        j += 1
                elif(UPDATE_MODES.REMOVE == mode):
                    for i in range(len(successors)-2,-1,-1):
                        self.__RemoveFromAssociateCache(successors[i], eObj, eFeature, posWithoutFilter+j+1) #old position
                        self.__AddToAssociateCache(successors[i], eObj, eFeature, posWithoutFilter+j) #new position  
                        j += 1
        return eOldValue
    
    def __UpdateSingleValueEFeatureValidatePosition(self,position,oldValue,eValue):
        featureLength = 1
        nElements = 0 if (oldValue==None) else 1
        (mode,absPos) = GetUpdateModeAndAbsPosition(nElements,position,eValue)
        ValidateUpdatePosition(mode,nElements,featureLength,position)
          
    def __InsertReplaceOrRemoveInESet(self,eSet,targetElement,mode,value):
        #find all elements passing the mask after the element desired    
        sucessors = []
        n = len(eSet)
        elements = [e for e in eSet]
        for i in range(n-1,-1,-1):
            succesor = elements[i]
            sucessors.append(succesor)
            if succesor == targetElement:
                break
        #EOrderedSets can not be inserted at any position, so remove all elements after the desired position first ...
        for s in sucessors:
            eSet.remove(s)
        #... then eventually (replace or insert) add a new element ...
        if (mode == UPDATE_MODES.REPLACE or 
            mode == UPDATE_MODES.INSERT):
            eSet.add(value)
        #... and finally re-add the successors, either all (insert) or one less (remove, replace)
        sucessorReaddStart = len(sucessors)-1 
        if (mode == UPDATE_MODES.REPLACE or 
            mode == UPDATE_MODES.REMOVE):
            sucessorReaddStart = len(sucessors)-2     
        for i in range(sucessorReaddStart,-1,-1):
            eSet.add(sucessors[i])     
        return sucessors
    
    def __UpdateChildStateAndCache(self,eObj):
        '''Updates the orphans variable as well as all internal caches that are related to the child state of the object''' 
        eAnchestors = self.__GetEAnchastors(eObj)
        eParent = eObj.eContainer()
        eOldParent = eObj._eoqOldParent
        #Update the orphans array if the object has no parent any more
        if(None == eParent and not eObj in self.orphans):
            self.orphans[eObj] = eObj
        elif(None != eParent ): 
            if None == eOldParent: #eObj in self.orphans: #only update the orphans, if the old parent is None, i.e. this was an orphan before
                self.orphans.pop(eObj)
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
        '''Enables the caching of associates, typed children and more by adding internal variables to the eObjects'''
        eObj._eoqAssociatesCache = {}
        eObj._eoqChildrenByClassCache = {}
        eObj._eoqOldParent = None # safe the old parent for a short moment after an update operation
        
    def __GetEAnchastors(self,eObj):
        '''Returns all parents in a row
        '''
        eAnchestors = []
        eParent = eObj.eContainer()
        while None != eParent:
            eAnchestors.append(eParent)
            eParent = eParent.eContainer()
        return eAnchestors
        
    def __AddToAssociateCache(self, eObj:EObject, eAssociate:EObject, eFeature:EAssociation, position:int):
        key = (eAssociate,eFeature)
        fName = self._ReadFeatureSafeNameRaw(eFeature,None)
        eObj._eoqAssociatesCache[key] = [eAssociate,eFeature,position,fName]
        #do not forget to update the opposite cache
        eOpposite = eFeature.eOpposite
        if(eOpposite):
            opPosition = 0
            if(eOpposite.many):
                opPosition = eObj.eGet(eOpposite).index(eAssociate)
            opKey = (eObj,eOpposite)
            opFName = self._ReadFeatureSafeNameRaw(eOpposite,None)
            eAssociate._eoqAssociatesCache[opKey] = [eObj,eOpposite,opPosition,opFName]
        
    def __RemoveFromAssociateCache(self, eObj:EObject, eAssociate:EObject, eFeature:EAssociation, position:int):
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
                    opKey = (eObj,eOpposite)
                    s._eoqAssociatesCache[opKey][2] = i
                    i += 1

            
            
    def __UpdateClassNameCache(self,eClass,oldName=None):
        if(eClass and eClass.name):
            # names cache
            namesChacheEntry = {}
            if(eClass.name in self.classNamesCache):
                namesChacheEntry = self.classNamesCache[eClass.name]
            else:
                self.classNamesCache[eClass.name] = namesChacheEntry
            namesChacheEntry[eClass] = eClass
            
        if(oldName):
            if (oldName in self.classNamesCache) and (eClass in self.classNamesCache[oldName]):
                oldCacheEntry = self.classNamesCache[oldName]
                del oldCacheEntry[eClass]
                if(0 == len(oldCacheEntry)):
                    del self.classNamesCache[oldName]
                
    def __UpdatePackagesCache(self,ePackage,oldId=None):
        if(ePackage and ePackage.nsURI):
            self.packageIdCache[ePackage.nsURI] = ePackage
        if(oldId):
            if(oldId in self.packageIdCache):
                del self.packageIdCache[oldId]
                         
    def __GetGenericFeatureHandler(self,eObj,featureName,handlerTable):
        #ROOT
        unsupportedFeatureErrorMsg = 'Generic feature %s is not supported for %s'
        if(self == eObj):
            try: return handlerTable[GENERIC_ELEMENTS.MDB][featureName] 
            except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.MDB))
        else:
            try: 
                #@ELEMENT
                return handlerTable[GENERIC_ELEMENTS.ELEMENT][featureName]
            except KeyError: #no handler for EObjects matches or is registered
                eType = type(eObj)
                #CLASS
                if(EClass == eType): 
                    try: return handlerTable[GENERIC_ELEMENTS.CLASS][featureName]
                    except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.CLASS))
                #PACKAGE
                elif(EPackage == eType): 
                    try: return handlerTable[GENERIC_ELEMENTS.M2MODEL][featureName]
                    except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.M2MODEL))
                #Attribute
                elif(EAttribute == eType): 
                    try: return handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][featureName]
                    except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.ATTRIBUTE))
                #ASSOCIATION
                elif(EAssociation == eType): 
                    try: return handlerTable[GENERIC_ELEMENTS.ASSOCIATION][featureName]
                    except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.ASSOCIATION))
                #COMPOSITION
                elif(EComposition == eType): 
                    try: return handlerTable[GENERIC_ELEMENTS.COMPOSITION][featureName]
                    except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.COMPOSITION))
                #ENUM
                elif(EEnum == eType):
                    try: return handlerTable[GENERIC_ELEMENTS.ENUM][featureName]
                    except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.ENUM))
                #ENUMOPTION
                elif(EEnumLiteral == eType): 
                    try: return handlerTable[GENERIC_ELEMENTS.ENUMOPTION][featureName]
                    except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.ENUMOPTION))
                #ASSOCIATION (legacy support for references used in ecore internally)
                elif(EReference == eType and not eObj.containment): 
                    try: return handlerTable[GENERIC_ELEMENTS.ASSOCIATION][featureName]
                    except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.ASSOCIATION))
                #COMPOSITION (legacy support for references used in ecore internally)
                elif(EReference == eType and eObj.containment): 
                    try: return handlerTable[GENERIC_ELEMENTS.COMPOSITION][featureName]
                    except KeyError: raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.COMPOSITION))
        #if we get here no known generic feature matches 
        raise EOQ_ERROR_DOES_NOT_EXIST(unsupportedFeatureErrorMsg%(featureName,GENERIC_ELEMENTS.ELEMENT))
    
    def __RegisterBaseElements(self)->None:
        '''Assignes IDs to all generic elements as well a to elements from the ecore meta model
        
        '''
        self.rootObj = self.__EncFirstTime(self,Obj(GENERIC_ELEMENTS.MDB))
        #self.baseElements[self.__EncFirstTime(self,Obj(GENERIC_ELEMENTS.MDB))] = self
        #Encode ECORE meta model
        self.baseElements[self.__EncFirstTime(ECORE_PACKAGE)] = ECORE_PACKAGE #the ecore package
        #encode classes
        self.baseElements[self.__EncFirstTime(EObject.eClass,Obj(GENERIC_ELEMENTS.ELEMENT))] = EObject.eClass
        self.baseElements[self.__EncFirstTime(EPackage.eClass,Obj(GENERIC_ELEMENTS.M2MODEL))] = EPackage.eClass
        self.baseElements[self.__EncFirstTime(EClass.eClass,Obj(GENERIC_ELEMENTS.CLASS))] = EClass.eClass
        self.baseElements[self.__EncFirstTime(EAttribute.eClass,Obj(GENERIC_ELEMENTS.ATTRIBUTE))] = EAttribute.eClass
        self.baseElements[self.__EncFirstTime(EAssociation.eClass,Obj(GENERIC_ELEMENTS.ASSOCIATION))] = EAssociation.eClass
        self.baseElements[self.__EncFirstTime(EComposition.eClass,Obj(GENERIC_ELEMENTS.COMPOSITION))] = EComposition.eClass
        self.baseElements[self.__EncFirstTime(EEnum.eClass,Obj(GENERIC_ELEMENTS.ENUM))] = EEnum.eClass
        self.baseElements[self.__EncFirstTime(EEnumLiteral.eClass,Obj(GENERIC_ELEMENTS.ENUMOPTION))] = EEnumLiteral.eClass
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
        self.__InitCaching(EAssociation.eClass)
        self.__InitCaching(EComposition.eClass)
        self.__InitCaching(EBoolean)
        self.__InitCaching(EInt)
        self.__InitCaching(ELong)
        self.__InitCaching(EFloat)
        self.__InitCaching(EDouble)
        self.__InitCaching(EString)
        self.__InitCaching(EDate)
        #class caches
        self.classNamesCache = {} #class name vs. class implementation
        self.classNamesCache[GENERIC_ELEMENTS.ELEMENT] = {EObject.eClass : EObject.eClass}
        self.classNamesCache['EObject'] = {EObject.eClass : EObject.eClass}
        self.classNamesCache[GENERIC_ELEMENTS.M2MODEL] = {EPackage.eClass : EPackage.eClass}
        self.classNamesCache['EPackage'] = {EPackage.eClass : EPackage.eClass}
        self.classNamesCache[GENERIC_ELEMENTS.CLASS] = {EClass.eClass : EClass.eClass}
        self.classNamesCache['EClass'] = {EClass.eClass : EClass.eClass}
        self.classNamesCache[GENERIC_ELEMENTS.ENUM] = {EEnum.eClass : EEnum.eClass}
        self.classNamesCache['EEnum'] = {EEnum.eClass : EEnum.eClass}
        self.classNamesCache[GENERIC_ELEMENTS.ENUMOPTION] = {EEnumLiteral.eClass : EEnumLiteral.eClass}
        self.classNamesCache['EEnumLiteral'] = {EEnumLiteral.eClass : EEnumLiteral.eClass}
        self.classNamesCache[GENERIC_ELEMENTS.ATTRIBUTE] = {EAttribute.eClass : EAttribute.eClass}
        self.classNamesCache['EAttribute'] = {EAttribute.eClass : EAttribute.eClass}
        self.classNamesCache[GENERIC_ELEMENTS.ASSOCIATION] = {EAssociation.eClass : EAssociation.eClass}
        self.classNamesCache[GENERIC_ELEMENTS.COMPOSITION] = {EComposition.eClass : EComposition.eClass}
        self.packageIdCache = {}
        self.packageIdCache[ECORE_PACKAGE.nsURI] = ECORE_PACKAGE
        
    def __InitArtificialFeatures(self):
        '''Create floating features for those generics not directly supported by pyecore
        such that they are visible as normal features from the outside.
        '''
        #create an EStructuralFeature for each unsupported element. This is not attached to the class
        self.artificialFeatures[GENERIC_ELEMENT_FEATURES.DOCUMENTATION] = self.__CreateAndEncodeArtificialAttribute(GENERIC_ELEMENT_FEATURES.DOCUMENTATION)
        self.artificialFeatures[GENERIC_ELEMENT_FEATURES.CONSTRAINTS] = self.__CreateAndEncodeArtificialAttribute(GENERIC_ELEMENT_FEATURES.CONSTRAINTS)
        self.artificialFeatures[GENERIC_ELEMENT_FEATURES.OWNER] = self.__CreateAndEncodeArtificialAttribute(GENERIC_ELEMENT_FEATURES.OWNER)
        self.artificialFeatures[GENERIC_ELEMENT_FEATURES.GROUP] = self.__CreateAndEncodeArtificialAttribute(GENERIC_ELEMENT_FEATURES.GROUP)
        self.artificialFeatures[GENERIC_ELEMENT_FEATURES.PERMISSIONS] = self.__CreateAndEncodeArtificialAttribute(GENERIC_ELEMENT_FEATURES.PERMISSIONS)
        self.artificialFeatures[GENERIC_ATTRIBUTE_FEATURES.UNIT] = self.__CreateAndEncodeArtificialAttribute(GENERIC_ATTRIBUTE_FEATURES.UNIT)
        #register the new features as base elements to prevent modifications
        for v in self.artificialFeatures.values():
            self.baseElements[v[0]] = v[1]
        #build a lookup table for which feature belongs to which element
        self.artificialAttributesLut[EObject.eClass]    = [self.artificialFeatures[GENERIC_ELEMENT_FEATURES.DOCUMENTATION][0], 
                                                           self.artificialFeatures[GENERIC_ELEMENT_FEATURES.CONSTRAINTS][0],
                                                           self.artificialFeatures[GENERIC_ELEMENT_FEATURES.OWNER][0],
                                                           self.artificialFeatures[GENERIC_ELEMENT_FEATURES.GROUP][0],
                                                           self.artificialFeatures[GENERIC_ELEMENT_FEATURES.PERMISSIONS][0] ]
        self.artificialAttributesLut[EAttribute.eClass] = [self.artificialFeatures[GENERIC_ATTRIBUTE_FEATURES.UNIT][0]]
    
    def __GetAllArtificialAttributesForEClass(self, eClass:EClass)->list:
        artificialAttributes = []
        for k,v in self.artificialAttributesLut.items():
            if(isinstance(eClass,k)):
            #if( (eClass == k) or (k in eClass.eAllSuperTypes()) ):
                artificialAttributes += v
        return artificialAttributes
        
    def __CreateAndEncodeArtificialAttribute(self,featureName:str)->(Obj,EAttribute):
        upper = -1 if IsMultivalueFeature(featureName) else 1
        #normalizedFeatureName = NormalizeFeatureName(featureName)
        eAttribute = EAttribute(name=featureName, eType=EString, upper=upper)
        attribute = self.__EncFirstTime(eAttribute)
        return (attribute,eAttribute)
        
    
    def __InitGenericCreateHandlerTable(self):
        handlerTable = {}
        handlerTable[GENERIC_ELEMENTS.M2MODEL] = self._CreatePackage
        handlerTable[GENERIC_ELEMENTS.CLASS] = self._CreateClass
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE] = self._CreateAttribute
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION] = self._CreateAssociation
        handlerTable[GENERIC_ELEMENTS.COMPOSITION] = self._CreateComposition
        handlerTable[GENERIC_ELEMENTS.INHERITANCE] = self._CreateInheritance
        handlerTable[GENERIC_ELEMENTS.CONSTRAINT] = self._CreateConstraint
        handlerTable[GENERIC_ELEMENTS.ENUM] = self._CreateEnum
        handlerTable[GENERIC_ELEMENTS.ENUMOPTION] = self._CreateEnumoption
        handlerTable[GENERIC_ELEMENTS.M1MODEL] = self._CreateM1Model
        return handlerTable
    
    def __InitGenericReadHandlerTable(self):
        handlerTable = {}
        handlerTable[GENERIC_ELEMENTS.ELEMENT] = {}
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.CLASS]             = self._ReadElementClass
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.PARENT]            = self._ReadElementParent
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.ASSOCIATES]        = self._ReadElementAssociates
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.DOCUMENTATION]     = self._ReadElementDocumentation
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.CONSTRAINTS]       = self._ReadElementConstraints
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.OWNER]             = self._ReadElementOwner
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.GROUP]             = self._ReadElementGroup
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.PERMISSIONS]       = self._ReadElementPermissions
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.CHILDREN]          = self._ReadElementChildren
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.ALLCHILDREN]       = self._ReadElementAllChildren
        handlerTable[GENERIC_ELEMENTS.CLASS] = {}
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ID]                    = self._ReadClassId
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.NAME]                  = self._ReadAnyName
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ATTRIBUTES]            = self._ReadClassAttributes
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ALLATTRIBUTES]         = self._ReadClassAllAttributes
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ASSOCIATIONS]          = self._ReadClassAssociations
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ALLASSOCIATIONS]       = self._ReadClassAllAssociations
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.COMPOSITIONS]          = self._ReadClassCompositions
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ALLCOMPOSITIONS]       = self._ReadClassAllCompositions
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.SUPERTYPES]            = self._ReadClassSupertypes
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ALLSUPERTYPES]         = self._ReadClassAllSupertypes
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.SUBTYPES]              = self._ReadClassSubtypes
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ALLSUBTYPES]           = self._ReadClassAllSubtypes
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.INSTANCES]             = self._ReadClassInstances
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.INCARNATIONS]          = self._ReadClassIncarnations
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ASSOCIATIONSFORME]     = self._ReadClassAssociationsForMe
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.COMPOSITIONSFORME]     = self._ReadClassCompositionsForMe
        handlerTable[GENERIC_ELEMENTS.M2MODEL] = {}
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.NAME]              = self._ReadAnyName
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.ID]                = self._ReadPackageId
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.CLASSES]           = self._ReadPackageClasses
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.ENUMS]             = self._ReadPackageEnums
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.SUBPACKAGES]       = self._ReadPackageSubpackages
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE] = {}
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][GENERIC_ATTRIBUTE_FEATURES.NAME]          = self._ReadAnyName
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][GENERIC_ATTRIBUTE_FEATURES.SNAME]         = self._ReadFeatureSafeName
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][GENERIC_ATTRIBUTE_FEATURES.TYPE]          = self._ReadAttributeType
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][GENERIC_ATTRIBUTE_FEATURES.MUL]           = self._ReadAttributeLen
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][GENERIC_ATTRIBUTE_FEATURES.UNIT]          = self._ReadAttributeUnit
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION] = {}                                   
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.SRCNAME]      = self._ReadAssociationSrcName
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.SRCSNAME]     = self._ReadAssociationSrcSafeName
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.SRCTYPE]      = self._ReadAssociationSrcType
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.SRCMUL]       = self._ReadAssociationSrcMul
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.DSTNAME]      = self._ReadAssociationDstName
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.DSTSNAME]     = self._ReadAssociationDstSafeName
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.DSTTYPE]      = self._ReadAssociationDstType
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.DSTMUL]       = self._ReadAssociationDstMul
        handlerTable[GENERIC_ELEMENTS.COMPOSITION] = {}                                  
        handlerTable[GENERIC_ELEMENTS.COMPOSITION][GENERIC_COMPOSITION_FEATURES.NAME]      = self._ReadAnyName
        handlerTable[GENERIC_ELEMENTS.COMPOSITION][GENERIC_COMPOSITION_FEATURES.SNAME]     = self._ReadFeatureSafeName
        handlerTable[GENERIC_ELEMENTS.COMPOSITION][GENERIC_COMPOSITION_FEATURES.TYPE]      = self._ReadCompositionType
        handlerTable[GENERIC_ELEMENTS.COMPOSITION][GENERIC_COMPOSITION_FEATURES.MUL]       = self._ReadCompositionLen
        handlerTable[GENERIC_ELEMENTS.ENUM] = {}
        handlerTable[GENERIC_ELEMENTS.ENUM][GENERIC_ENUM_FEATURES.NAME]                    = self._ReadAnyName
        handlerTable[GENERIC_ELEMENTS.ENUM][GENERIC_ENUM_FEATURES.OPTIONS]                 = self._ReadEnumOptions
        handlerTable[GENERIC_ELEMENTS.ENUMOPTION] = {}
        handlerTable[GENERIC_ELEMENTS.ENUMOPTION][GENERIC_ENUMOPTION_FEATURES.NAME]        = self._ReadAnyName
        handlerTable[GENERIC_ELEMENTS.ENUMOPTION][GENERIC_ENUMOPTION_FEATURES.VALUE]       = self._ReadEnumoptionValue
        handlerTable[GENERIC_ELEMENTS.MDB] = {}
        handlerTable[GENERIC_ELEMENTS.MDB][GENERIC_MDB_FEATURES.ROOT]                    = self._ReadRootRoot
        handlerTable[GENERIC_ELEMENTS.MDB][GENERIC_MDB_FEATURES.ORPHANS]                 = self._ReadRootOrphans
        return handlerTable
    
    def __InitGenericUpdateHandlerTable(self):
        handlerTable = {}
        handlerTable[GENERIC_ELEMENTS.ELEMENT] = {}
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.DOCUMENTATION]     = self._UpdateElementDocumentation
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.CONSTRAINTS]       = self._UpdateElementConstraints
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.OWNER]             = self._UpdateElementOwner
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.GROUP]             = self._UpdateElementGroup
        handlerTable[GENERIC_ELEMENTS.ELEMENT][GENERIC_ELEMENT_FEATURES.PERMISSIONS]       = self._UpdateElementPermissions
        handlerTable[GENERIC_ELEMENTS.CLASS] = {}
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.NAME]                  = self._UpdateClassName
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ATTRIBUTES]            = self._UpdateClassAttributes
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.ASSOCIATIONS]          = self._UpdateClassAssociations
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.COMPOSITIONS]          = self._UpdateClassCompositions
        handlerTable[GENERIC_ELEMENTS.CLASS][GENERIC_CLASS_FEATURES.SUPERTYPES]            = self._UpdateClassSupertypes
        handlerTable[GENERIC_ELEMENTS.M2MODEL] = {}
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.NAME]              = self._UpdateAnyName
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.ID]                = self._UpdatePackageId
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.CLASSES]           = self._UpdatePackageClasses
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.ENUMS]             = self._UpdatePackageEnums
        handlerTable[GENERIC_ELEMENTS.M2MODEL][GENERIC_PACKAGE_FEATURES.SUBPACKAGES]       = self._UpdatePackageSubpackages
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE] = {}
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][GENERIC_ATTRIBUTE_FEATURES.NAME]          = self._UpdateAnyName
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][GENERIC_ATTRIBUTE_FEATURES.TYPE]          = self._UpdateAttributeType
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][GENERIC_ATTRIBUTE_FEATURES.MUL]           = self._UpdateAttributeLen
        handlerTable[GENERIC_ELEMENTS.ATTRIBUTE][GENERIC_ATTRIBUTE_FEATURES.UNIT]          = self._UpdateAttributeUnit
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION] = {}
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.SRCNAME]   = self._UpdateAssociationSrcName
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.SRCTYPE]   = self._UpdateAssociationSrcType
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.SRCMUL]    = self._UpdateAssociationSrcMul
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.DSTNAME]   = self._UpdateAssociationDstName
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.DSTTYPE]   = self._UpdateAssociationDstType
        handlerTable[GENERIC_ELEMENTS.ASSOCIATION][GENERIC_ASSOCIATION_FEATURES.DSTMUL]    = self._UpdateAssociationDstMul
        handlerTable[GENERIC_ELEMENTS.COMPOSITION] = {}
        handlerTable[GENERIC_ELEMENTS.COMPOSITION][GENERIC_COMPOSITION_FEATURES.NAME]      = self._UpdateAnyName
        handlerTable[GENERIC_ELEMENTS.COMPOSITION][GENERIC_COMPOSITION_FEATURES.TYPE]      = self._UpdateCompositionType
        handlerTable[GENERIC_ELEMENTS.COMPOSITION][GENERIC_COMPOSITION_FEATURES.MUL]       = self._UpdateCompositionLen
        handlerTable[GENERIC_ELEMENTS.ENUM] = {}
        handlerTable[GENERIC_ELEMENTS.ENUM][GENERIC_ENUM_FEATURES.NAME]                    = self._UpdateAnyName
        handlerTable[GENERIC_ELEMENTS.ENUM][GENERIC_ENUM_FEATURES.OPTIONS]                 = self._UpdateEnumOptions
        handlerTable[GENERIC_ELEMENTS.ENUMOPTION] = {}
        handlerTable[GENERIC_ELEMENTS.ENUMOPTION][GENERIC_ENUMOPTION_FEATURES.NAME]        = self._UpdateAnyName
        handlerTable[GENERIC_ELEMENTS.ENUMOPTION][GENERIC_ENUMOPTION_FEATURES.VALUE]       = self._UpdateEnumoptionValue
        handlerTable[GENERIC_ELEMENTS.MDB] = {}
        handlerTable[GENERIC_ELEMENTS.MDB][GENERIC_MDB_FEATURES.ROOT]                    = self._UpdateRootRoot
        return handlerTable

    def __ValidateValueUniqueness(self,eValue,scope,featureName,excludeEObj=None):
        for c in scope:
            if(c.eGet(featureName) == eValue and c != excludeEObj):
                raise EOQ_ERROR_INVALID_VALUE('Value "%s" is not unique within feature %s'%(eValue,featureName))
            
    def __VaidateFeatureNameMultiplicity(self,isNameMultivalue,isFeatureMultivalue,featureName,normalizedFeatureName):
        if(isNameMultivalue and not isFeatureMultivalue):
            self.config.logger.Warn('Warning: Feature name %s indicates multi value feature, but it is a single value feature. Use %s to prevent this warning.'%(featureName,normalizedFeatureName))
        elif(not isNameMultivalue and isFeatureMultivalue):
            self.config.logger.Warn('Feature name %s indicates single value feature, but it is a multi value feature. Use %s%s to prevent this warning.'%(featureName,featureName,FEATURE_MULTIVALUE_POSTFIX))
            
    def __ValidateType(self, value, expectedType, varname:str, isNoneOk=False):
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
            
    def __ValidateMultiplicity(self,mul:int,varname:str="multiplicity"):
        if(mul == -1 or mul > 0):
            return
        #else error
        raise EOQ_ERROR_INVALID_VALUE("%s: Expected positive value or -1 but got %s"%(varname,mul))
            
    def __ValidateTypes(self, value, expectedTypes:List[Any], varname:str):
        for t in expectedTypes:
            if(isinstance(value,t)):
                return
        #if we get here, no type matched.
        raise EOQ_ERROR_INVALID_VALUE("%s: Expected %s but got %s"%(varname,[t.__name__ for t in expectedTypes],type(value).__name__))
    
    def __ValidateValueTypeAndGet(self, value : VAL, expectedType, varname:str, isNoneOk=False):
        self.__ValidateType(value,expectedType,varname,isNoneOk)
        return value.GetVal()
    
    def __ValidateAndReturnUniqueClassId(self, classIdStr:str) -> EClass:
        if(ECORE_CLASSID_SEPERATOR in classIdStr):
            classes = self.__FindClassByIdOrNameRaw(classIdStr)
            nClasses = len(classes)
            if(1 == nClasses):
                return classes[0]
            elif(0 == nClasses):
                raise EOQ_ERROR_INVALID_VALUE('Class with id  %s does not exist.'%(classIdStr))
            else:
                raise EOQ_ERROR_INVALID_VALUE('Class with id  %s is ambiguous. Found %d options.'%(classIdStr))
        else:
            raise EOQ_ERROR_INVALID_VALUE('%s is no valid class id.'%(classIdStr))
    
    def __PreventMetaMetaAccess(self,target:Obj,isRootOk=True)->None:
        #check if a base element is given, which is not allowed to be deleted.
        if(target in self.baseElements or (not isRootOk and target == self.rootObj)):
            raise EOQ_ERROR_UNSUPPORTED('Invalid target %s: meta-meta content of meta-meta elements is not accessible'%(target))
    
    def __GetUpdateRecoveryInfo(self, eObj:EObject):
        if(None==eObj):
            return (NON(),NON(),NON())
        else:
            parent = self._ReadElementParent(eObj, None)
            return (parent[0],parent[1],parent[2])
        
    def __RegisterNewEAnnotation(self, eAnnotation:EAnnotation):
        self.__InitCaching(eAnnotation) #annotations will never have associates, but needs to be in the cache
        self.__EncFirstTime(eAnnotation)
        
    

