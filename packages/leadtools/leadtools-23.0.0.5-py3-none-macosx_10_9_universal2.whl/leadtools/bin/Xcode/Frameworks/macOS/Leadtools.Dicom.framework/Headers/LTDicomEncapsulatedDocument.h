// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomEncapsulatedDocument.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomEncapsulatedDocumentType.h>
#import <Leadtools.Dicom/LTDicomDateValue.h>
#import <Leadtools.Dicom/LTDicomTimeValue.h>
#import <Leadtools.Dicom/LTDicomDateTimeValue.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomEncapsulatedDocument : NSObject

@property (nonatomic, assign)         LTDicomEncapsulatedDocumentType type;

@property (nonatomic, assign)         NSInteger instanceNumber;

@property (nonatomic, copy, nullable) NSString *burnedInAnnotation;
@property (nonatomic, copy, nullable) NSString *documentTitle;
@property (nonatomic, copy, nullable) NSString *verificationFlag;
@property (nonatomic, copy, nullable) NSString *HL7InstanceIdentifier;
@property (nonatomic, copy, nullable) NSString *mimeTypeOfEncapsulatedDocument;

@property (nonatomic, strong)         LTDicomDateValue *contentDate;
@property (nonatomic, strong)         LTDicomTimeValue *contentTime;
@property (nonatomic, strong)         LTDicomDateTimeValue *acquisitionDateTime;

@property (nonatomic, strong)         NSArray<NSString *> *listOfMimeTypes;

@end

NS_ASSUME_NONNULL_END
