document.addEventListener('DOMContentLoaded', () => {
  // localStorage keys
  const SESSION_KEY = 'dashboard_user';
  const ROLE_KEY = 'dashboard_role';

  // [수정] 로그인 안 되어 있으면 index.html로 (단, 이미 index.html이면 무한루프 방지)
  if(!localStorage.getItem(SESSION_KEY) && !window.location.pathname.includes('index.html')){
    window.location.href = 'index.html';
    return;
  }

  const userArea = document.getElementById('userArea');
  const roiControls = document.getElementById('roiControls');
  const roiStart = document.getElementById('roiStart');
  const roiReset = document.getElementById('roiReset');
  const roiDone = document.getElementById('roiDone');
  const roiLog = document.getElementById('roiLog');
  const roiInfo = document.getElementById('roiInfo');
  const videoFeed = document.getElementById('video-feed');
  const videoUploader = document.getElementById('videoUploader');
  const uploadTrigger = document.getElementById('uploadTrigger');
  const roleControls = document.getElementById('roleControls');
  const roleLabel = document.getElementById('roleLabel');
  const roleUserBtn = document.getElementById('roleUser');
  const roleAdminBtn = document.getElementById('roleAdmin');

  let roiMode = false;
  let roiPoints = [];

  function isLoggedIn(){
    return !!localStorage.getItem(SESSION_KEY);
  }

  function getRole(){
    return localStorage.getItem(ROLE_KEY) || 'user';
  }

  function setRole(role){
    localStorage.setItem(ROLE_KEY, role);
    updateRoleUI();
  }

  function setActiveNav(page){
    document.querySelectorAll('.sidebar a').forEach(x => x.classList.remove('active'));
    const link = document.querySelector(`.sidebar a[data-page="${page}"]`);
    if(link) link.classList.add('active');
  }

  function updateNavVisibility(){
    const logged = isLoggedIn();
    document.querySelectorAll('.sidebar a').forEach(a => {
      if(!logged && a.dataset.page !== 'overview'){
        a.classList.add('hidden');
      } else {
        a.classList.remove('hidden');
      }
    });
    if(!logged){
      showPage('overview');
      setActiveNav('overview');
    }
  }

  function updateRoleUI(){
    const logged = isLoggedIn();
    if(!logged){
      if(roleControls) roleControls.classList.add('hidden');
      if(roiControls) roiControls.classList.add('hidden');
      if(roiInfo) roiInfo.classList.add('hidden');
      return;
    }
    if(roleControls) roleControls.classList.remove('hidden');
    const role = getRole();
    if(roleLabel) roleLabel.textContent = role === 'admin' ? '관리자' : '일반';
    
    if(role === 'admin'){
      if(roiControls) roiControls.classList.remove('hidden');
      if(roiInfo) roiInfo.classList.remove('hidden');
    } else {
      if(roiControls) roiControls.classList.add('hidden');
      if(roiInfo) roiInfo.classList.add('hidden');
    }
  }

  function renderUser(){
    const user = localStorage.getItem(SESSION_KEY);
    if(user){
      if(!localStorage.getItem(ROLE_KEY)) setRole('user');
      userArea.innerHTML = `<span style="color:#9fb4c9;margin-right:8px">${user}</span><button id='logoutBtn' class='btn'>로그아웃</button>`;
      document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.removeItem(SESSION_KEY);
        window.location.href = 'index.html';
      });
    } else {
      userArea.innerHTML = `<button id='loginBtn' class='btn'>로그인</button>`;
      document.getElementById('loginBtn').addEventListener('click', () => { window.location.href = 'login.html'; });
    }
    updateNavVisibility();
    updateRoleUI();
  }

  // navigation
  document.querySelectorAll('.sidebar a').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      if(!isLoggedIn() && a.dataset.page !== 'overview') return;
      document.querySelectorAll('.sidebar a').forEach(x => x.classList.remove('active'));
      a.classList.add('active');
      showPage(a.dataset.page);
    });
  });

  function showPage(page){
    if(!isLoggedIn() && page !== 'overview') page = 'overview';
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    const el = document.getElementById(page);
    if(el) el.classList.remove('hidden');
    
    const statusEl = document.querySelector('.status');
    if(page === 'live'){
      if(statusEl) statusEl.classList.remove('hidden');
    } else {
      if(statusEl) statusEl.classList.add('hidden');
    }
  }

  function setRoiLog(){
    if(!roiLog) return;
    if(roiPoints.length === 0){
      roiLog.textContent = '(클릭 좌표가 여기에 표시됩니다)';
      return;
    }
    roiLog.textContent = roiPoints.map((p, i) => `#${i+1} x:${p.x.toFixed(3)} y:${p.y.toFixed(3)} (px ${p.px}, ${p.py})`).join('\n');
  }

  // ROI 제어 이벤트
  roiStart.addEventListener('click', () => {
    if(getRole() !== 'admin') return;
    roiMode = true;
    roiStart.textContent = 'ROI 설정 중...';
    roiStart.classList.add('active');
  });

  roiReset.addEventListener('click', () => {
    if(getRole() !== 'admin') return;
    roiPoints = [];
    roiMode = false;
    roiStart.textContent = 'ROI 설정 시작';
    roiStart.classList.remove('active');
    setRoiLog();
  });

  roiDone.addEventListener('click', () => {
    if(getRole() !== 'admin') return;
    if(roiPoints.length < 3) {
        alert("최소 3개 이상의 점을 찍어주세요.");
        return;
    }
    
    roiMode = false;
    roiStart.textContent = 'ROI 설정 시작';
    roiStart.classList.remove('active');

    // [핵심 보완] 서버 전송 로직
    fetch('/set_roi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ points: roiPoints })
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            alert(`서버에 ${roiPoints.length}개의 좌표가 저장되었습니다.`);
        }
    })
    .catch(err => console.error("ROI 전송 실패:", err));
  });

  // [수정] 영상 클릭 좌표 계산 보정
  videoFeed.addEventListener('click', (e) => {
    if(!isLoggedIn()) return;
    if(getRole() !== 'admin') return;
    if(!roiMode) return;

    const rect = videoFeed.getBoundingClientRect();
    
    // 0~1 사이의 상대 좌표
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    
    // 실제 영상 해상도 기준 픽셀 좌표 (NaturalWidth 사용)
    const px = Math.round(x * videoFeed.naturalWidth);
    const py = Math.round(y * videoFeed.naturalHeight);

    roiPoints.push({ x, y, px, py });
    setRoiLog();
  });

  let currentObjectUrl = null;
  if(videoUploader) {
    videoUploader.addEventListener('change', (e) => {
      const file = e.target.files?.[0];
      if(!file) return;
      if(currentObjectUrl){
        URL.revokeObjectURL(currentObjectUrl);
        currentObjectUrl = null;
      }
      const url = URL.createObjectURL(file);
      currentObjectUrl = url;
      videoFeed.src = url;
    });
  }

  if(uploadTrigger) {
    uploadTrigger.addEventListener('click', () => {
      videoUploader.value = '';
      videoUploader.click();
    });
  }

  if(roleUserBtn) roleUserBtn.addEventListener('click', () => setRole('user'));
  if(roleAdminBtn) roleAdminBtn.addEventListener('click', () => setRole('admin'));

  // initial render
  showPage('live');
  renderUser();
  setRoiLog();
});