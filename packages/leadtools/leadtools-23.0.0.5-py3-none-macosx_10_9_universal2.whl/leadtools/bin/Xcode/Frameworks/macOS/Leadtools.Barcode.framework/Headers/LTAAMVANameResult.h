// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTAAMVANameResult.h
//  Leadtools.Barcode
//

#import <Leadtools/LTLeadtools.h>

NS_ASSUME_NONNULL_BEGIN

LT_CLASS_AVAILABLE(10_10, 8_0, 20_0)
@interface LTAAMVANameResult : NSObject <NSCopying, NSSecureCoding>

@property (nonatomic, copy)   NSString *value;
@property (nonatomic, assign) BOOL inferredFromFullName;

@end

NS_ASSUME_NONNULL_END
