// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTOneDBarcodeWriteOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTBarcodeWriteEnums.h>
#import <Leadtools.Barcode/LTOneDBarcodeEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTOneDBarcodeWriteOptions : LTBarcodeWriteOptions

@property (nonatomic, copy, readonly)  NSString *friendlyName;

@property (nonatomic, assign)          LTBarcodeOutputTextPosition textPosition;

@property (nonatomic, assign)          LTCode128BarcodeTableEncoding code128TableEncoding;

@property (nonatomic, assign)          LTCode11BarcodeCheckDigitType code11CheckDigitType;

@property (nonatomic, assign)          LTMSIBarcodeModuloType msiModuloType;

@property (nonatomic, assign)          BOOL useXModule;
@property (nonatomic, assign)          BOOL enableErrorCheck;
@property (nonatomic, assign)          BOOL setGS1DatabarLinkageBit;
@property (nonatomic, assign)          BOOL writeTruncatedGS1Databar;

@property (nonatomic, assign)          NSInteger xModule;

@end

NS_ASSUME_NONNULL_END
