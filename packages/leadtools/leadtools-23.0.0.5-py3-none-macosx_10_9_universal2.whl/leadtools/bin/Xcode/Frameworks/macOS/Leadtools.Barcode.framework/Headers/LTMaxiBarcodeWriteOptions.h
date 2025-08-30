// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTMaxiBarcodeWriteOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTMaxiBarcodeEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTMaxiBarcodeWriteOptions : LTBarcodeWriteOptions

@property (nonatomic, copy, readonly)  NSString *friendlyName;
@property (nonatomic, copy)            NSString *postalCodeChar;

@property (nonatomic, assign)          LTMaxiBarcodeSymbolModel symbolModel;

@property (nonatomic, assign)          NSInteger resolution;
@property (nonatomic, assign)          NSInteger countryCode;
@property (nonatomic, assign)          NSInteger serviceClass;
@property (nonatomic, assign)          NSInteger postalCodeNum;
@property (nonatomic, assign)          NSInteger year;

@property (nonatomic, assign)          BOOL openSystemStandard;

@end

NS_ASSUME_NONNULL_END
