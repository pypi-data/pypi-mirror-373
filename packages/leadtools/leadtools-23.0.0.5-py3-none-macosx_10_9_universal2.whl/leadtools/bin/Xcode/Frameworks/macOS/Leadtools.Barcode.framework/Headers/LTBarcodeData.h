// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTBarcodeData.h
//  Leadtools.Barcode
//

#import <Leadtools/LTPrimitives.h>

#import <Leadtools.Barcode/LTGlobalEnums.h>
#import <Leadtools.Barcode/LTAAMVAID.h>

@class LTAAMVAID;

NS_ASSUME_NONNULL_BEGIN

__deprecated_msg("Deprecated starting LEADTOOLS 19.0. Use 'copyWithZone' instead.")
@protocol LTBarcodeDataDelegate

@optional
- (instancetype)copy;
- (void)copyTo:(NSObject*)data; // 'data' parameter should be a class of type LTBarcodeData

@end



NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTBarcodeData : NSObject <NSCopying>

@property (nonatomic, assign)           LTBarcodeSymbology symbology;

@property (nonatomic, assign)           LeadRect bounds;
@property (nonatomic, assign)           LeadRectD rect;

@property (nonatomic, copy, nullable)   NSString *value;
@property (nonatomic, copy, nullable)   NSString *utf8Value;

@property (nonatomic, assign)           NSInteger rotationAngle;

@property (nonatomic, copy)             id tag;

@property (nonatomic, strong, nullable) NSData *data;
@property (nonatomic, strong, nullable) NSData *utf8Data;

@property (nonatomic, assign)           NSInteger barWidthReduction;


- (instancetype)initWithSymbology:(LTBarcodeSymbology)symbology data:(nullable NSData *)data NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithSymbology:(LTBarcodeSymbology)symbology value:(nullable NSString *)value;

+ (nullable LTBarcodeData *)createDefaultBarcodeData:(LTBarcodeSymbology)symbology;
+ (Class)barcodeDataTypeForSymbology:(LTBarcodeSymbology)symbology;

+ (nullable NSString *)parseECIData:(NSData *)data error:(NSError **)error NS_SWIFT_NAME(parseECIData(_:));
+ (nullable LTAAMVAID *)parseAAMVAData:(NSData *)data strictMode:(BOOL)strictMode error:(NSError **)error LT_AVAILABLE(10_10, 8_0, 20_0) NS_SWIFT_NAME(parseAAMVAData(_:strictMode:));

- (void)updateRect;
- (void)updateValue;

@end



@interface LTBarcodeData (Deprecated)

+ (Class)getBarcodeDataType:(LTBarcodeSymbology)symbology LT_DEPRECATED_USENEW(19_0, "barcodeDataTypeForSymbology:");

- (nullable NSData *)getData LT_DEPRECATED_USENEW(19_0, "data");

@end

NS_ASSUME_NONNULL_END
