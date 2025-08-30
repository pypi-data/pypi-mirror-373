// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTBarcodeOptions.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTGlobalEnums.h>

NS_ASSUME_NONNULL_BEGIN

@protocol LTBarcodeOptionsDelegate

@required
@property (nonatomic, strong, readonly) NSArray<NSNumber *> *supportedSymbologies;

@optional
- (instancetype)copy LT_DEPRECATED_USENEW(19_0, "copyWithZone:");
- (void)copyTo:(NSObject*)options LT_DEPRECATED_USENEW(19_0, "copyWithZone:"); // 'options' parameter should be a class of type LTBarcodeOptions

@end


NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTBarcodeOptions : NSObject <LTBarcodeOptionsDelegate, NSCopying>

- (BOOL)isSupportedSymbology:(LTBarcodeSymbology)symbology;

@end

NS_ASSUME_NONNULL_END
