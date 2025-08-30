// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomCompoundGraphic.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomAnnotationObject.h>
#import <Leadtools.Dicom/LTDicomGraphicObject.h>
#import <Leadtools.Dicom/LTDicomTextObject.h>
#import <Leadtools.Dicom/LTDicomLineStyle.h>
#import <Leadtools.Dicom/LTDicomFillStyle.h>
#import <Leadtools.Dicom/LTDicomTextStyle.h>
#import <Leadtools.Dicom/LTDicomMajorTick.h>

typedef NS_ENUM(NSInteger, LTDicomAnnotationCompoundGraphicType) {
	LTDicomAnnotationCompoundGraphicTypeMultiLine    = 6,
	LTDicomAnnotationCompoundGraphicTypeInfiniteLine = 7,
	LTDicomAnnotationCompoundGraphicTypeCutLine      = 8,
	LTDicomAnnotationCompoundGraphicTypeRangeLine    = 9,
	LTDicomAnnotationCompoundGraphicTypeRuler        = 10,
	LTDicomAnnotationCompoundGraphicTypeAxis         = 11,
	LTDicomAnnotationCompoundGraphicTypeCrossHair    = 12,
	LTDicomAnnotationCompoundGraphicTypeArrow        = 13,
	LTDicomAnnotationCompoundGraphicTypeRectangle    = 14,
	LTDicomAnnotationCompoundGraphicTypeEllipse      = 5,
};

typedef NS_ENUM(NSInteger, LTDicomAnnotationTickAlignmentType) {
	LTDicomAnnotationTickAlignmentTypeNone   = 0,
	LTDicomAnnotationTickAlignmentTypeTop    = 1,
	LTDicomAnnotationTickAlignmentTypeCenter = 2,
	LTDicomAnnotationTickAlignmentTypeBottom = 3,
};

typedef NS_ENUM(NSInteger, LTDicomAnnotationTickLabelAlignmentType) {
	LTDicomAnnotationTickLabelAlignmentTypeNone   = 0,
	LTDicomAnnotationTickLabelAlignmentTypeTop    = 1,
	LTDicomAnnotationTickLabelAlignmentTypeBottom = 3,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomCompoundGraphic : LTDicomAnnotationObject

@property (nonatomic, assign)           LTDicomAnnotationCompoundGraphicType type;
@property (nonatomic, assign)           LTDicomAnnotationUnitsRelativityType units;
@property (nonatomic, assign)           LTDicomAnnotationTickAlignmentType tickAlignment;
@property (nonatomic, assign)           LTDicomAnnotationTickLabelAlignmentType tickLabelAlignment;

@property (nonatomic, assign)           BOOL filled;
@property (nonatomic, assign)           BOOL showTickLabel;

@property (nonatomic, assign, readonly) NSUInteger annotationPointCount;
@property (nonatomic, assign, readonly) NSUInteger majorTickCount;

@property (nonatomic, assign, readonly) const LTDicomAnnotationPoint *annotationPoints NS_RETURNS_INNER_POINTER;
- (void)setAnnotationPoints:(LTDicomAnnotationPoint *)annotationPoints count:(NSUInteger)count;

@property (nonatomic, assign)           LTDicomAnnotationPoint rotationPoint;

@property (nonatomic, copy, nullable)   LTDicomLineStyle *lineStyle;
@property (nonatomic, copy, nullable)   LTDicomFillStyle *fillStyle;
@property (nonatomic, copy, nullable)   LTDicomTextStyle *textStyle;

@property (nonatomic, assign)           double rotationAngle;
@property (nonatomic, assign)           float gapLength;
@property (nonatomic, assign)           float diameterOfVisibility;

@property (nonatomic, strong, readonly) NSMutableArray<LTDicomMajorTick *> *majorTicks;

@end

NS_ASSUME_NONNULL_END
