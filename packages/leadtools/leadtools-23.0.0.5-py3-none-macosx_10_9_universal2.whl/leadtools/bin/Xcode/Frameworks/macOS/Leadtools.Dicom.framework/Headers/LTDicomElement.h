// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomElement.h
//  Leadtools.Dicom
//

#include <Leadtools.Dicom/LTDicomTag.h>
#include <Leadtools.Dicom/LTDicomVR.h>

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomElement : NSObject

@property (nonatomic, assign, readonly) LTDicomTagCode tag;
@property (nonatomic, assign, readonly) NSUInteger length;
@property (nonatomic, assign, readonly) LTDicomVRType VR;

@property (nonatomic, assign, readonly) NSUInteger offset;
@property (nonatomic, assign, readonly) NSUInteger valueOffset;
@property (nonatomic, assign, readonly) NSUInteger valueLength;

- (instancetype)init __unavailable;

@end
