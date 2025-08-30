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

@protocol LTDicomNetDelegate <NSObject>

@optional
- (void)dicomNet:(LTDicomNet *)net didConnect:(LTDicomErrorCode)error;
- (void)dicomNet:(LTDicomNet *)net didAccept:(LTDicomErrorCode)error;
- (void)dicomNet:(LTDicomNet *)net didClose:(LTDicomErrorCode)error otherNet:(nullable LTDicomNet *)otherNet;

- (void)dicomNet:(LTDicomNet *)net didReceiveAssociateRequest:(LTDicomAssociate *)association;
- (void)dicomNet:(LTDicomNet *)net didReceiveAssociateAccept:(LTDicomAssociate *)association;
- (void)dicomNet:(LTDicomNet *)net didReceiveAssociateReject:(LTDicomAssociateRejectResultType)result source:(LTDicomAssociateRejectSourceType)source reason:(LTDicomAssociateRejectReasonType)reason;

- (void)dicomNetDidReceiveReleaseRequest:(LTDicomNet *)net;
- (void)dicomNetDidReceiveReleaseResponse:(LTDicomNet *)net;
- (void)dicomNet:(LTDicomNet *)net didReceiveAbort:(LTDicomAbortSourceType)source reason:(LTDicomAbortReasonType)reason;

- (void)dicomNet:(LTDicomNet *)net didReceiveData:(uint8_t)presentationID commandSet:(null_unspecified LTDicomDataSet *)cs dataSet:(nullable LTDicomDataSet *)ds;

- (void)dicomNet:(LTDicomNet *)net didReceive:(LTDicomErrorCode)error pduType:(LTDicomPduType)pduType buffer:(const void *)buffer length:(NSUInteger)length;
- (void)dicomNet:(LTDicomNet *)net didSend:(LTDicomErrorCode)error pduType:(LTDicomPduType)pduType length:(NSUInteger)length;



- (void)dicomNet:(LTDicomNet *)net didReceiveCStoreRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance priority:(LTDicomCommandPriorityType)priority moveAE:(NSString *)moveAE moveMessageID:(uint16_t)moveMessageID dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)dicomNet:(LTDicomNet *)net didReceiveCStoreResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status;

- (void)dicomNet:(LTDicomNet *)net didReceiveCFindRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass priority:(LTDicomCommandPriorityType)priority dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)dicomNet:(LTDicomNet *)net didReceiveCFindResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status dataSet:(nullable LTDicomDataSet *)dataSet;

- (void)dicomNet:(LTDicomNet *)net didReceiveCGetRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass priority:(LTDicomCommandPriorityType)priority dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)dicomNet:(LTDicomNet *)net didReceiveCGetResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status remaining:(uint16_t)remaining completed:(uint16_t)completed failed:(uint16_t)failed warning:(uint16_t)warning dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)dicomNet:(LTDicomNet *)net didReceiveCMoveRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass priority:(LTDicomCommandPriorityType)priority moveAE:(NSString *)moveAE dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)dicomNet:(LTDicomNet *)net didReceiveCMoveResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status remaining:(uint16_t)remaining completed:(uint16_t)completed failed:(uint16_t)failed warning:(uint16_t)warning dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)dicomNet:(LTDicomNet *)net didReceiveCCancelRequest:(uint8_t)presentationID messageID:(uint16_t)messageID;

- (void)dicomNet:(LTDicomNet *)net didReceiveCEchoRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass;
- (void)dicomNet:(LTDicomNet *)net didReceiveCEchoResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass status:(LTDicomCommandStatusType)status;



- (void)dicomNet:(LTDicomNet *)net didReceiveNReportRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance dicomEvent:(uint16_t)dicomEvent dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)dicomNet:(LTDicomNet *)net didReceiveNReportResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dicomEvent:(uint16_t)dicomEvent dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)dicomNet:(LTDicomNet *)net didReceiveNGetRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance attributes:(unsigned int *)attributes attributesCount:(NSUInteger)count;
- (void)dicomNet:(LTDicomNet *)net didReceiveNGetResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)dicomNet:(LTDicomNet *)net didReceiveNSetRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)dicomNet:(LTDicomNet *)net didReceiveNSetResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)dicomNet:(LTDicomNet *)net didReceiveNActionRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance action:(uint16_t)action dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)dicomNet:(LTDicomNet *)net didReceiveNActionResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status action:(uint16_t)action dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)dicomNet:(LTDicomNet *)net didReceiveNCreateRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance dataSet:(null_unspecified LTDicomDataSet *)dataSet;
- (void)dicomNet:(LTDicomNet *)net didReceiveNCreateResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status dataSet:(null_unspecified LTDicomDataSet *)dataSet;

- (void)dicomNet:(LTDicomNet *)net didReceiveNDeleteRequest:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance;
- (void)dicomNet:(LTDicomNet *)net didReceiveNDeleteResponse:(uint8_t)presentationID messageID:(uint16_t)messageID affectedClass:(NSString *)affectedClass instance:(NSString *)instance status:(LTDicomCommandStatusType)status;

- (void)dicomNet:(LTDicomNet *)net didReceiveUnknown:(uint8_t)presentationID commandSet:(null_unspecified LTDicomDataSet *)cs dataSet:(nullable LTDicomDataSet *)ds;

@end



@interface LTDicomNet (Delegate)

- (instancetype)initWithDelegate:(null_unspecified id<LTDicomNetDelegate>)delegate;
- (instancetype)initWithDelegate:(null_unspecified id<LTDicomNetDelegate>)delegate path:(nullable NSString *)path securityMode:(LTDicomNetSecurityMode)mode reserved:(BOOL)reserved error:(NSError **)error;

@end

NS_ASSUME_NONNULL_END
