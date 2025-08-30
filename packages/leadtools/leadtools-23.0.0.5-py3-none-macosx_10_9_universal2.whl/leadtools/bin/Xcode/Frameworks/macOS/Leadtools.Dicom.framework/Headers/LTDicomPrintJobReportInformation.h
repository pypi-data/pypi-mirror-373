// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomPrintJobReportInformation.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomPrintJobReportInformation : NSObject

@property (nonatomic, copy, nullable) NSString *executionStatusInfo;
@property (nonatomic, copy, nullable) NSString *printJobID;
@property (nonatomic, copy, nullable) NSString *filmSessionLabel;
@property (nonatomic, copy, nullable) NSString *printerName;

@end

NS_ASSUME_NONNULL_END
