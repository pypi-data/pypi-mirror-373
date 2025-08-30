// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTAAMVAID.h
//  Leadtools.Barcode
//

#import <Leadtools.Barcode/LTGlobalEnums.h>
#import <Leadtools.Barcode/LTAAMVASubfile.h>
#import <Leadtools.Barcode/LTAAMVANameResult.h>

NS_ASSUME_NONNULL_BEGIN

LT_CLASS_AVAILABLE(10_10, 8_0, 20_0)
@interface LTAAMVAID : NSObject <NSCopying>

@property (nonatomic, copy, readonly, nullable)   LTAAMVANameResult *firstName;
@property (nonatomic, copy, readonly, nullable)   LTAAMVANameResult *middleName;
@property (nonatomic, copy, readonly, nullable)   LTAAMVANameResult *lastName;

@property (nonatomic, copy, readonly, nullable)   NSString *issuerIdentificationNumber;
@property (nonatomic, copy, readonly, nullable)   NSString *jurisdictionVersion;

@property (nonatomic, copy, readonly, nullable)   NSString *addressStreet1;
@property (nonatomic, copy, readonly, nullable)   NSString *addressStreet2;
@property (nonatomic, copy, readonly, nullable)   NSString *addressCity;
@property (nonatomic, copy, readonly, nullable)   NSString *addressStateAbbreviation;
@property (nonatomic, copy, readonly, nullable)   NSString *addressPostalCode;

@property (nonatomic, copy, readonly, nullable)   NSString *idNumber;
@property (nonatomic, copy, readonly, nullable)   NSString *dateOfBirth;
@property (nonatomic, copy, readonly, nullable)   NSString *expirationDate;
@property (nonatomic, copy, readonly, nullable)   NSString *issueDate;

@property (nonatomic, assign, readonly)           LTAAMVAJurisdiction jurisdiction;
@property (nonatomic, assign, readonly)           LTAAMVAVersion version;
@property (nonatomic, assign, readonly)           LTAAMVARegion addressRegion;
@property (nonatomic, assign, readonly)           LTAAMVAEyeColor eyeColor;
@property (nonatomic, assign, readonly)           LTAAMVAHairColor hairColor;
@property (nonatomic, assign, readonly)           LTAAMVASex sex;

@property (nonatomic, assign, readonly)           BOOL over18Available;
@property (nonatomic, assign, readonly)           BOOL over18;
@property (nonatomic, assign, readonly)           BOOL over19Available;
@property (nonatomic, assign, readonly)           BOOL over19;
@property (nonatomic, assign, readonly)           BOOL over21Available;
@property (nonatomic, assign, readonly)           BOOL over21;

@property (nonatomic, assign, readonly)           BOOL expirationAvailable;
@property (nonatomic, assign, readonly)           BOOL expired;

@property (nonatomic, assign, readonly)           NSInteger numberOfEntries;

@property (nonatomic, strong, readonly, nullable) NSArray<LTAAMVASubfile *> *subfiles;

@end

NS_ASSUME_NONNULL_END
