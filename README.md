# 주제선택 수강신청 (웹 버전)

학생은 로그인 없이 주소만 열어 학번+개인코드로 신청하고, 관리자는 아이디/비밀번호로 로그인합니다. 화면은 `index.html` 한 파일, 데이터는 Firebase(Firestore)에 저장합니다.

## 파일
| 파일 | 설명 |
|---|---|
| `index.html` | 사이트 전체 (학생 신청, 관리자 메뉴) |
| `firebase-config.js` | Firebase 연결 값과 관리자 이메일 (직접 채우는 파일) |
| `firestore.rules` | 데이터 접근 규칙 (Firebase 콘솔에 붙여 넣는 파일) |
| `build.py` | Claude에서 고친 최신 원본으로 `index.html`을 다시 만드는 스크립트 (배포에는 불필요) |

## 설정 순서 (처음 한 번, 약 20분)
1. **Firebase 프로젝트** — https://console.firebase.google.com 에서 프로젝트 생성 (Analytics는 꺼도 됨)
2. **웹 앱 등록** — 프로젝트 설정 > 내 앱 > `</>` 추가. 나오는 `apiKey`, `authDomain`, `projectId`, `appId`를 `firebase-config.js`에 붙여 넣기
3. **Firestore** — 빌드 > Firestore Database > 만들기 (프로덕션 모드, 위치 `asia-northeast3` 서울)
4. **로그인 방법** — 빌드 > Authentication > 시작하기 > 로그인 방법에서 **익명**과 **이메일/비밀번호**를 사용 설정
5. **관리자 계정 만들기** — Authentication > 사용자 > 사용자 추가에서 이메일 `admin@sugang.school`(다른 이메일을 쓰면 아래 2곳도 같게 수정)과 **관리자 비밀번호(6자 이상)**를 입력. 비밀번호는 이 콘솔에서만 입력하고 파일에는 쓰지 않습니다.
6. **회원가입 끄기** — Authentication > 설정 > 사용자 작업에서 "새 계정 만들기(회원가입)" 사용 중지 (관리자 계정을 만든 뒤에)
7. **허용 도메인** — Authentication > 설정 > 승인된 도메인에 `아이디.github.io` 추가
8. **관리자 이메일 일치** — `firebase-config.js`의 `adminEmail`·`admins`와 `firestore.rules`의 `isAdmin()` 안 이메일을 같게
9. **규칙 올리기** — Firestore Database > 규칙 탭에 `firestore.rules` 내용을 붙여 넣고 게시
10. **(권장) API 키 제한** — Google Cloud 콘솔 > 사용자 인증 정보에서 웹 API 키를 "웹사이트 제한"으로 `아이디.github.io/*`만 허용
11. **GitHub Pages** — 이 폴더를 (공개) 저장소에 올리고 Settings > Pages > Branch `main` / `(root)`, Enforce HTTPS 켜기

## 사용
- 학생 주소: `https://아이디.github.io/저장소이름/`
- 관리자 로그인: 같은 주소 뒤에 `#admin`을 붙여 열면(`.../저장소이름/#admin`) 로그인 창이 나옵니다. 아이디 `admin`, 비밀번호는 5번에서 정한 값입니다. 학생 화면에는 관리자 입구가 보이지 않습니다.
- 첫 사용: 수강신청 관리 > 새 수강신청 > 과목 관리에서 과목 등록 > 학생 명단에서 엑셀 업로드 > 개인코드 CSV 내려받아 학생에게 배부 > 설정에서 접수 시작

## 알아 둘 점
- 학생 이름·개인코드는 관리자만 읽는 `admin/roster`에만 있고, 공개되는 것은 확인용 해시와 코드로 잠근 이름뿐입니다.
- 정원 확인과 신청 저장은 Firestore 트랜잭션으로 처리하고, 규칙에서도 정원 초과를 막습니다.
- 학생 쪽 개인코드 확인은 화면에서 해시로 합니다. 학교 안 신청용으로는 충분하지만 더 높은 보안이 필요하면 Cloud Functions로 옮겨야 합니다.
- Claude 안의 시험용 데이터는 이 사이트로 옮겨지지 않습니다. 과목·명단은 다시 등록하세요.
- `firebase-config.js`를 채우지 않고 열면 "이 브라우저에서만 저장됩니다" 경고와 함께 시험 모드로 열리며, 이때 관리자 로그인은 `admin`/`1234`입니다. 실제 배포에서는 쓰이지 않습니다.
