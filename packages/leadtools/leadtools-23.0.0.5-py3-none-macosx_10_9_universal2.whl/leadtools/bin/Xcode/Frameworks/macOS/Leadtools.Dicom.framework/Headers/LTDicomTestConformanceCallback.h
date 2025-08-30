// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomTestConformanceCallback.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomElement.h>

typedef NS_OPTIONS(NSUInteger, LTDicomTestConformanceFlags) {
	LTDicomTestConformanceFlagsNone                  = 0,
	LTDicomTestConformanceFlagsUnknownClass          = 0x0001,
	LTDicomTestConformanceFlagsUnknownTag            = 0x0002,
	LTDicomTestConformanceFlagsUnknownVr             = 0x0004,
	LTDicomTestConformanceFlagsWrongVr               = 0x0008,
	LTDicomTestConformanceFlagsMinValMultiplicity    = 0x0010,
	LTDicomTestConformanceFlagsMaxValMultiplicity    = 0x0020,
	LTDicomTestConformanceFlagsDivideValMultiplicity = 0x0040,
	LTDicomTestConformanceFlagsImage                 = 0x0080,
	LTDicomTestConformanceFlagsElement               = 0x0100,
	LTDicomTestConformanceFlagsElementExists         = 0x0200,
	LTDicomTestConformanceFlagsMemory                = 0x0400,
};

typedef BOOL (^LTDicomTestConformanceCallback)(LTDicomElement *element, LTDicomTestConformanceFlags flags);
