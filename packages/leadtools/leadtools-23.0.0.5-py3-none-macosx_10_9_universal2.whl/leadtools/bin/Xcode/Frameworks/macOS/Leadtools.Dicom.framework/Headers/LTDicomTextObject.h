// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomTextObject.h
//  Leadtools.Dicom
//

typedef NS_ENUM(NSInteger, LTDicomAnnotationUnitsRelativityType) {
	LTDicomAnnotationUnitsRelativityTypePixel   = 1,
	LTDicomAnnotationUnitsRelativityTypeDisplay = 2,
};

typedef NS_ENUM(NSInteger, LTTextAnnotationJustificationType) {
	LTTextAnnotationJustificationTypeLeft   = 0,
	LTTextAnnotationJustificationTypeRight  = 1,
	LTTextAnnotationJustificationTypeCenter = 2,
};

#import <Leadtools.Dicom/LTDicomAnnotationObject.h>
#import <Leadtools.Dicom/LTDicomTextStyle.h>

typedef struct {
    CGFloat x;
    CGFloat y;
} LTDicomAnnotationPoint;

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomTextObject : LTDicomAnnotationObject

@property (nonatomic, copy, nullable) NSString *textValue;

@property (nonatomic, assign)         LTDicomAnnotationPoint anchorPoint;
@property (nonatomic, assign)         LTDicomAnnotationPoint tlhCorner;
@property (nonatomic, assign)         LTDicomAnnotationPoint brhCorner;

@property (nonatomic, assign)         LTDicomAnnotationUnitsRelativityType boundingBoxUnits;
@property (nonatomic, assign)         LTTextAnnotationJustificationType textJustification;
@property (nonatomic, assign)         LTDicomAnnotationUnitsRelativityType anchorPointUnits;

@property (nonatomic, assign)         BOOL anchorPointsVisible;

@property (nonatomic, strong)         LTDicomTextStyle *textStyle;

@end

NS_ASSUME_NONNULL_END
