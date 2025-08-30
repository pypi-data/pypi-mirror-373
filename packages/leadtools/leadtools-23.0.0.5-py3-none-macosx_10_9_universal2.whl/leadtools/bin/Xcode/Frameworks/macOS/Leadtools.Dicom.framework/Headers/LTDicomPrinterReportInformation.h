// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomPrinterReportInformation.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomPrinterReportInformation : NSObject

@property (nonatomic, copy, nullable) NSString *printerStatusInfo;
@property (nonatomic, copy, nullable) NSString *filmDestination;
@property (nonatomic, copy, nullable) NSString *printerName;

@end

NS_ASSUME_NONNULL_END
