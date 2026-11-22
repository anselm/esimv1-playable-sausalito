// A sheet of moving water for a three.js scene. What is measured comes in from outside: the level
// (set the mesh's y), the wind's speed and where it blows from, the sun. What is decoration is the
// motion: four trains of sine waves whose height and direction follow the wind, with no fetch, no
// depth, no current and no swell. It is not a wave model and should not be read as sea state.
//
//   const water = makeWater(THREE, { width, depth })
//   water.set({ level_m, wind_ms, wind_from_deg, sunDir, sunColor, sky, color, calm })
//   water.tick(seconds)      // each frame

export function makeWater(THREE, { width, depth }) {
  const uniforms = THREE.UniformsUtils.merge([THREE.UniformsLib.fog, {
    uTime: { value: 0 }, uWind: { value: new THREE.Vector2(1, 0) }, uSteep: { value: 0.05 },
    uSun: { value: new THREE.Vector3(0, 1, 0) }, uSunColor: { value: new THREE.Color(1, 1, 1) },
    uSky: { value: new THREE.Color(0.6, 0.75, 0.9) }, uColor: { value: new THREE.Color(0.1, 0.3, 0.4) }, uCalm: { value: 0 },
  }])
  const mat = new THREE.ShaderMaterial({
    uniforms, fog: true,
    vertexShader: `
      varying vec3 vWorld;
      #include <fog_pars_vertex>
      void main() { vec4 w = modelMatrix * vec4(position, 1.0); vWorld = w.xyz; vec4 mvPosition = viewMatrix * w; gl_Position = projectionMatrix * mvPosition;
        #include <fog_vertex>
      }`,
    fragmentShader: `
      uniform float uTime, uSteep, uCalm; uniform vec2 uWind; uniform vec3 uSun, uSunColor, uSky, uColor;
      varying vec3 vWorld;
      #include <fog_pars_fragment>
      // one train: slope of a sine wave of length L travelling along d at the deep-water speed
      vec2 train(vec2 p, vec2 d, float L, float steep) { float k = 6.2831853 / L, c = sqrt(9.81 / k); return d * steep * cos(k * (dot(d, p) - c * uTime)); }
      vec2 rot(vec2 v, float a) { float s = sin(a), c = cos(a); return vec2(c * v.x - s * v.y, s * v.x + c * v.y); }
      void main() {
        vec2 p = vWorld.xz; float d = distance(cameraPosition, vWorld), near = 1.0 - clamp(d / 1800.0, 0.0, 1.0), mid = 1.0 - clamp(d / 6000.0, 0.0, 0.75);
        // patches of rougher and smoother water, so the trains do not read as ruled lines
        float gust = 0.65 + 0.35 * sin(p.x * 0.0071 + 1.3 * sin(p.y * 0.0043 + uTime * 0.05)) * sin(p.y * 0.0063 - uTime * 0.03);
        vec2 s = (train(p, uWind, 41.0, uSteep * 0.7) + train(p, rot(uWind, 0.37), 23.3, uSteep * 0.7) + train(p, rot(uWind, -0.52), 13.1, uSteep * 0.8)) * mid
               + (train(p, rot(uWind, 0.93), 7.7, uSteep) + train(p, rot(uWind, -1.21), 4.3, uSteep * 0.9) + train(p, rot(uWind, 1.9), 2.3, uSteep * 0.6)) * near;
        s *= gust;
        vec3 n = normalize(vec3(-s.x, 1.0, -s.y));
        vec3 v = normalize(cameraPosition - vWorld);
        float fres = 0.03 + 0.97 * pow(1.0 - max(dot(n, v), 0.0), 5.0);
        vec3 h = normalize(v + uSun);
        float glint = pow(max(dot(n, h), 0.0), 220.0) * step(0.0, uSun.y);
        vec3 col = mix(uColor, uSky, fres * (1.0 - uCalm)) * (0.55 + 0.45 * max(dot(n, uSun), 0.0)) + uSunColor * glint * (1.0 - uCalm) * 1.6;
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
        #include <fog_fragment>
      }`,
  })
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, depth).rotateX(-Math.PI / 2), mat)
  mesh.set = (o) => {
    if (o.level_m != null) mesh.position.y = o.level_m
    if (o.wind_from_deg != null) { const a = o.wind_from_deg * Math.PI / 180; uniforms.uWind.value.set(-Math.sin(a), Math.cos(a)) }   // x east, z south
    if (o.wind_ms != null) uniforms.uSteep.value = Math.min(0.22, 0.012 + 0.013 * o.wind_ms)
    if (o.sunDir) uniforms.uSun.value.copy(o.sunDir).normalize()
    if (o.sunColor) uniforms.uSunColor.value.copy(o.sunColor)
    if (o.sky) uniforms.uSky.value.copy(o.sky)
    if (o.color) uniforms.uColor.value.copy(o.color)
    if (o.calm != null) uniforms.uCalm.value = o.calm
  }
  mesh.tick = (t) => { uniforms.uTime.value = t }
  return mesh
}
