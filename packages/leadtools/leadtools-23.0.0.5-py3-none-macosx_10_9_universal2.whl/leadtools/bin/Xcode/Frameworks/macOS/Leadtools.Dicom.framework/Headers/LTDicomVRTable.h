// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomVRTable.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomVR.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomVRTable : NSObject

@property (nonatomic, assign, readonly)        NSUInteger count;
@property (class, nonatomic, strong, readonly) LTDicomVRTable *sharedInstance NS_SWIFT_NAME(shared);

- (void)defaultTable;
- (void)reset;

- (nullable LTDicomVR *)removeVR:(LTDicomVR *)vr;

@property (nonatomic, strong, readonly, nullable) LTDicomVR *first;
@property (nonatomic, strong, readonly, nullable) LTDicomVR *last;

- (nullable LTDicomVR *)previous:(LTDicomVR *)vr;
- (nullable LTDicomVR *)next:(LTDicomVR *)vr;

- (BOOL)exists:(LTDicomVR *)vr;

- (nullable LTDicomVR *)find:(LTDicomVRType)type NS_SWIFT_NAME(find(type:));
- (nullable LTDicomVR *)findByIndex:(NSUInteger)index NS_SWIFT_NAME(find(index:));

- (BOOL)setName:(NSString *)name forVR:(LTDicomVR *)vr;

@end

NS_ASSUME_NONNULL_END
