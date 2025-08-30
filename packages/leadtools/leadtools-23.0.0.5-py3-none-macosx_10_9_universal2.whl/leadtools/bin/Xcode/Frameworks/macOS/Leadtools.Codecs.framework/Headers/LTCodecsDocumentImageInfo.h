// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTCodecsDocumentImageInfo.h
//  Leadtools.Codecs
//

#import <Leadtools.Codecs/LTCodecsDefines.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTCodecsDocumentImageInfo : NSObject

@property (nonatomic, assign, readonly) BOOL isDocumentFile;

@property (nonatomic, assign, readonly) double pageWidth;
@property (nonatomic, assign, readonly) double pageHeight;

@property (nonatomic, assign, readonly) LTCodecsRasterizeDocumentUnit unit;

- (instancetype)init __unavailable;

@end

NS_ASSUME_NONNULL_END
