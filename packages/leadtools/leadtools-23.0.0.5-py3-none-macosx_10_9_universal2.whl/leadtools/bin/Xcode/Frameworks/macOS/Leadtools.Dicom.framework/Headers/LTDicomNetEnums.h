// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomNetEnums.h
//  Leadtools.Dicom
//

typedef NS_OPTIONS(NSUInteger, LTDicomOpenSslOptionsFlags) {
	LTDicomOpenSslOptionsFlagsNone              = 0,
	LTDicomOpenSslOptionsFlagsNoSslV2           = 0x01000000,
	LTDicomOpenSslOptionsFlagsNoSslV3           = 0x02000000,
	LTDicomOpenSslOptionsFlagsNoTlsV1           = 0x04000000,
	LTDicomOpenSslOptionsFlagsAllBugWorkarounds = 0x00000FFF,
};

typedef NS_OPTIONS(NSUInteger, LTDicomOpenSslVerificationFlags) {
	LTDicomOpenSslVerificationFlagsNone                    = 0x00,
	LTDicomOpenSslVerificationFlagsPeer                    = 0x01,
	LTDicomOpenSslVerificationFlagsFailIfNoPeerCertificate = 0x02,
	LTDicomOpenSslVerificationFlagsClientOnce              = 0x04,
	LTDicomOpenSslVerificationFlagsAll                     = 0x07,
};

typedef NS_OPTIONS(NSUInteger, LTDicomNetIpTypeFlags) {
	LTDicomNetIpTypeFlagsNone       = 0x000,
	LTDicomNetIpTypeFlagsIpv4       = 0x001,
	LTDicomNetIpTypeFlagsIpv6       = 0x002,
	LTDicomNetIpTypeFlagsIpv4OrIpv6 = 0x003,
};

typedef NS_ENUM(NSUInteger, LTDicomNetSecurityMode) {
	LTDicomNetSecurityModeNone = 0xABCD0000,
	LTDicomNetSecurityModeIscl = 0xABCD0001,
	LTDicomNetSecurityModeTls  = 0xABCD0002,
};

typedef NS_ENUM(NSInteger, LTDicomTlsCipherSuiteType) {
	LTDicomTlsCipherSuiteTypeNone                    = 0,
	LTDicomTlsCipherSuiteTypeDheRsaWithDesCbcSha     = 0x12,
	LTDicomTlsCipherSuiteTypeDheRsaWith3DesEdeCbcSha = 0x13,
	LTDicomTlsCipherSuiteTypeDheRsaAes256Sha         = 0x14,
};

typedef NS_ENUM(NSInteger, LTDicomTlsEncryptionMethodType) {
	LTDicomTlsEncryptionMethodTypeNone     = 0x00,
	LTDicomTlsEncryptionMethodTypeDes      = 0x01,
	LTDicomTlsEncryptionMethodTypeThreeDes = 0x02,
	LTDicomTlsEncryptionMethodTypeRc4      = 0x03,
	LTDicomTlsEncryptionMethodTypeRc2      = 0x04,
	LTDicomTlsEncryptionMethodTypeIdea     = 0x05,
	LTDicomTlsEncryptionMethodTypeFortezza = 0x06,
	LTDicomTlsEncryptionMethodTypeAes      = 0x07,
};

typedef NS_ENUM(NSInteger, LTDicomTlsMacMethodType) {
	LTDicomTlsMacMethodTypeNone = 0x00,
	LTDicomTlsMacMethodTypeSha1 = 0x10,
	LTDicomTlsMacMethodTypeMd5  = 0x11,
};

typedef NS_ENUM(NSInteger, LTDicomTlsAuthenticationMethodType) {
	LTDicomTlsAuthenticationMethodTypeNone = 0,
	LTDicomTlsAuthenticationMethodTypeRsa  = 0x20,
	LTDicomTlsAuthenticationMethodTypeDss  = 0x21,
	LTDicomTlsAuthenticationMethodTypeDh   = 0x022,
};

typedef NS_ENUM(NSInteger, LTDicomTlsExchangeMethodType) {
	LTDicomTlsExchangeMethodTypeNone         = 0x00,
	LTDicomTlsExchangeMethodTypeRsaSignedDhe = 0x40,
	LTDicomTlsExchangeMethodTypeRsa          = 0x41,
	LTDicomTlsExchangeMethodTypeDh           = 0x42,
	LTDicomTlsExchangeMethodTypeDss          = 0x43,
	LTDicomTlsExchangeMethodTypeFortezza     = 0x44,
};

typedef NS_ENUM(NSInteger, LTDicomSslMethodType) {
	LTDicomSslMethodTypeSslV2  = 0x01,
	LTDicomSslMethodTypeSslV3  = 0x02,
	LTDicomSslMethodTypeTlsV1  = 0x03,
	LTDicomSslMethodTypeSslV23 = 0x04,
};

typedef NS_ENUM(NSInteger, LTDicomTlsCertificateType) {
	LTDicomTlsCertificateTypePem  = 1,
	LTDicomTlsCertificateTypeAsn1 = 2,
};

typedef NS_ENUM(NSInteger, LTDicomIsclMutualAuthenticationMode) {
	LTDicomIsclMutualAuthenticationModeThreePFourW = 0x00000000,
};

typedef NS_ENUM(NSInteger, LTDicomIsclEncryptionMethodType) {
	LTDicomIsclEncryptionMethodTypeNone   = 0x00000000,
	LTDicomIsclEncryptionMethodTypeDesCbc = 0x00001212,
};

typedef NS_ENUM(NSInteger, LTDicomIsclSigningMethodType) {
	LTDicomIsclSigningMethodTypeNone   = 0x00000000,
	LTDicomIsclSigningMethodTypeMd5    = 0x00001441,
	LTDicomIsclSigningMethodTypeDesMac = 0x00004001,
};

typedef NS_ENUM(NSInteger, LTDicomAssociateRejectResultType) {
	LTDicomAssociateRejectResultTypePermanent = 1,
	LTDicomAssociateRejectResultTypeTransient = 2,
};

typedef NS_ENUM(NSInteger, LTDicomAssociateRejectSourceType) {
	LTDicomAssociateRejectSourceTypeUser      = 1,
	LTDicomAssociateRejectSourceTypeProvider1 = 2,
	LTDicomAssociateRejectSourceTypeProvider2 = 3,
};

typedef NS_ENUM(NSInteger, LTDicomAssociateRejectReasonType) {
	LTDicomAssociateRejectReasonTypeUnknown     = 1,
	LTDicomAssociateRejectReasonTypeApplication = 2,
	LTDicomAssociateRejectReasonTypeCalling     = 3,
	LTDicomAssociateRejectReasonTypeCalled      = 7,
	LTDicomAssociateRejectReasonTypeVersion     = 2,
	LTDicomAssociateRejectReasonTypeCongestion  = 1,
	LTDicomAssociateRejectReasonTypeLimit       = 2,
};

typedef NS_ENUM(NSInteger, LTDicomAbortSourceType) {
	LTDicomAbortSourceTypeUser     = 0,
	LTDicomAbortSourceTypeProvider = 2,
};

typedef NS_ENUM(NSInteger, LTDicomAbortReasonType) {
	LTDicomAbortReasonTypeUnknown               = 0,
	LTDicomAbortReasonTypeUnrecognized          = 1,
	LTDicomAbortReasonTypeUnexpected            = 2,
	LTDicomAbortReasonTypeUnrecognizedParameter = 4,
	LTDicomAbortReasonTypeUnexpectedParameter   = 5,
	LTDicomAbortReasonTypeInvalidParameterValue = 6,
};
