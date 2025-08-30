// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomImageBoxParameters.h
//  Leadtools.Dicom
//

#import <CoreGraphics/CGBase.h> // CGFloat

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomImageBoxParameters : NSObject

@property (nonatomic, assign)         NSInteger imagePosition;
@property (nonatomic, assign)         NSInteger minDensity;
@property (nonatomic, assign)         NSInteger maxDensity;

@property (nonatomic, assign)         CGFloat requestedImageSize;

@property (nonatomic, copy, nullable) NSString *polarity;
@property (nonatomic, copy, nullable) NSString *magnificationType;
@property (nonatomic, copy, nullable) NSString *smoothingType;
@property (nonatomic, copy, nullable) NSString *configurationInformation;
@property (nonatomic, copy, nullable) NSString *requestedDecimateCropBehavior;

@end

NS_ASSUME_NONNULL_END
