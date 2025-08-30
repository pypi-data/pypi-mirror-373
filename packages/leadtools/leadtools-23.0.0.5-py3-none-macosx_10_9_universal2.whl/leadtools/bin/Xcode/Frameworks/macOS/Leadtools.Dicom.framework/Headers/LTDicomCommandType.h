// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomCommandType.h
//  Leadtools.Dicom
//

typedef NS_ENUM(NSInteger, LTDicomCommandType) {
	LTDicomCommandTypeUndefined = 0,
	LTDicomCommandTypeCStore    = 0x0001,
	LTDicomCommandTypeCFind     = 0x0020,
	LTDicomCommandTypeCGet      = 0x0010,
	LTDicomCommandTypeCMove     = 0x0021,
	LTDicomCommandTypeCCancel   = 0x0FFF,
	LTDicomCommandTypeCEcho     = 0x0030,
	LTDicomCommandTypeNReport   = 0x0100,
	LTDicomCommandTypeNGet      = 0x0110,
	LTDicomCommandTypeNSet      = 0x0120,
	LTDicomCommandTypeNAction   = 0x0130,
	LTDicomCommandTypeNCreate   = 0x0140,
	LTDicomCommandTypeNDelete   = 0x0150,
};

typedef NS_ENUM(NSInteger, LTDicomCommandStatusType) {
	LTDicomCommandStatusTypeSuccess                             = 0x0000,
	LTDicomCommandStatusTypeCancel                              = 0xFE00,
	LTDicomCommandStatusTypeAttributeListError                  = 0x0107,
	LTDicomCommandStatusTypeAttributeOutOfRange                 = 0x0116,
	LTDicomCommandStatusTypeClassNotSupported                   = 0x0122,
	LTDicomCommandStatusTypeClassInstanceConflict               = 0x0119,
	LTDicomCommandStatusTypeDuplicateInstance                   = 0x0111,
	LTDicomCommandStatusTypeDuplicateInvocation                 = 0x0210,
	LTDicomCommandStatusTypeInvalidArgumentValue                = 0x0115,
	LTDicomCommandStatusTypeInvalidAttributeValue               = 0x0106,
	LTDicomCommandStatusTypeInvalidObjectInstance               = 0x0117,
	LTDicomCommandStatusTypeMissingAttribute                    = 0x0120,
	LTDicomCommandStatusTypeMissingAttributeValue               = 0x0121,
	LTDicomCommandStatusTypeMistypedArgument                    = 0x0212,
	LTDicomCommandStatusTypeNoSuchArgument                      = 0x0114,
	LTDicomCommandStatusTypeNoSuchAttribute                     = 0x0105,
	LTDicomCommandStatusTypeNoSuchEventType                     = 0x0113,
	LTDicomCommandStatusTypeNoSuchObjectInstance                = 0x0112,
	LTDicomCommandStatusTypeNoSuchClass                         = 0x0118,
	LTDicomCommandStatusTypeProcessingFailure                   = 0x0110,
	LTDicomCommandStatusTypeResourceLimitation                  = 0x0213,
	LTDicomCommandStatusTypeUnrecognizedOperation               = 0x0211,
    LTDicomCommandStatusTypeDuplicateTransactionUid             = 0x0131,
	LTDicomCommandStatusTypeRefusedOutOfResources               = 0xA700,
	LTDicomCommandStatusTypeRefusedUnableToCalculateMatches     = 0xA701,
	LTDicomCommandStatusTypeRefusedUnableToPerformSuboperations = 0xA702,
	LTDicomCommandStatusTypeRefusedMoveDestinationUnknown       = 0xA801,
	LTDicomCommandStatusTypeFailure                             = 0xC001,
	LTDicomCommandStatusTypeReserved2                           = 0xC002,
	LTDicomCommandStatusTypeReserved3                           = 0xC003,
	LTDicomCommandStatusTypeReserved4                           = 0xC004,
	LTDicomCommandStatusTypeWarning                             = 0xB000,
	LTDicomCommandStatusTypePending                             = 0xFF00,
	LTDicomCommandStatusTypePendingWarning                      = 0xFF01,

};

typedef NS_ENUM(NSInteger, LTDicomCommandPriorityType) {
	LTDicomCommandPriorityTypeLow    = 0x0002,
	LTDicomCommandPriorityTypeMedium = 0x0000,
	LTDicomCommandPriorityTypeHigh   = 0x0001,
};
