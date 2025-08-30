// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomAgeValue.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomDateValue.h>
#import <Leadtools.Dicom/LTDicomTimeValue.h>

typedef NS_ENUM(char, LTDicomAgeReferenceType) {
    LTDicomAgeReferenceTypeDays   = 'D',
    LTDicomAgeReferenceTypeWeeks  = 'W',
    LTDicomAgeReferenceTypeMonths = 'M',
    LTDicomAgeReferenceTypeYears  = 'Y',
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomAgeValue : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign, readonly)        BOOL isEmpty;

@property (nonatomic, assign)                  NSInteger number;
@property (nonatomic, assign)                  LTDicomAgeReferenceType reference;

@property (class, nonatomic, strong, readonly) LTDicomAgeValue *empty;

- (instancetype)initWithNumber:(NSInteger)number reference:(LTDicomAgeReferenceType)reference NS_DESIGNATED_INITIALIZER;

@end

NS_ASSUME_NONNULL_END
