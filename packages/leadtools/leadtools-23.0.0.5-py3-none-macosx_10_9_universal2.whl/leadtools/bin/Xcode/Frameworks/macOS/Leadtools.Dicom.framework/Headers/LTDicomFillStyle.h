// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomFillStyle.h
//  Leadtools.Dicom
//

typedef NS_OPTIONS(NSUInteger, LTDicomAnnotationFillOptions) {
	LTDicomAnnotationFillOptionsNone                       = 0x000,
	LTDicomAnnotationFillOptionsPatternOffColorCielabValue = 0x001,
	LTDicomAnnotationFillOptionsPatternOffOpacity          = 0x002,
};

typedef NS_ENUM(NSInteger, LTDicomAnnotationFillModeType) {
	LTDicomAnnotationFillModeTypeNone      = 0,
	LTDicomAnnotationFillModeTypeSolid     = 1,
	LTDicomAnnotationFillModeTypeStippeled = 2,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomFillStyle : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign)                  LTDicomAnnotationFillOptions fillOptions;
@property (nonatomic, assign)                  LTDicomAnnotationFillModeType fillMode;

@property (nonatomic, assign)                  float patternOnOpacity;
@property (nonatomic, assign)                  float patternOffOpacity;

@property (nonatomic, assign, null_resettable) const uint16_t *patternOnColorCieLabValue NS_RETURNS_INNER_POINTER; //[3]
@property (nonatomic, assign, null_resettable) const uint16_t *patternOffColorCieLabValue NS_RETURNS_INNER_POINTER; //[3]

@property (nonatomic, assign, null_resettable) const uint8_t *fillPattern NS_RETURNS_INNER_POINTER; //[128]

@end

NS_ASSUME_NONNULL_END
