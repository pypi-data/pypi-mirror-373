// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTGS1DatabarStackedBarcodeWriteOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeWriteOptions.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTGS1DatabarStackedBarcodeWriteOptions : LTBarcodeWriteOptions

@property (nonatomic, copy, readonly)  NSString *friendlyName;

@property (nonatomic, assign)          BOOL useXModule;
@property (nonatomic, assign)          BOOL setLinkageBit;
@property (nonatomic, assign)          BOOL useStackedOmniDirectionalFormat;

@property (nonatomic, assign)          NSInteger xModule;
@property (nonatomic, assign)          NSInteger expandedStackedRowsCount;

@end

NS_ASSUME_NONNULL_END
