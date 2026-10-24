"""Builds index.html (Firebase web version) from the published artifact source.
usage: python3 build.py <artifact source html>"""
import sys

SRC = sys.argv[1]
s = open(SRC, encoding='utf-8').read()

# 1) swap the Claude capabilities block for Firebase
a = s.index('/* ---- capabilities ---- */')
b = s.index('/* ---- state ---- */')
FB = r'''/* ---- Firebase (web version) ---- */
let db = null, user = null, downloads = null;
const CFG = window.APP_CONFIG || {};
const fbOk = !!(window.firebase && CFG.firebase && CFG.firebase.apiKey && !/여기에|YOUR/i.test(CFG.firebase.apiKey));
let isAdmin = false, canWrite = true, local = true;
if(fbOk){
  local = false;
  firebase.initializeApp(CFG.firebase);
  const auth = firebase.auth(), fs = firebase.firestore();
  let cur = await new Promise(res => { const off = auth.onAuthStateChanged(x => { off(); res(x); }); });
  if(!cur){ try{ cur = (await auth.signInAnonymously()).user; }catch(e){ canWrite = false; } }
  const admins = (CFG.admins || []).map(x => String(x).toLowerCase());
  isAdmin = !!(cur && cur.email && admins.indexOf(cur.email.toLowerCase()) >= 0);
  const sleepMs = ms => new Promise(r => setTimeout(r, ms));
  db = {
    doc: p => fs.doc(p),
    collection: c => fs.collection(c),
    /* seat claim in one transaction: the capacity check and the write are atomic */
    claimSeat: async (sid, no, add, cap) => {
      const ref = fs.doc('enroll/' + sid);
      for(let i = 0; i < 8; i++){
        try{
          return await fs.runTransaction(async t => {
            const snap = await t.get(ref);
            const dd = snap.exists ? (snap.data() || {}) : {};
            let list = (dd.students || []).slice(), tt = Object.assign({}, dd.t || {});
            const has = list.indexOf(no) >= 0;
            if(add){ if(has) return 'ok'; if(list.length >= cap) return 'full'; list.push(no); tt[no] = Date.now(); }
            else { if(!has) return 'ok'; list = list.filter(x => x !== no); delete tt[no]; }
            t.set(ref, {students:list, t:tt});
            return 'ok';
          });
        }catch(e){
          if(e && e.code === 'permission-denied') return add ? 'full' : 'busy';
          await sleepMs(200 + Math.random() * 600);
        }
      }
      return 'busy';
    }
  };
  user = {canEdit: async () => isAdmin, can: async () => canWrite};
  downloads = {save: async ({filename, data}) => {
    const blob = data instanceof Blob ? data : new Blob([data], {type:'text/csv;charset=utf-8'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename;
    document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
    return {status:'saved'};
  }};
  /* admin sign-in: Firebase email/password. The id "admin" stands for the admin email in firebase-config.js */
  window.__fbLogin = async (id, pw, errEl) => {
    const email = id === 'admin' ? String(CFG.adminEmail || '') : (id.indexOf('@') >= 0 ? id : '');
    if(!email || !pw){ errEl.textContent = '아이디 또는 비밀번호가 맞지 않습니다.'; return; }
    try{ await auth.signInWithEmailAndPassword(email, pw); }
    catch(e){ errEl.textContent = '아이디 또는 비밀번호가 맞지 않습니다.'; return; }
    const u = auth.currentUser;
    if(!(u && u.email && admins.indexOf(u.email.toLowerCase()) >= 0)){
      errEl.textContent = '관리 권한이 없는 계정입니다.'; try{ await auth.signOut(); }catch(e){} return;
    }
    try{ sessionStorage.setItem('juje-adm', '1'); }catch(e){}
    location.reload();
  };
  window.__fbOut = async () => {
    try{ sessionStorage.removeItem('juje-adm'); }catch(e){}
    try{ await auth.signOut(); }catch(e){}
    location.reload();
  };
} else {
  db = makeLocalDB(); isAdmin = true;
  const w = document.createElement('div');
  w.style.cssText = 'background:#B0372E;color:#fff;padding:10px 16px;text-align:center;font-size:14px';
  w.textContent = '서버(Firebase) 설정이 없어 이 브라우저에서만 저장됩니다. firebase-config.js를 채운 뒤 다시 올려 주세요.';
  document.body.insertBefore(w, document.body.firstChild);
}
/* admin screen is a separate login; the entry link is hidden in the web version (open the page with #admin) */
const ADM_ID = 'admin', ADM_PW = fbOk ? '\u0000' : '1234';
let adm = false;
try{ adm = isAdmin && sessionStorage.getItem('juje-adm') === '1'; }catch(e){}

'''
s = s[:a] + FB + s[b:]

# 2) seat claim goes through the transaction when available
old = "async function claim(sid, no, add, cap){\n"
assert old in s
s = s.replace(old, old + "  if(db.claimSeat) return db.claimSeat(sid, no, add, cap);\n")

# 3) admin entry: hidden link in the web version, Firebase sign-in/out
n = s.count("adm || !isAdmin || !!S.me")
assert n == 2, n
s = s.replace("adm || !isAdmin || !!S.me", "!!window.__fbLogin || adm || !isAdmin || !!S.me")
old = "  const err = $('#aErr');\n"
assert s.count(old) == 1
s = s.replace(old, old + "  if(window.__fbLogin){ window.__fbLogin($('#aId').value.trim(), $('#aPw').value, err); return; }\n")
old = "  applyAdm(); toast('관리자 로그아웃했습니다.');"
assert s.count(old) == 1
s = s.replace(old, "  if(window.__fbOut){ window.__fbOut(); return; }\n" + old)
old = "\napplyAdm();\n"
assert s.count(old) == 1
s = s.replace(old, old + "if(location.hash === '#admin' && !adm) $('#admLogin').hidden = false;\nwindow.addEventListener('hashchange', () => { if(location.hash === '#admin' && !adm) $('#admLogin').hidden = false; });\n")

# 4) wrap the fragment in a full HTML document
i = s.index('</style>') + len('</style>')
head, body = s[:i], s[i:]
HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore-compat.js"></script>
<script src="firebase-config.js"></script>
'''
head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
out = HEAD + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n'
out = out.replace('jeju-sugang', 'juje-sugang').replace('jeju-adm', 'juje-adm')
open('index.html', 'w', encoding='utf-8').write(out)
print('index.html', len(out))
