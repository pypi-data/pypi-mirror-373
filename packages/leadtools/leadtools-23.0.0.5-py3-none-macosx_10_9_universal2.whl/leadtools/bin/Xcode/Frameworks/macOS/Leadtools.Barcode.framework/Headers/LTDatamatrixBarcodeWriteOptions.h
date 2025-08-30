// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDatamatrixBarcodeWriteOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTBarcodeWriteEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDatamatrixBarcodeWriteOptions : LTBarcodeWriteOptions

@property (nonatomic, copy, readonly)  NSString *friendlyName;

@property (nonatomic, assign)          LTBarcodeAlignment horizontalAlignment;

@property (nonatomic, assign)          LTBarcodeAlignment verticalAlignment;

@property (nonatomic, assign)          BOOL disableCompression;
@property (nonatomic, assign)          BOOL HRItoGS1;

@property (nonatomic, assign)          NSInteger groupNumber;
@property (nonatomic, assign)          NSInteger groupTotal;

@property (nonatomic, assign)          unsigned char fileIdNumberLowByte;
@property (nonatomic, assign)          unsigned char fileIdNumberHighByte;

@property (nonatomic, assign)          NSInteger xModule;

@end

NS_ASSUME_NONNULL_END
