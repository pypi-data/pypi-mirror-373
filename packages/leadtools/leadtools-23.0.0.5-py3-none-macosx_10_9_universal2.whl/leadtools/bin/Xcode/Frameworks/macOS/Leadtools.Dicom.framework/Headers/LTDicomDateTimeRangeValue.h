// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomDateTimeRangeValue.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomRangeType.h>
#import <Leadtools.Dicom/LTDicomDateTimeValue.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomDateTimeRangeValue : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign, readonly)        BOOL isEmpty;

@property (nonatomic, assign)                  LTDicomRangeType type;
@property (nonatomic, strong)                  LTDicomDateTimeValue *dateTime1;
@property (nonatomic, strong)                  LTDicomDateTimeValue *dateTime2;

@property (class, nonatomic, strong, readonly) LTDicomDateTimeRangeValue *empty;

- (instancetype)initWithType:(LTDicomRangeType)type dateTime1:(LTDicomDateTimeValue *)dateTime1 dateTime2:(LTDicomDateTimeValue *)dateTime2 NS_DESIGNATED_INITIALIZER;

@end

NS_ASSUME_NONNULL_END
