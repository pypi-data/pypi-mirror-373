// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomShadowStyle.h
//  Leadtools.Dicom
//

#import <CoreGraphics/CGBase.h> // CGFloat

typedef NS_ENUM(NSInteger, LTDicomAnnotationShadowStyleType) {
	LTDicomAnnotationShadowStyleTypeOff      = 0,
	LTDicomAnnotationShadowStyleTypeNormal   = 1,
	LTDicomAnnotationShadowStyleTypeOutlined = 2,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomShadowStyle : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign)                  LTDicomAnnotationShadowStyleType shadowStyle;

@property (nonatomic, assign)                  CGFloat shadowOffsetX;
@property (nonatomic, assign)                  CGFloat shadowOffsetY;

@property (nonatomic, assign)                  float shadowOpacity;

@property (nonatomic, assign, null_resettable) const uint16_t *shadowColorCieLabValue NS_RETURNS_INNER_POINTER; //[3]

@end

NS_ASSUME_NONNULL_END
