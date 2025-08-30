// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTHolePunchRemoveCommand.h
//  Leadtools.ImageProcessing.Core
//

#import <Leadtools/LTRasterCommand.h>
#import <Leadtools/LTRasterRegion.h>
#import <Leadtools/LTRasterImage.h>
#import <Leadtools/LTPrimitives.h>

#import <Leadtools.ImageProcessing.Core/LTEnums.h>

typedef NS_OPTIONS(NSUInteger, LTHolePunchRemoveCommandFlags) {
    LTHolePunchRemoveCommandFlagsNone = 0x0000,
    LTHolePunchRemoveCommandFlagsUseDpi = 0x00000001,
    LTHolePunchRemoveCommandFlagsSingleRegion = 0x00000002,
    LTHolePunchRemoveCommandFlagsLeadRegion = 0x00000004,
    LTHolePunchRemoveCommandFlagsCallBackRegion = 0x00000008,
    LTHolePunchRemoveCommandFlagsImageUnchanged = 0x00000010,
    LTHolePunchRemoveCommandFlagsUseSize = 0x00000020,
    LTHolePunchRemoveCommandFlagsUseCount = 0x00000040,
    LTHolePunchRemoveCommandFlagsUseLocation = 0x00000080,
    LTHolePunchRemoveCommandFlagsUseNormalDetection = 0x00000000,
    LTHolePunchRemoveCommandFlagsUseAdvancedDetection = 0x00010000
};

typedef NS_ENUM(NSInteger, LTHolePunchRemoveCommandLocation) {
    LTHolePunchRemoveCommandLocationLeft = 0x0001,
    LTHolePunchRemoveCommandLocationRight = 0x0002,
    LTHolePunchRemoveCommandLocationTop = 0x0003,
    LTHolePunchRemoveCommandLocationBottom = 0x0004
};

NS_ASSUME_NONNULL_BEGIN

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTHolePunchRemoveCommandEventArgs : NSObject

@property (nonatomic, assign, readonly) LeadRect boundingRectangle;
@property (nonatomic, assign, readonly) NSInteger holeIndex;
@property (nonatomic, assign, readonly) NSInteger holeTotalCount;
@property (nonatomic, assign, readonly) NSInteger whiteCount;
@property (nonatomic, assign, readonly) NSInteger blackCount;
@property (nonatomic, assign) LTRemoveStatus status;

- (instancetype)init __unavailable;
- (instancetype)initWithImage:(LTRasterImage*)image region:(LTRasterRegion*)region boundingRectangle:(LeadRect)boundingRectangle holeIndex:(NSInteger)holeIndex holeTotalCount:(NSInteger)holeTotalCount whiteCount:(NSInteger)whiteCount blackCount:(NSInteger)blackCount NS_DESIGNATED_INITIALIZER;

@end

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

typedef void (^LTHolePunchRemoveCommandStatus)(LTRasterImage *image, LTHolePunchRemoveCommandEventArgs *args, LTRemoveStatus *status);

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTHolePunchRemoveCommand : LTRasterCommand

@property (nonatomic, strong, readonly, nullable) LTRasterImage *image;
@property (nonatomic, strong, readonly, nullable) LTRasterImage *imageRegion;
@property (nonatomic, strong, readonly, nullable) LTRasterRegion *region;

@property (nonatomic, assign)                     LTHolePunchRemoveCommandFlags flags;
@property (nonatomic, assign)                     NSInteger minimumHoleCount;
@property (nonatomic, assign)                     NSInteger maximumHoleCount;
@property (nonatomic, assign)                     NSInteger minimumHoleWidth;
@property (nonatomic, assign)                     NSInteger minimumHoleHeight;
@property (nonatomic, assign)                     NSInteger maximumHoleWidth;
@property (nonatomic, assign)                     NSInteger maximumHoleHeight;
@property (nonatomic, assign)                     LTHolePunchRemoveCommandLocation location;

- (instancetype)initWithFlags:(LTHolePunchRemoveCommandFlags)flags location:(LTHolePunchRemoveCommandLocation)location minimumHoleCount:(NSInteger)minimumHoleCount maximumHoleCount:(NSInteger)maximumHoleCount minimumHoleWidth:(NSInteger)minimumHoleWidth minimumHoleHeight:(NSInteger)minimumHoleHeight maximumHoleWidth:(NSInteger)maximumHoleWidth maximumHoleHeight:(NSInteger)maximumHoleHeight NS_DESIGNATED_INITIALIZER;

- (BOOL)run:(LTRasterImage *)image progress:(nullable LTRasterCommandProgress)progressHandler status:(nullable LTHolePunchRemoveCommandStatus)holePunchRemoveStatus error:(NSError **)error;

@end

NS_ASSUME_NONNULL_END
