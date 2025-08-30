// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTMinimumToZeroCommand.h
//  Leadtools.ImageProcessing.Core
//

#import <Leadtools/LTRasterCommand.h>

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTMinimumToZeroCommand : LTRasterCommand

@property (nonatomic, assign, readonly) NSUInteger shiftAmount;

@end
