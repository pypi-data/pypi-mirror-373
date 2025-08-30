// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDicomPaletteColorLutAttributes.h
//  Leadtools.Dicom
//

typedef NS_ENUM(NSInteger, LTDicomPaletteColorLutType) {
	LTDicomPaletteColorLutTypeRed,
	LTDicomPaletteColorLutTypeGreen,
	LTDicomPaletteColorLutTypeBlue,
};

NS_ASSUME_NONNULL_BEGIN

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDicomPaletteColorLutAttributes : NSObject

@property (nonatomic, assign)         BOOL isSegmented;

@property (nonatomic, assign)         NSInteger redNumberOfEntries;
@property (nonatomic, assign)         NSInteger redFirstStoredPixelValueMapped;
@property (nonatomic, assign)         NSInteger redEntryBits;

@property (nonatomic, assign)         NSInteger greenNumberOfEntries;
@property (nonatomic, assign)         NSInteger greenFirstStoredPixelValueMapped;
@property (nonatomic, assign)         NSInteger greenEntryBits;

@property (nonatomic, assign)         NSInteger blueNumberOfEntries;
@property (nonatomic, assign)         NSInteger blueFirstStoredPixelValueMapped;
@property (nonatomic, assign)         NSInteger blueEntryBits;

@property (nonatomic, copy, nullable) NSString *UID;

@end

NS_ASSUME_NONNULL_END
