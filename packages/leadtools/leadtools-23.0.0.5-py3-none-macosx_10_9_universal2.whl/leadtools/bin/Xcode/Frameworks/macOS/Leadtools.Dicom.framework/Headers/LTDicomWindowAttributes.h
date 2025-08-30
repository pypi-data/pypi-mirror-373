// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomWindowAttributes.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomWindowAttributes : NSObject

@property (nonatomic, assign) double windowCenter;
@property (nonatomic, assign) double windowWidth;

@property (nonatomic, copy)   NSString *explanation;

@end

NS_ASSUME_NONNULL_END
