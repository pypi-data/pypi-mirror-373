// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomGraphicLayer.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomGraphicLayer : NSObject

@property (nonatomic, copy, nullable) NSString *layerName;
@property (nonatomic, copy, nullable) NSString *layerDescription;

@property (nonatomic, assign)         NSInteger layerOrder;
@property (nonatomic, assign)         NSInteger grayscale;
@property (nonatomic, assign)         NSInteger rgbLayerColor;

@end

NS_ASSUME_NONNULL_END
