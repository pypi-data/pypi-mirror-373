// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomCodeSequenceItem.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomDateTimeValue.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomCodeSequenceItem : NSObject

@property (nonatomic, strong, nullable) NSString *codeValue;
@property (nonatomic, strong, nullable) NSString *codingSchemeDesignator;
@property (nonatomic, strong, nullable) NSString *codingSchemeVersion;
@property (nonatomic, strong, nullable) NSString *codeMeaning;
@property (nonatomic, strong, nullable) NSString *contextIdentifier;
@property (nonatomic, strong, nullable) NSString *mappingResource;
@property (nonatomic, strong, nullable) NSString *contextGroupExtensionCreatorUID;

@property (nonatomic, strong, nullable) LTDicomDateTimeValue *contextGroupVersion;
@property (nonatomic, strong, nullable) LTDicomDateTimeValue *contextGroupLocalVersion;

@end

NS_ASSUME_NONNULL_END
