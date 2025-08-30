// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTAAMVADataElementInfo.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTGlobalEnums.h>

NS_ASSUME_NONNULL_BEGIN

LT_CLASS_AVAILABLE(10_10, 8_0, 20_0)
@interface LTAAMVADataElementInfo : NSObject <NSCopying, NSSecureCoding>

@property (nonatomic, copy)           NSString *elementID;
@property (nonatomic, copy, nullable) NSString *friendlyName;
@property (nonatomic, copy, nullable) NSString *definition;

@property (nonatomic, assign)         NSInteger valueMaxLength;
@property (nonatomic, assign)         NSInteger validCharacters;
@property (nonatomic, assign)         NSInteger validSubfileTypes;

@property (nonatomic, assign)         LTAAMVALengthType lengthType;

+ (nullable NSDictionary<NSString *, LTAAMVADataElementInfo *> *)retrieveAllInfoForVersion:(LTAAMVAVersion)version;

@end

NS_ASSUME_NONNULL_END
