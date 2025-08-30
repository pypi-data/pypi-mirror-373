// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTPosterizeCommand.h
//  Leadtools.ImageProcessing.Color
//

#import <Leadtools/LTRasterCommand.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTPosterizeCommand : LTRasterCommand

@property (nonatomic, assign) NSUInteger levels;

- (instancetype)initWithLevels:(NSUInteger)levels NS_DESIGNATED_INITIALIZER;

@end

NS_ASSUME_NONNULL_END
