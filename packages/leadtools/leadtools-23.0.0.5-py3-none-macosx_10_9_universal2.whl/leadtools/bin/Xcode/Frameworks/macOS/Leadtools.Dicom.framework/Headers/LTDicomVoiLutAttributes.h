// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomVoiLutAttributes.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomVoiLutAttributes : NSObject

@property (nonatomic, assign)         NSUInteger numberOfEntries;
@property (nonatomic, assign)         NSUInteger entryBits;

@property (nonatomic, assign)         NSInteger firstStoredPixelValueMapped;

@property (nonatomic, copy, nullable) NSString *lutExplanation;

@end

NS_ASSUME_NONNULL_END
