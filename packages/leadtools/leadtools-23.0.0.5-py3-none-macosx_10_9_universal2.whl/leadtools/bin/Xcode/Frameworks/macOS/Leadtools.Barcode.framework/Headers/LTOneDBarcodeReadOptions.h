// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTOneDBarcodeReadOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTBarcodeReadEnums.h>
#import <Leadtools.Barcode/LTOneDBarcodeEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTOneDBarcodeReadOptions : LTBarcodeReadOptions

@property (nonatomic, copy, readonly)  NSString *friendlyName;

@property (nonatomic, assign)          LTBarcodeSearchDirection searchDirection;

@property (nonatomic, assign)          LTBarcodeReturnCheckDigit returnCheckDigit;

@property (nonatomic, assign)          LTCode11BarcodeCheckDigitType code11CheckDigitType;

@property (nonatomic, assign)          LTMSIBarcodeModuloType msiModuloType;

@property (nonatomic, assign)          NSInteger granularity;
@property (nonatomic, assign)          NSInteger minimumStringLength;
@property (nonatomic, assign)          NSInteger maximumStringLength;
@property (nonatomic, assign)          NSInteger whiteLinesNumber;

@property (nonatomic, assign)          BOOL enableFastMode;
@property (nonatomic, assign)          BOOL enableErrorCheck;
@property (nonatomic, assign)          BOOL avoidCorruptedBlocks;
@property (nonatomic, assign)          BOOL allowPartialRead;
@property (nonatomic, assign)          BOOL code39Extended;
@property (nonatomic, assign)          BOOL resizeSmall1D;
@property (nonatomic, assign)          BOOL enableDoublePass;
@property (nonatomic, assign)          BOOL calculateBarWidthReduction;
@property (nonatomic, assign)          BOOL enablePreprocessing;

@end

NS_ASSUME_NONNULL_END
