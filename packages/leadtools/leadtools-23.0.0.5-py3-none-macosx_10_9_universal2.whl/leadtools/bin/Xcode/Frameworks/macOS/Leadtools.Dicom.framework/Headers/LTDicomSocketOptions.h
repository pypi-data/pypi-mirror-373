// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomSocketOptions.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomSocketOptions : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign) BOOL noDelay;

@property (nonatomic, assign) NSInteger sendBufferSize;
@property (nonatomic, assign) NSInteger receiveBufferSize;

@end

NS_ASSUME_NONNULL_END
