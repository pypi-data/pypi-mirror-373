// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomPresentationStateInformation.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomDateValue.h>
#import <Leadtools.Dicom/LTDicomTimeValue.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomPresentationStateInformation : NSObject

@property (nonatomic, assign)         NSInteger instanceNumber;

@property (nonatomic, copy, nullable) NSString *presentationLabel;
@property (nonatomic, copy, nullable) NSString *presentationDescription;
@property (nonatomic, copy, nullable) NSString *presentationCreator;

@property (nonatomic, strong)         LTDicomDateValue *presentationCreationDate;
@property (nonatomic, strong)         LTDicomTimeValue *presentationCreationTime;

@end

NS_ASSUME_NONNULL_END
