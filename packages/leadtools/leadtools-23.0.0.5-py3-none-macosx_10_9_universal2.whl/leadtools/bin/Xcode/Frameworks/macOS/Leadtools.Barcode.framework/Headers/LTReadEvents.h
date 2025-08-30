// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTReadEvents.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTBarcodeReadOptions.h>
#import <Leadtools.Barcode/LTBarcodeData.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, LTBarcodeReadSymbologyOperation) {
   LTBarcodeReadSymbologyOperationPreRead,
   LTBarcodeReadSymbologyOperationPostRead
};

typedef NS_ENUM(NSInteger, LTBarcodeReadSymbologyStatus) {
   LTBarcodeReadSymbologyStatusContinue,
   LTBarcodeReadSymbologyStatusSkip,
   LTBarcodeReadSymbologyStatusAbort
};

/****************************************************************/
/* LTBarcodeReadSymbologyEventArgs Interface                    */
/****************************************************************/

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTBarcodeReadSymbologyEventArgs : NSObject

@property (nonatomic, assign, readonly)             LTBarcodeReadSymbologyOperation operation;

@property (nonatomic, assign, readonly, nullable)   LTBarcodeSymbology *symbologies;

@property (nonatomic, assign, readonly)             NSUInteger symbologiesCount;

@property (nonatomic, assign)                       LTBarcodeReadSymbologyStatus status;

@property (nonatomic, strong, readonly, nullable)   LTBarcodeReadOptions *options;

@property (nonatomic, strong, readonly, nullable)   LTBarcodeData *data;

@property (nonatomic, strong, readonly, nullable)   NSError *error;

@end

@protocol LTReadSymbologyDelegate<NSObject>

@required

- (void)readSymbology:(id)sender e:(LTBarcodeReadSymbologyEventArgs*)e;

@end


/****************************************************************/
/* LTBarcodeReaderBarcodeFoundEventArgs Interface               */
/****************************************************************/

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTBarcodeReaderBarcodeFoundEventArgs : NSObject

@property (nonatomic, strong, readonly, nullable)   LTBarcodeData *data;

@property (nonatomic, assign)                       BOOL abort;

@property (nonatomic, strong, readonly, nullable)   NSError *error;

@end

@protocol LTBarcodeReaderBarcodeFoundDelegate<NSObject>

@required

- (void)barcodeFound:(id)sender e:(LTBarcodeReaderBarcodeFoundEventArgs*)e;

@end


/****************************************************************/
/* LTBarcodeReaderProgressEventArgs Interface                   */
/****************************************************************/

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTBarcodeReaderProgressEventArgs : NSObject

@property (nonatomic, assign)                       NSInteger percent;

@property (nonatomic, assign)                       BOOL cancel;

@property (nonatomic, strong, readonly, nullable)   NSError *error;

@end

@protocol LTBarcodeReaderProgressDelegate<NSObject>

@required

- (void)barcodeReaderProgress:(id)sender e:(LTBarcodeReaderProgressEventArgs*)e;

@end

NS_ASSUME_NONNULL_END
