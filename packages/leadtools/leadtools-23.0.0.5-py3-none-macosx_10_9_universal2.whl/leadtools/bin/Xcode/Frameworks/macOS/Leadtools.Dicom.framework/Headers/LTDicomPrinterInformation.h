// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomPrinterInformation.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomPrinterInformation : NSObject

@property (nonatomic, copy, nullable) NSString *timeOfLastCalibration;
@property (nonatomic, copy, nullable) NSString *dateOfLastCalibration;
@property (nonatomic, copy, nullable) NSString *softwareVersions;
@property (nonatomic, copy, nullable) NSString *deviceSerialNumber;
@property (nonatomic, copy, nullable) NSString *manufacturerModelName;
@property (nonatomic, copy, nullable) NSString *manufacturer;
@property (nonatomic, copy, nullable) NSString *printerName;
@property (nonatomic, copy, nullable) NSString *printerStatusInfo;
@property (nonatomic, copy, nullable) NSString *printerStatus;

@end

NS_ASSUME_NONNULL_END
