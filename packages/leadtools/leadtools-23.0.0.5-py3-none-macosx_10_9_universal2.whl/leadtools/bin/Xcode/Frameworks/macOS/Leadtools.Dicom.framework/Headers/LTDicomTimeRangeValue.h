// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomTimeRangeValue.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomRangeType.h>
#import <Leadtools.Dicom/LTDicomTimeValue.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomTimeRangeValue : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign, readonly)        BOOL isEmpty;

@property (nonatomic, assign)                  LTDicomRangeType type;
@property (nonatomic, strong)                  LTDicomTimeValue *time1;
@property (nonatomic, strong)                  LTDicomTimeValue *time2;

@property (class, nonatomic, strong, readonly) LTDicomTimeRangeValue *empty;

- (instancetype)initWithType:(LTDicomRangeType)type time1:(LTDicomTimeValue *)time1 time2:(LTDicomTimeValue *)time2 NS_DESIGNATED_INITIALIZER;

@end

NS_ASSUME_NONNULL_END
