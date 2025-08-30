// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomTextStyle.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomShadowStyle.h>

typedef NS_OPTIONS(NSUInteger, LTDicomAnnotationTextOptions) {
	LTDicomAnnotationTextOptionsNone     = 0x000,
	LTDicomAnnotationTextOptionsFontName = 0x001,
};

typedef NS_ENUM(NSInteger, LTDicomAnnotationHorizontalAlignmentType) {
	LTDicomAnnotationHorizontalAlignmentTypeNone   = 0,
	LTDicomAnnotationHorizontalAlignmentTypeLeft   = 1,
	LTDicomAnnotationHorizontalAlignmentTypeCenter = 2,
	LTDicomAnnotationHorizontalAlignmentTypeRight  = 3,
};

typedef NS_ENUM(NSInteger, LTDicomAnnotationVerticalAlignmentType) {
	LTDicomAnnotationVerticalAlignmentTypeNone   = 0,
	LTDicomAnnotationVerticalAlignmentTypeTop    = 1,
	LTDicomAnnotationVerticalAlignmentTypeCenter = 2,
	LTDicomAnnotationVerticalAlignmentTypeBottom = 3,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomTextStyle : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign)                  LTDicomAnnotationTextOptions textOptions;
@property (nonatomic, assign)                  LTDicomAnnotationHorizontalAlignmentType horizontalAlign;
@property (nonatomic, assign)                  LTDicomAnnotationVerticalAlignmentType verticalAlign;

@property (nonatomic, strong, nullable)        NSString *fontName;
@property (nonatomic, strong, nullable)        NSString *cssFontName;

@property (nonatomic, assign, null_resettable) const uint16_t *textColorCieLabValue NS_RETURNS_INNER_POINTER; //[3]

@property (nonatomic, strong)                  LTDicomShadowStyle *shadow;

@property (nonatomic, assign)                  BOOL underlined;
@property (nonatomic, assign)                  BOOL bold;
@property (nonatomic, assign)                  BOOL italic;

@end

NS_ASSUME_NONNULL_END
