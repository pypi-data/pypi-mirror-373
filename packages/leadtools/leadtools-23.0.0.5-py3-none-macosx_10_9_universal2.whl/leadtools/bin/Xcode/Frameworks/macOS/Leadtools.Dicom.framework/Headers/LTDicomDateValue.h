// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomDateValue.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomDateValue : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign)                     NSInteger year;
@property (nonatomic, assign)                     NSInteger month;
@property (nonatomic, assign)                     NSInteger day;

@property (nonatomic, assign, readonly)           BOOL isEmpty;
@property (nonatomic, strong, readonly, nullable) NSDate *date;

@property (class, nonatomic, strong, readonly)    LTDicomDateValue *empty;
@property (class, nonatomic, strong, readonly)    LTDicomDateValue *now;


- (instancetype)initWithYear:(NSInteger)year month:(NSInteger)month day:(NSInteger)day NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithDate:(NSDate *)date;

@end

NS_ASSUME_NONNULL_END
