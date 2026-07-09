# 따릉이 대여 데이터 — 기초 EDA 리포트

## 1. 데이터 개요
- 행/열: (181행, 5열)
- 기간: 2025-01-01 ~ 2025-06-29
- 주요 컬럼: date, rentals, avg_temp, rainfall, station_area

## 2. 구조 진단 (shape / info / describe)
- 자료형 요약: (날짜 열은 datetime[us]으로 인식됨 / rentals, avg_temp는 float64형 / rainfall은 int64형 / station_area는 str형)
- 수치 요약에서 눈에 띈 점: (rentals 평균 4531.757225, avg_temp 최댓값 250.000000 → 이상치 의심)

## 3. 품질 진단 (결측 / 중복 / 표기)
- 결측: rentals 8건
- 중복: 1건
- 표기 혼재: station_area에 ' 강남 '(공백) 존재

## 4. 패턴 (시각화에서 읽은 것)
- 추이: (계절성 — 봄~여름 증가 등)
- 관계: (기온과 대여 수의 양의 관계 등)

## 5. 다음 분석 제안
- 이상치(기온 이상치 250도)/결측(rentals 8건)을 제거하고 다시 분석해보기 , 지역에 따른 렌탈 수 확인해보기, 강수량에 따른 렌탈 수 확인해보기