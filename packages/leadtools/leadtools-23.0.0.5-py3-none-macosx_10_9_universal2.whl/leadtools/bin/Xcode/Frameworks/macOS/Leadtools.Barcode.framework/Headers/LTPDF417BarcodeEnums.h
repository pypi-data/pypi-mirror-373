// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTPDF417BarcodeEnums.h
//  Leadtools.Barcode
//

typedef NS_ENUM(NSInteger, LTPDF417BarcodeReadMode) {
    LTPDF417BarcodeReadModeMode0,
    LTPDF417BarcodeReadModeMode1,
    LTPDF417BarcodeReadModeMode2,
    LTPDF417BarcodeReadModeMode3Basic,
    LTPDF417BarcodeReadModeMode3Extended,
};

typedef NS_ENUM(NSInteger, LTPDF417BarcodeECCLevel) {
    LTPDF417BarcodeECCLevelLevel0,
    LTPDF417BarcodeECCLevelLevel1,
    LTPDF417BarcodeECCLevelLevel2,
    LTPDF417BarcodeECCLevelLevel3,
    LTPDF417BarcodeECCLevelLevel4,
    LTPDF417BarcodeECCLevelLevel5,
    LTPDF417BarcodeECCLevelLevel6,
    LTPDF417BarcodeECCLevelLevel7,
    LTPDF417BarcodeECCLevelLevel8,
    LTPDF417BarcodeECCLevelUsePercentage
};
