// *************************************************************
// Copyright (c) 1991-2025 Apryse Software Corp.
// All Rights Reserved.
// *************************************************************
//
//  LTDocumentWriterEmptyPage.h
//  Leadtools.Document.Writer
//

#import <Leadtools.Document.Writer/LTDocumentWriterPage.h>

NS_CLASS_AVAILABLE(10_10, 8_0)
@interface LTDocumentWriterEmptyPage : LTDocumentWriterPage <NSCopying>

@property (nonatomic, assign) double width;
@property (nonatomic, assign) double height;

@end
