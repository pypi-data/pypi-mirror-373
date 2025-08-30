// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomDateTimeValue.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomDateValue.h>
#import <Leadtools.Dicom/LTDicomTimeValue.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomDateTimeValue : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign)                     NSInteger year;
@property (nonatomic, assign)                     NSInteger month;
@property (nonatomic, assign)                     NSInteger day;
@property (nonatomic, assign)                     NSInteger hours;
@property (nonatomic, assign)                     NSInteger minutes;
@property (nonatomic, assign)                     NSInteger seconds;
@property (nonatomic, assign)                     NSInteger fractions;
@property (nonatomic, assign)                     NSInteger offset;

@property (nonatomic, assign, readonly)           BOOL isEmpty;
@property (nonatomic, assign, readonly, nullable) NSDate *date;

@property (class, nonatomic, strong, readonly)    LTDicomDateTimeValue *empty;
@property (class, nonatomic, strong, readonly)    LTDicomDateTimeValue *now;

- (instancetype)initWithYear:(NSInteger)year month:(NSInteger)month day:(NSInteger)day hours:(NSInteger)hours minutes:(NSInteger)minutes seconds:(NSInteger)seconds fractions:(NSInteger)fractions offset:(NSInteger)offset NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithDate:(NSDate *)date;

@end

NS_ASSUME_NONNULL_END
