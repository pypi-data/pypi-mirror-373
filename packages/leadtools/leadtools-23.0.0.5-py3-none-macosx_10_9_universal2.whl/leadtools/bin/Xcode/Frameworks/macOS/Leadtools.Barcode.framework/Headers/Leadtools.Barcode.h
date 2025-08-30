// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  Leadtools.Barcode.h
//  Leadtools.Barcode
//

#if !defined(LEADTOOLS_BARCODE_FRAMEWORK)
#define LEADTOOLS_BARCODE_FRAMEWORK

#import <Leadtools.Barcode/LTGlobalEnums.h>
#import <Leadtools.Barcode/LTBarcodeData.h>
#import <Leadtools.Barcode/LTReadEvents.h>
#import <Leadtools.Barcode/LTBarcodeReader.h>
#import <Leadtools.Barcode/LTBarcodeOptions.h>
#import <Leadtools.Barcode/LTBarcodeReadEnums.h>
#import <Leadtools.Barcode/LTBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTBarcodeWriteEnums.h>
#import <Leadtools.Barcode/LTBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTBarcodeEngine.h>
#import <Leadtools.Barcode/LTBarcodeWriter.h>
#import <Leadtools.Barcode/LTAAMVADataElementInfo.h>
#import <Leadtools.Barcode/LTAAMVADataElement.h>
#import <Leadtools.Barcode/LTAAMVAID.h>
#import <Leadtools.Barcode/LTAAMVANameResult.h>
#import <Leadtools.Barcode/LTAAMVASubfile.h>
#import <Leadtools.Barcode/LTDatamatrixBarcodeData.h>
#import <Leadtools.Barcode/LTDatamatrixBarcodeEnums.h>
#import <Leadtools.Barcode/LTDatamatrixBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTDatamatrixBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTFourStateBarcodeEnums.h>
#import <Leadtools.Barcode/LTFourStateBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTFourStateBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTGS1DatabarStackedBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTGS1DatabarStackedBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTMicroPDF417BarcodeData.h>
#import <Leadtools.Barcode/LTMicroPDF417BarcodeEnums.h>
#import <Leadtools.Barcode/LTMicroPDF417BarcodeReadOptions.h>
#import <Leadtools.Barcode/LTMicroPDF417BarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTOneDBarcodeEnums.h>
#import <Leadtools.Barcode/LTOneDBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTOneDBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTPatchCodeBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTPatchCodeBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTPDF417BarcodeData.h>
#import <Leadtools.Barcode/LTPDF417BarcodeEnums.h>
#import <Leadtools.Barcode/LTPDF417BarcodeReadOptions.h>
#import <Leadtools.Barcode/LTPDF417BarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTPostNetPlanetBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTPostNetPlanetBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTQRBarcodeData.h>
#import <Leadtools.Barcode/LTQRBarcodeEnums.h>
#import <Leadtools.Barcode/LTQRBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTQRBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTBarcodeError.h>
#import <Leadtools.Barcode/LTAztecBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTAztecBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTAztecBarcodeData.h>
#import <Leadtools.Barcode/LTMaxiBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTMaxiBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTMaxiBarcodeData.h>
#import <Leadtools.Barcode/LTMicroQRBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTMicroQRBarcodeWriteOptions.h>
#import <Leadtools.Barcode/LTMicroQRBarcodeData.h>
#import <Leadtools.Barcode/LTPharmaCodeBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTPharmaCodeBarcodeWriteOptions.h>

// Versioning
#import <Leadtools/LTLeadtools.h>

LEADTOOLS_EXPORT const unsigned char LeadtoolsBarcodeVersionString[];
LEADTOOLS_EXPORT const double LeadtoolsBarcodeVersionNumber;

#endif // #if !defined(LEADTOOLS_BARCODE_FRAMEWORK)
