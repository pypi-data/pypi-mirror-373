// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomWaveformGroup.h
//  Leadtools.Dicom
//

@class LTDicomWaveformChannel;

typedef NS_ENUM(NSInteger, LTDicomWaveformSampleInterpretationType) {
	LTDicomWaveformSampleInterpretationTypeSigned16BitLinear   = 0,
	LTDicomWaveformSampleInterpretationTypeUnsigned16BitLinear = 1,
	LTDicomWaveformSampleInterpretationTypeSigned8BitLinear    = 2,
	LTDicomWaveformSampleInterpretationTypeUnsigned8BitLinear  = 3,
	LTDicomWaveformSampleInterpretationTypeMulaw8Bit           = 4,
	LTDicomWaveformSampleInterpretationTypeAlaw8Bit            = 5,
};

typedef NS_ENUM(NSInteger, LTDicomWaveformOriginalityType) {
	LTDicomWaveformOriginalityTypeOriginal = 0,
	LTDicomWaveformOriginalityTypeDerived  = 1,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomWaveformGroup : NSObject

@property (nonatomic, assign, readonly)         NSUInteger channelCount;
@property (nonatomic, assign, readonly)         NSUInteger samplesPerChannel;
@property (nonatomic, assign, readonly)         NSUInteger triggerSamplePosition;

@property (nonatomic, assign, readonly)         NSInteger waveformPaddingValue;

@property (nonatomic, assign)                   double samplingFrequency;
@property (nonatomic, assign, readonly)         double multiplexGroupTimeOffset;
@property (nonatomic, assign, readonly)         double triggerTimeOffset;

@property (nonatomic, assign, readonly)         LTDicomWaveformSampleInterpretationType sampleInterpretation;
@property (nonatomic, assign)                   LTDicomWaveformOriginalityType waveformOriginality;

@property (nonatomic, copy, readonly, nullable) NSString *multiplexGroupLabel;

- (instancetype)init;

- (void)reset;

- (nullable LTDicomWaveformChannel *)channelAtIndex:(NSUInteger)index;
- (nullable LTDicomWaveformChannel *)addChannelAtIndex:(NSInteger)index;
- (NSUInteger)deleteChannelAtIndex:(NSUInteger)index;

- (BOOL)setSamplesPerChannel:(NSUInteger)samples;
- (BOOL)setMultiplexGroupTimeOffset:(double)offset include:(BOOL)include;
- (BOOL)setTriggerTimeOffset:(double)offset include:(BOOL)include;
- (BOOL)setTriggerSamplePosition:(NSUInteger)samplePosition include:(BOOL)include;
- (BOOL)setWaveformPaddingValue:(NSInteger)paddingValue include:(BOOL)include;
- (BOOL)setSampleInterpretation:(LTDicomWaveformSampleInterpretationType)sampleInterpretation;
- (BOOL)setMultiplexGroupLabel:(NSString *)label;

- (BOOL)loadAudio:(NSString *)fileName error:(NSError **)error;
- (BOOL)saveAudio:(NSString *)fileName error:(NSError **)error;

@end

NS_ASSUME_NONNULL_END
