// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTPharmaCodeBarcodeWriteOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeWriteOptions.h>

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTPharmaCodeBarcodeWriteOptions : LTBarcodeWriteOptions

@property (nonatomic, copy, readonly) NSString *friendlyName;

@property (nonatomic, assign)         BOOL useXModule;
@property (nonatomic, assign)         NSInteger xModule;

@end
