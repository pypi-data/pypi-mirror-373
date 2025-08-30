// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomImageFlags.h
//  Leadtools.Dicom
//

typedef NS_OPTIONS(NSUInteger, LTDicomGetImageFlags) {
	LTDicomGetImageFlagsNone                            = 0,
	LTDicomGetImageFlagsAutoLoadOverlays                = 0x0001,
	LTDicomGetImageFlagsAutoApplyModalityLut            = 0x0002,
	LTDicomGetImageFlagsAutoApplyVoiLut                 = 0x0004,
	LTDicomGetImageFlagsAllowRangeExpansion             = 0x0008,
	LTDicomGetImageFlagsAutoScaleModalityLut            = 0x0010,
	LTDicomGetImageFlagsAutoScaleVoiLut                 = 0x0020,
	LTDicomGetImageFlagsAutoDetectInvalidRleCompression = 0x0040,
	LTDicomGetImageFlagsRleSwapSegments                 = 0x0080,
	LTDicomGetImageFlagsLoadCorrupted                   = 0x0100,
	LTDicomGetImageFlagsVoiLutPaintOnly                 = 0x0200,
};

typedef NS_OPTIONS(NSUInteger, LTDicomSetImageFlags) {
	LTDicomSetImageFlagsNone                   = 0,
	LTDicomSetImageFlagsAutoSaveOverlays       = 0x00000001,
	LTDicomSetImageFlagsAutoSetVoiLut          = 0x00000002,
	LTDicomSetImageFlagsMinimizeJpegSize       = 0x00000004,
	LTDicomSetImageFlagsKeepLutsIntact         = 0x20000000,
	LTDicomSetImageFlagsMfgOverwriteShared     = 0x00000008,
	LTDicomSetImageFlagsMfgVoiLutPerFrame      = 0x00000010,
	LTDicomSetImageFlagsMfgVoiLutShared        = 0x00000020,
	LTDicomSetImageFlagsMfgModalityLutPerFrame = 0x00000040,
	LTDicomSetImageFlagsMfgModalityLutShared   = 0x00000080,
	LTDicomSetImageFlagsOptimizedMemory        = 0x00000200,
};

typedef NS_ENUM(NSInteger, LTDicomImageCompressionType) {
	LTDicomImageCompressionTypeNone,
	LTDicomImageCompressionTypeRle,
	LTDicomImageCompressionTypeJpegLossless,
	LTDicomImageCompressionTypeJpegLossy,
	LTDicomImageCompressionTypeJpegLsLossless,
	LTDicomImageCompressionTypeJpegLsLossy,
	LTDicomImageCompressionTypeJ2kLossless,
	LTDicomImageCompressionTypeJ2kLossy,
	LTDicomImageCompressionTypeMpeg2,
	LTDicomImageCompressionTypeMpeg2Hd,
	LTDicomImageCompressionTypeH265,
	LTDicomImageCompressionTypeUnknown,
	LTDicomImageCompressionTypeJpxLossless,
	LTDicomImageCompressionTypeJpxLossy,
};

typedef NS_ENUM(NSInteger, LTDicomImagePhotometricInterpretationType) {
	LTDicomImagePhotometricInterpretationTypeMonochrome1,
	LTDicomImagePhotometricInterpretationTypeMonochrome2,
	LTDicomImagePhotometricInterpretationTypePaletteColor,
	LTDicomImagePhotometricInterpretationTypeRgb,
	LTDicomImagePhotometricInterpretationTypeArgb,
	LTDicomImagePhotometricInterpretationTypeCmyk,
	LTDicomImagePhotometricInterpretationTypeYbrFull422,
	LTDicomImagePhotometricInterpretationTypeYbrFull,
	LTDicomImagePhotometricInterpretationTypeYbrRct,
	LTDicomImagePhotometricInterpretationTypeYbrIct,
};
