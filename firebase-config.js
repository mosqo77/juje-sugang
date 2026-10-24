// Firebase 콘솔 > 프로젝트 설정 > 내 앱(웹)에서 복사한 값으로 바꾸세요.
// 이 값은 비밀번호가 아니라 공개되어도 되는 식별 정보입니다. (접근 제한은 firestore.rules가 담당합니다)
window.APP_CONFIG = {
  firebase: {
    apiKey: "여기에-apiKey",
    authDomain: "여기에-프로젝트ID.firebaseapp.com",
    projectId: "여기에-프로젝트ID",
    appId: "여기에-appId"
  },
  // 관리자 로그인에서 아이디 "admin"이 가리키는 이메일입니다.
  // Firebase 콘솔 > Authentication > 사용자 추가에서 이 이메일로 관리자 계정을 만드세요(비밀번호는 거기서만 입력).
  adminEmail: "admin@sugang.school",
  // 관리자로 인정할 이메일 목록. firestore.rules의 목록과 같아야 합니다.
  admins: ["admin@sugang.school"]
};
