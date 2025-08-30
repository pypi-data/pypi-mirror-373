// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTBarcodeReader.h
//  Leadtools.Barcode
//

#import <Leadtools/LTRasterImage.h>
#import <Leadtools/LTPrimitives.h>

#import <Leadtools.Barcode/LTBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTBarcodeData.h>
#import <Leadtools.Barcode/LTReadEvents.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, LTBarcodeReaderErrorMode) {
   LTBarcodeReaderErrorModeDefault,
   LTBarcodeReaderErrorModeIgnoreAll
};

typedef NS_ENUM(NSInteger, LTBarcodeImageType) {
   LTBarcodeImageTypeScannedDocument,
   LTBarcodeImageTypePicture,
   LTBarcodeImageTypeUnknown
};

@class LTBarcodeEngine;
NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTBarcodeReader : NSObject

@property (nonatomic, weak, nullable)   id<LTReadSymbologyDelegate> delegate;
@property (nonatomic, weak, nullable)   id<LTBarcodeReaderBarcodeFoundDelegate> barcodeFoundDelegate;
@property (nonatomic, weak, nullable)   id<LTBarcodeReaderProgressDelegate> barcodeProgressDelegate;

@property (nonatomic, strong, readonly) LTBarcodeEngine *engine;

@property (nonatomic, assign)           LTBarcodeImageType imageType;

@property (nonatomic, assign)           NSInteger maximumImageWidth;
@property (nonatomic, assign)           NSInteger maximumImageHeight;

@property (nonatomic, assign)           LTBarcodeReaderErrorMode errorMode;

@property (nonatomic, strong, readonly) NSArray<__kindof LTBarcodeReadOptions *> *allDefaultOptions;

@property (nonatomic, strong, readonly) NSArray<NSNumber *> *availableSymbologies;

- (instancetype)init __unavailable;

+ (Class)barcodeReadOptionsTypeForSymbology:(LTBarcodeSymbology)symbology;

- (LTBarcodeReadOptions *)defaultOptionsForSymbology:(LTBarcodeSymbology)symbology;

- (nullable LTBarcodeData *)readBarcode:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds symbology:(LTBarcodeSymbology)symbology error:(NSError **)error NS_SWIFT_NOTHROW;
- (nullable LTBarcodeData *)readBarcode:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds symbology:(LTBarcodeSymbology)symbology options:(nullable LTBarcodeReadOptions *)options error:(NSError **)error NS_SWIFT_NOTHROW;

- (nullable LTBarcodeData *)readBarcode:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds symbologies:(nullable NSArray<NSNumber *> *)symbologies error:(NSError **)error NS_SWIFT_NOTHROW;
- (nullable LTBarcodeData *)readBarcode:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds symbologies:(nullable NSArray<NSNumber *> *)symbologies options:(nullable NSArray<LTBarcodeReadOptions *> *)options error:(NSError **)error NS_SWIFT_NOTHROW;

- (nullable NSArray<LTBarcodeData *> *)readBarcodes:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds maximumBarcodes:(NSUInteger)maximumBarcodes symbologies:(nullable NSArray<NSNumber *> *)symbologies error:(NSError **)error NS_SWIFT_NOTHROW;
- (nullable NSArray<LTBarcodeData *> *)readBarcodes:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds maximumBarcodes:(NSUInteger)maximumBarcodes symbologies:(nullable NSArray<NSNumber *> *)symbologies options:(nullable NSArray<LTBarcodeReadOptions *> *)options error:(NSError **)error NS_SWIFT_NOTHROW;

@end



@interface LTBarcodeReader (Deprecated)

+ (Class)getBarcodeReadOptionsType:(LTBarcodeSymbology)symbology LT_DEPRECATED_USENEW(19_0, "barcodeReadOptionsTypeForSymbology:");

- (void)getAvailableSymbologies:(LTBarcodeSymbology * _Nullable * _Nonnull)availableSymbologies availableSymbologiesCount:(NSUInteger *)availableSymbologiesCount LT_DEPRECATED_USENEW(19_0, "availableSymbologies");
- (void)freeAvailableSymbologies:(LTBarcodeSymbology *)availableSymbologies LT_DEPRECATED(19_0);

- (NSArray *)getAllDefaultOptions LT_DEPRECATED_USENEW(19_0, "allDefaultOptions");
- (LTBarcodeReadOptions*)getDefaultOptions:(LTBarcodeSymbology)symbology LT_DEPRECATED_USENEW(19_0, "defaultOptionsForSymbology:");

- (nullable LTBarcodeData *)readBarcode:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds symbologies:(nullable LTBarcodeSymbology *)symbologies symbologiesCount:(NSUInteger)symbologiesCount error:(NSError **)error LT_DEPRECATED_USENEW(19_0, "readBarcode:searchBounds:symbologies:error:");
- (nullable LTBarcodeData *)readBarcode:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds symbologies:(nullable LTBarcodeSymbology *)symbologies symbologiesCount:(NSUInteger)symbologiesCount options:(nullable NSArray<LTBarcodeReadOptions *> *)options error:(NSError **)error LT_DEPRECATED_USENEW(19_0, "readBarcode:searchBounds:symbologies:options:error:");
- (nullable NSArray<LTBarcodeData *> *)readBarcodes:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds maximumBarcodes:(NSInteger)maximumBarcodes symbologies:(nullable LTBarcodeSymbology *)symbologies symbologiesCount:(NSUInteger)symbologiesCount error:(NSError **)error LT_DEPRECATED_USENEW(19_0, "readBarcodes:searchBounds:maximumBarcodes:symbologies:error:");
- (nullable NSArray<LTBarcodeData *> *)readBarcodes:(LTRasterImage *)image searchBounds:(LeadRect)searchBounds maximumBarcodes:(NSInteger)maximumBarcodes symbologies:(nullable LTBarcodeSymbology *)symbologies symbologiesCount:(NSUInteger)symbologiesCount options:(nullable NSArray<LTBarcodeReadOptions *> *)options error:(NSError **)error LT_DEPRECATED_USENEW(19_0, "readBarcodes:searchBounds:maximumBarcodes:symbologies:options:error:");

@end

NS_ASSUME_NONNULL_END
