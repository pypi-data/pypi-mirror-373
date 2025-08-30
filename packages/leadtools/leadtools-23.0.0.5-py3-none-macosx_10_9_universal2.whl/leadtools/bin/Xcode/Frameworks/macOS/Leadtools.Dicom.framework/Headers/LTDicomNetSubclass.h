// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomNetSubclass.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomNet.h>

NS_ASSUME_NONNULL_BEGIN

@interface LTDicomNet (EventsProtected)

- (void)onConnect:(LTDicomErrorCode)error;
- (void)onAccept:(LTDicomErrorCode)error;
- (void)onClose:(LTDicomErrorCode)error net:(LTDicomNet *)net;

- (void)onReceiveAssociateRequest:(LTDicomAssociate *)association;
- (void)onReceiveAssociateAccept:(LTDicomAssociate *)association;
- (void)onReceiveAssociateReject:(LTDicomAssociateRejectResultType)result source:(LTDicomAssociateRejectSourceType)source reason:(LTDicomAssociateRejectReasonType)reason;

- (void)onReceiveReleaseRequest;
- (void)onReceiveReleaseResponse;
- (void)onReceiveAbort:(LTDicomAbortSourceType)source reason:(LTDicomAbortReasonType)reason;

- (void)onSecureLinkReady:(LTDicomErrorCode)error;

- (BOOL)getChallengeIscl:(uint64_t *)challenge parameter:(uint64_t)parameter;
- (BOOL)internalAuthenticateIscl:(uint64_t)challenge response:(uint64_t *)response parameter:(uint64_t)parameter;
- (BOOL)externalAuthenticateIscl:(uint64_t)challenge response:(uint64_t)response parameter:(uint64_t)parameter;

- (void)onNonSecureReceivedIscl:(LTDicomErrorCode)error buffer:(const void *)buffer length:(NSUInteger)length;
- (void)onReceivedISCLPacket:(LTDicomErrorCode)error buffer:(const void *)buffer length:(NSUInteger)length;
- (void)onNonSecureSendIscl:(LTDicomErrorCode)error type:(uint8_t)type length:(NSUInteger)length;

- (void)onReceiveData:(uint8_t)presentationID commandSet:(null_unspecified LTDicomDataSet *)cs dataSet:(nullable LTDicomDataSet *)ds;

- (void)onReceive:(LTDicomErrorCode)error pduType:(LTDicomPduType)pduType buffer:(const void *)buffer length:(NSUInteger)length;
- (void)onSend:(LTDicomErrorCode)error pduType:(LTDicomPduType)pduType length:(NSUInteger)length;



- (void)onReceiveCStoreRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance priority:(LTDicomCommandPriorityType)priority moveAE:(NSString *)moveAE moveMessageID:(uint16_t)moveMessageID dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)onReceiveCStoreResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status;

- (void)onReceiveCFindRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass priority:(LTDicomCommandPriorityType)priority dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)onReceiveCFindResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)onReceiveCGetRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass priority:(LTDicomCommandPriorityType)priority dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)onReceiveCGetResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status remaining:(uint16_t)remaining completed:(uint16_t)completed failed:(uint16_t)failed warning:(uint16_t)warning dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)onReceiveCMoveRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass priority:(LTDicomCommandPriorityType)priority moveAE:(NSString *)moveAE dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)onReceiveCMoveResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status remaining:(uint16_t)remaining completed:(uint16_t)completed failed:(uint16_t)failed warning:(uint16_t)warning dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)onReceiveCCancelRequest:(uint8_t)presentationID messageID:(uint16_t)messageID;

- (void)onReceiveCEchoRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass;
- (void)onReceiveCEchoResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status;



- (void)onReceiveNReportRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance dicomEvent:(uint16_t)dicomEvent dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)onReceiveNReportResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dicomEvent:(uint16_t)dicomEvent dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)onReceiveNGetRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance attributes:(unsigned int *)attributes attributesCount:(NSUInteger)count;
- (void)onReceiveNGetResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)onReceiveNSetRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)onReceiveNSetResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)onReceiveNActionRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance action:(uint16_t)action dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)onReceiveNActionResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status action:(uint16_t)action dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)onReceiveNCreateRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)onReceiveNCreateResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)onReceiveNDeleteRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance;
- (void)onReceiveNDeleteResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status;

- (void)onReceiveUnknown:(uint8_t)presentationID commandSet:(null_unspecified LTDicomDataSet *)cs dataSet:(nullable LTDicomDataSet *)ds;
- (nullable NSString *)onPrivateKeyPassword:(BOOL)encryption;

@end

NS_ASSUME_NONNULL_END
