// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomIodTable.h
//  Leadtools.Dicom
//

#import <Leadtools.Dicom/LTDicomIod.h>

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomIodTable : NSObject

+ (instancetype)sharedInstance;

- (void)defaultTable;
- (void)reset;

- (BOOL)loadXml:(NSString *)file error:(NSError **)error NS_SWIFT_NAME(loadXml(_:));
- (BOOL)loadXmlData:(NSData *)data error:(NSError **)error NS_SWIFT_NAME(loadXml(_:));

- (nullable LTDicomIod *)insert:(nullable LTDicomIod *)neighbor child:(BOOL)child code:(NSUInteger)code name:(NSString *)name type:(LTDicomIodType)type usage:(LTDicomIodUsageType)usage description:(NSString *)desc NS_SWIFT_NAME(insertIod(neighbor:child:code:name:type:usage:description:));
- (nullable LTDicomIod *)insert:(nullable LTDicomIod *)neighbor child:(BOOL)child class:(LTDicomClassType)code name:(NSString *)name type:(LTDicomIodType)type usage:(LTDicomIodUsageType)usage description:(NSString *)desc NS_SWIFT_NAME(insertIod(neighbor:child:class:name:type:usage:description:));
- (nullable LTDicomIod *)insert:(nullable LTDicomIod *)neighbor child:(BOOL)child module:(LTDicomModuleType)code name:(NSString *)name type:(LTDicomIodType)type usage:(LTDicomIodUsageType)usage description:(NSString *)desc NS_SWIFT_NAME(insertIod(neighbor:child:module:name:type:usage:description:));

- (nullable LTDicomIod *)removeIod:(LTDicomIod *)iod;

- (nullable LTDicomIod *)getRoot:(LTDicomIod *)iod;
- (nullable LTDicomIod *)getParent:(LTDicomIod *)iod;

- (nullable LTDicomIod *)first:(nullable LTDicomIod *)iod tree:(BOOL)tree;
- (nullable LTDicomIod *)last:(nullable LTDicomIod *)iod tree:(BOOL)tree;
- (nullable LTDicomIod *)previous:(LTDicomIod *)iod tree:(BOOL)tree;
- (nullable LTDicomIod *)next:(LTDicomIod *)iod tree:(BOOL)tree;

- (BOOL)exists:(LTDicomIod *)iod;

- (nullable LTDicomIod *)find:(nullable LTDicomIod *)iod code:(NSUInteger)code type:(LTDicomIodType)type tree:(BOOL)tree;
- (nullable LTDicomIod *)find:(nullable LTDicomIod *)iod class:(LTDicomClassType)code type:(LTDicomIodType)type tree:(BOOL)tree;
- (nullable LTDicomIod *)find:(nullable LTDicomIod *)iod module:(LTDicomModuleType)code type:(LTDicomIodType)type tree:(BOOL)tree;

- (nullable LTDicomIod *)findClass:(LTDicomClassType)type;
- (nullable LTDicomIod *)findModule:(LTDicomModuleType)type forClass:(LTDicomClassType)classType;
- (nullable LTDicomIod *)findModule:(LTDicomClassType)type byIndex:(NSUInteger)index;

- (BOOL)setName:(NSString *)name forIod:(LTDicomIod *)iod;
- (BOOL)setDescription:(NSString *)desc forIod:(LTDicomIod *)iod;

- (NSUInteger)numberOfModulesForClass:(LTDicomClassType)type;

@end

NS_ASSUME_NONNULL_END
