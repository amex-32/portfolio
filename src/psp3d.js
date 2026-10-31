// Console 3D de la page 404 : modèle model/psp.glb, écran dessiné en direct, boutons branchés sur le vrai lecteur.
// Génère js/psp3d.js (voir README) ; chargé par js/hud.js sur la 404 uniquement.
import { Box3, CanvasTexture, Group, MeshBasicMaterial, PerspectiveCamera, PMREMGenerator, DirectionalLight, Quaternion, Raycaster, Scene, SRGBColorSpace, Vector2, Vector3, WebGLRenderer, ACESFilmicToneMapping } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

// boutons du modèle : 1-4 croix, 5-8 triangle, rond, croix, carré
const KEYS = { button2: '.pl-next', button4: '.pl-prev', button5: '.pl-like', button6: '.pl-next', button7: '.pl-play', button8: '.pl-shuffle' };

window.akPsp = function (stage, o) {
  const accent = () => getComputedStyle(document.documentElement).getPropertyValue('--fill').trim();
  const W = 480, H = 272, screen = document.createElement('canvas'), c = screen.getContext('2d');
  screen.width = W; screen.height = H;
  const bars = Array.from({ length: 28 }, () => .06);
  let on0 = o.calm ? 0 : Infinity; // allumage de l'écran, à l'horloge réelle : il ne dépend pas de la cadence de GSAP
  const clock = (s) => { s = Math.floor(s) || 0; return Math.floor(s / 60) + ':' + ('0' + s % 60).slice(-2); };
  function paint() {
    const a = window.akAudio, pl = window.akPlayer, on = a && !a.paused, d = a && isFinite(a.duration) ? a.duration : 0, fill = accent();
    c.fillStyle = '#0e0e0e'; c.fillRect(0, 0, W, H);
    const lit = Math.min(1, Math.floor(Math.max(0, (performance.now() - on0) / 240) * 5) / 5);
    c.save(); c.beginPath(); c.rect(0, H / 2 * (1 - lit), W, H * lit); c.clip();
    c.fillStyle = fill; c.font = "16px 'JetBrains Mono', monospace"; c.textAlign = 'left'; c.fillText('MUSIC', 20, 32);
    c.textAlign = 'right'; c.fillText(on ? 'PLAY' : 'PAUSE', W - 20, 32);
    c.textAlign = 'left'; c.fillStyle = '#e8e8e2'; c.font = "33px 'Departure Mono', monospace";
    let title = pl ? pl.tracks[pl.current()].t : 'NO DISC';
    while (c.measureText(title).width > W - 40 && title.length > 3) title = title.slice(0, -1);
    c.fillText(title, 20, 78);
    c.fillStyle = fill;
    bars.forEach((v, i) => { // barres décoratives : l'audio n'est pas analysé
      bars[i] = on && !o.calm ? .06 + Math.random() * .94 : .06;
      c.fillRect(20 + i * 16, 190 - bars[i] * 90, 12, bars[i] * 90);
    });
    c.strokeStyle = '#4a4a4a'; c.strokeRect(20.5, 206.5, W - 41, 12);
    c.fillRect(22, 208, (W - 44) * (d ? a.currentTime / d : 0), 9);
    c.fillStyle = '#8c8c8c'; c.font = "16px 'JetBrains Mono', monospace";
    c.fillText(clock(a && a.currentTime), 20, 246); c.textAlign = 'right'; c.fillText(clock(d), W - 20, 246);
    c.fillStyle = 'rgba(0,0,0,.28)'; for (let y = 0; y < H; y += 3) c.fillRect(0, y, W, 1);
    c.restore();
  }
  // sans WebGL ou sans modèle, il reste l'écran à plat : le lecteur marche toujours
  const flat = () => { on0 = 0; screen.className = 'flat'; stage.textContent = ''; stage.appendChild(screen); paint(); const id = setInterval(() => { if (!screen.isConnected) clearInterval(id); else paint(); }, 160); };

  let gl;
  try { gl = new WebGLRenderer({ antialias: true, alpha: true }); } catch (e) { return flat(); }
  gl.setPixelRatio(Math.min(devicePixelRatio, 2));
  gl.toneMapping = ACESFilmicToneMapping; gl.toneMappingExposure = 1.15;
  const scene = new Scene(), camera = new PerspectiveCamera(26, 1, .1, 200), pivot = new Group();
  const pm = new PMREMGenerator(gl);
  scene.environment = pm.fromScene(new RoomEnvironment(), .04).texture; pm.dispose();
  const rim = new DirectionalLight(accent(), 2.4); rim.position.set(-6, 4, -8); scene.add(rim, pivot);
  const fit = () => {
    const w = stage.clientWidth, h = stage.clientHeight, t = Math.tan(camera.fov * Math.PI / 360);
    gl.setSize(w, h); camera.aspect = w / h;
    camera.position.z = Math.max(5.2 / t, 10 / t / camera.aspect);
    camera.updateProjectionMatrix();
  };
  new ResizeObserver(fit).observe(stage); fit();

  const tex = new CanvasTexture(screen); tex.colorSpace = SRGBColorSpace; tex.flipY = false;
  let rx = .14, ry = -.5, base = ry, drag = null, parts = [], last = 0, wake = 0;
  new GLTFLoader().load(o.url, (g) => {
    const model = g.scene, align = new Group();
    model.updateMatrixWorld(true);
    model.traverse((m) => {
      if (!m.isMesh) return;
      parts.push(m);
      if (!m.name.startsWith('screen')) return;
      // l'écran occupe une zone de l'atlas : ses UV sont ramenés à toute la toile
      const uv = m.geometry.attributes.uv, box = new Box3().setFromBufferAttribute(uv);
      for (let i = 0; i < uv.count; i++) uv.setXY(i, (uv.getX(i) - box.min.x) / (box.max.x - box.min.x), (box.max.y - uv.getY(i)) / (box.max.y - box.min.y));
      m.material = new MeshBasicMaterial({ map: tex, toneMapped: false });
      // le modèle est posé incliné : on le redresse d'après la normale de l'écran
      m.geometry.computeBoundingBox();
      const up = new Vector3(0, 1, 1).normalize().transformDirection(m.matrixWorld);
      align.quaternion.copy(new Quaternion().setFromUnitVectors(up, new Vector3(0, 0, 1)));
    });
    align.add(model); pivot.add(align); align.updateMatrixWorld(true);
    pivot.position.sub(new Box3().setFromObject(pivot).getCenter(new Vector3()));
    if (!o.calm && window.gsap) {
      window.gsap.from(pivot.scale, { x: .02, y: .02, z: .02, duration: .32, ease: 'steps(7)', delay: o.at });
    }
    if (!o.calm) on0 = performance.now() + (o.at + .4) * 1000;
    stage.appendChild(gl.domElement);
    gl.setAnimationLoop(frame);
  }, undefined, flat);

  function frame(ms) {
    if (!gl.domElement.isConnected) { gl.setAnimationLoop(null); gl.dispose(); return; } // navigation douce : la page a changé
    if (!drag && !o.calm && ms > wake) ry = base + Math.sin((ms - wake) / 1800) * .28;
    pivot.rotation.set(rx, ry, 0);
    if (ms - last > 160) { last = ms; paint(); tex.needsUpdate = true; }
    gl.render(scene, camera);
  }

  const ray = new Raycaster(), hit = (e) => {
    const r = gl.domElement.getBoundingClientRect();
    ray.setFromCamera(new Vector2((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1), camera);
    const m = ray.intersectObjects(parts)[0];
    return m && KEYS[m.object.name.split('_')[0]] ? m.object : null;
  };
  stage.addEventListener('pointerdown', (e) => {
    drag = { x: e.clientX, y: e.clientY, ry, rx, moved: 0 };
    stage.setPointerCapture(e.pointerId);
  });
  stage.addEventListener('pointermove', (e) => {
    if (!drag) { stage.style.cursor = parts.length && hit(e) ? 'pointer' : ''; return; }
    drag.moved = Math.max(drag.moved, Math.abs(e.clientX - drag.x) + Math.abs(e.clientY - drag.y));
    ry = drag.ry + (e.clientX - drag.x) * .01;
    rx = Math.max(-.7, Math.min(.7, drag.rx + (e.clientY - drag.y) * .01));
  });
  const drop = (e) => {
    if (!drag) return;
    const tap = drag.moved < 6; drag = null; base = ry;
    wake = performance.now() + 10000; // après un contact, elle reste immobile 10 s
    const b = tap && e.type === 'pointerup' && hit(e);
    if (!b) return;
    o.act(KEYS[b.name.split('_')[0]]);
    if (!o.calm && window.gsap) window.gsap.to(b.position, { y: '-=.08', z: '-=.08', duration: .07, yoyo: true, repeat: 1 });
  };
  stage.addEventListener('pointerup', drop); stage.addEventListener('pointercancel', drop);
};
