// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomTagTable.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomTag.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomTagTable : NSObject

@property (nonatomic, assign, readonly)        NSUInteger count;
@property (class, nonatomic, strong, readonly) LTDicomTagTable *sharedInstance NS_SWIFT_NAME(shared);

- (void)defaultTable;
- (void)defaultTable:(BOOL)ignorePrivateTags NS_SWIFT_NAME(defaultTable(ignorePrivateTags:));
- (void)reset;

- (BOOL)loadXml:(NSString *)file error:(NSError **)error NS_SWIFT_NAME(loadXml(_:));
- (BOOL)loadXmlData:(NSData *)data error:(NSError **)error NS_SWIFT_NAME(loadXml(_:));

- (nullable LTDicomTag *)insert:(LTDicomTagCode)code mask:(NSUInteger)mask vr:(LTDicomVRType)vr minVM:(NSUInteger)minVM maxVM:(NSUInteger)maxVM vmDivider:(NSUInteger)VMDivider name:(NSString *)name NS_SWIFT_NAME(insert(code:mask:vr:minVM:maxVM:vmDivisder:name:));

- (nullable LTDicomTag *)removeTag:(LTDicomTag *)tag;

@property (nonatomic, strong, readonly, nullable) LTDicomTag *first;
@property (nonatomic, strong, readonly, nullable) LTDicomTag *last;

- (nullable LTDicomTag *)previous:(LTDicomTag *)tag;
- (nullable LTDicomTag *)next:(LTDicomTag *)tag;

- (BOOL)exists:(LTDicomTag *)tag;

- (nullable LTDicomTag *)find:(LTDicomTagCode)code NS_SWIFT_NAME(find(code:));
- (nullable LTDicomTag *)findByIndex:(NSUInteger)index NS_SWIFT_NAME(find(index:));

- (BOOL)setName:(NSString *)name forTag:(LTDicomTag *)tag;

@end

NS_ASSUME_NONNULL_END
