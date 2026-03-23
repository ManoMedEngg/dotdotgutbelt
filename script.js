const canvas = document.getElementById('drawCanvas');
const ctx = canvas.getContext('2d');
let drawing = false;
let points = [];

// Support high-DPI and mobile responsive canvas
function resizeCanvas() {
  const scale = window.devicePixelRatio || 1;
  // Use clientWidth/clientHeight (CSS layout size) to avoid feedback loop
  const cssW = canvas.clientWidth || 400;
  const cssH = canvas.clientHeight || 400;
  canvas.width = Math.floor(cssW * scale);
  canvas.height = Math.floor(cssH * scale);
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  points = [];
  drawWaterDroplets();
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Water droplet effect
function drawWaterDroplets() {
  const w = canvas.clientWidth || 400;
  const h = canvas.clientHeight || 400;
  for (let i = 0; i < 8; i++) {
    const x = Math.random() * w;
    const y = Math.random() * h;
    const r = 8 + Math.random() * 12;
    ctx.save();
    ctx.globalAlpha = 0.18 + Math.random() * 0.12;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, 2 * Math.PI);
    ctx.fillStyle = '#00eaff';
    ctx.shadowColor = '#00eaff';
    ctx.shadowBlur = 12;
    ctx.fill();
    ctx.restore();
  }
}

canvas.addEventListener('mousedown', (e) => {
  drawing = true;
  points = [];
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawWaterDroplets();
  ctx.beginPath();
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  ctx.moveTo(x, y);
  points.push([x, y]);
});

canvas.addEventListener('touchstart', (e) => {
  e.preventDefault();
  if (e.touches.length !== 1) return;
  drawing = true;
  points = [];
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawWaterDroplets();
  const rect = canvas.getBoundingClientRect();
  const x = e.touches[0].clientX - rect.left;
  const y = e.touches[0].clientY - rect.top;
  ctx.beginPath();
  ctx.moveTo(x, y);
  points.push([x, y]);
}, { passive: false });

canvas.addEventListener('mousemove', (e) => {
  if (!drawing) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  ctx.lineTo(x, y);
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 3;
  ctx.shadowColor = '#00eaff';
  ctx.shadowBlur = 8;
  ctx.stroke();
  points.push([x, y]);
});

canvas.addEventListener('touchmove', (e) => {
  e.preventDefault();
  if (!drawing || e.touches.length !== 1) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.touches[0].clientX - rect.left;
  const y = e.touches[0].clientY - rect.top;
  ctx.lineTo(x, y);
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 3;
  ctx.shadowColor = '#00eaff';
  ctx.shadowBlur = 8;
  ctx.stroke();
  points.push([x, y]);
}, { passive: false });

canvas.addEventListener('mouseup', () => {
  drawing = false;
  ctx.shadowBlur = 0;
});

canvas.addEventListener('mouseleave', () => {
  drawing = false;
  ctx.shadowBlur = 0;
});

canvas.addEventListener('touchend', (e) => {
  e.preventDefault();
  drawing = false;
  ctx.shadowBlur = 0;
}, { passive: false });

document.getElementById('clearBtn').onclick = () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawWaterDroplets();
  points = [];
};

function getCircleScore(pts) {
  if (pts.length < 10) return 0;
  let sumX = 0, sumY = 0;
  for (const [x, y] of pts) {
    sumX += x;
    sumY += y;
  }
  const cx = sumX / pts.length;
  const cy = sumY / pts.length;

  let sumR = 0;
  for (const [x, y] of pts) {
    sumR += Math.hypot(x - cx, y - cy);
  }
  const avgR = sumR / pts.length;

  let sumErr = 0;
  for (const [x, y] of pts) {
    const r = Math.hypot(x - cx, y - cy);
    sumErr += Math.abs(r - avgR);
  }
  const meanErr = sumErr / pts.length;

  let score = Math.max(0, 100 - (meanErr / avgR) * 100);
  return Math.round(score);
}

function showPopup(message, showImage = false) {
  const popup = document.getElementById('popup');
  const popupMessage = document.getElementById('popupMessage');
  const popupImage = document.getElementById('popupImage');
  popupMessage.innerHTML = message;
  if (showImage) {
    popupImage.src = 'dank.jpeg';
    popupImage.classList.remove('hidden');
  } else {
    popupImage.classList.add('hidden');
  }
  popup.classList.remove('hidden');
}

document.getElementById('submitBtn').onclick = () => {
  const score = getCircleScore(points);
  if (score >= 60 && score <= 100) {
    showPopup(
      `🎉 <b>Happy Birthday!</b> 🎂<br>That was a <b>${score}%</b> perfect circle!<br>Thanks for playing! 🥳<br><span style="font-size:2rem;">🎈🎊🎁</span>`,
      true
    );
  } else {
    showPopup(
      `😅 Oops! Your circle was <b>${score}%</b> round.<br>Try again for a perfect birthday surprise! <span style="font-size:2rem;">🔄</span>`
    );
  }
};

document.getElementById('closePopup').onclick = () => {
  document.getElementById('popup').classList.add('hidden');
};

document.getElementById('popup').onclick = (e) => {
  if (e.target === document.getElementById('popup')) {
    document.getElementById('popup').classList.add('hidden');
  }
};
