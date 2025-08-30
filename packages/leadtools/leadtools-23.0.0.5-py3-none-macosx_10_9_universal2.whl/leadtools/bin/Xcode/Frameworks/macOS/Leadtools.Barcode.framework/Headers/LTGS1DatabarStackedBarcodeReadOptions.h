// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTGS1DatabarStackedBarcodeReadOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTBarcodeReadEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTGS1DatabarStackedBarcodeReadOptions : LTBarcodeReadOptions

@property (nonatomic, copy, readonly)  NSString *friendlyName;

@property (nonatomic, assign)          LTBarcodeSearchDirection searchDirection;

@property (nonatomic, assign)          BOOL enableFastMode;

@property (nonatomic, assign)          NSInteger granularity;

@property (nonatomic, assign)          LTBarcodeReturnCheckDigit returnCheckDigit;

@end

NS_ASSUME_NONNULL_END
