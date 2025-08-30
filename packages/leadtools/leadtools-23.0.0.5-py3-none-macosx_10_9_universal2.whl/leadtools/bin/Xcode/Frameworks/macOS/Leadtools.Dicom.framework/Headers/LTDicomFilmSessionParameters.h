// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomFilmSessionParameters.h
//  Leadtools.Dicom
//

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomFilmSessionParameters : NSObject

@property (nonatomic, assign)         NSInteger numberOfCopies;
@property (nonatomic, assign)         NSInteger memoryAllocation;

@property (nonatomic, copy, nullable) NSString *ownerID;
@property (nonatomic, copy, nullable) NSString *printPriority;
@property (nonatomic, copy, nullable) NSString *mediumType;
@property (nonatomic, copy, nullable) NSString *filmDestination;
@property (nonatomic, copy, nullable) NSString *filmSessionLabel;

- (instancetype)init __unavailable;

@end

NS_ASSUME_NONNULL_END
