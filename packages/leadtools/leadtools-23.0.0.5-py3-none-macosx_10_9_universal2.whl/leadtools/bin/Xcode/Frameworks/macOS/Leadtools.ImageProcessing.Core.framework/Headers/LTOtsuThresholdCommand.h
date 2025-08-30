// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTOtsuThresholdCommand.h
//  Leadtools.ImageProcessing.Core
//

#import <Leadtools/LTRasterCommand.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTOtsuThresholdCommand : LTRasterCommand

@property (nonatomic, assign) NSInteger clusters;

- (instancetype)initWithClusters:(NSInteger)clusters NS_DESIGNATED_INITIALIZER;

@end

NS_ASSUME_NONNULL_END
