import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="졸라맨 원소 RPG", page_icon="⚔️", layout="wide")

st.title("🗡️ 졸라맨 원소 RPG (메이플스토리 스타일)")
st.caption("방향키와 키보드를 사용해 직접 캐릭터를 조작하고 5대 대지역을 탐험하세요!")

# HTML5 Canvas + JS 메이플스토리 스타일 실시간 게임 엔진
game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            background-color: #08090c;
            color: #fff;
            font-family: sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        #gameContainer {
            position: relative;
            box-shadow: 0 0 30px rgba(0, 230, 255, 0.2);
            border-radius: 10px;
            overflow: hidden;
            border: 2px solid #28324a;
        }
        canvas { background: #000; display: block; }
        #uiOverlay {
            position: absolute;
            top: 15px; left: 15px;
            pointer-events: none;
            background: rgba(10, 14, 23, 0.88);
            padding: 10px 16px;
            border-radius: 8px;
            border: 1px solid #3b4c7a;
            font-size: 13px;
            line-height: 1.5;
        }
        #mapText {
            position: absolute;
            top: 15px; right: 15px;
            background: rgba(10, 14, 23, 0.88);
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid #3b4c7a;
            font-weight: bold;
            color: #ffeb3b;
            font-size: 13px;
        }
        .stat-val { color: #00ffcc; font-weight: bold; }
        .controls {
            margin-top: 10px;
            color: #9aaec4;
            font-size: 13px;
            background: #141a26;
            padding: 6px 16px;
            border-radius: 20px;
        }
        #evolutionChoice {
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 20, 32, 0.95);
            border: 2px solid #00e5ff;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            display: none;
        }
        .choice-btn {
            background: #232d42; color: #fff;
            border: 1px solid #00e5ff;
            padding: 8px 14px; margin: 5px;
            border-radius: 6px; cursor: pointer; font-weight: bold;
        }
        .choice-btn:hover { background: #00e5ff; color: #000; }
    </style>
</head>
<body>

<div id="gameContainer">
    <canvas id="gameCanvas" width="920" height="480"></canvas>
    
    <div id="uiOverlay">
        <div><strong>👑 등급:</strong> <span id="rankText" class="stat-val">1등급 (x1.0)</span></div>
        <div><strong>❤️ HP:</strong> <span id="hpText" class="stat-val">100/100</span> | <strong>⚡ EN:</strong> <span id="enText" class="stat-val">50/50</span></div>
        <div><strong>⚔️ 출력:</strong> <span id="atkText" class="stat-val">15</span> | <strong>🔮 제어력:</strong> <span id="ctrlText" class="stat-val">5</span></div>
        <div><strong>🔥 속성:</strong> <span id="elemText" class="stat-val">기초 화염</span></div>
    </div>

    <div id="mapText">📍 인간 지역 - 고대 마법 유적</div>

    <div id="evolutionChoice">
        <h3 style="color:#00e5ff; margin-top:0;">✨ 마력 각성 선택지</h3>
        <p id="choiceDesc" style="font-size:13px; color:#ccc;">제어력이 한계에 도달했습니다. 불꽃의 형태를 고르세요.</p>
        <div id="choiceButtons"></div>
    </div>
</div>

<div class="controls">
    🎮 조작법: [← / →] 이동 | [Space] 점프 | [↑] 포탈 이동 | [Z] 검격 공격 | [X] 속성 파동 스킬
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const RANK_MULT = { 1: 1.0, 2: 3.0, 3: 10.0, 4: 50.0, 5: 1000.0 };

const player = {
    x: 100, y: 300, width: 24, height: 48,
    vx: 0, vy: 0,
    isGrounded: false, facing: 'right',
    rank: 1, baseHp: 100, baseEn: 50, baseAtk: 15, baseControl: 5,
    element: '기초 화염',
    affinity: { life: 0 },
    kills: 0,
    isAttacking: false, attackTimer: 0,
    isSkill: false, skillTimer: 0,
    choicePending: false
};

const REGIONS = [
    { name: "인간 지역 - 고대 마법 유적", bgColor: ['#0a0d14', '#182033'], platColor: '#2d3748', mHp: 40, mAtk: 5, mType: '슬라임' },
    { name: "몬스터 지역 - 생명의 대림", bgColor: ['#0a1a0f', '#13331c'], platColor: '#1e4d2b', mHp: 150, mAtk: 20, mType: '변이 야수' },
    { name: "천사 지역 - 규율의 신전", bgColor: ['#1a190a', '#3d3814'], platColor: '#5e5421', mHp: 600, mAtk: 80, mType: '빛의 수호자' },
    { name: "악마 지역 - 본능의 심연", bgColor: ['#1a0a14', '#3d1433'], platColor: '#5e214d', mHp: 3000, mAtk: 350, mType: '심연 마수' },
    { name: "초월자 지역 - 차원 균열", bgColor: ['#0a181a', '#14383d'], platColor: '#21595e', mHp: 20000, mAtk: 1500, mType: '차원 파괴자' }
];

let currentRegionIdx = 0;

const platforms = [
    { x: 0, y: 420, width: 920, height: 60 },
    { x: 90, y: 320, width: 200, height: 16 },
    { x: 630, y: 320, width: 200, height: 16 },
    { x: 350, y: 230, width: 220, height: 16 },
    { x: 140, y: 150, width: 160, height: 16 }
];

const portals = [
    { x: 20, y: 340, width: 40, height: 80, targetDir: -1 },
    { x: 860, y: 340, width: 40, height: 80, targetDir: 1 }
];

let monsters = [];
let particles = [];
let damageTexts = [];

function spawnMonsters() {
    monsters = [];
    const reg = REGIONS[currentRegionIdx];
    for (let i = 0; i < 3; i++) {
        monsters.push({
            x: 240 + i * 200, y: 180,
            width: 32, height: 32,
            hp: reg.mHp, maxHp: reg.mHp,
            vx: (i % 2 === 0 ? 1 : -1) * 1.5,
            type: reg.mType
        });
    }
}
spawnMonsters();

const keys = {};
window.addEventListener('keydown', e => keys[e.key] = true);
window.addEventListener('keyup', e => keys[e.key] = false);

function addDamageText(x, y, damage, color = '#ffeb3b') {
    damageTexts.push({ x, y, text: Math.floor(damage), opacity: 1, vy: -2, color });
}

function checkEvolution() {
    if (player.choicePending) return;

    if (player.baseControl >= 15 && player.element === '기초 화염') {
        player.choicePending = true;
        document.getElementById('evolutionChoice').style.display = 'block';
        document.getElementById('choiceDesc').innerText = "제어력이 성숙해졌습니다. 응축된 불꽃의 형태를 고르세요.";
        document.getElementById('choiceButtons').innerHTML = `
            <button class="choice-btn" onclick="selectEvolution('용암 파동')">🌋 용암 파동</button>
            <button class="choice-btn" onclick="selectEvolution('플라즈마')">⚡ 플라즈마</button>
        `;
    } else if (player.affinity.life >= 20 && (player.element === '용암 파동' || player.element === '플라즈마')) {
        player.choicePending = true;
        document.getElementById('evolutionChoice').style.display = 'block';
        document.getElementById('choiceDesc').innerText = "생명의 신의 기운이 극에 달했습니다. 최종 각성을 이루세요.";
        document.getElementById('choiceButtons').innerHTML = `
            <button class="choice-btn" onclick="selectEvolution('🔥 불사조의 야성염')">🔥 불사조의 야성염</button>
        `;
    }
}

function selectEvolution(elemName) {
    player.element = elemName;
    player.baseAtk += 20;
    player.baseControl += 10;
    player.choicePending = false;
    document.getElementById('evolutionChoice').style.display = 'none';
}

function attackHit(range, isSkill = false) {
    const mult = RANK_MULT[player.rank];
    const dmg = (isSkill ? player.baseAtk * 3.0 : player.baseAtk) * mult;

    const hitBox = {
        x: player.facing === 'right' ? player.x + player.width : player.x - range,
        y: player.y - 10,
        width: range, height: player.height + 20
    };

    monsters.forEach((m, idx) => {
        if (hitBox.x < m.x + m.width && hitBox.x + hitBox.width > m.x &&
            hitBox.y < m.y + m.height && hitBox.y + hitBox.height > m.y) {
            
            m.hp -= dmg;
            addDamageText(m.x + 10, m.y - 10, dmg, isSkill ? '#ff4d4d' : '#ffffff');

            for (let i = 0; i < 8; i++) {
                particles.push({
                    x: m.x + m.width/2, y: m.y + m.height/2,
                    vx: (Math.random() - 0.5) * 6, vy: (Math.random() - 0.5) * 6,
                    life: 15, color: isSkill ? '#ff6b35' : '#00e5ff'
                });
            }

            if (m.hp <= 0) {
                monsters.splice(idx, 1);
                player.kills++;
                player.baseAtk += 4;
                player.baseControl += 2;
                player.affinity.life += 5;

                if (player.kills >= 3 && player.rank === 1) player.rank = 2;
                checkEvolution();

                setTimeout(() => {
                    const reg = REGIONS[currentRegionIdx];
                    monsters.push({
                        x: Math.random() * 600 + 150, y: 100,
                        width: 32, height: 32,
                        hp: reg.mHp, maxHp: reg.mHp,
                        vx: 1.5, type: reg.mType
                    });
                }, 2000);
            }
        }
    });
}

function update() {
    if (player.choicePending) return;

    const mult = RANK_MULT[player.rank];
    const speed = 4.8;

    if (keys['ArrowLeft']) { player.vx = -speed; player.facing = 'left'; }
    else if (keys['ArrowRight']) { player.vx = speed; player.facing = 'right'; }
    else { player.vx = 0; }

    if ((keys['Space'] || keys[' ']) && player.isGrounded) {
        player.vy = -11;
        player.isGrounded = false;
    }

    if (keys['ArrowUp']) {
        portals.forEach(port => {
            if (player.x < port.x + port.width && player.x + player.width > port.x &&
                player.y < port.y + port.height && player.y + player.height > port.y) {
                if (port.targetDir === 1 && currentRegionIdx < REGIONS.length - 1) {
                    currentRegionIdx++; player.x = 80; spawnMonsters();
                } else if (port.targetDir === -1 && currentRegionIdx > 0) {
                    currentRegionIdx--; player.x = 800; spawnMonsters();
                }
            }
        });
    }

    if ((keys['z'] || keys['Z']) && !player.isAttacking && !player.isSkill) {
        player.isAttacking = true; player.attackTimer = 12; attackHit(50, false);
    }
    if (player.attackTimer > 0) player.attackTimer--; else player.isAttacking = false;

    if ((keys['x'] || keys['X']) && !player.isSkill && !player.isAttacking) {
        player.isSkill = true; player.skillTimer = 20; attackHit(90, true);
    }
    if (player.skillTimer > 0) player.skillTimer--; else player.isSkill = false;

    player.vy += 0.55;
    player.x += player.vx;
    player.y += player.vy;

    player.isGrounded = false;
    platforms.forEach(plat => {
        if (player.x < plat.x + plat.width &&
            player.x + player.width > plat.x &&
            player.y + player.height >= plat.y &&
            player.y + player.height <= plat.y + 16 &&
            player.vy >= 0) {
            
            player.y = plat.y - player.height;
            player.vy = 0;
            player.isGrounded = true;
        }
    });

    if (player.x < 0) player.x = 0;
    if (player.x > canvas.width - player.width) player.x = canvas.width - player.width;

    monsters.forEach(m => {
        m.x += m.vx;
        if (m.x < 50 || m.x > 840) m.vx *= -1;
    });

    particles.forEach((p, i) => {
        p.x += p.vx; p.y += p.vy; p.life--;
        if (p.life <= 0) particles.splice(i, 1);
    });

    damageTexts.forEach((d, i) => {
        d.y += d.vy; d.opacity -= 0.03;
        if (d.opacity <= 0) damageTexts.splice(i, 1);
    });

    const reg = REGIONS[currentRegionIdx];
    document.getElementById('mapText').innerText = `📍 ${reg.name}`;
    document.getElementById('rankText').innerText = `${player.rank}등급 (x${mult})`;
    document.getElementById('hpText').innerText = `${Math.floor(player.baseHp * mult)}/${Math.floor(player.baseHp * mult)}`;
    document.getElementById('enText').innerText = `${Math.floor(player.baseEn * mult)}/${Math.floor(player.baseEn * mult)}`;
    document.getElementById('atkText').innerText = `${Math.floor(player.baseAtk * mult)}`;
    document.getElementById('ctrlText').innerText = `${Math.floor(player.baseControl * mult)}`;
    document.getElementById('elemText').innerText = player.element;
}

function draw() {
    const reg = REGIONS[currentRegionIdx];
    const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
    grad.addColorStop(0, reg.bgColor[0]);
    grad.addColorStop(1, reg.bgColor[1]);
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    platforms.forEach(plat => {
        ctx.fillStyle = reg.platColor;
        ctx.fillRect(plat.x, plat.y, plat.width, plat.height);
        ctx.fillStyle = 'rgba(255,255,255,0.15)';
        ctx.fillRect(plat.x, plat.y, plat.width, 4);
    });

    portals.forEach(port => {
        ctx.fillStyle = 'rgba(0, 229, 255, 0.3)';
        ctx.fillRect(port.x, port.y, port.width, port.height);
        ctx.strokeStyle = '#00e5ff'; ctx.lineWidth = 2;
        ctx.strokeRect(port.x, port.y, port.width, port.height);
    });

    monsters.forEach(m => {
        ctx.fillStyle = '#ff3366';
        ctx.beginPath(); ctx.arc(m.x + m.width/2, m.y + m.height/2, m.width/2, 0, Math.PI * 2); ctx.fill();

        ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(m.x, m.y - 10, m.width, 5);
        ctx.fillStyle = '#00ffcc'; ctx.fillRect(m.x, m.y - 10, (m.hp / m.maxHp) * m.width, 5);
    });

    particles.forEach(p => {
        ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, 4, 4);
    });

    const px = player.x + player.width / 2;
    const py = player.y;

    if (player.rank >= 2) {
        ctx.strokeStyle = `rgba(0, 229, 255, ${0.4 + Math.sin(Date.now() / 150) * 0.2})`;
        ctx.lineWidth = 4;
        ctx.beginPath(); ctx.arc(px, py + 20, 32 + player.rank * 4, 0, Math.PI * 2); ctx.stroke();
    }

    ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(px, py + 10, 8, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(px, py + 18); ctx.lineTo(px, py + 34); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(px, py + 34); ctx.lineTo(px - 8, py + 48); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(px, py + 34); ctx.lineTo(px + 8, py + 48); ctx.stroke();

    ctx.beginPath(); ctx.moveTo(px, py + 22);
    if (player.isAttacking) {
        const dir = player.facing === 'right' ? 1 : -1;
        ctx.lineTo(px + (26 * dir), py + 18); ctx.stroke();
        ctx.strokeStyle = '#00ffff'; ctx.beginPath();
        ctx.arc(px, py + 20, 40, player.facing === 'right' ? -0.8 : 2.2, player.facing === 'right' ? 0.8 : 4.0);
        ctx.stroke();
    } else if (player.isSkill) {
        const dir = player.facing === 'right' ? 1 : -1;
        ctx.lineTo(px + (18 * dir), py + 10); ctx.stroke();
        ctx.fillStyle = player.element.includes('불사조') ? '#ff1744' : '#ff9100';
        ctx.beginPath(); ctx.arc(px + (58 * dir), py + 20, 28, 0, Math.PI * 2); ctx.fill();
    } else {
        ctx.lineTo(px - 8, py + 28); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(px, py + 22); ctx.lineTo(px + 8, py + 28); ctx.stroke();
    }

    damageTexts.forEach(d => {
        ctx.fillStyle = d.color; ctx.font = 'bold 16px sans-serif';
        ctx.globalAlpha = d.opacity; ctx.fillText(d.text, d.x, d.y); ctx.globalAlpha = 1.0;
    });
}

function gameLoop() {
    update(); draw(); requestAnimationFrame(gameLoop);
}

gameLoop();
</script>
</body>
</html>
"""

# Streamlit 내부에 렌더링
components.html(game_html, height=580)
