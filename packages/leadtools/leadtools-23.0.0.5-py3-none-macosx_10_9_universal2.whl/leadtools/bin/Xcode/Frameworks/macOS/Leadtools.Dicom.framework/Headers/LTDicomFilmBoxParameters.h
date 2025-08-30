// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomFilmBoxParameters.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomFilmBoxParameters : NSObject

@property (nonatomic, assign)         NSInteger maxDensity;
@property (nonatomic, assign)         NSInteger minDensity;
@property (nonatomic, assign)         NSInteger illumination;
@property (nonatomic, assign)         NSInteger reflectedAmbientLight;

@property (nonatomic, copy, nullable) NSString *imageDisplayFormat;
@property (nonatomic, copy, nullable) NSString *filmOrientation;
@property (nonatomic, copy, nullable) NSString *filmSizeID;
@property (nonatomic, copy, nullable) NSString *magnificationType;
@property (nonatomic, copy, nullable) NSString *configurationInformation;
@property (nonatomic, copy, nullable) NSString *annotationDisplayFormatID;
@property (nonatomic, copy, nullable) NSString *smoothingType;
@property (nonatomic, copy, nullable) NSString *borderDensity;
@property (nonatomic, copy, nullable) NSString *emptyImageDensity;
@property (nonatomic, copy, nullable) NSString *trim;
@property (nonatomic, copy, nullable) NSString *requestedResolutionID;

@end

NS_ASSUME_NONNULL_END
