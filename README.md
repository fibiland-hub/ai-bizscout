# AI BizScout

기업 맞춤형 정부지원사업·R&D 공고 자동 탐색 및 Gmail 보고 시스템.

## 목표
- 공식 공고 출처에서 신규·변경 공고 수집
- 원문 링크, 접수 기간, 지원 자격, 제출 서류 등 구조화
- 기업 프로필 기반 관련성 평가
- 검증된 정보만 Gmail로 담당자에게 전달
- 불확실하거나 누락된 중요 정보는 자동 발송 보류

## 현재 상태
초기 안전 중심 프로토타입. 실제 공고 수집기 및 Gmail 연동은 아직 연결되지 않았습니다.

## 시작
```bash
python -m unittest discover -s tests -v
```

## 보안
비밀번호, Gmail 토큰, API 키, 기업 내부 정보는 저장소에 커밋하지 마세요.
공개 저장소라면 GitHub Settings > General > Danger Zone에서 비공개 전환을 권장합니다.
