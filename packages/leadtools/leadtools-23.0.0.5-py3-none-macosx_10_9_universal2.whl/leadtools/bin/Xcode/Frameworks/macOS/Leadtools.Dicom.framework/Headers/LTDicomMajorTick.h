// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomMajorTick.h
//  Leadtools.Dicom
//

#import <CoreGraphics/CGBase.h> // CGFloat

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomMajorTick : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign)         CGFloat tickPosition;

@property (nonatomic, copy, nullable) NSString *tickLabel;

- (instancetype)initWithPosition:(CGFloat)position label:(nullable NSString *)label NS_DESIGNATED_INITIALIZER;

@end

NS_ASSUME_NONNULL_END
