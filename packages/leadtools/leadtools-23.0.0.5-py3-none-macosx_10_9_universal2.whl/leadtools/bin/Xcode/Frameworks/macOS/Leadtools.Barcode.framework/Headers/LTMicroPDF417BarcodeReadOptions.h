// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTMicroPDF417BarcodeReadOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTBarcodeReadEnums.h>
#import <Leadtools.Barcode/LTMicroPDF417BarcodeEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTMicroPDF417BarcodeReadOptions : LTBarcodeReadOptions

@property (nonatomic, copy, readonly)  NSString *friendlyName;

@property (nonatomic, assign)          LTBarcodeSearchDirection searchDirection;

@property (nonatomic, assign)          BOOL enablePreprocessing;

@property (nonatomic, assign)          LTMicroPDF417BarcodeReadMode readMode;

@property (nonatomic, assign)          BOOL enableDoublePass;
@property (nonatomic, assign)          BOOL enableDoublePassIfSuccess;
@property (nonatomic, assign)          BOOL readOptionalMacroFileNameField;
@property (nonatomic, assign)          BOOL readOptionalMacroSegmentCountField;
@property (nonatomic, assign)          BOOL readOptionalMacroTimestampField;
@property (nonatomic, assign)          BOOL readOptionalMacroSenderField;
@property (nonatomic, assign)          BOOL readOptionalMacroAddresseeField;
@property (nonatomic, assign)          BOOL readOptionalMacroFileSizeField;
@property (nonatomic, assign)          BOOL readOptionalMacroChecksumField;
@property (nonatomic, assign)          BOOL readOptionalMacro79AndAZField;

@end

NS_ASSUME_NONNULL_END
