// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomDateRangeValue.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomRangeType.h>
#import <Leadtools.Dicom/LTDicomDateValue.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomDateRangeValue : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign, readonly)        BOOL isEmpty;

@property (nonatomic, assign)                  LTDicomRangeType type;
@property (nonatomic, strong)                  LTDicomDateValue *date1;
@property (nonatomic, strong)                  LTDicomDateValue *date2;

@property (class, nonatomic, strong, readonly) LTDicomDateRangeValue *empty;

- (instancetype)initWithType:(LTDicomRangeType)type date1:(LTDicomDateValue *)date1 date2:(LTDicomDateValue *)date2 NS_DESIGNATED_INITIALIZER;

@end

NS_ASSUME_NONNULL_END
