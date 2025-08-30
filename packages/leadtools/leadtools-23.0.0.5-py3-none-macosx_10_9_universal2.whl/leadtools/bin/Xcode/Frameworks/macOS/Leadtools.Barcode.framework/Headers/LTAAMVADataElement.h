// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTAAMVADataElement.h
//  Leadtools.Barcode
//

#import <Leadtools/LTLeadtools.h>

NS_ASSUME_NONNULL_BEGIN

LT_CLASS_AVAILABLE(10_10, 8_0, 20_0)
@interface LTAAMVADataElement : NSObject <NSCopying, NSSecureCoding>

@property (nonatomic, copy) NSString *elementID;
@property (nonatomic, copy) NSString *value;

@end

NS_ASSUME_NONNULL_END
