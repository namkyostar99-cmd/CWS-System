document.addEventListener('DOMContentLoaded', () => {
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const submitLogin = document.getElementById('submitLogin');
  const showSignupInline = document.getElementById('showSignupInline');
  const signupInline = document.getElementById('signupInline');
  const cancelSignup = document.getElementById('cancelSignup');
  const submitSignup = document.getElementById('submitSignup');
  const su_username = document.getElementById('su_username');
  const su_password = document.getElementById('su_password');
  const su_password_confirm = document.getElementById('su_password_confirm');

  const USERS_KEY = 'dashboard_users';
  const SESSION_KEY = 'dashboard_user';
  const ROLE_KEY = 'dashboard_role';

  function getUsers(){
    try{ return JSON.parse(localStorage.getItem(USERS_KEY) || '{}'); }catch(e){return {}};
  }
  function setUsers(u){ localStorage.setItem(USERS_KEY, JSON.stringify(u)); }

  function resetSignup(){
    su_username.value = '';
    su_password.value = '';
    su_password_confirm.value = '';
  }

  function resetLogin(){
    usernameInput.value = '';
    passwordInput.value = '';
  }

  // ---------------------------------------------------------
  // [수정] 관리자 여부에 따라 역할을 설정하는 함수
  function setRoleByUsername(username){
    if(username === 'admin') {
      localStorage.setItem(ROLE_KEY, 'admin');
    } else {
      localStorage.setItem(ROLE_KEY, 'user');
    }
  }
  // ---------------------------------------------------------

  if(localStorage.getItem(SESSION_KEY)){
    window.location.href = 'monitoring.html';
    return;
  }

  showSignupInline.addEventListener('click', (e) => {
    e.preventDefault();
    signupInline.classList.toggle('hidden');
  });

  cancelSignup.addEventListener('click', () => {
    signupInline.classList.add('hidden');
    resetSignup();
  });

  submitSignup.addEventListener('click', () => {
    const u = su_username.value.trim();
    const p = su_password.value;
    const pc = su_password_confirm.value;
    if(!u){ alert('사용자명을 입력하세요'); return; }
    if(p.length < 4){ alert('비밀번호는 4자 이상이어야 합니다'); return; }
    if(p !== pc){ alert('비밀번호가 일치하지 않습니다'); return; }
    const users = getUsers();
    if(users[u]){ alert('이미 존재하는 사용자명입니다'); return; }
    users[u] = p; setUsers(users);
    
    localStorage.setItem(SESSION_KEY, u);
    setRoleByUsername(u); // 가입 즉시 로그인 시 역할 부여
    window.location.href = 'monitoring.html';
  });

  submitLogin.addEventListener('click', () => {
    const u = usernameInput.value.trim();
    const p = passwordInput.value;

    if(!u){ alert('사용자명을 입력하세요'); return; }

    // 1. [핵심 추가] 하드코딩된 관리자 계정 체크
    if(u === 'admin' && p === '1234') {
      localStorage.setItem(SESSION_KEY, u);
      localStorage.setItem(ROLE_KEY, 'admin');
      alert('관리자 계정으로 로그인되었습니다.');
      window.location.href = 'monitoring.html';
      return;
    }

    // 2. 일반 가입자 체크 로직
    const users = getUsers();
    if(!users[u]){ alert('존재하지 않는 사용자입니다. 회원가입 해주세요.'); return; }
    if(users[u] !== p){ alert('비밀번호가 틀렸습니다'); return; }
    
    localStorage.setItem(SESSION_KEY, u);
    setRoleByUsername(u); // 일반 유저는 'user' 역할 부여
    window.location.href = 'monitoring.html';
  });

  document.addEventListener('keydown', (e) => {
    if(e.key === 'Enter') submitLogin.click();
  });
});