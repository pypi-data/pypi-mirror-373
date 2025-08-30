// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomAnnotationObject.h
//  Leadtools.Dicom
//

typedef NS_OPTIONS(NSUInteger, LTDicomAnnotationOptions) {
	LTDicomAnnotationOptionsNone                      = 0x000,
	LTDicomAnnotationOptionsLine                      = 0x001,
	LTDicomAnnotationOptionsFill                      = 0x002,
	LTDicomAnnotationOptionsText                      = 0x004,
	LTDicomAnnotationOptionsGraphicGroupId            = 0x008,
	LTDicomAnnotationOptionsCompoundGraphicInstanceId = 0x010,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomAnnotationObject : NSObject //ABSTRACT CLASS

@property (nonatomic, copy, nullable)   NSString *layerName;

@property (nonatomic, assign)           NSUInteger compoundGraphicInstanceId;
@property (nonatomic, assign)           NSUInteger graphicGroupId;

@property (nonatomic, assign)           LTDicomAnnotationOptions options;

@property (nonatomic, assign, readonly) BOOL isValidCompoundGraphicInstanceId;
@property (nonatomic, assign, readonly) BOOL isValidGraphicGroupId;

@end

NS_ASSUME_NONNULL_END
