// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomNet.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomNetEnums.h>
#import <Leadtools.Dicom/LTDicomCommandType.h>
#import <Leadtools.Dicom/LTDicomAssociate.h>
#import <Leadtools.Dicom/LTDicomPduType.h>
#import <Leadtools.Dicom/LTDicomDataSet.h>
#import <Leadtools.Dicom/LTDicomError.h>
#import <Leadtools.Dicom/LTDicomSocketOptions.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomOpenSslContextCreationSettings : NSObject

@property (nonatomic, assign)         LTDicomSslMethodType methodType;
@property (nonatomic, assign)         LTDicomOpenSslVerificationFlags verificationFlags;
@property (nonatomic, assign)         LTDicomOpenSslOptionsFlags options;

@property (nonatomic, assign)         NSInteger maximumVerificationDepth;

@property (nonatomic, copy, nullable) NSString *certificationAuthoritiesFileName;

- (instancetype)initWithMethodType:(LTDicomSslMethodType)methodType verificationFlags:(LTDicomOpenSslVerificationFlags)verificationFlags options:(LTDicomOpenSslOptionsFlags)options maximumVerificationDepth:(NSInteger)maximumVerificationDepth certificationAuthoritiesFileName:(NSString *)certificationAuthoritiesFileName NS_DESIGNATED_INITIALIZER;
- (instancetype)init __unavailable;

@end

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomNet : NSObject

@property (nonatomic, strong)                     LTDicomSocketOptions *socketOptions;
@property (nonatomic, strong, readonly)           LTDicomSocketOptions *defaultSocketOptions;

@property (nonatomic, assign, readonly)           BOOL isActivated;
@property (nonatomic, assign, readonly)           BOOL isConnected;
@property (nonatomic, assign, readonly)           BOOL isAssociated;

@property (nonatomic, assign, readonly)           NSUInteger queueSend;
@property (nonatomic, assign, readonly)           NSUInteger numberOfClients;

@property (nonatomic, strong, readonly, nullable) LTDicomNet *server;

@property (nonatomic, strong, readonly, nullable) NSString *hostAddress;
@property (nonatomic, assign, readonly)           NSUInteger hostPort;
@property (nonatomic, strong, readonly, nullable) NSString *peerAddress;
@property (nonatomic, assign, readonly)           NSUInteger peerPort;

+ (void)startup;
+ (void)shutdown;

- (instancetype)initWithPath:(nullable NSString *)path securityMode:(LTDicomNetSecurityMode)mode error:(NSError **)error;
- (instancetype)initWithPath:(nullable NSString *)path securityMode:(LTDicomNetSecurityMode)mode reserved:(BOOL)reserved error:(NSError **)error;
- (instancetype)init;

- (BOOL)initializeWithPath:(nullable NSString *)path mode:(LTDicomNetSecurityMode)mode openSslContextCreationSettings:(nullable LTDicomOpenSslContextCreationSettings *)settings error:(NSError **)error;

- (BOOL)closeForced:(BOOL)forced error:(NSError **)error NS_SWIFT_NAME(close(forced:));

- (nullable LTDicomNet *)clientAtIndex:(NSUInteger)index;

@end



@interface LTDicomNet (Associate)

@property (nonatomic, strong, readonly, nullable) LTDicomAssociate *association;

- (BOOL)sendAssociateRequest:(LTDicomAssociate *)associate error:(NSError **)error;
- (BOOL)sendAssociateAccept:(LTDicomAssociate *)associate error:(NSError **)error;
- (BOOL)sendAssociateReject:(LTDicomAssociateRejectResultType)result source:(LTDicomAssociateRejectSourceType)source reason:(LTDicomAssociateRejectReasonType)reason error:(NSError **)error;

- (BOOL)sendData:(NSUInteger)presentationID commandSet:(LTDicomDataSet *)commandSet dataSet:(nullable LTDicomDataSet *)dataSet error:(NSError **)error;

- (BOOL)sendReleaseRequest:(NSError **)error;
- (BOOL)sendReleaseResponse:(NSError **)error;
- (BOOL)sendAbort:(LTDicomAbortSourceType)source reason:(LTDicomAbortReasonType)reason error:(NSError **)error;

@end



@interface LTDicomNet (Connect)

@property (nonatomic, assign, readonly) LTDicomNetIpTypeFlags ipType;

- (BOOL)connect:(nullable NSString *)hostAddress hostPort:(NSUInteger)hostPort peerAddress:(NSString *)peerAddress peerPort:(NSUInteger)peerPort error:(NSError **)error;
- (BOOL)connect:(nullable NSString *)hostAddress hostPort:(NSUInteger)hostPort peerAddress:(NSString *)peerAddress peerPort:(NSUInteger)peerPort ipType:(LTDicomNetIpTypeFlags)ipType error:(NSError **)error;

- (BOOL)listen:(NSString *)hostAddress hostPort:(NSUInteger)hostPort maximumNumberOfPeers:(NSUInteger)max error:(NSError **)error;
- (BOOL)listen:(NSString *)hostAddress hostPort:(NSUInteger)hostPort maximumNumberOfPeers:(NSUInteger)max ipType:(LTDicomNetIpTypeFlags)ipType error:(NSError **)error;

- (BOOL)accept:(LTDicomNet *)net error:(NSError **)error;

- (void)close;

@end



@interface LTDicomNet (CCommand)

- (BOOL)sendCStoreRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance priority:(LTDicomCommandPriorityType)priority moveAE:(NSString *)moveAE moveMessageID:(uint16_t)moveMessageID dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;
- (BOOL)sendCStoreResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status error:(NSError **)error;

- (BOOL)sendCFindRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass priority:(LTDicomCommandPriorityType)priority dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;
- (BOOL)sendCFindResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;

- (BOOL)sendCGetRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass priority:(LTDicomCommandPriorityType)priority dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;
- (BOOL)sendCGetResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status remaining:(uint16_t)remaining completed:(uint16_t)completed failed:(uint16_t)failed warning:(uint16_t)warning dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;

- (BOOL)sendCMoveRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass priority:(LTDicomCommandPriorityType)priority moveAE:(NSString *)moveAE dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;
- (BOOL)sendCMoveResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status remaining:(uint16_t)remaining completed:(uint16_t)completed failed:(uint16_t)failed warning:(uint16_t)warning dataSet:(nullable LTDicomDataSet *)dataSet error:(NSError **)error;

- (BOOL)sendCCancelRequest:(uint8_t)presentationID messageID:(uint16_t)messageID error:(NSError **)error;

- (BOOL)sendCEchoRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass error:(NSError **)error;
- (BOOL)sendCEchoResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status error:(NSError **)error;

@end



@interface LTDicomNet (NCommand)

- (BOOL)sendNReportRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance dicomEvent:(uint16_t)dicomEvent dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;
- (BOOL)sendNReportResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dicomEvent:(uint16_t)dicomEvent dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;

- (BOOL)sendNGetRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance attributes:(unsigned int *)attributes attributesCount:(NSUInteger)count error:(NSError **)error;
- (BOOL)sendNGetResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;

- (BOOL)sendNSetRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;
- (BOOL)sendNSetResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;

- (BOOL)sendNActionRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance action:(uint16_t)action dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;
- (BOOL)sendNActionResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status action:(uint16_t)action dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;

- (BOOL)sendNCreateRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;
- (BOOL)sendNCreateResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet error:(NSError **)error;

- (BOOL)sendNDeleteRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance error:(NSError **)error;
- (BOOL)sendNDeleteResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status error:(NSError **)error;

@end



@interface LTDicomNet (TLS)

@property (nonatomic, assign, readonly) LTDicomTlsCipherSuiteType tlsCipherSuite;

- (LTDicomTlsCipherSuiteType)tlsCipherSuiteAtIndex:(NSUInteger)index;
- (BOOL)setTlsCipherSuite:(LTDicomTlsCipherSuiteType)cipher atIndex:(NSUInteger)index error:(NSError **)error;

- (LTDicomTlsEncryptionMethodType)tlsEncryptionAlgorithmForCipher:(LTDicomTlsCipherSuiteType)cipher;
- (LTDicomTlsAuthenticationMethodType)tlsAuthenticationAlgorithmForCipher:(LTDicomTlsCipherSuiteType)cipher;
- (LTDicomTlsMacMethodType)tlsIntegrityAlgorithmForCipher:(LTDicomTlsCipherSuiteType)cipher;
- (LTDicomTlsExchangeMethodType)tlsKeyExchangeAlgorithmForCipher:(LTDicomTlsCipherSuiteType)cipher;

- (NSUInteger)tlsEncryptionKeyLength:(LTDicomTlsCipherSuiteType)cipher;
- (NSUInteger)tlsMutualAuthenticationKeyLength:(LTDicomTlsCipherSuiteType)cipher;

- (BOOL)setTlsClientCertificate:(NSString *)pathToCertificate certificateType:(LTDicomTlsCertificateType)certificateType keyFile:(nullable NSString *)pathToKeyFile error:(NSError **)error;

@end



@interface LTDicomNet (ISCL)

@property (nonatomic, assign, readonly) NSUInteger isclCommunicationBlockLength;
@property (nonatomic, assign, readonly) NSUInteger isclPeerRequestedMessageLength;
@property (nonatomic, assign, readonly) NSUInteger isclIndexForEncryption;
@property (nonatomic, assign, readonly) NSUInteger isclIndexForMutualAuthentication;
@property (nonatomic, assign, readonly) NSUInteger isclStatus;

@property (nonatomic, assign, readonly) NSUInteger lastIsclOrTlsError;

@property (nonatomic, assign, readonly) LTDicomIsclEncryptionMethodType isclPeerEncryption;
@property (nonatomic, assign, readonly) LTDicomIsclSigningMethodType isclPeerMac;

@property (nonatomic, assign, readonly) BOOL isIsclQueueEmpty;

- (BOOL)setIsclMaxCommunicationBlockLength:(NSUInteger)maxCommunicationBlockLength error:(NSError **)error;
- (BOOL)setIsclMaxMessageLength:(NSUInteger)maxMessageLength error:(NSError **)error;
- (BOOL)setIsclMutualAuthenticationAlgorithm:(LTDicomIsclMutualAuthenticationMode)mutualAuthenticationMode error:(NSError **)error;
- (BOOL)setIsclDefaultEncryptionMode:(LTDicomIsclEncryptionMethodType)encryptionMode error:(NSError **)error;
- (BOOL)setIsclDefaultSigningMode:(LTDicomIsclSigningMethodType)signingMode error:(NSError **)error;

- (BOOL)setIsclAuthenticationData:(NSData *)data error:(NSError **)error;
- (nullable NSData *)getIsclPeerAuthenticationData:(NSError **)error;

- (BOOL)setIsclMutualAuthenticationKey:(uint64_t)key atIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)setIsclIndexForMutualAuthentication:(NSUInteger)index error:(NSError **)error;

- (BOOL)setIsclEncryptionKey:(uint64_t)key atIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)setIsclEncryptionKeyIndex:(NSUInteger)index error:(NSError **)error;

- (BOOL)sendNonSecureIscl:(NSData *)data range:(NSRange)dataRange error:(NSError **)error;

@end

NS_ASSUME_NONNULL_END










