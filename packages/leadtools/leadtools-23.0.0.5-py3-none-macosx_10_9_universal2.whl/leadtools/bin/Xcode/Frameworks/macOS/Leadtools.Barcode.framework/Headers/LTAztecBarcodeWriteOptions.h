// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTAztecBarcodeWriteOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTBarcodeWriteEnums.h>
#import <Leadtools.Barcode/LTAztecBarcodeEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTAztecBarcodeWriteOptions : LTBarcodeWriteOptions

@property (nonatomic, copy, readonly)  NSString *friendlyName;

@property (nonatomic, assign)          LTAztecBarcodeSymbolModel symbolModel;

@property (nonatomic, assign)          NSInteger xModule;
@property (nonatomic, assign)          NSInteger quietZone;
@property (nonatomic, assign)          NSInteger errorCorrectionRate;
@property (nonatomic, assign)          NSInteger aztecRuneValue;

@property (nonatomic, assign)          BOOL aztecRune;

@end

NS_ASSUME_NONNULL_END
