// Avatar de l'accueil et de la page À propos : modèle model/avatar.glb, tourne sur lui-même, rendu en caractères ASCII dans la couleur d'accent.
// Inclus dans js/psp3d.js (voir README) ; chargé par js/hud.js sur ces pages uniquement.
import { AmbientLight, Box3, DirectionalLight, Group, MeshLambertMaterial, PerspectiveCamera, Scene, Vector3, WebGLRenderer, WebGLRenderTarget } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const CHARS = '.,:;-~=+*oxX%#&@';
const CELL_W = 2.4, CELL_H = 4; // taille d'un caractère : voir .avatar-box pre

window.akAvatar = function (box, o) {
  let gl;
  try { gl = new WebGLRenderer({ antialias: false, alpha: true }); } catch (e) { box.hidden = true; return; }
  const scene = new Scene(), camera = new PerspectiveCamera(20, 1, .1, 50), pivot = new Group();
  const target = new WebGLRenderTarget(1, 1), pre = document.createElement('pre');
  const sun = new DirectionalLight('#fff', 2.6); sun.position.set(2, 3, 4);
  scene.add(new AmbientLight('#fff', 1.1), sun, pivot);

  let view = 1, frames = 0, seen = true, cols = 1, rows = 1, pixels;
  const fit = () => {
    const w = box.clientWidth, h = box.clientHeight;
    if (!w || !h) return; // box masquée par le CSS
    cols = Math.ceil(w / CELL_W); rows = Math.ceil(h / CELL_H);
    target.setSize(cols, rows); pixels = new Uint8Array(cols * rows * 4);
    camera.aspect = w / h;
    camera.position.z = view / 2 / Math.tan(camera.fov * Math.PI / 360) / Math.min(1, camera.aspect);
    camera.updateProjectionMatrix();
    frames = 0;
  };
  new ResizeObserver(fit).observe(box); fit();

  new GLTFLoader().load(o.url, (g) => {
    const meshes = [];
    g.scene.traverse((m) => { if (m.isMesh) meshes.push(m); });
    meshes.forEach((m) => {
      if (m.name.startsWith('carryable')) return m.removeFromParent(); // le jouet n'est pas rattaché à la main : il flotte à la taille
      const was = m.material;
      m.material = new MeshLambertMaterial({ map: was.map, color: was.color, vertexColors: !!m.geometry.attributes.color });
    });
    pivot.add(g.scene);
    const size = new Box3().setFromObject(g.scene, true), mid = size.getCenter(new Vector3());
    g.scene.position.sub(mid);
    view = (size.max.y - size.min.y) * 1.08; fit();
    box.appendChild(pre);
    gl.setRenderTarget(target);
    gl.setAnimationLoop(frame);
    new IntersectionObserver((e) => { seen = e[0].isIntersecting; }).observe(box);
  }, undefined, () => { box.hidden = true; });

  function frame(ms) {
    if (!pre.isConnected) { gl.setAnimationLoop(null); target.dispose(); gl.dispose(); return; } // navigation douce : la page a changé
    if (!seen || box.closest('.slide:not(.on)')) return; // hors écran ou diapo du carrousel masquée
    if (o.calm && frames) return; // image fixe
    frames++;
    pivot.rotation.y = o.calm ? -.4 : ms * .0009;
    gl.render(scene, camera);
    gl.readRenderTargetPixels(target, 0, 0, cols, rows, pixels);
    const light = (i) => Math.sqrt((pixels[i] * .299 + pixels[i + 1] * .587 + pixels[i + 2] * .114) / 255); // la cible de rendu reste en valeurs linéaires
    let low = 1, high = 0, text = '';
    for (let i = 0; i < pixels.length; i += 4) {
      if (pixels[i + 3] < 128) continue;
      const l = light(i); low = Math.min(low, l); high = Math.max(high, l);
    }
    for (let y = rows - 1; y >= 0; y--) { // WebGL lit de bas en haut
      for (let x = 0; x < cols; x++) {
        const i = (y * cols + x) * 4;
        // étalé sur toute la rampe, sinon le personnage n'utilise que quelques caractères
        text += pixels[i + 3] < 128 ? ' ' : CHARS[Math.min(CHARS.length - 1, Math.floor((light(i) - low) / (high - low || 1) * CHARS.length))];
      }
      text += '\n';
    }
    pre.textContent = text;
  }
};
