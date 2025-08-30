// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomJpeg2000Options.h
//  Leadtools.Dicom
//

#import <Leadtools/LTPrimitives.h>

typedef NS_ENUM(NSInteger, LTDicomJpeg2000CompressionControl) {
	LTDicomJpeg2000CompressionControlLossless      = 0,
	LTDicomJpeg2000CompressionControlRatio         = 1,
	LTDicomJpeg2000CompressionControlTargetSize    = 2,
	LTDicomJpeg2000CompressionControlQualityFactor = 3,
};

typedef NS_ENUM(NSInteger, LTDicomJpeg2000ProgressionsOrder) {
	LTDicomJpeg2000ProgressionsOrderLayerResolutionComponentPosition = 0,
	LTDicomJpeg2000ProgressionsOrderResolutionLayerComponentPosition = 1,
	LTDicomJpeg2000ProgressionsOrderResolutionPositionComponentLayer = 2,
	LTDicomJpeg2000ProgressionsOrderPositionComponentResolutionLayer = 3,
	LTDicomJpeg2000ProgressionsOrderComponentPositionResolutionLayer = 4,
};

typedef NS_ENUM(NSInteger, LTDicomJpeg2000RegionOfInterest) {
	LTDicomJpeg2000RegionOfInterestUseLeadRegion      = 0,
	LTDicomJpeg2000RegionOfInterestUseOptionRectangle = 1,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomJpeg2000Options : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign) BOOL useColorTransform;
@property (nonatomic, assign) BOOL derivedQuantization;
@property (nonatomic, assign) BOOL useSopMarker;
@property (nonatomic, assign) BOOL useEphMarker;
@property (nonatomic, assign) BOOL useRegionOfInterest;

@property (nonatomic, assign) LTDicomJpeg2000CompressionControl compressionControl;
@property (nonatomic, assign) LTDicomJpeg2000ProgressionsOrder progressingOrder;
@property (nonatomic, assign) LTDicomJpeg2000RegionOfInterest regionOfInterest;

@property (nonatomic, assign) float compressionRatio;
@property (nonatomic, assign) float regionOfInterestWeight;

@property (nonatomic, assign) uint64_t targetFileSize;

@property (nonatomic, assign) NSInteger imageAreaHorizontalOffset;
@property (nonatomic, assign) NSInteger imageAreaVerticalOffset;
@property (nonatomic, assign) NSInteger referenceTileWidth;
@property (nonatomic, assign) NSInteger referenceTileHeight;
@property (nonatomic, assign) NSInteger tileHorizontalOffset;
@property (nonatomic, assign) NSInteger tileVerticalOffset;
@property (nonatomic, assign) NSInteger decompositionLevels;

@property (nonatomic, assign) LeadRect regionOfInterestRectangle;

@property (class, nonatomic, assign, readonly) NSInteger maximumNumberOfComponents;
@property (class, nonatomic, assign, readonly) NSInteger maximumDecompressionLevels;

@end

NS_ASSUME_NONNULL_END
