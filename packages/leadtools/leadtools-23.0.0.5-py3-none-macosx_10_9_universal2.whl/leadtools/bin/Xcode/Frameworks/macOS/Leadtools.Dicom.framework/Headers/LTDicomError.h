// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomError.h
//  Leadtools.Dicom
//

#import <Leadtools/LTLeadtools.h>

typedef NS_ENUM(NSInteger, LTDicomErrorCode) {
	LTDicomErrorCodeSuccess                                = 0,
	LTDicomErrorCodeSupportLocked                          = 1,
	LTDicomErrorCodeNoMemory                               = 2,
	LTDicomErrorCodeOpen                                   = 3,
	LTDicomErrorCodeRead                                   = 4,
	LTDicomErrorCodeWrite                                  = 5,
	LTDicomErrorCodeSeek                                   = 6,
	LTDicomErrorCodeEnd                                    = 7,
	LTDicomErrorCodeFormat                                 = 8,
	LTDicomErrorCodeParameter                              = 9,
	LTDicomErrorCodeImage                                  = 10,
	LTDicomErrorCodeCompression                            = 11,
	LTDicomErrorCodePhotometricInterpretation              = 12,
	LTDicomErrorCodeConversion                             = 13,
	LTDicomErrorCodeRange                                  = 14,
	LTDicomErrorCodeBitsPerPixel                           = 15,
	LTDicomErrorCodeQualityFactor                          = 16,
	LTDicomErrorCodeDICOMDIRFolder                         = 200,
	LTDicomErrorCodeFile                                   = 201,
	LTDicomErrorCodeFileId                                 = 202,
	LTDicomErrorCodeJ2KLocked                              = 203,
	LTDicomErrorCodeLutDescriptorMissing                   = 204,
	LTDicomErrorCodeModalityLutMissing                     = 205,
	LTDicomErrorCodeBadPixelRepresentation                 = 206,
	LTDicomErrorCodePaletteColorLutDataMissing             = 207,
	LTDicomErrorCodeFeatureNotSupported                    = 208,
	LTDicomErrorCodeVoiLutMissing                          = 209,
	LTDicomErrorCodeOverlayAttributesMissing               = 210,
	LTDicomErrorCodeOverlayActivationLayerMissing          = 211,
	LTDicomErrorCodeOverlayDataMissing                     = 212,
	LTDicomErrorCodeInvalidStructSize                      = 213,
	LTDicomErrorCodeNULLPointer                            = 214,
	LTDicomErrorCodeImageProcessingAssemblyMissing         = 215,
	LTDicomErrorCodeCryptoLibraryLoadFailed                = 216,
	LTDicomErrorCodeInvalidMacTransferSyntax               = 217,
	LTDicomErrorCodePrivateKeyLoadFailed                   = 218,
	LTDicomErrorCodeCertificateLoadFailed                  = 219,
	LTDicomErrorCodeCertificateReadFailed                  = 220,
	LTDicomErrorCodeKeysMismatch                           = 221,
	LTDicomErrorCodeInvalidMacAlgorithm                    = 222,
	LTDicomErrorCodeInvalidEncryptionAlgorithm             = 223,
	LTDicomErrorCodeMacIDNumberAllocateFailed              = 224,
	LTDicomErrorCodeCryptoLibFailure                       = 225,
	LTDicomErrorCodeMacParameterMissing                    = 226,
	LTDicomErrorCodeMacIDNumberMissing                     = 227,
	LTDicomErrorCodeUnknownMacAlgorithm                    = 228,
	LTDicomErrorCodeSignatureMissing                       = 229,
	LTDicomErrorCodeInvalidSignature                       = 230,
	LTDicomErrorCodeCmpCodecMissing                        = 231,
	LTDicomErrorCodeJ2KCodecMissing                        = 232,
	LTDicomErrorCodeCantReplaceExistingCharacterSet        = 233,

	LTDicomErrorCodePrintSCUClassNotSupported              = 301,
	LTDicomErrorCodePrintSCUTimeout                        = 302,
	LTDicomErrorCodePrintSCUAssociateRQRejected            = 303,
	LTDicomErrorCodePrintSCUFailureStatus                  = 304,
	LTDicomErrorCodeSopInstanceUidAlreadyExists            = 305,
	LTDicomErrorCodeIncompatibleListOfImages               = 306,

	LTDicomErrorCodeBadPDUType                             = 17,
	LTDicomErrorCodeBadPDULength                           = 18,
	LTDicomErrorCodeBadPDUID                               = 19,

	LTDicomErrorCodeNetFailure                             = 29,
	LTDicomErrorCodeNetAccess                              = 30,
	LTDicomErrorCodeNetAddressInUse                        = 31,
	LTDicomErrorCodeNetAddressNotAvailable                 = 32,
	LTDicomErrorCodeNetAddressNotSupported                 = 33,
	LTDicomErrorCodeNetConnectionAborted                   = 34,
	LTDicomErrorCodeNetConnectionRefused                   = 35,
	LTDicomErrorCodeNetConnectionReset                     = 36,
	LTDicomErrorCodeNetDestinationRequired                 = 37,
	LTDicomErrorCodeNetArgumentIncorrect                   = 38,
	LTDicomErrorCodeNetBlockingOperationInProgress         = 39,
	LTDicomErrorCodeNetBlockingCanceled                    = 40,
	LTDicomErrorCodeNetInvalidSocket                       = 41,
	LTDicomErrorCodeNetSocketAlreadyConnected              = 42,
	LTDicomErrorCodeNetNoMoreFile                          = 43,
	LTDicomErrorCodeNetMessageSize                         = 44,
	LTDicomErrorCodeNetDown                                = 45,
	LTDicomErrorCodeNetReset                               = 46,
	LTDicomErrorCodeNetUnReach                             = 47,
	LTDicomErrorCodeNetNoBuffers                           = 48,
	LTDicomErrorCodeNetNotConnected                        = 49,
	LTDicomErrorCodeNetNotSocket                           = 50,
	LTDicomErrorCodeNetOperationNotSupported               = 51,
	LTDicomErrorCodeNetProtocolNotSupported                = 52,
	LTDicomErrorCodeNetProtocolType                        = 53,
	LTDicomErrorCodeNetShutdown                            = 54,
	LTDicomErrorCodeNetSocketNotSupported                  = 55,
	LTDicomErrorCodeNetTimeout                             = 56,
	LTDicomErrorCodeNetWouldBlock                          = 57,
	LTDicomErrorCodeNetHostNotFound                        = 58,
	LTDicomErrorCodeNetNoData                              = 59,
	LTDicomErrorCodeNetNoRecovery                          = 60,
	LTDicomErrorCodeNetNotInitialised                      = 61,
	LTDicomErrorCodeNetSystemNotReady                      = 62,
	LTDicomErrorCodeNetTryAgain                            = 63,
	LTDicomErrorCodeNetVersionNotSupported                 = 64,

	LTDicomErrorCodeNetSecurityBreach                      = 65,

	LTDicomErrorCodeTLSInternalError                       = 66,
	LTDicomErrorCodeSecurityLocked                         = 67,
	LTDicomErrorCodeTLSLibraryNotLoaded                    = 68,
	LTDicomErrorCodeBadSecurityMode                        = 69,
	LTDicomErrorCodeAnnotationFailure                      = 70,
	LTDicomErrorCodeAnnotationSupport                      = 71,
	LTDicomErrorCodeAnnotationAssemblyMissing              = 72,
	LTDicomErrorCodeTagAlreadyExists                       = 73,
	LTDicomErrorCodeAnnotationFileDoesntExist              = 74,

	LTDicomErrorCodeTLSCloseNotify                         = 128,
	LTDicomErrorCodeTLSUnexpectedMessage                   = 129,
	LTDicomErrorCodeTLSBadRecordMac                        = 130,
	LTDicomErrorCodeTLSDecryptFailed                       = 131,
	LTDicomErrorCodeTLSRecordOverflow                      = 132,
	LTDicomErrorCodeTLSDecompressionFailure                = 133,
	LTDicomErrorCodeTLSHandshakeFailure                    = 134,
	LTDicomErrorCodeTLSBadCertificate                      = 135,
	LTDicomErrorCodeTLSUnsupportedCertificate              = 136,
	LTDicomErrorCodeTLSCertificateRevoked                  = 137,
	LTDicomErrorCodeTLSCertificateExpired                  = 138,
	LTDicomErrorCodeTLSCertificateUnknown                  = 139,
	LTDicomErrorCodeTLSIllegalParameter                    = 140,
	LTDicomErrorCodeTLSUnknownCa                           = 141,
	LTDicomErrorCodeTLSAccessDenied                        = 142,
	LTDicomErrorCodeTLSDecodeError                         = 143,
	LTDicomErrorCodeTLSDecryptError                        = 144,
	LTDicomErrorCodeTLSExportRestriction                   = 145,
	LTDicomErrorCodeTLSProtocolVersion                     = 146,
	LTDicomErrorCodeTLSInsufficientSecurity                = 147,
	LTDicomErrorCodeTLSInternalError1                      = 148,
	LTDicomErrorCodeTLSUserCanceled                        = 149,
	LTDicomErrorCodeTLSNoRenegotiation                     = 150,
	LTDicomErrorCodeTLSNoKeepalive                         = 151,
	LTDicomErrorCodeTLSClosedControlled                    = 152,
	LTDicomErrorCodeTLSUnableToGetIssuerCert               = 160,
	LTDicomErrorCodeTLSUnableToGetCrl                      = 161,
	LTDicomErrorCodeTLSUnableToDecryptCertSignature        = 162,
	LTDicomErrorCodeTLSUnableToDecryptCrlSignature         = 163,
	LTDicomErrorCodeTLSUnableToDecodeIssuerPublicKey       = 164,
	LTDicomErrorCodeTLSCertSignatureFailure                = 165,
	LTDicomErrorCodeTLSCrlSignatureFailure                 = 166,
	LTDicomErrorCodeTLSCertNotYetValid                     = 167,
	LTDicomErrorCodeTLSCertHasExpired                      = 168,
	LTDicomErrorCodeTLSCrlNotYetValid                      = 169,
	LTDicomErrorCodeTLSCrlHasExpired                       = 170,
	LTDicomErrorCodeTLSErrorInCertNotBeforeField           = 171,
	LTDicomErrorCodeTLSErrorInCertNotAfterField            = 172,
	LTDicomErrorCodeTLSErrorInCrlLastUpdateField           = 173,
	LTDicomErrorCodeTLSErrorInCrlNextUpdateField           = 174,
	LTDicomErrorCodeTLSOutOfMem                            = 175,
	LTDicomErrorCodeTLSDepthZeroSelfSignedCert             = 176,
	LTDicomErrorCodeTLSSelfSignedCertInChain               = 177,
	LTDicomErrorCodeTLSUnableToGetIssuerCertLocally        = 178,
	LTDicomErrorCodeTLSUnableToVerifyLeafSignature         = 179,
	LTDicomErrorCodeTLSCertChainTooLong                    = 180,
	LTDicomErrorCodeTLSCertRevoked                         = 181,
	LTDicomErrorCodeTLSInvalidCa                           = 182,
	LTDicomErrorCodeTLSPathLengthExceeded                  = 183,
	LTDicomErrorCodeTLSInvalidPurpose                      = 184,
	LTDicomErrorCodeTLSCertUntrusted                       = 185,
	LTDicomErrorCodeTLSCertRejected                        = 186,
	LTDicomErrorCodeTLSSubjectIssuerMismatch               = 187,
	LTDicomErrorCodeTLSAkidSkidMismatch                    = 188,
	LTDicomErrorCodeTLSAkidIssuerSerialMismatch            = 189,
	LTDicomErrorCodeTLSKeyusageNoCertsign                  = 190,
	LTDicomErrorCodeTLSApplicationVerification             = 191,
	LTDicomErrorCodeTLSInvalidCtx                          = 192,
	LTDicomErrorCodeTLSInvalidCtxVerifyDepth               = 193,
	LTDicomErrorCodeTLSInvalidCtxVerifyMode                = 194,
	LTDicomErrorCodeTLSInvalidCtxCafile                    = 195,

	LTDicomErrorCodeISCLBadOption                          = 100,
	LTDicomErrorCodeISCLBadLength                          = 101,
	LTDicomErrorCodeISCLLocalIccard                        = 102,
	LTDicomErrorCodeISCLRemoteIccard                       = 103,
	LTDicomErrorCodeISCLBadMsgid                           = 104,
	LTDicomErrorCodeISCLBadVersion                         = 105,
	LTDicomErrorCodeISCLBadMutualAuthMethod                = 106,
	LTDicomErrorCodeISCLBadCommblockLength                 = 107,
	LTDicomErrorCodeISCLReceivedNak                        = 108,
	LTDicomErrorCodeISCLMsgTransmission                    = 109,
	LTDicomErrorCodeISCLPeerSmallLength                    = 110,
	LTDicomErrorCodeISCLLocalSmallLength                   = 111,
	LTDicomErrorCodeISCLDecrypt                            = 112,
	LTDicomErrorCodeISCLBadMac                             = 113,
	LTDicomErrorCodeISCLRndNoForSessionKeyExpected         = 114,
	LTDicomErrorCodeISCLPeerRefuseClose                    = 115,

	LTDicomErrorCodePrivateCreatorGroupInvalid             = 235,
	LTDicomErrorCodePrivateCreatorDataElementAlreadyExists = 236,
	LTDicomErrorCodePrivateCreatorDataElementMissing       = 237,
	LTDicomErrorCodePrivateCreatorElementsAllAllocated     = 238,
	LTDicomErrorCodePrivateCreatorElementInvalid           = 239,

	LTDicomErrorCodeEncapsulatedDocumentMissing            = 240,
	LTDicomErrorCodeInvalidElementLength                   = 241,
	LTDicomErrorCodeEncapsulatedDocumentFailure            = 242,
	LTDicomErrorCodeEncapsulatedDocumentInvalidType        = 243,

	LTDicomErrorCodeIpv4Ipv6Conflict                       = 307,

	LTDicomErrorCodeJlsFilterMissing                       = 308,

	LTDicomErrorCodeXmlInvalidFormat                       = 400,
	LTDicomErrorCodeXmlModuleListMissing                   = 401,
	LTDicomErrorCodeXmlInvalidIodList                      = 402,
	LTDicomErrorCodeXmlInvalidIodModuleItem                = 403,
	LTDicomErrorCodeXmlModuleNotFound                      = 404,
	LTDicomErrorCodeXmlInvalidModuleElement                = 405,
	LTDicomErrorCodeXmlInvalidModuleList                   = 406,
	LTDicomErrorCodeXmlInvalidModulelistModuleAttribute    = 407,
	LTDicomErrorCodeXmlInvalidIodListModuleAttribute       = 408,
	LTDicomErrorCodeXmlInvalidIodListIodAttribute          = 409,
	LTDicomErrorCodeXmlInvalidElementList                  = 410,
	LTDicomErrorCodeXmlInvalidElementListItemAttribute     = 411,
	LTDicomErrorCodeXmlInvalidUidListItemAttribute         = 412,
	LTDicomErrorCodeXmlInvalidConceptGroupList             = 413,
	LTDicomErrorCodeXmlInvalidContextGroupAttribute        = 414,
	LTDicomErrorCodeXmlInvalidCodedConceptAttribute        = 415,

	LTDicomErrorCodeElementAlreadyExists                   = 416,
	LTDicomErrorCodeTransferSyntaxNotSupported             = 417,
	LTDicomErrorCodeCanceled                               = 418,
	LTDicomErrorCodeClassNotFound                          = 419,

	LTDicomErrorCodeJP2CodecMissing                        = 420,
    LTDicomErrorCodeTooManyOpenFiles                       = 421,
    LTDicomErrorCodeDiskFull                               = 422,
    LTDicomErrorCodeNetHostUnreachable                     = 423
};

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

NS_ASSUME_NONNULL_BEGIN

LEADTOOLS_EXPORT NSErrorDomain const LTDicomErrorDomain;
LEADTOOLS_EXPORT NSExceptionName const LeadtoolsDicomException;

LEADTOOLS_EXPORT NSError *LTDicomErrorWithCode(LTDicomErrorCode code);
LEADTOOLS_EXPORT NSException *LTDicomExceptionWithCode(LTDicomErrorCode code);



@interface NSError (LTDicomErrorCode)

- (instancetype)initWithDicomError:(LTDicomErrorCode)code;
+ (NSError *)errorWithDicomError:(LTDicomErrorCode)code OBJC_SWIFT_UNAVAILABLE("use object initializers instead");

@end

@interface NSException (LTDicomErrorCode)

- (instancetype)initWithDicomError:(LTDicomErrorCode)code;
+ (NSException *)exceptionWithDicomError:(LTDicomErrorCode)code OBJC_SWIFT_UNAVAILABLE("use object initializers instead");

@end

NS_ASSUME_NONNULL_END
