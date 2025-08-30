// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomVR.h
//  Leadtools.Dicom
//

typedef NS_ENUM(NSInteger, LTDicomVRType) {
    LTDicomVRTypeAE = 0x4145,
    LTDicomVRTypeAS = 0x4153,
    LTDicomVRTypeAT = 0x4154,
    LTDicomVRTypeCS = 0x4353,
    LTDicomVRTypeDA = 0x4441,
    LTDicomVRTypeDS = 0x4453,
    LTDicomVRTypeDT = 0x4454,
    LTDicomVRTypeFD = 0x4644,
    LTDicomVRTypeFL = 0x464C,
    LTDicomVRTypeIS = 0x4953,
    LTDicomVRTypeLO = 0x4C4F,
    LTDicomVRTypeLT = 0x4C54,
    LTDicomVRTypeOB = 0x4F42,
    LTDicomVRTypeOD = 0x4F44,
    LTDicomVRTypeOF = 0x4F46,
    LTDicomVRTypeOL = 0x4F4C,
    LTDicomVRTypeOW = 0x4F57,
    LTDicomVRTypePN = 0x504E,
    LTDicomVRTypeSH = 0x5348,
    LTDicomVRTypeSL = 0x534C,
    LTDicomVRTypeSQ = 0x5351,
    LTDicomVRTypeSS = 0x5353,
    LTDicomVRTypeST = 0x5354,
    LTDicomVRTypeTM = 0x544D,
    LTDicomVRTypeUC = 0x5543,
    LTDicomVRTypeUI = 0x5549,
    LTDicomVRTypeUL = 0x554C,
    LTDicomVRTypeUN = 0x554E,
    LTDicomVRTypeUR = 0x5552,
    LTDicomVRTypeUS = 0x5553,
    LTDicomVRTypeUT = 0x5554,

    // DICOM 2021a
    LTDicomVRTypeOV = 0x4F56U,    // Other 64-bit Very Long
    LTDicomVRTypeSV = 0x5356U,    // Signed 64-bit Very Long (8 bytes fixed). Represents an integer n in the range:- 2^63 <= n <= 2^63 - 1
    LTDicomVRTypeUV = 0x5556U,    // Unsigned binary integer 64 bits long (8 bytes fixed). Represents an integer n in the range: 0 <= n < 2^64
};

typedef NS_ENUM(NSInteger, LTDicomVRRestriction) {
    LTDicomVRRestrictionNotApplicable      = 0x0004,
    LTDicomVRRestrictionBinaryFixed        = 0x0100,
    LTDicomVRRestrictionBinaryMaximum      = 0x0101,
    LTDicomVRRestrictionBinaryAny          = 0x0103,
    LTDicomVRRestrictionStringFixed        = 0x0200,
    LTDicomVRRestrictionStringMaximum      = 0x0201,
    LTDicomVRRestrictionStringMaximumGroup = 0x0202,
    LTDicomVRRestrictionTextFixed          = 0x0400,
    LTDicomVRRestrictionTextMaximum        = 0x0401,
    LTDicomVRRestrictionTextMaximumGroup   = 0x0402,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomVR : NSObject

@property (nonatomic, assign, readonly)         LTDicomVRType code;
@property (nonatomic, assign, readonly)         LTDicomVRRestriction restriction;

@property (nonatomic, assign, readonly)         NSUInteger unitSize;
@property (nonatomic, assign, readonly)         NSUInteger length;

@property (nonatomic, copy, readonly, nullable) NSString *name;

- (instancetype)init __unavailable;

@end

NS_ASSUME_NONNULL_END
