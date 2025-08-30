// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomModalityLutAttributes.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomModalityLutAttributes : NSObject

@property (nonatomic, assign)         BOOL isModalityLutSequence;
@property (nonatomic, assign)         BOOL isRescaleSlopeIntercept;

@property (nonatomic, assign)         NSUInteger numberOfEntries;
@property (nonatomic, assign)         NSUInteger entryBits;

@property (nonatomic, assign)         NSInteger firstStoredPixelValueMapped;

@property (nonatomic, assign)         double rescaleIntercept;
@property (nonatomic, assign)         double rescaleSlope;

@property (nonatomic, copy, nullable) NSString *lutExplanation;
@property (nonatomic, copy, nullable) NSString *lutType;
@property (nonatomic, copy, nullable) NSString *rescaleType;

@end

NS_ASSUME_NONNULL_END
