// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTBackGroundRemovalCommand.h
//  Leadtools.ImageProcessing.Core
//

#import <Leadtools/LTRasterCommand.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTBackGroundRemovalCommand : LTRasterCommand

@property (nonatomic, assign) NSUInteger bGRemovalFactor;

- (instancetype)initWithRemovalFactor:(NSUInteger)removalFactor NS_DESIGNATED_INITIALIZER;

@end

NS_ASSUME_NONNULL_END
