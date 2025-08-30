// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomImageInformation.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomImageFlags.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomImageInformation : NSObject

@property (nonatomic, assign)         LTDicomImageCompressionType compression;
@property (nonatomic, assign)         LTDicomImagePhotometricInterpretationType photometricInterpretation;

@property (nonatomic, copy, nullable) NSString *photometricInterpretationName;

@property (nonatomic, assign)         NSUInteger samplesPerPixel;
@property (nonatomic, assign)         NSUInteger bitsAllocated;
@property (nonatomic, assign)         NSUInteger bitsStored;
@property (nonatomic, assign)         NSUInteger highBit;
@property (nonatomic, assign)         NSUInteger redEntries;
@property (nonatomic, assign)         NSUInteger redFirst;
@property (nonatomic, assign)         NSUInteger redBits;
@property (nonatomic, assign)         NSUInteger greenEntries;
@property (nonatomic, assign)         NSUInteger greenFirst;
@property (nonatomic, assign)         NSUInteger greenBits;
@property (nonatomic, assign)         NSUInteger blueEntries;
@property (nonatomic, assign)         NSUInteger blueFirst;
@property (nonatomic, assign)         NSUInteger blueBits;
@property (nonatomic, assign)         NSUInteger paletteEntries;
@property (nonatomic, assign)         NSUInteger paletteFirst;
@property (nonatomic, assign)         NSUInteger frameCount;

@property (nonatomic, assign)         NSInteger rows;
@property (nonatomic, assign)         NSInteger columns;
@property (nonatomic, assign)         NSInteger pixelRepresentation;
@property (nonatomic, assign)         NSInteger planarConfiguration;
@property (nonatomic, assign)         NSInteger xResolution;
@property (nonatomic, assign)         NSInteger yResolution;
@property (nonatomic, assign)         NSInteger smallestImagePixelValue;
@property (nonatomic, assign)         NSInteger largestImagePixelValue;
@property (nonatomic, assign)         NSInteger bitsPerPixel;

@property (nonatomic, assign)         BOOL isSmallestImagePixelValue;
@property (nonatomic, assign)         BOOL isLargestImagePixelValue;
@property (nonatomic, assign)         BOOL isGray;

@end

NS_ASSUME_NONNULL_END
