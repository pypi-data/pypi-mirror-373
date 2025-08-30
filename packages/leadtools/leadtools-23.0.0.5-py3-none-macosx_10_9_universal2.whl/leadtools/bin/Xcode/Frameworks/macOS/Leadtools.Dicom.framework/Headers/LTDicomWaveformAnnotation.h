// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomWaveformAnnotation.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomCodeSequenceItem.h>
#import <Leadtools.Dicom/LTDicomDateTimeValue.h>

typedef NS_ENUM(NSInteger, LTDicomTemporalRangeType) {
	LTDicomTemporalRangeTypeUndefined    = 0,
	LTDicomTemporalRangeTypePoint        = 1,
	LTDicomTemporalRangeTypeMultipoint   = 2,
	LTDicomTemporalRangeTypeSegment      = 3,
	LTDicomTemporalRangeTypeMultisegment = 4,
	LTDicomTemporalRangeTypeBegin        = 5,
	LTDicomTemporalRangeTypeEnd          = 6,
};

typedef NS_ENUM(NSInteger, LTDicomTemporalPointType) {
	LTDicomTemporalPointTypeUndefined,
	LTDicomTemporalPointTypeReferencedSamplePositions,
	LTDicomTemporalPointTypeReferencedTimeOffsets,
	LTDicomTemporalPointTypeReferencedDatetime,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomWaveformAnnotation : NSObject

@property (nonatomic, assign, readonly) NSUInteger numericValueCount;
@property (nonatomic, assign, readonly) NSUInteger temporalPointCount;
@property (nonatomic, assign)           NSInteger annGroupNumber;

@property (nonatomic, assign, readonly) LTDicomTemporalPointType temporalPointType;
@property (nonatomic, assign)           LTDicomTemporalRangeType temporalRange;

@property (nonatomic, strong, nullable) LTDicomCodeSequenceItem *codedName;
@property (nonatomic, strong, nullable) LTDicomCodeSequenceItem *codedValue;
@property (nonatomic, strong, nullable) LTDicomCodeSequenceItem *measurementUnits;

@property (nonatomic, copy, nullable)   NSString *unformattedTextValue;

- (void)setNumericValue:(double *)values length:(NSUInteger)length;
- (nullable double *)getNumericValue NS_RETURNS_INNER_POINTER;
- (NSUInteger)getNumericValue:(double *)buffer length:(NSUInteger)length;

- (void)setReferencedSamplePositions:(unsigned int *)positions length:(NSUInteger)length;
- (nullable const unsigned int *)getReferencedSamplePositions NS_RETURNS_INNER_POINTER;
- (NSUInteger)getReferencedSamplePositions:(unsigned int *)buffer length:(NSUInteger)length;

- (void)setReferencedTimeOffsets:(double *)offsets length:(NSUInteger)length;
- (nullable double *)getReferencedTimeOffsets NS_RETURNS_INNER_POINTER;
- (NSUInteger)getReferencedTimeOffsets:(double *)buffer length:(NSUInteger)length;

@property (nonatomic, strong, nullable) NSArray<LTDicomDateTimeValue *> *referencedDateTime;

@end

NS_ASSUME_NONNULL_END
