// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomUid.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomUidType.h>

typedef NS_ENUM(NSInteger, LTDicomUIDCategory) {
	LTDicomUIDCategoryOther,
	LTDicomUIDCategoryTransfer1,
	LTDicomUIDCategoryTransfer2,
	LTDicomUIDCategoryClass,
	LTDicomUIDCategoryMetaClass,
	LTDicomUIDCategoryInstance,
	LTDicomUIDCategoryApplication,
	LTDicomUIDCategoryFrameOfReference,
	LTDicomUIDCategoryLdapOid,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomUid : NSObject

@property (nonatomic, assign, readonly)         LTDicomUIDCategory type;

@property (nonatomic, copy, readonly, nullable) NSString *code;
@property (nonatomic, copy, readonly, nullable) NSString *name;

- (instancetype)init __unavailable;

@end

NS_ASSUME_NONNULL_END
