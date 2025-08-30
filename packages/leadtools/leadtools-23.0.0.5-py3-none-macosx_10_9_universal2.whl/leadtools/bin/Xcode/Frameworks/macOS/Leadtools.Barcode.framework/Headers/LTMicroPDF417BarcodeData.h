// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTMicroPDF417BarcodeData.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeData.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTMicroPDF417BarcodeData : LTBarcodeData <NSCopying>

@property (nonatomic, assign)             LTBarcodeSymbology symbology;

@property (nonatomic, assign, readonly)   BOOL isLinked;

@property (nonatomic, assign)             NSUInteger dataCode;

@end

NS_ASSUME_NONNULL_END
