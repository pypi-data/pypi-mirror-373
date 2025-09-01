---
id: converters
title: 변환기
sidebar_position: 1
---

# 변환기

Synapse SDK는 컴퓨터 비전 데이터셋을 위한 포괄적인 데이터 형식 변환 유틸리티를 제공합니다. 이러한 변환기는 머신 러닝 워크플로우에서 일반적으로 사용되는 다양한 어노테이션 형식 간의 원활한 변환을 가능하게 합니다.

## 개요

변환기 시스템은 다음 간의 양방향 변환을 지원합니다:

- **DM 형식** - Synapse Data Manager의 네이티브 어노테이션 형식 (v1 ⟷ v2 마이그레이션 지원)
- **COCO 형식** - Microsoft Common Objects in Context 형식
- **Pascal VOC 형식** - Visual Object Classes XML 형식  
- **YOLO 형식** - You Only Look Once 텍스트 기반 형식

모든 변환기는 분류된 데이터셋(train/valid/test 분할 포함)과 분류되지 않은 데이터셋 모두를 지원합니다. 또한 모든 변환기는 이제 개별 파일 처리를 위한 단일 파일 변환 모드를 지원합니다.

## 지원되는 어노테이션 타입

| 어노테이션 타입 | DM | COCO | Pascal VOC | YOLO |
|----------------|----|----|-----------|------|
| 바운딩 박스 | ✅ | ✅ | ✅ | ✅ |
| 폴리곤 | ✅ | ✅ | ❌ | ✅ |
| 세그멘테이션 | ✅ | ✅ | ✅ | ❌ |
| 키포인트 | ✅ | ✅ | ❌ | ✅ |
| 분류 | ✅ | ✅ | ❌ | ❌ |