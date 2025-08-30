// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDatamatrixBarcodeData.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeData.h>
#import <Leadtools.Barcode/LTDatamatrixBarcodeEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDatamatrixBarcodeData : LTBarcodeData <NSCopying>

@property (nonatomic, assign) LTBarcodeSymbology symbology;

@property (nonatomic, assign) LTDatamatrixBarcodeSymbolSize symbolSize;

@end

NS_ASSUME_NONNULL_END
