// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomContextGroupTable.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomContextGroup.h>
#import <Leadtools.Dicom/LTDicomDateTimeValue.h>
#import <Leadtools.Dicom/LTDicomCodedConcept.h>

typedef NS_OPTIONS(NSUInteger, LTDicomContextGroupTableInsertFlags) {
	LTDicomContextGroupTableInsertFlagsNone               = 0,
	LTDicomContextGroupTableInsertFlagsDisallowDuplicates = 0x01,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomContextGroupTable : NSObject

@property (nonatomic, assign, readonly)        NSUInteger count;
@property (class, nonatomic, strong, readonly) LTDicomContextGroupTable *sharedInstance NS_SWIFT_NAME(shared);

- (BOOL)loadXml:(NSString *)file error:(NSError **)error NS_SWIFT_NAME(loadXml(_:));
- (BOOL)loadXmlData:(NSData *)data error:(NSError **)error NS_SWIFT_NAME(loadXml(_:));

- (BOOL)load:(NSString *)contextID error:(NSError **)error NS_SWIFT_NAME(load(id:));
- (BOOL)loadByType:(LTDicomContextIdentifierType)contextID error:(NSError **)error NS_SWIFT_NAME(load(type:));

@property (nonatomic, strong, readonly, nullable) LTDicomContextGroup *first;
@property (nonatomic, strong, readonly, nullable) LTDicomContextGroup *last;

- (nullable LTDicomContextGroup *)next:(LTDicomContextGroup *)contextGroup;
- (nullable LTDicomContextGroup *)previous:(LTDicomContextGroup *)contextGroup;

- (nullable LTDicomContextGroup *)find:(NSString *)contextID NS_SWIFT_NAME(find(id:));
- (nullable LTDicomContextGroup *)findByType:(LTDicomContextIdentifierType)contextID NS_SWIFT_NAME(find(type:));
- (nullable LTDicomContextGroup *)findByIndex:(NSUInteger)index NS_SWIFT_NAME(find(index:));

- (nullable LTDicomContextGroup *)insert:(NSString *)contextIdentifier name:(NSString *)name extensible:(BOOL)isExtensible contextGroupVersion:(LTDicomDateTimeValue *)contextGroupVersion flags:(LTDicomContextGroupTableInsertFlags)flags NS_SWIFT_NAME(insert(id:name:extensible:contextGroupVersion:flags:));
- (nullable LTDicomContextGroup *)insertByType:(LTDicomContextIdentifierType)contextIdentifier name:(NSString *)name extensible:(BOOL)isExtensible contextGroupVersion:(LTDicomDateTimeValue *)contextGroupVersion flags:(LTDicomContextGroupTableInsertFlags)flags NS_SWIFT_NAME(insert(type:name:extensible:contextGroupVersion:flags:));

- (void)reset;
- (LTDicomContextGroup *)deleteContextGroup:(LTDicomContextGroup *)contextGroup;

- (BOOL)isDefaultContextGroup:(LTDicomContextGroup *)group;
- (BOOL)exists:(LTDicomContextGroup *)group;



- (nullable LTDicomCodedConcept *)firstCodedConcept:(LTDicomContextGroup *)contextGroup;
- (nullable LTDicomCodedConcept *)lastCodedConcept:(LTDicomContextGroup *)contextGroup;
- (nullable LTDicomCodedConcept *)nextCodedConcept:(LTDicomCodedConcept *)codedConcept;
- (nullable LTDicomCodedConcept *)previousCodedConcept:(LTDicomCodedConcept *)codedConcept;
- (nullable LTDicomContextGroup *)contextGroupForCodedConcept:(LTDicomCodedConcept *)codedConcept;

- (NSUInteger)codedConceptCount:(LTDicomContextGroup *)contextGroup;

- (nullable LTDicomCodedConcept *)findCodedConcept:(LTDicomContextGroup *)contextGroup codingSchemeDesignator:(NSString *)codingSchemeDesignator codeValue:(NSString *)codeValue NS_SWIFT_NAME(findCodedConcept(group:codingSchemeDesignator:codeValue:));
- (nullable LTDicomCodedConcept *)findCodedConceptByIndex:(LTDicomContextGroup *)contextGroup index:(NSUInteger)index NS_SWIFT_NAME(findCodedConcept(group:index:));

- (BOOL)setCodeMeaning:(NSString *)codeMeaning forCodedConcept:(LTDicomCodedConcept *)codedConcept;

- (nullable LTDicomCodedConcept *)insertCodedConcept:(LTDicomContextGroup *)contextGroup codingSchemeDesignator:(NSString *)codingSchemeDesignator codingSchemeVersion:(NSString *)codingSchemeVersion codeValue:(NSString *)codeValue codeMeaning:(NSString *)codeMeaning contextGroupLocalVersion:(LTDicomDateTimeValue *)contextGroupLocalVersion contextGroupExtensionCreatorUID:(NSString *)contextGroupExtensionCreatorUID flags:(LTDicomContextGroupTableInsertFlags)flags;

- (nullable LTDicomCodedConcept *)deleteCodedConcept:(LTDicomCodedConcept *)codedConcept;

- (BOOL)codedConceptExists:(LTDicomCodedConcept *)codedConcept;

@end

NS_ASSUME_NONNULL_END
