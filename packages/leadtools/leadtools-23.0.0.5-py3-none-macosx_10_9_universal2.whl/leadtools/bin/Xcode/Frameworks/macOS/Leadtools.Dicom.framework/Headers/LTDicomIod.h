// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomIod.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomTag.h>
#import <Leadtools.Dicom/LTDicomIodEnums.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomIod : NSObject

@property (nonatomic, assign, readonly)         LTDicomClassType classCode;
@property (nonatomic, assign, readonly)         LTDicomModuleType moduleCode;
@property (nonatomic, assign, readonly)         LTDicomIodType type;
@property (nonatomic, assign, readonly)         LTDicomIodUsageType usage;

@property (nonatomic, assign, readonly)         LTDicomTagCode tagCode;

@property (nonatomic, copy, readonly, nullable) NSString *name;

- (instancetype)init __unavailable;

@end

NS_ASSUME_NONNULL_END
