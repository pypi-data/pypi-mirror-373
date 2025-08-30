// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTMicroQRBarcodeWriteOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTMicroQRBarcodeEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTMicroQRBarcodeWriteOptions : LTBarcodeWriteOptions

@property (nonatomic, copy, readonly)  NSString *friendlyName;

@property (nonatomic, assign)          NSInteger xModule;

@property (nonatomic, assign)          LTMicroQRBarcodeSymbolModel symbolModel;

@end

NS_ASSUME_NONNULL_END
