// Avatar de la page À propos : modèle model/avatar.glb, tourne sur lui-même, rendu en deux tons dans la couleur d'accent.
// Inclus dans js/psp3d.js (voir README) ; chargé par js/hud.js sur cette page uniquement.
import { AmbientLight, Box3, Color, DirectionalLight, Group, MeshLambertMaterial, PerspectiveCamera, Scene, Vector3, WebGLRenderer } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

// posté après la conversion sRGB : luminance en quatre paliers tramés, contour dans l'accent, lignes de balayage
const TONE = `
  float l = dot(gl_FragColor.rgb, vec3(.299, .587, .114));
  float grain = fract(52.9829189 * fract(dot(floor(gl_FragCoord.xy), vec2(.06711056, .00583715))));
  float rim = pow(1. - abs(dot(normalize(normal), normalize(vViewPosition))), 3.);
  vec3 tone = mix(vec3(.05), uFill, floor(l * 4. + grain) / 4.);
  gl_FragColor.rgb = mix(tone, uFill, step(.5, rim)) * (mod(gl_FragCoord.y, 3.) < 1. ? .78 : 1.);
`;

window.akAvatar = function (box, o) {
  let gl;
  try { gl = new WebGLRenderer({ antialias: false, alpha: true }); } catch (e) { box.hidden = true; return; }
  gl.setPixelRatio(.75); // gros pixels, agrandis nets par le CSS
  const scene = new Scene(), camera = new PerspectiveCamera(20, 1, .1, 50), pivot = new Group();
  const uFill = { value: new Color() };
  const accent = () => uFill.value.set(getComputedStyle(document.documentElement).getPropertyValue('--fill').trim()).convertLinearToSRGB();
  const sun = new DirectionalLight('#fff', 2.6); sun.position.set(2, 3, 4);
  scene.add(new AmbientLight('#fff', 1.1), sun, pivot);
  accent();

  let view = 1, frames = 0, seen = true;
  const fit = () => {
    const w = box.clientWidth, h = box.clientHeight;
    gl.setSize(w, h); camera.aspect = w / h;
    camera.position.z = view / 2 / Math.tan(camera.fov * Math.PI / 360) / Math.min(1, camera.aspect);
    camera.updateProjectionMatrix();
  };
  new ResizeObserver(fit).observe(box); fit();

  new GLTFLoader().load(o.url, (g) => {
    const meshes = [];
    g.scene.traverse((m) => { if (m.isMesh) meshes.push(m); });
    meshes.forEach((m) => {
      if (m.name.startsWith('carryable')) return m.removeFromParent(); // le jouet n'est pas rattaché à la main : il flotte à la taille
      const was = m.material;
      m.material = new MeshLambertMaterial({ map: was.map, color: was.color, vertexColors: !!m.geometry.attributes.color });
      m.material.onBeforeCompile = (s) => {
        s.uniforms.uFill = uFill;
        s.fragmentShader = 'uniform vec3 uFill;\n' + s.fragmentShader.replace('#include <dithering_fragment>', TONE);
      };
    });
    pivot.add(g.scene);
    const size = new Box3().setFromObject(g.scene, true), mid = size.getCenter(new Vector3());
    g.scene.position.sub(mid);
    view = (size.max.y - size.min.y) * 1.08; fit();
    box.appendChild(gl.domElement);
    if (o.calm) { pivot.rotation.y = -.4; return gl.render(scene, camera); }
    gl.setAnimationLoop(frame);
    new IntersectionObserver((e) => { seen = e[0].isIntersecting; }).observe(box);
  }, undefined, () => { box.hidden = true; });

  function frame(ms) {
    if (!gl.domElement.isConnected) { gl.setAnimationLoop(null); gl.dispose(); return; } // navigation douce : la page a changé
    if (!seen) return;
    if (++frames % 40 === 0) accent(); // le thème peut changer
    pivot.rotation.y = ms * .0009;
    gl.render(scene, camera);
  }
};
