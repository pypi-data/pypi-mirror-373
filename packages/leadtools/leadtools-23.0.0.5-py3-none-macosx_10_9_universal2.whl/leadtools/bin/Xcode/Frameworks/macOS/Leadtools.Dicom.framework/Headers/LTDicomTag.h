// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomTag.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomVR.h>

NS_ASSUME_NONNULL_BEGIN

typedef NSUInteger LTDicomTagCode;

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomTag : NSObject

@property (nonatomic, assign, readonly)         LTDicomTagCode code;
@property (nonatomic, assign, readonly)         NSUInteger mask;
@property (nonatomic, assign, readonly)         NSUInteger minVM;
@property (nonatomic, assign, readonly)         NSUInteger maxVM;
@property (nonatomic, assign, readonly)         NSUInteger VMDivider;

@property (nonatomic, assign, readonly)         LTDicomVRType VR;

@property (nonatomic, copy, readonly, nullable) NSString *name;
@property (nonatomic, copy, readonly)           NSString *hexString;

- (instancetype)init __unavailable;

@end

NS_ASSUME_NONNULL_END

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

@interface LTDicomTag (Tags)

#import <Leadtools.Dicom/LTDicomTagConstants.h>

@property (class, nonatomic, assign, readonly) LTDicomTagCode undefined;
@property (class, nonatomic, assign, readonly) LTDicomTagCode referencedGrayscalePresentationStateSequence;
@property (class, nonatomic, assign, readonly) LTDicomTagCode sopAuthorizationDateAndTime;
@property (class, nonatomic, assign, readonly) LTDicomTagCode patientPrimaryLanguageCodeModifierSequence;
@property (class, nonatomic, assign, readonly) LTDicomTagCode lookupTableNumber;

@end
