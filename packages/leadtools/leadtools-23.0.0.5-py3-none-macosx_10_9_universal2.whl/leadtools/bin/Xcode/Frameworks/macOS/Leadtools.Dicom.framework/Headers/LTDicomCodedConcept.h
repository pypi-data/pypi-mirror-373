// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomCodedConcept.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomDateTimeValue.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomCodedConcept : NSObject

@property (nonatomic, copy, readonly, nullable)   NSString *codingSchemeDesignator;
@property (nonatomic, copy, readonly, nullable)   NSString *codingSchemeVersion;
@property (nonatomic, copy, readonly, nullable)   NSString *codeValue;
@property (nonatomic, copy, readonly, nullable)   NSString *codeMeaning;
@property (nonatomic, copy, readonly, nullable)   NSString *contextGroupExtensionCreatorUID;

@property (nonatomic, strong, readonly)           LTDicomDateTimeValue *contextGroupLocalVersion;

- (instancetype)init __unavailable;

@end

NS_ASSUME_NONNULL_END
