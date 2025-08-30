// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomUidTable.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomUid.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomUidTable : NSObject

@property (nonatomic, assign, readonly)        NSUInteger count;
@property (class, nonatomic, strong, readonly) LTDicomUidTable *sharedInstance NS_SWIFT_NAME(shared);

- (void)defaultTable;
- (void)reset;

- (BOOL)loadXml:(NSString *)file error:(NSError **)error NS_SWIFT_NAME(loadXml(_:));
- (BOOL)loadXmlData:(NSData *)data error:(NSError **)error NS_SWIFT_NAME(loadXml(_:));

- (nullable LTDicomUid *)insert:(NSString *)code name:(NSString *)name type:(LTDicomUIDCategory)type NS_SWIFT_NAME(insert(code:name:type:));

- (nullable LTDicomUid *)removeUid:(LTDicomUid *)uid;

@property (nonatomic, strong, readonly, nullable) LTDicomUid *first;
@property (nonatomic, strong, readonly, nullable) LTDicomUid *last;

- (nullable LTDicomUid *)previous:(LTDicomUid *)uid;
- (nullable LTDicomUid *)next:(LTDicomUid *)uid;

- (BOOL)exists:(LTDicomUid *)uid;

- (nullable LTDicomUid *)find:(NSString *)code NS_SWIFT_NAME(find(code:));
- (nullable LTDicomUid *)findByIndex:(NSUInteger)index NS_SWIFT_NAME(find(index:));

- (BOOL)setName:(NSString *)name forUid:(LTDicomUid *)uid;

@end

NS_ASSUME_NONNULL_END
