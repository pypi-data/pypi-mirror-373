// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTAAMVASubfile.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTGlobalEnums.h>
#import <Leadtools.Barcode/LTAAMVADataElement.h>

NS_ASSUME_NONNULL_BEGIN

LT_CLASS_AVAILABLE(10_10, 8_0, 20_0)
@interface LTAAMVASubfile : NSObject <NSCopying, NSSecureCoding>

@property (nonatomic, assign, readonly)           LTAAMVASubfileType subfileType;

@property (nonatomic, copy, readonly)             NSString *subfileTypeCode;

@property (nonatomic, assign, readonly)           NSInteger offset;
@property (nonatomic, assign, readonly)           NSInteger length;

@property (nonatomic, strong, readonly, nullable) NSDictionary<NSString *, LTAAMVADataElement *> *dataElements;

@end

NS_ASSUME_NONNULL_END
