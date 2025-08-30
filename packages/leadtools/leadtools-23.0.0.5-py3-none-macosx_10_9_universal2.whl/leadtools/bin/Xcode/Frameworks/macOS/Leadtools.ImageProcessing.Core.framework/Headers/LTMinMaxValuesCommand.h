// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTMinMaxValuesCommand.h
//  Leadtools.ImageProcessing.Core
//

#import <Leadtools/LTRasterCommand.h>

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTMinMaxValuesCommand : LTRasterCommand

@property (nonatomic, assign, readonly) NSInteger minimumValue;
@property (nonatomic, assign, readonly) NSInteger maximumValue;

@end
