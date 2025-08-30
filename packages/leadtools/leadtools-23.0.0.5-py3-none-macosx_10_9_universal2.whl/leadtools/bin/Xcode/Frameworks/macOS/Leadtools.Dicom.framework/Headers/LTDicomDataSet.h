// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomDataSet.h
//  Leadtools.Dicom
//

#import <Leadtools/LTRasterImage.h>

#import <Leadtools.Dicom/LTDicomAgeValue.h>
#import <Leadtools.Dicom/LTDicomCharacterSet.h>
#import <Leadtools.Dicom/LTDicomCodeSequenceItem.h>
#import <Leadtools.Dicom/LTDicomCommandType.h>
#import <Leadtools.Dicom/LTDicomCompoundGraphic.h>
#import <Leadtools.Dicom/LTDicomCopyCallback.h>
#import <Leadtools.Dicom/LTDicomDateRangeValue.h>
#import <Leadtools.Dicom/LTDicomDateTimeValue.h>
#import <Leadtools.Dicom/LTDicomDateValue.h>
#import <Leadtools.Dicom/LTDicomElement.h>
#import <Leadtools.Dicom/LTDicomEncapsulatedDocument.h>
#import <Leadtools.Dicom/LTDicomGraphicLayer.h>
#import <Leadtools.Dicom/LTDicomGraphicObject.h>
#import <Leadtools.Dicom/LTDicomImageFlags.h>
#import <Leadtools.Dicom/LTDicomImageInformation.h>
#import <Leadtools.Dicom/LTDicomIod.h>
#import <Leadtools.Dicom/LTDicomJpeg2000Options.h>
#import <Leadtools.Dicom/LTDicomModalityLutAttributes.h>
#import <Leadtools.Dicom/LTDicomModule.h>
#import <Leadtools.Dicom/LTDicomPaletteColorLutAttributes.h>
#import <Leadtools.Dicom/LTDicomPresentationStateInformation.h>
#import <Leadtools.Dicom/LTDicomTestConformanceCallback.h>
#import <Leadtools.Dicom/LTDicomTextObject.h>
#import <Leadtools.Dicom/LTDicomTimeRangeValue.h>
#import <Leadtools.Dicom/LTDicomTimeValue.h>
#import <Leadtools.Dicom/LTDicomVoiLutAttributes.h>
#import <Leadtools.Dicom/LTDicomVR.h>
#import <Leadtools.Dicom/LTDicomWaveformGroup.h>
#import <Leadtools.Dicom/LTDicomWindowAttributes.h>

typedef NS_OPTIONS(NSUInteger, LTDicomDataSetFlags) {
	LTDicomDataSetFlagsNone              = 0,
	LTDicomDataSetFlagsMetaHeaderPresent = 0x0001,
	LTDicomDataSetFlagsMetaHeaderAbsent  = 0x0002,
	LTDicomDataSetFlagsLittleEndian      = 0x0004,
	LTDicomDataSetFlagsBigEndian         = 0x0008,
	LTDicomDataSetFlagsImplicitVR        = 0x0010,
	LTDicomDataSetFlagsExplicitVR        = 0x0020,
};

typedef NS_ENUM(NSInteger, LTDicomDataSetInitializeType) {
	LTDicomDataSetInitializeTypeImplicitVRLittleEndian = 0x0004 | 0x0010,
	LTDicomDataSetInitializeTypeExplicitVRLittleEndian = 0x0004 | 0x0020,
	LTDicomDataSetInitializeTypeExplicitVRBigEndian    = 0x0008 | 0x0020,
};

typedef NS_OPTIONS(NSUInteger, LTDicomDataSetInitializeFlags) {
	LTDicomDataSetInitializeFlagsNone                     = 0,
	LTDicomDataSetInitializeFlagsLittleEndian             = 0x0004,
	LTDicomDataSetInitializeFlagsBigEndian                = 0x0008,
	LTDicomDataSetInitializeFlagsImplicitVR               = 0x0010,
	LTDicomDataSetInitializeFlagsExplicitVR               = 0x0020,
	LTDicomDataSetInitializeFlagsAddMandatoryElementsOnly = 0x1000,
	LTDicomDataSetInitializeFlagsAddMandatoryModulesOnly  = 0x2000,
};

typedef NS_OPTIONS(NSUInteger, LTDicomDataSetLoadFlags) {
	LTDicomDataSetLoadFlagsNone              = 0,
	LTDicomDataSetLoadFlagsMetaHeaderPresent = 0x0001,
	LTDicomDataSetLoadFlagsMetaHeaderAbsent  = 0x0002,
	LTDicomDataSetLoadFlagsLittleEndian      = 0x0004,
	LTDicomDataSetLoadFlagsBigEndian         = 0x0008,
	LTDicomDataSetLoadFlagsImplicitVR        = 0x0010,
	LTDicomDataSetLoadFlagsExplicitVR        = 0x0020,
	LTDicomDataSetLoadFlagsLoadAndClose      = 0x0200,
};

typedef NS_OPTIONS(NSUInteger, LTDicomDataSetSaveFlags) {
	LTDicomDataSetSaveFlagsNone                   = 0,
	LTDicomDataSetSaveFlagsMetaHeaderPresent      = 0x0001,
	LTDicomDataSetSaveFlagsMetaHeaderAbsent       = 0x0002,
	LTDicomDataSetSaveFlagsLittleEndian           = 0x0004,
	LTDicomDataSetSaveFlagsBigEndian              = 0x0008,
	LTDicomDataSetSaveFlagsImplicitVR             = 0x0010,
	LTDicomDataSetSaveFlagsExplicitVR             = 0x0020,

	LTDicomDataSetSaveFlagsGroupLengths           = 0x0040,
	LTDicomDataSetSaveFlagsLengthExplicit         = 0x0080,
	LTDicomDataSetSaveFlagsExcludeMetaHeaderGroup = 0x0100,
};

typedef NS_OPTIONS(NSUInteger, LTChangeTransferSyntaxFlags) {
	LTChangeTransferSyntaxFlagsNone                                  = 0,
	LTChangeTransferSyntaxFlagsMinimizeJpegSize                      = 0x00000001,
	LTChangeTransferSyntaxFlagsRescaleModalityLutWhenLossyCompressed = 0x00000002,
	LTChangeTransferSyntaxFlagsYbrFull                               = 0x00000100,
};

typedef NS_ENUM(NSInteger, LTDicomCertificateFormat) {
	LTDicomCertificateFormatPem = 0,
	LTDicomCertificateFormatDer = 1,
};

typedef NS_ENUM(NSInteger, LTDicomMacAlgorithm) {
	LTDicomMacAlgorithmRipemd160 = 0,
	LTDicomMacAlgorithmSha1      = 1,
	LTDicomMacAlgorithmMD5       = 2,
};

typedef NS_OPTIONS(NSUInteger, LTDicomSetOverlayFlags) {
	LTDicomSetOverlayFlagsNone       = 0,
	LTDicomSetOverlayFlagsNoOverride = 0x0001,
};

typedef NS_ENUM(NSInteger, LTDicomSecurityProfile) {
	LTDicomSecurityProfileNone             = 0,
	LTDicomSecurityProfileBaseRsa          = 1,
	LTDicomSecurityProfileCreatorRsa       = 2,
	LTDicomSecurityProfileAuthorizationRsa = 3,
};

typedef NS_ENUM(NSInteger, LTDicomDirKeyType) {
	LTDicomDirKeyTypePatient,
	LTDicomDirKeyTypeStudy,
	LTDicomDirKeyTypeSeries,
	LTDicomDirKeyTypeImage,
	LTDicomDirKeyTypeOverlay,
	LTDicomDirKeyTypeModalityLut,
	LTDicomDirKeyTypeVoiLut,
	LTDicomDirKeyTypeCurve,
	LTDicomDirKeyTypeStoredPrint,
	LTDicomDirKeyTypeRTDose,
	LTDicomDirKeyTypeRTStructureSet,
	LTDicomDirKeyTypeRTPlan,
	LTDicomDirKeyTypeRTTreatRecord,
	LTDicomDirKeyTypeTopic,
	LTDicomDirKeyTypeVisit,
	LTDicomDirKeyTypeResults,
	LTDicomDirKeyTypeInterpretation,
	LTDicomDirKeyTypeStudyComponent,
	LTDicomDirKeyTypePresentation,
	LTDicomDirKeyTypeWaveform,
	LTDicomDirKeyTypeSRDocument,
	LTDicomDirKeyTypePrivate,
	LTDicomDirKeyTypeKeyObjectDoc,
	LTDicomDirKeyTypeSpectroscopy,
	LTDicomDirKeyTypeRawData,
	LTDicomDirKeyTypeRegistration,
	LTDicomDirKeyTypeFiducial,
	LTDicomDirKeyTypeHangingProtocol,
	LTDicomDirKeyTypeEncapDoc,
	LTDicomDirKeyTypeHL7StrucDoc,
	LTDicomDirKeyTypeValueMap,
	LTDicomDirKeyTypeStereometric,
	LTDicomDirKeyTypeUnknown,
};

typedef NS_ENUM(NSInteger, LTDicomGetValueResult) {
	LTDicomGetValueResultSuccess                                 = 0,
	LTDicomGetValueResultElementPresentWithValue                 = 0,
	LTDicomGetValueResultElementPresentWithValueConversionFailed = 1,
	LTDicomGetValueResultElementPresentWithNoValue               = 2,
	LTDicomGetValueResultElementNotPresent                       = 3,
	LTDicomGetValueResultInvalidType                             = 4,
};

typedef NS_ENUM(NSInteger, LTDicomInsertElementAndSetValueResult) {
	LTDicomInsertElementAndSetValueResultSuccess                   = 0,
	LTDicomInsertElementAndSetValueResultElementAddedValueSet      = 0,
	LTDicomInsertElementAndSetValueResultElementExistedValueSet    = 1,
	LTDicomInsertElementAndSetValueResultElementAddedValueNotSet   = 2,
	LTDicomInsertElementAndSetValueResultElementExistedValueNotSet = 3,
	LTDicomInsertElementAndSetValueResultElementNotAdded           = 4,
};

NS_ASSUME_NONNULL_BEGIN

typedef _Nonnull id (^GetValueDelegate)(NSString *value);
typedef BOOL (^LTDicomGetImageCallback)(NSUInteger page, NSUInteger count);



NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomDataSet : NSObject

@property (nonatomic, assign, readonly) LTDicomClassType informationClass;
@property (nonatomic, assign, readonly) LTDicomDataSetFlags informationFlags;
@property (nonatomic, assign, readonly) LTDicomCommandType informationCommand;

@property (nonatomic, assign, readonly) BOOL isRequestCommand;

@property (nonatomic, assign, readonly) NSUInteger moduleCount;

- (instancetype)init;
- (instancetype)initWithTemporaryDirectory:(NSString *)path;

- (void)initialize:(LTDicomClassType)classType type:(LTDicomDataSetInitializeType)type;
- (void)initialize:(LTDicomClassType)classType flags:(LTDicomDataSetInitializeFlags)flags;

- (void)initializeCommandSet:(LTDicomCommandType)commandType request:(BOOL)request;

- (BOOL)load:(NSString *)file flags:(LTDicomDataSetLoadFlags)flags error:(NSError **)error NS_SWIFT_NAME(load(file:flags:));
- (BOOL)loadData:(NSData *)data flags:(LTDicomDataSetLoadFlags)flags error:(NSError **)error NS_SWIFT_NAME(load(data:flags:));
- (BOOL)loadBuffer:(void *)buffer size:(NSUInteger)bufferSize flags:(LTDicomDataSetFlags)flags error:(NSError **)error NS_SWIFT_NAME(load(buffer:size:flags:));

- (BOOL)save:(NSString *)file flags:(LTDicomDataSetSaveFlags)flags error:(NSError **)error;
- (nullable NSData *)save:(LTDicomDataSetSaveFlags)flags error:(NSError **)error NS_SWIFT_NAME(save(flags:));

- (BOOL)testConformance:(LTDicomTestConformanceCallback)callback;

- (nullable LTDicomElement *)insertElement:(nullable LTDicomElement *)neighbor child:(BOOL)child tag:(LTDicomTagCode)tag VR:(LTDicomVRType)vr sequence:(BOOL)sequence index:(NSInteger)index error:(NSError **)error;
- (nullable LTDicomElement *)insertKey:(LTDicomElement *)parent key:(LTDicomDirKeyType)key optional:(BOOL)optional;
- (nullable LTDicomElement *)insertKey:(LTDicomElement *)parent stringKey:(NSString *)key optional:(BOOL)optional;
- (nullable LTDicomModule *)insertModule:(LTDicomModuleType)module optional:(BOOL)optional;

- (nullable LTDicomElement *)deleteElement:(LTDicomElement *)element NS_SWIFT_NAME(deleteElement(_:));
- (void)deleteModule:(LTDicomModuleType)module NS_SWIFT_NAME(deleteModule(_:));
- (void)deleteKey:(LTDicomElement *)element;
- (void)reset;

- (nullable LTDicomElement *)rootElement:(LTDicomElement *)element;
- (nullable LTDicomElement *)parentElement:(LTDicomElement *)element;
- (nullable LTDicomElement *)childElement:(LTDicomElement *)element includeVolatile:(BOOL)includeVolatile;
- (nullable LTDicomElement *)firstElement:(nullable LTDicomElement *)element tree:(BOOL)tree includeVolatile:(BOOL)includeVolatile;
- (nullable LTDicomElement *)lastElement:(nullable LTDicomElement *)element tree:(BOOL)tree includeVolatile:(BOOL)includeVolatile;
- (nullable LTDicomElement *)nextElement:(LTDicomElement *)element tree:(BOOL)tree includeVolatile:(BOOL)includeVolatile;
- (nullable LTDicomElement *)previousElement:(LTDicomElement *)element tree:(BOOL)tree includeVolatile:(BOOL)includeVolatile;

- (nullable LTDicomElement *)rootKey:(LTDicomElement *)element;
- (nullable LTDicomElement *)parentKey:(LTDicomElement *)element;
- (nullable LTDicomElement *)childKey:(LTDicomElement *)element;
- (nullable LTDicomElement *)firstKey:(nullable LTDicomElement *)element tree:(BOOL)tree;
- (nullable LTDicomElement *)lastKey:(nullable LTDicomElement *)element tree:(BOOL)tree;
- (nullable LTDicomElement *)nextKey:(LTDicomElement *)element tree:(BOOL)tree;
- (nullable LTDicomElement *)previousKey:(LTDicomElement *)element tree:(BOOL)tree;

- (nullable LTDicomElement *)findFirstElement:(nullable LTDicomElement *)element tag:(LTDicomTagCode)tag tree:(BOOL)tree;
- (nullable LTDicomElement *)findLastElement:(nullable LTDicomElement *)element tag:(LTDicomTagCode)tag tree:(BOOL)tree;
- (nullable LTDicomElement *)findNextElement:(LTDicomElement *)element tree:(BOOL)tree;
- (nullable LTDicomElement *)findPreviousElement:(LTDicomElement *)element tree:(BOOL)tree;
- (nullable LTDicomElement *)findFirstDescendant:(LTDicomElement *)parentElement tag:(LTDicomTagCode)tag nextLevelOnly:(BOOL)nextLevelOnly;
- (nullable LTDicomElement *)findNextDescendant:(LTDicomElement *)parentElement childElement:(LTDicomElement *)childElement nextLevelOnly:(BOOL)nextLevelOnly;

- (nullable LTDicomElement *)findInsertElement:(nullable LTDicomElement *)element tag:(LTDicomTagCode)tag tree:(BOOL)tree error:(NSError **)error;

- (nullable LTDicomElement *)findFirstKey:(nullable LTDicomElement *)element key:(LTDicomDirKeyType)key tree:(BOOL)tree;
- (nullable LTDicomElement *)findFirstKey:(nullable LTDicomElement *)element stringKey:(NSString *)key tree:(BOOL)tree;
- (nullable LTDicomElement *)findLastKey:(nullable LTDicomElement *)element key:(LTDicomDirKeyType)key tree:(BOOL)tree;
- (nullable LTDicomElement *)findLastKey:(nullable LTDicomElement *)element stringKey:(NSString *)key tree:(BOOL)tree;
- (nullable LTDicomElement *)findNextKey:(LTDicomElement *)element tree:(BOOL)tree;
- (nullable LTDicomElement *)findPreviousKey:(LTDicomElement *)element tree:(BOOL)tree;

- (nullable LTDicomModule *)findModule:(LTDicomModuleType)module NS_SWIFT_NAME(findModule(_:));
- (nullable LTDicomModule *)findModuleByIndex:(NSUInteger)index NS_SWIFT_NAME(findModuleByIndex(_:));

- (NSUInteger)levelForElement:(LTDicomElement *)element NS_SWIFT_NAME(level(for:));

- (BOOL)elementExists:(LTDicomElement *)element NS_SWIFT_NAME(exists(_:));
- (BOOL)isVolatileElement:(LTDicomElement *)element NS_SWIFT_NAME(isVolatile(_:));

- (BOOL)copyElementsInDataSet:(LTDicomDataSet *)dataSet destinationElement:(nullable LTDicomElement *)dst sourceElement:(nullable LTDicomElement *)src error:(NSError **)error;
- (BOOL)copyElementsInDataSet:(LTDicomDataSet *)dataSet destinationElement:(nullable LTDicomElement *)dst sourceElement:(nullable LTDicomElement *)src callback:(LTDicomCopyCallback)callback error:(NSError **)error;

- (void)freeElementValue:(LTDicomElement *)element;

- (BOOL)removeType3EmptyElements;

@end



@interface LTDicomDataSet (GetValues)

@property (nonatomic, assign, readonly) LTDicomGetValueResult getValueResult;

- (NSData *)getPreamble:(NSUInteger)length;

- (nullable NSData *)binaryValueForElement:(LTDicomElement *)element length:(NSUInteger)length;
- (BOOL)binaryValueForElement:(LTDicomElement *)element buffer:(unsigned char *)buffer offset:(NSUInteger)offset length:(NSUInteger)length;

- (nullable NSData *)intValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (nullable NSArray<NSNumber *> *)intValuesForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (BOOL)intValueForElement:(LTDicomElement *)element buffer:(int *)buffer index:(NSUInteger)index count:(NSUInteger)count;

- (nullable NSData *)shortValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (nullable NSArray<NSNumber *> *)shortValuesForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (BOOL)shortValueForElement:(LTDicomElement *)element buffer:(short *)buffer index:(NSUInteger)index count:(NSUInteger)count;

- (nullable NSData *)doubleValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (nullable NSData *)doubleValueExtForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (nullable NSArray<NSNumber *> *)doubleValuesForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (nullable NSArray<NSNumber *> *)doubleValuesExtForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (BOOL)doubleValueForElement:(LTDicomElement *)element buffer:(double *)buffer index:(NSUInteger)index count:(NSUInteger)count;
- (BOOL)doubleValueExtForElement:(LTDicomElement *)element buffer:(double *)buffer index:(NSUInteger)index count:(NSUInteger)count;

- (nullable NSData *)floatValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (nullable NSArray<NSNumber *> *)floatValuesForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (BOOL)floatValueForElement:(LTDicomElement *)element buffer:(float *)buffer index:(NSUInteger)index count:(NSUInteger)count;

- (nullable NSString *)stringValueForElement:(LTDicomElement *)element index:(NSUInteger)index;
- (nullable NSString *)stringValueForElement:(LTDicomElement *)element index:(NSUInteger)index encoding:(NSStringEncoding)encoding;
- (nullable NSString *)stringValueForElement:(LTDicomElement *)element index:(NSUInteger)index usedEncoding:(NSStringEncoding * __nullable)usedEncoding;
- (nullable NSString *)convertValueForElement:(LTDicomElement *)element error:(NSError **)error;

- (nullable NSData *)byteValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (BOOL)byteValueForElement:(LTDicomElement *)element buffer:(unsigned char *)buffer index:(NSUInteger)index count:(NSUInteger)count;

- (nullable NSData *)longValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (nullable NSArray<NSNumber *> *)longValuesForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (BOOL)longValueForElement:(LTDicomElement *)element buffer:(int64_t *)buffer index:(NSUInteger)index count:(NSUInteger)count;

- (NSArray<LTDicomDateValue *> *)dateValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (NSArray<LTDicomTimeValue *> *)timeValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (NSArray<LTDicomDateTimeValue *> *)dateTimeValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;
- (NSArray<LTDicomAgeValue *> *)ageValueForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count;

- (nullable LTDicomDateRangeValue *)dateRangeValueForElement:(LTDicomElement *)element index:(NSUInteger)index error:(NSError **)error;
- (nullable LTDicomTimeRangeValue *)timeRangeValueForElement:(LTDicomElement *)element index:(NSUInteger)index error:(NSError **)error;

- (LTDicomDirKeyType)keyValueForElement:(LTDicomElement *)element;
- (nullable NSString *)keyValueStringForElement:(LTDicomElement *)element;
- (NSUInteger)valueCountForElement:(LTDicomElement *)element;

@end



@interface LTDicomDataSet (SetValues)

@property (nonatomic, assign, readonly) LTDicomInsertElementAndSetValueResult insertElementAndSetValueResult;

- (void)setPreamble:(NSData *)preamble length:(NSUInteger)length;

- (BOOL)setStringValue:(NSString *)value forElement:(LTDicomElement *)element;
- (BOOL)setStringValue:(NSString *)value forElement:(LTDicomElement *)element characterSet:(LTDicomCharacterSetType)characterSet;
- (BOOL)setStringValues:(NSArray<NSString *> *)values forElement:(LTDicomElement *)element error:(NSError **)error;
- (BOOL)setStringValues:(NSArray<NSString *> *)values forElement:(LTDicomElement *)element characterSet:(LTDicomCharacterSetType)characterSet error:(NSError **)error;

- (BOOL)setConvertValue:(NSString *)value forElement:(LTDicomElement *)element count:(NSUInteger)count;

- (BOOL)setBinaryValue:(unsigned char *)value forElement:(LTDicomElement *)element length:(NSUInteger)length;
- (BOOL)setBinaryValueWithData:(NSData *)value forElement:(LTDicomElement *)element;
- (BOOL)setBinaryValueWithFile:(NSString *)fileName forElement:(LTDicomElement *)element;

- (BOOL)setByteValue:(unsigned char *)value forElement:(LTDicomElement *)element count:(NSUInteger)count;

- (BOOL)setShortValue:(NSData *)value forElement:(LTDicomElement *)element;
- (BOOL)setShortValue:(short *)value forElement:(LTDicomElement *)element count:(NSUInteger)count;
- (BOOL)setShortValues:(NSArray<NSNumber *> *)values forElement:(LTDicomElement *)element count:(NSUInteger)count;

- (BOOL)setIntValue:(NSData *)value forElement:(LTDicomElement *)element error:(NSError **)error;
- (BOOL)setIntValue:(int *)value forElement:(LTDicomElement *)element count:(NSUInteger)count error:(NSError **)error;
- (BOOL)setIntValues:(NSArray<NSNumber *> *)values forElement:(LTDicomElement *)element count:(NSUInteger)count error:(NSError **)error;

- (BOOL)setLongValue:(NSData *)value forElement:(LTDicomElement *)element error:(NSError **)error;
- (BOOL)setLongValue:(int64_t *)value forElement:(LTDicomElement *)element count:(NSUInteger)count error:(NSError **)error;
- (BOOL)setLongValues:(NSArray<NSNumber *> *)values forElement:(LTDicomElement *)element count:(NSUInteger)count error:(NSError **)error;

- (BOOL)setFloatValue:(NSData *)value forElement:(LTDicomElement *)element;
- (BOOL)setFloatValue:(float *)value forElement:(LTDicomElement *)element count:(NSUInteger)count;
- (BOOL)setFloatValues:(NSArray<NSNumber *> *)values forElement:(LTDicomElement *)element count:(NSUInteger)count;

- (BOOL)setDoubleValue:(NSData *)value forElement:(LTDicomElement *)element;
- (BOOL)setDoubleValue:(double *)value forElement:(LTDicomElement *)element count:(NSUInteger)count;
- (BOOL)setDoubleValues:(NSArray<NSNumber *> *)values forElement:(LTDicomElement *)element count:(NSUInteger)count;
- (BOOL)setDoubleValueExt:(NSData *)value forElement:(LTDicomElement *)element error:(NSError **)error;
- (BOOL)setDoubleValueExt:(double *)value forElement:(LTDicomElement *)element count:(NSUInteger)count error:(NSError **)error;
- (BOOL)setDoubleValuesExt:(NSArray<NSNumber *> *)values forElement:(LTDicomElement *)element count:(NSUInteger)count error:(NSError **)error;

- (BOOL)setAgeValues:(NSArray<LTDicomAgeValue *> *)values forElement:(LTDicomElement *)element;
- (BOOL)setDateValues:(NSArray<LTDicomDateValue *> *)values forElement:(LTDicomElement *)element;
- (BOOL)setDateValue:(LTDicomDateValue *)value forElement:(LTDicomElement *)element;
- (BOOL)setTimeValues:(NSArray<LTDicomTimeValue *> *)values forElement:(LTDicomElement *)element;
- (BOOL)setDateTimeValues:(NSArray<LTDicomDateTimeValue *> *)values forElement:(LTDicomElement *)element;
- (BOOL)setDateRangeValues:(NSArray<LTDicomDateRangeValue *> *)values forElement:(LTDicomElement *)element;
- (BOOL)setTimeRangeValues:(NSArray<LTDicomTimeRangeValue *> *)values forElement:(LTDicomElement *)element;

- (BOOL)setDateValuesWithNSDate:(NSArray<NSDate *> *)values forElement:(LTDicomElement *)element;
- (BOOL)setTimeValuesWithNSDate:(NSArray<NSDate *> *)values forElement:(LTDicomElement *)element;
- (BOOL)setDateTimeValuesWithNSDate:(NSArray<NSDate *> *)values forElement:(LTDicomElement *)element;

- (BOOL)setValue:(id)object forElement:(LTDicomElement *)element error:(NSError **)error;

- (instancetype)insertElement:(nullable LTDicomElement *)element andSetValue:(id)object tag:(LTDicomTagCode)tag tree:(BOOL)tree error:(NSError **)error;
- (instancetype)insertElementAndSetValue:(id)object tag:(LTDicomTagCode)tag error:(NSError **)error;

@end



@interface LTDicomDataSet (ReadAndEdit)

- (instancetype)beginEditSequence:(nullable LTDicomElement *)element tag:(LTDicomTagCode)tag tree:(BOOL)tree error:(NSError **)error;
- (instancetype)beginEditSequence:(NSUInteger)tag error:(NSError **)error;
- (instancetype)endEditSequence;

- (instancetype)beginReadSequence:(nullable LTDicomElement *)element tag:(LTDicomTagCode)tag tree:(BOOL)tree;
- (instancetype)beginReadSequence:(NSUInteger)tag;
- (instancetype)endReadSequence;

- (instancetype)beginEditItem:(NSUInteger)index error:(NSError **)error;
- (instancetype)beginEditItem:(NSError **)error;
- (instancetype)endEditItem;

- (instancetype)beginReadItem:(NSUInteger)index;
- (instancetype)beginReadItem;
- (instancetype)endReadItem;

@end



@interface LTDicomDataSet (Images)

- (NSUInteger)numberOfImagesForElement:(LTDicomElement *)element;

- (nullable LTRasterImage *)imageForElement:(LTDicomElement *)element index:(NSUInteger)index bitsPerPixel:(NSUInteger)bitsPerPixel flags:(LTDicomGetImageFlags)flags error:(NSError **)error NS_SWIFT_NAME(image(for:index:bitsPerPixel:flags:));
- (nullable LTRasterImage *)imagesForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count bitsPerPixel:(NSUInteger)bitsPerPixel flags:(LTDicomGetImageFlags)flags error:(NSError **)error NS_SWIFT_NAME(images(for:index:count:bitsPerPixel:flags:));
- (nullable LTRasterImage *)imagesForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count bitsPerPixel:(NSUInteger)bitsPerPixel flags:(LTDicomGetImageFlags)flags callback:(LTDicomGetImageCallback)callback error:(NSError **)error NS_SWIFT_NAME(images(for:index:count:bitsPerPixel:flags:callback:));

- (BOOL)changeTransferSyntax:(NSString *)uid qualityFactor:(NSUInteger)qFactor flags:(LTChangeTransferSyntaxFlags)flags error:(NSError **)error;
- (BOOL)changeTransferSyntax:(NSString *)uid qualityFactor:(NSUInteger)qFactor flags:(LTChangeTransferSyntaxFlags)flags saveToFile:(NSString *)file saveFlags:(LTDicomDataSetSaveFlags)saveFlags error:(NSError **)error;

- (nullable LTDicomImageInformation *)imageInformationForElement:(LTDicomElement *)element index:(NSUInteger)index error:(NSError **)error;

- (BOOL)insertImage:(LTRasterImage *)image inElement:(LTDicomElement *)element atIndex:(NSUInteger)index compression:(LTDicomImageCompressionType)compression photometric:(LTDicomImagePhotometricInterpretationType)photometric bitsPerPixel:(NSUInteger)bitsPerPixel qualityFactor:(NSUInteger)qFactor flags:(LTDicomSetImageFlags)flags error:(NSError **)error;
- (BOOL)insertImages:(LTRasterImage *)image inElement:(LTDicomElement *)element atIndex:(NSUInteger)index compression:(LTDicomImageCompressionType)compression photometric:(LTDicomImagePhotometricInterpretationType)photometric bitsPerPixel:(NSUInteger)bitsPerPixel qualityFactor:(NSUInteger)qFactor flags:(LTDicomSetImageFlags)flags error:(NSError **)error;

- (BOOL)deleteImageForElement:(LTDicomElement *)element index:(NSUInteger)index count:(NSUInteger)count error:(NSError **)error;

@end



@interface LTDicomDataSet (Signature)

- (NSUInteger)numberOfSignaturesForElement:(LTDicomElement *)element;
- (NSUInteger)numberOfSignedElementsForItem:(LTDicomElement *)signatureItem;

- (nullable LTDicomElement *)signatureAtIndex:(NSUInteger)index forElement:(LTDicomElement *)element;
- (nullable LTDicomElement *)findSignature:(NSString *)signatureUID;
- (nullable NSString *)signatureUIDForItem:(LTDicomElement *)signatureItem;

- (LTDicomDateTimeValue *)signatureDateTimeForItem:(LTDicomElement *)signatureItem;

- (BOOL)saveCertificate:(LTDicomElement *)signatureItem toFile:(NSString *)file format:(LTDicomCertificateFormat)format error:(NSError **)error;

- (nullable LTDicomElement *)signedElementAtIndex:(NSUInteger)index forItem:(LTDicomElement *)signatureItem;

- (nullable NSString *)macTransferSyntaxForItem:(LTDicomElement *)signatureItem;
- (nullable NSString *)macAlgorithmForItem:(LTDicomElement *)signatureItem;

- (void)deleteSignature:(LTDicomElement *)signatureItem;
- (BOOL)verifySignature:(LTDicomElement *)signatureItem error:(NSError **)error;

- (nullable LTDicomElement *)createSignature:(LTDicomElement *)item privateKeyFile:(NSString *)privateKeyFile certificateFile:(NSString *)certificateFile password:(NSString *)password macTransferSyntax:(nullable NSString *)macTransferSyntax macAlgorithm:(LTDicomMacAlgorithm)macAlgorithm elementsToSign:(unsigned int *)elements count:(NSUInteger)count securityProfile:(LTDicomSecurityProfile)securityProfile error:(NSError **)error;

@end



@interface LTDicomDataSet (Waveforms)

@property (nonatomic, assign, readonly) NSUInteger waveformGroupCount;

- (nullable LTDicomWaveformGroup *)waveformGroupAtIndex:(NSUInteger)index error:(NSError **)error;

- (BOOL)deleteWaveformGroupAtIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)addWaveformGroup:(LTDicomWaveformGroup *)group atIndex:(NSInteger)index error:(NSError **)error;

@end



@interface LTDicomDataSet (ModalityLUT)

@property (nonatomic, strong, readonly, nullable) LTDicomModalityLutAttributes *modalityLutAttributes;
@property (nonatomic, assign, readonly, nullable) NSData *modalityLutData;

- (nullable LTDicomModalityLutAttributes *)modalityLutAttributesForFrame:(NSUInteger)frameIndex error:(NSError **)error;

- (BOOL)setModalityLut:(LTDicomModalityLutAttributes *)attributes data:(NSData *)data error:(NSError **)error;
- (BOOL)setModalityLut:(LTDicomModalityLutAttributes *)attributes forFrame:(NSUInteger)frameIndex data:(NSData *)data flags:(LTDicomSetImageFlags)flags error:(NSError **)error;

- (void)deleteModalityLut;
- (void)deleteModalityLutForFrame:(NSUInteger)frameIndex flags:(LTDicomSetImageFlags)flags;

@end



@interface LTDicomDataSet (PaletteColorLUT)

@property (nonatomic, strong, null_unspecified) LTDicomPaletteColorLutAttributes *paletteColorLutAttributes; // get = nullable, set = nonnull

- (nullable LTDicomPaletteColorLutAttributes *)paletteColorLutAttributes:(NSError **)error;
- (BOOL)setPaletteColorLutAttributes:(LTDicomPaletteColorLutAttributes *)paletteColorLutAttributes error:(NSError **)error;

- (nullable NSData *)paletteColorLutData:(LTDicomPaletteColorLutType)type error:(NSError **)error;
- (BOOL)paletteColorLutData:(unsigned short *)buffer count:(NSUInteger)count forType:(LTDicomPaletteColorLutType)type error:(NSError **)error;
- (nullable NSArray<NSNumber */*unsigned short*/> *)paletteColorLutDataArray:(LTDicomPaletteColorLutType)type error:(NSError **)error;

- (BOOL)setPaletteColorLutData:(NSData *)data forType:(LTDicomPaletteColorLutType)type error:(NSError **)error;
- (BOOL)setPaletteColorLutDataArray:(NSArray<NSNumber */*unsigned short*/> *)paletteColorLutData forType:(LTDicomPaletteColorLutType)type error:(NSError * _Nullable __autoreleasing *)error;

- (void)deletePaletteColorLut;

@end



@interface LTDicomDataSet (Window)

- (NSUInteger)numberOfWindowsForFrame:(NSUInteger)frameIndex;

- (nullable LTDicomWindowAttributes *)windowAttributesAtIndex:(NSUInteger)index error:(NSError **)error;
- (nullable LTDicomWindowAttributes *)windowAttributesForFrame:(NSUInteger)frameIndex atIndex:(NSUInteger)index error:(NSError **)error;

- (BOOL)setWindowAttributes:(LTDicomWindowAttributes *)attributes atIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)setWindowAttributes:(LTDicomWindowAttributes *)attributes forFrame:(NSUInteger)frameIndex atIndex:(NSUInteger)index flags:(LTDicomSetImageFlags)flags error:(NSError **)error;

- (void)deleteWindowAttributes;
- (void)deleteWindowAttributesForFrame:(NSUInteger)frameIndex flags:(LTDicomSetImageFlags)flags;

@end



@interface LTDicomDataSet (VOI_LUT)

@property (nonatomic, assign, readonly) NSUInteger voiLutCount;

- (nullable LTDicomVoiLutAttributes *)voiLutAttributesAtIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)setVoiLutAttributes:(LTDicomVoiLutAttributes *)attributes atIndex:(NSUInteger)index data:(NSData *)data error:(NSError **)error;

- (nullable NSData *)voiLutDataAtIndex:(NSUInteger)index error:(NSError **)error;

- (void)deleteVoiLut;

@end



@interface LTDicomDataSet (Overlays)

@property (nonatomic, assign, readonly) NSUInteger overlayCount;

- (nullable LTRasterOverlayAttributes *)overlayAttributesAtIndex:(NSUInteger)index error:(NSError **)error;
- (NSInteger)overlayGroupNumberAtIndex:(NSUInteger)index error:(NSError **)error;

- (BOOL)isOverlayInDataSet:(NSUInteger)index error:(NSError **)error;

- (nullable NSString *)overlayActivationLayerAtIndex:(NSUInteger)index error:(NSError **)error;

- (nullable LTRasterImage *)overlayImageAtIndex:(NSUInteger)index error:(NSError **)error;
- (nullable LTRasterImage *)overlayImagesAtIndex:(NSUInteger)index overlayFrame:(NSUInteger)overlayFrameIndex count:(NSUInteger)count error:(NSError **)error;

- (BOOL)setOverlayAttributes:(LTRasterOverlayAttributes *)attributes atIndex:(NSUInteger)index flags:(LTDicomSetOverlayFlags)flags error:(NSError **)error;
- (BOOL)setOverlayImage:(LTRasterImage *)overlayImage atIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)setOverlayImages:(LTRasterImage *)overlayImages atIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)deleteOverlayAtIndex:(NSUInteger)index error:(NSError **)error;

@end



@interface LTDicomDataSet (PresentationState)

@property (nonatomic, strong, readonly, nullable) LTDicomPresentationStateInformation *presentationStateInformation;
- (BOOL)setPresentationStateInformation:(LTDicomPresentationStateInformation *)presentationStateInformation error:(NSError **)error;

- (BOOL)addPresentationStateImageReference:(NSData *)image frameNumbers:(nullable NSArray<NSNumber *> *)frameNumbers framesCount:(NSUInteger)framesCount error:(NSError **)error;
- (BOOL)addPresentationStateImageReferenceWithName:(NSString *)imageFileName frameNumbers:(nullable NSArray<NSNumber *> *)frameNumbers framesCount:(NSUInteger)framesCount error:(NSError **)error;
- (BOOL)addPresentationStateImageReferenceWithDataSet:(LTDicomDataSet *)dataSet frameNumbers:(nullable NSArray<NSNumber *> *)frameNumbers framesCount:(NSUInteger)framesCount error:(NSError **)error;

- (void)removePresentationStateImageReference:(NSString *)sopInstanceUID;
- (void)removeAllPresentationStateImageReferences;

- (nullable NSString *)getPresentationStateImageReferenceSOPInstance:(LTDicomElement *)referencedSeriesSequenceItem imageIndex:(NSUInteger)imageIndex;
- (NSUInteger)numberOfPresentationStateImageReferences:(LTDicomElement *)referencedSeriesSequenceItem;

- (nullable LTDicomElement *)findFirstPresentationStateReferencedSeriesItem;
- (nullable LTDicomElement *)findNextPresentationStateReferencedSeriesItem:(LTDicomElement *)referencedSeriesItem;
- (nullable LTDicomElement *)getPresentationStateImageReference:(NSString *)sopInstanceUID;

@end



@interface LTDicomDataSet (Layers)

@property (nonatomic, assign, readonly) NSUInteger layerCount;

- (NSUInteger)createLayer:(LTDicomGraphicLayer *)graphicLayer error:(NSError **)error;
- (BOOL)removeLayerByIndex:(NSUInteger)layerIndex annSequence:(BOOL)annSequence error:(NSError **)error;
- (BOOL)removeLayerByName:(NSString *)layerName annSequence:(BOOL)annSequence error:(NSError **)error;
- (BOOL)removeAllLayers:(BOOL)annSequence error:(NSError **)error;

- (nullable LTDicomGraphicLayer *)layerInformationAtIndex:(NSUInteger)layerIndex error:(NSError **)error;
- (BOOL)setLayerInformation:(LTDicomGraphicLayer *)graphicLayer atIndex:(NSUInteger)layerIndex error:(NSError **)error;

- (NSUInteger)indexOfLayer:(NSString *)layerName;

- (NSUInteger)numberOfGraphicObjectLayers:(LTDicomElement *)graphicAnnSequenceItem;
- (NSUInteger)numberOfTextObjectLayers:(LTDicomElement *)graphicAnnSequenceItem;

- (void)removeGraphicObjectLayers:(LTDicomElement *)graphicAnnSequenceItem;
- (void)removeTextObjectLayers:(LTDicomElement *)graphicAnnSequenceItem;

- (nullable LTDicomElement *)layerElementAtIndex:(NSUInteger)layerIndex;
- (nullable LTDicomElement *)layerElementWithName:(NSString *)layerName;

@end



@interface LTDicomDataSet (GraphicObjects)

- (nullable LTDicomElement *)findFirstGraphicAnnSequenceItem;
- (nullable LTDicomElement *)findNextGraphicAnnSequenceItem:(LTDicomElement *)referencedSeriesItem;

- (nullable NSString *)layerNameForAnnSequenceItem:(LTDicomElement *)graphicAnnSequenceItem;
- (BOOL)setLayerName:(NSString *)layerName forAnnSequenceItem:(LTDicomElement *)graphicAnnSequenceItem error:(NSError **)error;

- (BOOL)createGraphicAnnSequenceItemAtIndex:(NSUInteger)index withName:(NSString *)layerName error:(NSError **)error;

- (BOOL)addLayerImageReference:(LTDicomElement *)graphicAnnSequenceItem withSOPInstance:(NSString *)imageSOPInstance error:(NSError **)error;

- (NSUInteger)numberOfImageReferencesForLayer:(LTDicomElement *)graphicAnnSequenceItem error:(NSError **)error;

- (nullable NSString *)SOPInstanceForImageReferenceLayer:(LTDicomElement *)graphicAnnSequenceItem atIndex:(NSUInteger)index;

- (void)removeImageReferenceFromLayer:(LTDicomElement *)graphicAnnSequenceItem withSOPInstance:(NSString *)imageSOPInstance;
- (void)removeAllImageReferencesFromLayer:(LTDicomElement *)graphicAnnSequenceItem;
- (void)removeAllImageReferences;

- (nullable LTDicomElement *)layerImageReferenceElementForLayer:(LTDicomElement *)graphicAnnSequenceItem withSOPInstance:(NSString *)imageSOPInstance;



- (BOOL)createGraphicObject:(LTDicomElement *)graphicAnnSequenceItem graphicObject:(LTDicomGraphicObject *)graphicObject checkLayer:(BOOL)checkLayer error:(NSError **)error;
- (void)removeGraphicObject:(LTDicomElement *)graphicAnnSequenceItem graphicObjectIndex:(NSUInteger)index;

- (nullable LTDicomGraphicObject *)informationForGraphicObject:(LTDicomElement *)graphicAnnSequenceItem atIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)setInformation:(LTDicomGraphicObject *)information forGraphicObject:(LTDicomElement *)graphicAnnSequenceItem atIndex:(NSUInteger)index error:(NSError **)error;

- (void)removeAllGraphicObjects:(LTDicomElement *)graphicAnnSequenceItem;

- (NSUInteger)numberOfGraphicObjects:(LTDicomElement *)graphicAnnSequenceItem;
- (NSUInteger)numberOfGraphicObjectPoints:(LTDicomElement *)graphicAnnSequenceItem atIndex:(NSUInteger)index;

- (nullable LTDicomElement *)elementForGraphicObject:(LTDicomElement *)graphicAnnSequenceItem atIndex:(NSUInteger)index;

@end



@interface LTDicomDataSet (CompoundGraphics)

- (BOOL)createCompoundGraphic:(LTDicomElement *)graphicAnnSequenceItem compoundGraphic:(LTDicomCompoundGraphic *)compoundGraphic checkLayer:(BOOL)checkLayer error:(NSError **)error;
- (void)removeCompoundGraphic:(LTDicomElement *)graphicAnnSequenceItem compoundGraphicIndex:(NSUInteger)index;

- (nullable LTDicomCompoundGraphic *)informationForCompoundGraphic:(LTDicomElement *)graphicAnnSequenceItem compoundGraphicIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)setInformation:(LTDicomCompoundGraphic *)information forCompoundGraphic:(LTDicomElement *)graphicAnnSequenceItem compoundGraphicIndex:(NSUInteger)index error:(NSError **)error;

- (NSUInteger)numberOfCompoundGraphicItems:(LTDicomElement *)graphicAnnSequenceItem error:(NSError **)error;
- (NSUInteger)numberOfPointsForCompoundGraphic:(LTDicomElement *)graphicAnnSequenceItem compoundGraphicIndex:(NSUInteger)index error:(NSError **)error;
- (NSUInteger)numberOfMajorTicksForCompoundGraphic:(LTDicomElement *)graphicAnnSequenceItem compoundGraphicIndex:(NSUInteger)index error:(NSError **)error;

- (BOOL)removeAllCompoundGraphics:(LTDicomElement *)graphicAnnSequenceItem error:(NSError **)error;

- (LTDicomElement *)elementForCompoundGraphic:(LTDicomElement *)graphicAnnSequenceItem objectIndex:(NSUInteger)index;

@end



@interface LTDicomDataSet (TextObjects)

- (BOOL)createTextObject:(LTDicomElement *)graphicAnnSequenceItem textObject:(LTDicomTextObject *)textObject checkLayer:(BOOL)checkLayer error:(NSError **)error;
- (BOOL)removeTextObject:(LTDicomElement *)graphicAnnSequenceItem atIndex:(NSUInteger)textObjectIndex error:(NSError **)error;

- (nullable LTDicomTextObject *)informationForTextObject:(LTDicomElement *)graphicAnnSequenceItem atIndex:(NSUInteger)textObjectIndex error:(NSError **)error;
- (BOOL)setInformation:(LTDicomTextObject *)textObject forTextObject:(LTDicomElement *)graphicAnnSequenceItem atIndex:(NSUInteger)textObjectIndex error:(NSError **)error;

- (NSUInteger)numberOfTextObjects:(LTDicomElement *)graphicAnnSequenceItem;
- (void)removeAllTextObjects:(LTDicomElement *)graphicAnnSequenceItem;

- (nullable LTDicomElement *)elementForTextObject:(LTDicomElement *)graphicAnnSequenceItem atIndex:(NSUInteger)objectIndex;

@end



@interface LTDicomDataSet (Jpeg2000)

@property (nonatomic, strong, nullable)           LTDicomJpeg2000Options *jpeg2000Options;
@property (nonatomic, strong, readonly, nullable) LTDicomJpeg2000Options *defaultJpeg2000Options;

- (nullable LTDicomJpeg2000Options *)jpeg2000Options:(NSError **)error;
- (BOOL)setJpeg2000Options:(nullable LTDicomJpeg2000Options *)jpeg2000Options error:(NSError **)error;

@end



@interface LTDicomDataSet (PrivateElements)

- (nullable LTDicomElement *)createPrivateCreatorDataElement:(LTDicomElement *)element elementGroup:(NSUInteger)elementGroup elementNumber:(NSUInteger)elementNumber idCode:(NSString *)idCode error:(NSError **)error;

- (NSUInteger)nextUnusedPrivateTag:(LTDicomElement *)privateCreatorDataElement error:(NSError **)error;

- (nullable LTDicomElement *)findFirstPrivateCreatorDataElement:(nullable LTDicomElement *)element tree:(BOOL)tree idCode:(NSString *)idCode elementGroup:(NSUInteger)elementGroup;
- (nullable LTDicomElement *)findNextPrivateCreatorDataElement:(LTDicomElement *)element tree:(BOOL)tree idCode:(NSString *)idCode elementGroup:(NSUInteger)elementGroup;

- (nullable LTDicomElement *)findFirstPrivateElement:(nullable LTDicomElement *)privateCreatorDataElement;
- (nullable LTDicomElement *)findNextPrivateElement:(LTDicomElement *)element privateCreatorDataElement:(LTDicomElement *)privateCreatorDataElement;

@end



@interface LTDicomDataSet (EncapsulatedDocument)

- (BOOL)encapsulatedDocumentForElement:(LTDicomElement *)element child:(BOOL)child outputData:(NSMutableData *)outputData encapsulatedDocument:(LTDicomEncapsulatedDocument *)encapsulatedDocument conceptNameCodeSequence:(LTDicomCodeSequenceItem *)conceptNameCodeSequence error:(NSError **)error;
- (BOOL)encapsulatedDocumentForElement:(LTDicomElement *)element child:(BOOL)child outputFile:(NSString *)outputFile encapsulatedDocument:(LTDicomEncapsulatedDocument *)encapsulatedDocument conceptNameCodeSequence:(LTDicomCodeSequenceItem *)conceptNameCodeSequence error:(NSError **)error;

- (BOOL)setEncapsulatedDocument:(LTDicomElement *)element child:(BOOL)child data:(NSData *)data encapsulatedDocument:(LTDicomEncapsulatedDocument *)encapsulatedDocument conceptNameCodeSequence:(LTDicomCodeSequenceItem *)conceptNameCodeSequence error:(NSError **)error;
- (BOOL)setEncapsulatedDocument:(LTDicomElement *)element child:(BOOL)child file:(NSString *)file encapsulatedDocument:(LTDicomEncapsulatedDocument *)encapsulatedDocument conceptNameCodeSequence:(LTDicomCodeSequenceItem *)conceptNameCodeSequence error:(NSError **)error;

@end

NS_ASSUME_NONNULL_END
