// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomPduType.h
//  Leadtools.Dicom
//

typedef NS_ENUM(NSInteger, LTDicomPduType) {
	LTDicomPduTypeUnknown          = 0x00,

	LTDicomPduTypeAssociateRequest = 0x01,
	LTDicomPduTypeAssociateAccept  = 0x02,
	LTDicomPduTypeAssociateReject  = 0x03,
	LTDicomPduTypeDataTransfer     = 0x04,
	LTDicomPduTypeReleaseRequest   = 0x05,
	LTDicomPduTypeReleaseResponse  = 0x06,
	LTDicomPduTypeAbort            = 0x07,
};
