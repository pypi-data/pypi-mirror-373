// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomTimeValue.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomTimeValue : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign)                     NSInteger hours;
@property (nonatomic, assign)                     NSInteger minutes;
@property (nonatomic, assign)                     NSInteger seconds;
@property (nonatomic, assign)                     NSInteger fractions;

@property (nonatomic, assign, readonly)           BOOL isEmpty;
@property (nonatomic, assign, readonly, nullable) NSDate *date;

@property (class, nonatomic, strong, readonly)    LTDicomTimeValue *empty;
@property (class, nonatomic, strong, readonly)    LTDicomTimeValue *now;

- (instancetype)initWithHours:(NSInteger)hours minutes:(NSInteger)minutes seconds:(NSInteger)seconds fractions:(NSInteger)fractions NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithDate:(NSDate *)date;

@end

NS_ASSUME_NONNULL_END
