// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTBarcodeError.h
//  Leadtools.Barcode
//

#import <Leadtools/LTLeadtools.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, LTBarcodeError) {
   LTBarcodeErrorInvalidType             = -411,
   LTBarcodeErrorInvalidTextOut          = -412,
   LTBarcodeErrorInvalidWidth            = -413,
   LTBarcodeErrorInvalidHeight           = -414,
   LTBarcodeErrorToSmall                 = -415,
   LTBarcodeErrorInvalidBarcodeString    = -416,
   LTBarcodeErrorInvalidUnits            = -418,
   LTBarcodeErrorInvalidMaximumCount     = -419,
   LTBarcodeErrorInvalidGroup            = -420,
   LTBarcodeErrorInvalidStringLength     = -424,
   LTBarcodeErrorInvalidBounds           = -425,
   LTBarcodeErrorBarcode1dLocked         = -426,
   LTBarcodeErrorBarcode2dReadLocked     = -427,
   LTBarcodeErrorBarcode2dWriteLocked    = -428,
   LTBarcodeErrorPdfReadLocked           = -429,
   LTBarcodeErrorPdfWriteLocked          = -430,
   LTBarcodeErrorDatamatrixReadLocked    = -432,
   LTBarcodeErrorDatamatrixWriteLocked   = -433,
   LTBarcodeErrorQrReadLocked            = -1380,
   LTBarcodeErrorQrWriteLocked           = -1381,
   LTBarcodeErrorAztecReadLocked         = -1370,
   LTBarcodeErrorAztecWriteLocked        = -1371,
   LTBarcodeErrorMaxiReadLocked          = -1372,
   LTBarcodeErrorMaxiWriteLocked         = -1373,
   LTBarcodeErrorMicroQrReadLocked       = -1374,
   LTBarcodeErrorMicroQrWriteLocked      = -1375,
   LTBarcodeErrorDllNotFound             = -1382,
   LTBarcodeErrorInvalidXModule          = -1481,
};

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTBarcodeErrorHelper : NSObject

+ (nullable NSString *)errorMessageForCode:(LTBarcodeError)code;

@end

@interface LTBarcodeErrorHelper (Deprecated)

+ (nullable NSString *)getCodeMessage:(LTBarcodeError)code LT_DEPRECATED_USENEW(19_0, "errorMessageForCode:");

@end

NS_ASSUME_NONNULL_END
