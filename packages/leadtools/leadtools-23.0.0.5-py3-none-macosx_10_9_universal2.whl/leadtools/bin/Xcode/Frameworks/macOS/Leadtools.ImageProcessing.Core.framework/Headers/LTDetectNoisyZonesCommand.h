// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDetectNoisyZonesCommand.h
//  Leadtools.ImageProcessing.Core
//

#import <Leadtools/LTRasterCommand.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDetectNoisyZonesCommand : LTRasterCommand

@property (nonatomic, strong, readonly) NSMutableArray<NSValue *> *zones; //LeadRect
@property (nonatomic, strong, readonly) NSMutableArray<NSValue *> *noisyZones; //bool

@end

NS_ASSUME_NONNULL_END
