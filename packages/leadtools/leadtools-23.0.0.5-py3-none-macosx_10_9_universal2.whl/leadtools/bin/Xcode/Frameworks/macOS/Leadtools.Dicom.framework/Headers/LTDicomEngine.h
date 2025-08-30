// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomEngine.h
//  Leadtools.Dicom
//

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomEngine : NSObject // STATIC CLASS

+ (void)startup;
+ (void)shutdown;

- (instancetype)init __unavailable;

@end
