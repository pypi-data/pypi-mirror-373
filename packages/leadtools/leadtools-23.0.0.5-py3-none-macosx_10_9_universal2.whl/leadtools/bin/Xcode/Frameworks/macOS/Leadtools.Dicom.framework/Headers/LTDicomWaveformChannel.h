// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomWaveformChannel.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomCodeSequenceItem.h>
#import <Leadtools.Dicom/LTDicomWaveformAnnotation.h>
#import <Leadtools.Dicom/LTDicomWaveformGroup.h>

typedef NS_ENUM(NSInteger, LTDicomChannelStatusType) {
	LTDicomChannelStatusTypeOK           = 0x01,
	LTDicomChannelStatusTypeTestData     = 0x02,
	LTDicomChannelStatusTypeDisconnected = 0x04,
	LTDicomChannelStatusTypeQuestionable = 0x08,
	LTDicomChannelStatusTypeInvalid      = 0x10,
	LTDicomChannelStatusTypeUncalibrated = 0x20,
	LTDicomChannelStatusTypeUnzeroed     = 0x40,
};

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomChannelSensitivity : NSObject

@property (nonatomic, assign, readonly)           BOOL include;

@property (nonatomic, assign, readonly)           double sensitivity;
@property (nonatomic, assign, readonly)           double sensitivityCF;
@property (nonatomic, assign, readonly)           double baseline;

@property (nonatomic, strong, readonly, nullable) LTDicomCodeSequenceItem *sensitivityUnits;

@end

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomWaveformChannel : NSObject

@property (nonatomic, assign, readonly)           NSUInteger index;
@property (nonatomic, assign, readonly)           NSUInteger channelSamplesCount;
@property (nonatomic, assign, readonly)           NSUInteger annotationCount;

@property (nonatomic, assign, readonly)           NSInteger waveformChannelNumber;
@property (nonatomic, assign, readonly)           NSInteger channelMinimumValue;
@property (nonatomic, assign, readonly)           NSInteger channelMaximumValue;

@property (nonatomic, assign, readonly)           double channelTimeSkew;
@property (nonatomic, assign, readonly)           double channelSampleSkew;
@property (nonatomic, assign, readonly)           double channelOffset;
@property (nonatomic, assign, readonly)           double filterLowFrequency;
@property (nonatomic, assign, readonly)           double filterHighFrequency;
@property (nonatomic, assign, readonly)           double notchFilterFrequency;
@property (nonatomic, assign, readonly)           double notchFilterBandwidth;

@property (nonatomic, assign)                     LTDicomChannelStatusType channelStatus;

@property (nonatomic, strong, readonly)           LTDicomWaveformGroup *group;
@property (nonatomic, strong, readonly, nullable) LTDicomChannelSensitivity *channelSensitivity;
@property (nonatomic, strong)                     LTDicomCodeSequenceItem *channelSource;

@property (nonatomic, copy, readonly, nullable)   NSString *channelLabel;

- (instancetype)init;

- (NSUInteger)setChannelSamples8:(unsigned char *)samples count:(NSUInteger)count;
- (NSUInteger)setChannelSamples16:(short *)samples count:(NSUInteger)count;
- (NSUInteger)setChannelSamples32:(int *)samples count:(NSUInteger)count;

- (nullable const int *)getChannelSamples:(NSUInteger *)count NS_RETURNS_INNER_POINTER;
- (NSUInteger)getChannelSamples:(int *)buffer length:(NSUInteger)length;

- (BOOL)setWaveformChannelNumber:(NSInteger)waveformChannel include:(BOOL)include;
- (BOOL)setChannelMinimumValue:(NSInteger)minimumValue include:(BOOL)include;
- (BOOL)setChannelMaximumValue:(NSInteger)maximumValue include:(BOOL)include;
- (BOOL)setChannelTimeSkew:(double)timeSkew;
- (BOOL)setChannelSampleSkew:(double)sampleSkew;
- (BOOL)setChannelOffset:(double)offset include:(BOOL)include;
- (BOOL)setFilterLowFrequency:(double)lowFrequency include:(BOOL)include;
- (BOOL)setFilterHighFrequency:(double)highFrequency include:(BOOL)include;
- (BOOL)setNotchFilterFrequency:(double)notchFrequency include:(BOOL)include;
- (BOOL)setNotchFilterBandwidth:(double)notchBandwidth include:(BOOL)include;
- (BOOL)setChannelLabel:(NSString *)label;

- (BOOL)setChannelSensitivityWithUnits:(LTDicomCodeSequenceItem *)units sensitivity:(double)sensitivity sensitivityCF:(double)sensitivityCF baseline:(double)baseline include:(BOOL)include error:(NSError **)error;

- (nullable LTDicomWaveformAnnotation *)annotationAtIndex:(NSUInteger)index;
- (BOOL)addAnnotation:(LTDicomWaveformAnnotation *)waveformAnnotation error:(NSError **)error;
- (NSUInteger)deleteAnnotationAtIndex:(NSUInteger)index;

@end

NS_ASSUME_NONNULL_END
