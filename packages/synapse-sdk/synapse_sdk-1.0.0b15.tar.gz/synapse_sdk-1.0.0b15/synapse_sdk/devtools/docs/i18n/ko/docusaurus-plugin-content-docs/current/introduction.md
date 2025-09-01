---
id: introduction
title: 소개
sidebar_position: 1
---

# Synapse SDK

ML 및 데이터 처리 플러그인을 구축하세요.

## 개요

Synapse SDK는...

### 주요 기능

- **🚀 플러그인 개발 및 테스트**: Synapse용 카테고리별로 구성된 모듈화되고 재사용 가능한 컴포넌트 개발
- **⚡ 분산 컴퓨팅**: 확장 가능한 분산 실행을 위해 구축됨
- **🔧 다중 실행 모드**: Job, Task 및 REST API 지원
- **📦 격리된 런타임 환경**: 각 플러그인은 종속성 관리와 함께 자체 환경에서 실행됨
- **📊 진행률 추적**: 내장된 진행률 모니터링 및 메트릭 보고

### 플러그인 카테고리

SDK는 플러그인을 특정 카테고리로 구성합니다:

1. **신경망** (`NEURAL_NET`): ML 모델 학습, 추론 및 배포
2. **내보내기** (`EXPORT`): 데이터 내보내기 및 변환 작업
3. **업로드** (`UPLOAD`): 파일 및 데이터 업로드 기능
4. **스마트 도구** (`SMART_TOOL`): 지능형 자동화 도구
5. **사후 어노테이션** (`POST_ANNOTATION`): 데이터 어노테이션 후 후처리
6. **사전 어노테이션** (`PRE_ANNOTATION`): 데이터 어노테이션 전 전처리
7. **데이터 검증** (`DATA_VALIDATION`): 데이터 품질 및 검증 확인

## 시작하기

Synapse SDK를 시작하려면:

1. [SDK 설치](./installation.md)
2. [빠른 시작 가이드 따라하기](./quickstart.md)
3. [API 참조 탐색](./api/index.md)
4. [예제 확인](./examples/index.md)

## 다음 단계

- [핵심 개념](./concepts/index.md) 학습하기
- [백엔드 연결](./configuration.md) 구성하기