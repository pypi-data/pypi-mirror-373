// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomModule.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomIod.h>
#import <Leadtools.Dicom/LTDicomElement.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomModule : NSObject

@property (nonatomic, assign, readonly)           LTDicomModuleType type;
@property (nonatomic, strong, readonly, nullable) NSArray<LTDicomElement *> *elements;

- (instancetype)init __unavailable;

@end

NS_ASSUME_NONNULL_END
