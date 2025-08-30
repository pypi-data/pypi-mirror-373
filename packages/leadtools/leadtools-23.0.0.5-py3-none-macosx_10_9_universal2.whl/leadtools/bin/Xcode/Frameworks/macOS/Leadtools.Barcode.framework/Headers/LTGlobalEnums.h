// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTGlobalEnums.h
//  Leadtools.Barcode
//

#import <Leadtools/LTLeadtools.h>

// Barcode symbologies supported by LEADTOOLS
typedef NS_ENUM(NSInteger, LTBarcodeSymbology) {
    LTBarcodeSymbologyUnknown,
    LTBarcodeSymbologyEAN13,
    LTBarcodeSymbologyEAN8,
    LTBarcodeSymbologyUPCA,
    LTBarcodeSymbologyUPCE,
    LTBarcodeSymbologyCode3Of9,
    LTBarcodeSymbologyCode128,
    LTBarcodeSymbologyCodeInterleaved2Of5,
    LTBarcodeSymbologyCodabar,
    LTBarcodeSymbologyUCCEAN128,
    LTBarcodeSymbologyCode93,
    LTBarcodeSymbologyEANEXT5,
    LTBarcodeSymbologyEANEXT2,
    LTBarcodeSymbologyMSI,
    LTBarcodeSymbologyCode11,
    LTBarcodeSymbologyCodeStandard2Of5,
    LTBarcodeSymbologyGS1Databar,
    LTBarcodeSymbologyGS1DatabarLimited,
    LTBarcodeSymbologyGS1DatabarExpanded,
    LTBarcodeSymbologyPatchCode,
    LTBarcodeSymbologyPostNet,
    LTBarcodeSymbologyPlanet,
    LTBarcodeSymbologyAustralianPost4State,
    LTBarcodeSymbologyRoyalMail4State,
    LTBarcodeSymbologyUSPS4State,
    LTBarcodeSymbologyGS1DatabarStacked,
    LTBarcodeSymbologyGS1DatabarExpandedStacked,
    LTBarcodeSymbologyPDF417,
    LTBarcodeSymbologyMicroPDF417,
    LTBarcodeSymbologyDatamatrix,
    LTBarcodeSymbologyQR,
    LTBarcodeSymbologyAztec,
    LTBarcodeSymbologyMaxi,
    LTBarcodeSymbologyMicroQR,
    LTBarcodeSymbologyPharmaCode
};

LT_ENUM_AVAILABLE(10_10, 8_0, 20_0)
typedef NS_ENUM(NSInteger, LTAAMVAEyeColor) {
    LTAAMVAEyeColorUnknown     = 0,
    LTAAMVAEyeColorBlack       = 1,
    LTAAMVAEyeColorBlue        = 2,
    LTAAMVAEyeColorBrown       = 3,
    LTAAMVAEyeColorDichromatic = 4,
    LTAAMVAEyeColorGray        = 5,
    LTAAMVAEyeColorGreen       = 6,
    LTAAMVAEyeColorHazel       = 7,
    LTAAMVAEyeColorMaroon      = 8,
    LTAAMVAEyeColorPink        = 9
};

LT_ENUM_AVAILABLE(10_10, 8_0, 20_0)
typedef NS_ENUM(NSInteger, LTAAMVAHairColor) {
    LTAAMVAHairColorUnknown = 0,
    LTAAMVAHairColorBald    = 1,
    LTAAMVAHairColorBlack   = 2,
    LTAAMVAHairColorBlonde  = 3,
    LTAAMVAHairColorBrown   = 4,
    LTAAMVAHairColorGray    = 5,
    LTAAMVAHairColorRed     = 6,
    LTAAMVAHairColorSandy   = 7,
    LTAAMVAHairColorWhite   = 8
};

LT_ENUM_AVAILABLE(10_10, 8_0, 20_0)
typedef NS_ENUM(NSInteger, LTAAMVALengthType) {
    LTAAMVALengthTypeVariable = 0,
    LTAAMVALengthTypeFixed    = 1
};

LT_ENUM_AVAILABLE(10_10, 8_0, 20_0)
typedef NS_ENUM(NSInteger, LTAAMVARegion) {
    LTAAMVARegionUnknown      = 0,
    LTAAMVARegionCanada       = 1,
    LTAAMVARegionUnitedStates = 2,
    LTAAMVARegionMexico       = 3
};

LT_ENUM_AVAILABLE(10_10, 8_0, 20_0)
typedef NS_ENUM(NSInteger, LTAAMVASex) {
    LTAAMVASexUnknown = 0,
    LTAAMVASexMale    = 1,
    LTAAMVASexFemale  = 2
};

LT_ENUM_AVAILABLE(10_10, 8_0, 20_0)
typedef NS_ENUM(NSInteger, LTAAMVASubfileType) {
    LTAAMVASubfileTypeJurisdictionSpecific = 0,
    LTAAMVASubfileTypeDL = 1 << 0,
    LTAAMVASubfileTypeID = 1 << 1
};

LT_ENUM_AVAILABLE(10_10, 8_0, 20_0)
typedef NS_ENUM(NSInteger, LTAAMVAValidCharacters) {
    LTAAMVAValidCharactersAlpha   = 1 << 0,
    LTAAMVAValidCharactersNumeric = 1 << 1,
    LTAAMVAValidCharactersSpecial = 1 << 2
};

LT_ENUM_AVAILABLE(10_10, 8_0, 20_0)
typedef NS_ENUM(NSInteger, LTAAMVAVersion) {
    LTAAMVAVersionVersionPre2000 = 1 << 0,
    LTAAMVAVersionVersion2000    = 1 << 1,
    LTAAMVAVersionVersion2003    = 1 << 2,
    LTAAMVAVersionVersion2005    = 1 << 3,
    LTAAMVAVersionVersion2009    = 1 << 4,
    LTAAMVAVersionVersion2010    = 1 << 5,
    LTAAMVAVersionVersion2011    = 1 << 6,
    LTAAMVAVersionVersion2012    = 1 << 7,
    LTAAMVAVersionVersion2013    = 1 << 8,
    LTAAMVAVersionVersion2016    = 1 << 9
};

LT_ENUM_AVAILABLE(10_10, 8_0, 20_0)
typedef NS_ENUM(NSInteger, LTAAMVAJurisdiction) {
    LTAAMVAJurisdictionUnknown            = 0,
    LTAAMVAJurisdictionAlabama            = 1,
    LTAAMVAJurisdictionAlaska             = 2,
    LTAAMVAJurisdictionAmericanSamoa      = 3,
    LTAAMVAJurisdictionArizona            = 4,
    LTAAMVAJurisdictionArkansas           = 5,
    LTAAMVAJurisdictionBritishColumbia    = 6,
    LTAAMVAJurisdictionCalifornia         = 7,
    LTAAMVAJurisdictionCoahuila           = 8,
    LTAAMVAJurisdictionColorado           = 9,
    LTAAMVAJurisdictionConnecticut        = 10,
    LTAAMVAJurisdictionDistrictOfColumbia = 11,
    LTAAMVAJurisdictionDelaware           = 12,
    LTAAMVAJurisdictionFlorida            = 13,
    LTAAMVAJurisdictionGeorgia            = 14,
    LTAAMVAJurisdictionGuam               = 15,
    LTAAMVAJurisdictionHawaii             = 16,
    LTAAMVAJurisdictionHidalgo            = 17,
    LTAAMVAJurisdictionIdaho              = 18,
    LTAAMVAJurisdictionIllinois           = 19,
    LTAAMVAJurisdictionIndiana            = 20,
    LTAAMVAJurisdictionIowa               = 21,
    LTAAMVAJurisdictionKansas             = 22,
    LTAAMVAJurisdictionKentucky           = 23,
    LTAAMVAJurisdictionLouisiana          = 24,
    LTAAMVAJurisdictionMaine              = 25,
    LTAAMVAJurisdictionManitoba           = 26,
    LTAAMVAJurisdictionMaryland           = 27,
    LTAAMVAJurisdictionMassachusetts      = 28,
    LTAAMVAJurisdictionMichigan           = 29,
    LTAAMVAJurisdictionMinnesota          = 30,
    LTAAMVAJurisdictionMississippi        = 31,
    LTAAMVAJurisdictionMissouri           = 32,
    LTAAMVAJurisdictionMontana            = 33,
    LTAAMVAJurisdictionNebraska           = 34,
    LTAAMVAJurisdictionNevada             = 35,
    LTAAMVAJurisdictionNewBrunswick       = 36,
    LTAAMVAJurisdictionNewHampshire       = 37,
    LTAAMVAJurisdictionNewJersey          = 38,
    LTAAMVAJurisdictionNewMexico          = 39,
    LTAAMVAJurisdictionNewYork            = 40,
    LTAAMVAJurisdictionNewfoundland       = 41,
    LTAAMVAJurisdictionNorthCarolina      = 42,
    LTAAMVAJurisdictionNorthDakota        = 43,
    LTAAMVAJurisdictionNovaScotia         = 44,
    LTAAMVAJurisdictionOhio               = 45,
    LTAAMVAJurisdictionOklahoma           = 46,
    LTAAMVAJurisdictionOntario            = 47,
    LTAAMVAJurisdictionOregon             = 48,
    LTAAMVAJurisdictionPennsylvania       = 49,
    LTAAMVAJurisdictionPrinceEdwardIsland = 50,
    LTAAMVAJurisdictionQuebec             = 51,
    LTAAMVAJurisdictionRhodeIsland        = 52,
    LTAAMVAJurisdictionSaskatchewan       = 53,
    LTAAMVAJurisdictionSouthCarolina      = 54,
    LTAAMVAJurisdictionSouthDakota        = 55,
    LTAAMVAJurisdictionTennessee          = 56,
    LTAAMVAJurisdictionStateDeptUsa       = 57,
    LTAAMVAJurisdictionTexas              = 58,
    LTAAMVAJurisdictionUsVirginIslands    = 59,
    LTAAMVAJurisdictionUtah               = 60,
    LTAAMVAJurisdictionVermont            = 61,
    LTAAMVAJurisdictionVirginia           = 62,
    LTAAMVAJurisdictionWashington         = 63,
    LTAAMVAJurisdictionWestVirginia       = 64,
    LTAAMVAJurisdictionWisconsin          = 65,
    LTAAMVAJurisdictionWyoming            = 66,
    LTAAMVAJurisdictionYukon              = 67
};
