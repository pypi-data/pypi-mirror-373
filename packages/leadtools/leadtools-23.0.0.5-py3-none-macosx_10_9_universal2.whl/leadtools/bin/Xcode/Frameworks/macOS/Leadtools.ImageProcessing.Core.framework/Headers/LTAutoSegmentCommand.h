// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTAutoSegmentCommand.h
//  Leadtools.ImageProcessing.Core
//

#import <Leadtools/LTRasterCommand.h>
#import <Leadtools/LTPrimitives.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTAutoSegmentCommand : LTRasterCommand

@property (nonatomic, assign) LeadRect segmentationRectangle;

- (instancetype)initWithRect:(LeadRect)rect NS_DESIGNATED_INITIALIZER;

@end

NS_ASSUME_NONNULL_END
