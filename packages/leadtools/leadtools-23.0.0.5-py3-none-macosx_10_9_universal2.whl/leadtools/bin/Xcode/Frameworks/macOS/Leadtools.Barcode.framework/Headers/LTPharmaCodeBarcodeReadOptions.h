// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTPharmaCodeBarcodeReadOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTBarcodeReadEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTPharmaCodeBarcodeReadOptions : LTBarcodeReadOptions

@property (nonatomic, copy, readonly) NSString *friendlyName;

@property (nonatomic, assign)         LTBarcodeSearchDirection searchDirection;

@end

NS_ASSUME_NONNULL_END
