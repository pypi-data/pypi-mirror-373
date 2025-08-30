// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomLineStyle.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomShadowStyle.h>

typedef NS_OPTIONS(NSUInteger, LTDicomAnnotationLineOptions) {
	LTDicomAnnotationLineOptionsNone                       = 0x000,
	LTDicomAnnotationLineOptionsPatternOffColorCielabValue = 0x001,
	LTDicomAnnotationLineOptionsPatternOffOpacity          = 0x002,
};

typedef NS_ENUM(NSInteger, LTDicomAnnotationDashStyleType) {
	LTDicomAnnotationDashStyleTypeNone   = 0,
	LTDicomAnnotationDashStyleTypeSolid  = 1,
	LTDicomAnnotationDashStyleTypeDashed = 2,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomLineStyle : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign)                  LTDicomAnnotationLineOptions lineOptions;
@property (nonatomic, assign)                  LTDicomAnnotationDashStyleType lineDashingStyle;

@property (nonatomic, assign)                  float patternOnOpacity;
@property (nonatomic, assign)                  float patternOffOpacity;

@property (nonatomic, assign)                  CGFloat lineThickness;

@property (nonatomic, assign)                  NSUInteger linePattern;

@property (nonatomic, strong)                  LTDicomShadowStyle *shadow;

@property (nonatomic, assign, null_resettable) const uint16_t *patternOnColorCieLabValue NS_RETURNS_INNER_POINTER; //[3]
@property (nonatomic, assign, null_resettable) const uint16_t *patternOffColorCieLabValue NS_RETURNS_INNER_POINTER; //[3]

@end

NS_ASSUME_NONNULL_END
