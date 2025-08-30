// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomOverlayBoxParameters.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomOverlayBoxParameters : NSObject

@property (nonatomic, assign)         NSInteger overlayOriginRow;
@property (nonatomic, assign)         NSInteger overlayOriginColumn;
@property (nonatomic, assign)         NSInteger magnifyToNumberOfColumns;

@property (nonatomic, copy, nullable) NSString *overlayOrImageMagnification;
@property (nonatomic, copy, nullable) NSString *overlayMagnificationType;
@property (nonatomic, copy, nullable) NSString *overlayForegroundDensity;
@property (nonatomic, copy, nullable) NSString *overlayBackgroundDensity;
@property (nonatomic, copy, nullable) NSString *overlaySmoothingType;

@end

NS_ASSUME_NONNULL_END
