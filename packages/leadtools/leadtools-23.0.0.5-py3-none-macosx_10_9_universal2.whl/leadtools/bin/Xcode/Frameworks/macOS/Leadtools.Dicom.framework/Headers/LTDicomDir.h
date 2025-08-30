// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomDir.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomDataSet.h>
#import <Leadtools.Dicom/LTDicomError.h>

typedef NS_ENUM(NSInteger, LTDicomDirInsertFileStatus) {
    LTDicomDirInsertFileStatusPreAdd  = 300,
    LTDicomDirInsertFileStatusSuccess = 0,
    LTDicomDirInsertFileStatusFailure = 350
};

typedef NS_ENUM(NSInteger, LTDicomDirInsertFileCommand) {
    LTDicomDirInsertFileCommandContinue = 0,
    LTDicomDirInsertFileCommandSkip     = 8,
    LTDicomDirInsertFileCommandStop     = 234
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomDirOptions : NSObject <NSCopying, NSCoding>

@property (nonatomic, assign) BOOL includeSubfolders;
@property (nonatomic, assign) BOOL rejectInvalidFileId;
@property (nonatomic, assign) BOOL insertIconImageSequence;

@property (class, nonatomic, strong, readonly) LTDicomDirOptions *empty;

@end



NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomDir : NSObject

@property (nonatomic, strong, readonly, nullable) LTDicomDataSet *dataSet;
@property (nonatomic, strong, nullable)           LTDicomDirOptions *options;

@property (nonatomic, copy, readonly, nullable)   NSString *destinationFolder;

- (instancetype)initWithDestinationFolder:(nullable NSString *)destinationFolder path:(nullable NSString *)path NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithDestinationFolder:(nullable NSString *)destinationFolder;

- (BOOL)load:(NSString *)path flags:(LTDicomDataSetLoadFlags)flags error:(NSError **)error;
- (BOOL)save:(NSError **)error;
- (void)reset:(NSString *)destinationFolder;

- (BOOL)insertFile:(nullable NSString *)fileName error:(NSError **)error;
- (BOOL)insertDataSet:(LTDicomDataSet *)dataSet fileName:(nullable NSString *)fileName error:(NSError **)error;

- (void)setFileSetId:(NSString *)Id;
- (BOOL)setDescriptorFile:(NSString *)fileName characterSet:(NSString *)characterSet error:(NSError **)error;

- (void)resetOptions;

- (LTDicomDirInsertFileCommand)onInsertFile:(NSString *)fileName dataSet:(LTDicomDataSet *)dataSet status:(LTDicomDirInsertFileStatus)status errorCode:(LTDicomErrorCode)code;



+ (NSArray<LTDicomDataSet *> *)sort:(NSArray<LTDicomDataSet *> *)dataSets;
+ (void)sortInPlace:(NSMutableArray<LTDicomDataSet *> *)dataSets;

@end

NS_ASSUME_NONNULL_END
