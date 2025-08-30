// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomAssociate.h
//  Leadtools.Dicom
//

typedef NS_ENUM(NSInteger, LTDicomAssociateAcceptResultType) {
	LTDicomAssociateAcceptResultTypeSuccess        = 0,
	LTDicomAssociateAcceptResultTypeUserReject     = 1,
	LTDicomAssociateAcceptResultTypeProviderReject = 2,
	LTDicomAssociateAcceptResultTypeAbstractSyntax = 3,
	LTDicomAssociateAcceptResultTypeTransferSyntax = 4,
};

typedef NS_ENUM(NSInteger, LTDicomRoleSupport) {
	LTDicomRoleSupportSupported   = 1,
	LTDicomRoleSupportUnsupported = 0,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomAssociate : NSObject

@property (nonatomic, assign)           BOOL isRequest;
@property (nonatomic, assign, readonly) BOOL isAsynchronous;

@property (nonatomic, assign)           NSUInteger version;
@property (nonatomic, assign, readonly) NSUInteger presentationContextCount;
@property (nonatomic, assign, readonly) NSUInteger invokedOperationsCount;
@property (nonatomic, assign, readonly) NSUInteger performedOperationsCount;
@property (nonatomic, assign, readonly) NSUInteger userInformationCount;

@property (nonatomic, assign)           NSInteger maxLength;

@property (nonatomic, strong)           NSString *called;
@property (nonatomic, strong)           NSString *calling;
@property (nonatomic, strong)           NSString *applicationContextName;
@property (nonatomic, strong, nullable) NSString *implementationVersionName;
@property (nonatomic, strong, nullable) NSString *implementationClass;

- (nullable instancetype)initWithRequest:(BOOL)request error:(NSError **)error NS_DESIGNATED_INITIALIZER;
- (instancetype)init __unavailable;

- (void)reset:(BOOL)request NS_SWIFT_NAME(reset(request:));
- (void)defaultAssociate;

- (uint8_t)presentationContextIDAtIndex:(NSUInteger)index NS_SWIFT_NAME(presentationContextID(at:));
- (BOOL)setPresentationContextID:(uint8_t)ID atIndex:(NSUInteger)index error:(NSError **)error NS_SWIFT_NAME(setPresentationContextID(_:at:));
- (BOOL)addPresentationContextID:(uint8_t)ID abstractSyntax:(NSString *)abstractSyntax result:(LTDicomAssociateAcceptResultType)result error:(NSError **)error NS_SWIFT_NAME(addPresentationContextID(_:abstractSyntax:result:));
- (void)deletePresentationContextWithID:(uint8_t)ID NS_SWIFT_NAME(deletePresentationContextID(_:));

- (LTDicomAssociateAcceptResultType)resultForID:(uint8_t)ID;
- (BOOL)setResult:(LTDicomAssociateAcceptResultType)result forID:(uint8_t)ID error:(NSError **)error;

- (nullable NSString *)abstractSyntaxForID:(uint8_t)ID;
- (BOOL)setAbstractSyntax:(NSString *)uid forID:(uint8_t)ID error:(NSError **)error;
- (uint8_t)findAbstractSyntax:(NSString *)uid;
- (uint8_t)findNextAbstractSyntax:(NSString *)uid forID:(uint8_t)ID;
- (NSUInteger)abstractSyntaxCount:(NSString *)uid;
- (nullable NSArray<NSNumber *> *)findAbstractSyntaxes:(NSString *)uid;

- (NSUInteger)transferSyntaxCountForID:(uint8_t)ID;
- (nullable NSString *)transferSyntaxForID:(uint8_t)ID atIndex:(NSUInteger)index;
- (BOOL)setTransferSyntax:(NSString *)uid forID:(uint8_t)ID atIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)addTransferSyntax:(NSString *)uid forID:(uint8_t)ID error:(NSError **)error;
- (void)deleteTransferSyntaxForID:(uint8_t)ID atIndex:(NSUInteger)index;

- (BOOL)isRoleSelect:(uint8_t)ID NS_SWIFT_NAME(isRoleSelect(id:));
- (LTDicomRoleSupport)userRole:(uint8_t)ID NS_SWIFT_NAME(userRole(id:));
- (LTDicomRoleSupport)providerRole:(uint8_t)ID NS_SWIFT_NAME(providerRole(id:));
- (BOOL)setRoleSelectForID:(uint8_t)ID enabled:(BOOL)enabled user:(LTDicomRoleSupport)user provider:(LTDicomRoleSupport)provider error:(NSError **)error;

- (NSUInteger)lengthOfExtendedDataForID:(uint8_t)ID;
- (nullable NSData *)extendedDataForID:(uint8_t)ID;
- (BOOL)setExtendedData:(nullable NSData *)data forID:(uint8_t)ID error:(NSError **)error;

- (BOOL)setAsynchronousOperations:(BOOL)enabled invokedCount:(NSUInteger)invokedCount performedCount:(NSUInteger)performedCount error:(NSError **)error NS_SWIFT_NAME(setAsynchronousOperations(enabled:invokedCount:performedCount:));

- (uint8_t)userInformationTypeAtIndex:(NSUInteger)index;
- (NSUInteger)lengthOfUserInformationAtIndex:(NSUInteger)index;
- (nullable NSData *)userInformationDataAtIndex:(NSUInteger)index;
- (BOOL)setUserInformationData:(nullable NSData *)data type:(uint8_t)type atIndex:(NSUInteger)index error:(NSError **)error;
- (BOOL)addUserInformationData:(nullable NSData *)data type:(uint8_t)type error:(NSError **)error;
- (void)deleteUserInformationAtIndex:(NSUInteger)index;

@end

NS_ASSUME_NONNULL_END
