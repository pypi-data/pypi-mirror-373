// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomGraphicObject.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomAnnotationObject.h>
#import <Leadtools.Dicom/LTDicomTextObject.h>
#import <Leadtools.Dicom/LTDicomLineStyle.h>
#import <Leadtools.Dicom/LTDicomFillStyle.h>

typedef NS_ENUM(NSInteger, LTDicomAnnotationType) {
	LTDicomAnnotationTypePoint        = 1,
	LTDicomAnnotationTypePolyline     = 2,
	LTDicomAnnotationTypeInterpolated = 3,
	LTDicomAnnotationTypeCircle       = 4,
	LTDicomAnnotationTypeEllipse      = 5,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomGraphicObject : LTDicomAnnotationObject

@property (nonatomic, assign)                     LTDicomAnnotationType type;
@property (nonatomic, assign)                     LTDicomAnnotationUnitsRelativityType units;

@property (nonatomic, assign)                     BOOL filled;

@property (nonatomic, assign, readonly)           NSInteger annotationPointCount;

@property (nonatomic, copy, nullable)             LTDicomLineStyle *lineStyle;
@property (nonatomic, copy, nullable)             LTDicomFillStyle *fillStyle;

@property (nonatomic, strong, readonly, nullable) NSArray<NSValue *> *annotationPoints; //LTDicomAnnoationPoint

- (void)setAnnotationPoints:(LTDicomAnnotationPoint *)annotationPoints count:(NSUInteger)count;

@end

NS_ASSUME_NONNULL_END
