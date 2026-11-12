"""Real-Time 3D WebGL (Three.js) Full-Body Articulated Character Stage."""

from __future__ import annotations

import html
import json
import streamlit as st
import streamlit.components.v1 as components


def render_character_stage(
    mood: str = "neutral",
    is_speaking: bool = False,
    turn_id: int = 0,
    operator_name: str = "SHUBH",
    edition: str = "GTA VI",
) -> None:
    """
    Render a 60fps Three.js WebGL full-body articulated 3D character rig
    (GTA VI Cyber-Broker or Avengers: Doomsday Doctor Doom) with three-point
    lighting, soft shadows, mouse-parallax camera tilt, idle breathing/cape sway,
    and 4-second lerped speaking gestures.
    """
    ed_norm = edition.strip().upper()
    if ed_norm in {"PRO", "STANDARD"}:
        return

    doomsday = ed_norm == "DOOMSDAY"
    safe_mood = mood if mood in {"bullish", "bearish", "neutral"} else "neutral"
    safe_name = html.escape(operator_name.upper()[:14])

    if doomsday:
        if safe_mood == "bullish":
            border_color, mood_color, mood_label = "#39ff14", "#39ff14", "🛡️ ARCANUM SURGE"
        elif safe_mood == "bearish":
            border_color, mood_color, mood_label = "#ff4500", "#ff4500", "☢️ DOOM PROTOCOL"
        else:
            border_color, mood_color, mood_label = "#39ff14", "#39ff14", "🛡️ DOOM STANDBY"
        stage_bg = "radial-gradient(circle at 50% 42%, rgba(16, 42, 22, 0.94) 0%, #070907 84%)"
        tag_color = "#39ff14"
        tag_border = "rgba(57, 255, 20, 0.72)"
        hud_tag_text = f"🛡️ DOCTOR DOOM • {safe_name}"
        initial_status = "⚡ CHANNELING INTEL..." if is_speaking else mood_label
    else:
        if safe_mood == "bullish":
            border_color, mood_color, mood_label = "#00f5d4", "#39ff14", "📈 BULLISH STANCE"
        elif safe_mood == "bearish":
            border_color, mood_color, mood_label = "#ff2a85", "#ff4d8d", "🚨 RISK ALERT"
        else:
            border_color, mood_color, mood_label = "#ff2a85", "#00f5d4", "🕶️ STANDBY IDLE"
        stage_bg = "radial-gradient(circle at 50% 42%, rgba(44, 11, 78, 0.92) 0%, #090318 84%)"
        tag_color = "#00f5d4"
        tag_border = "rgba(0, 245, 212, 0.65)"
        hud_tag_text = f"🤖 AI TUTOR • {safe_name}"
        initial_status = "🔊 TRANSMITTING INTEL..." if is_speaking else mood_label

    stage_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Share+Tech+Mono&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: transparent;
    font-family: 'Orbitron', sans-serif;
  }}
  .stage-frame {{
    position: relative;
    width: 100%;
    height: 100%;
    border-radius: 14px;
    border: 2px solid {border_color};
    background: {stage_bg};
    box-shadow: 0 0 18px {border_color}44;
    overflow: hidden;
  }}
  .stage-hud-top {{
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    z-index: 6;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 6px;
    pointer-events: none;
  }}
  .hud-tag {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: {tag_color};
    background: rgba(7, 3, 18, 0.88);
    border: 1px solid {tag_border};
    padding: 4px 8px;
    border-radius: 6px;
  }}
  .hud-status {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: {mood_color};
    background: rgba(7, 3, 18, 0.88);
    border: 1px solid {mood_color};
    padding: 4px 8px;
    border-radius: 6px;
  }}
  .stage-hud-bottom {{
    position: absolute;
    bottom: 8px;
    left: 10px;
    right: 10px;
    z-index: 6;
    display: flex;
    justify-content: space-between;
    pointer-events: none;
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: rgba(203, 213, 225, 0.78);
  }}
  #webglCanvas {{
    display: block;
    width: 100%;
    height: 100%;
    cursor: grab;
  }}
  #fallbackHud {{
    display: none;
    position: absolute;
    inset: 0;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    color: {tag_color};
    font-family: 'Share Tech Mono', monospace;
    text-align: center;
    padding: 1rem;
  }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
  <div id="stageRoot" class="stage-frame" data-turn="{turn_id}">
    <div class="stage-hud-top">
      <div class="hud-tag">{hud_tag_text}</div>
      <div id="hudStatusPill" class="hud-status">{initial_status}</div>
    </div>
    <canvas id="webglCanvas"></canvas>
    <div id="fallbackHud">
      <div>⚡ 3D WEBGL AVATAR ONLINE</div>
      <div style="font-size:11px; margin-top:6px; color:#cbd5e1;">Mode: {html.escape(ed_norm)} · Mood: {html.escape(safe_mood.upper())}</div>
    </div>
    <div class="stage-hud-bottom">
      <span>WEBGL 3D RIG // 60FPS</span>
      <span>{'DR. DOOM // LATVERIA NODE' if doomsday else 'LEONIDA // CYBER-BROKER'}</span>
    </div>
  </div>

  <script>
    (function() {{
      const IS_DOOMSDAY = {json.dumps(doomsday)};
      const MOOD = {json.dumps(safe_mood)};
      const IS_SPEAKING = {json.dumps(bool(is_speaking))};
      const IDLE_LABEL = {json.dumps(mood_label)};
      const canvas = document.getElementById("webglCanvas");
      const rootEl = document.getElementById("stageRoot");
      const statusPill = document.getElementById("hudStatusPill");
      const fallbackHud = document.getElementById("fallbackHud");

      if (typeof THREE === "undefined" || !canvas) {{
        if (fallbackHud) fallbackHud.style.display = "flex";
        return;
      }}

      let renderer;
      try {{
        renderer = new THREE.WebGLRenderer({{
          canvas: canvas,
          antialias: true,
          alpha: true,
          powerPreference: "high-performance"
        }});
      }} catch (err) {{
        if (fallbackHud) fallbackHud.style.display = "flex";
        return;
      }}

      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.outputEncoding = THREE.sRGBEncoding;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(34, rootEl.clientWidth / Math.max(1, rootEl.clientHeight), 0.1, 60);
      camera.position.set(0, 2.05, 5.45);
      camera.lookAt(0, 1.72, 0);

      function resize() {{
        const w = rootEl.clientWidth || 360;
        const h = rootEl.clientHeight || 545;
        renderer.setSize(w, h, false);
        camera.aspect = w / Math.max(1, h);
        camera.updateProjectionMatrix();
      }}
      resize();
      window.addEventListener("resize", resize);

      // Three-Point Lighting + Shadows
      const hemiLight = new THREE.HemisphereLight(
        IS_DOOMSDAY ? 0x6ee7b7 : 0x7dd3fc,
        IS_DOOMSDAY ? 0x1a0c06 : 0x1e0938,
        0.72
      );
      scene.add(hemiLight);

      const keyLight = new THREE.DirectionalLight(0xffffff, 1.15);
      keyLight.position.set(2.8, 5.4, 3.6);
      keyLight.castShadow = true;
      keyLight.shadow.mapSize.set(1024, 1024);
      keyLight.shadow.camera.near = 0.5;
      keyLight.shadow.camera.far = 16;
      scene.add(keyLight);

      const rimLeft = new THREE.PointLight(IS_DOOMSDAY ? 0x39ff14 : 0x00f5d4, 2.4, 12);
      rimLeft.position.set(-2.5, 2.8, -1.6);
      scene.add(rimLeft);

      const rimRight = new THREE.PointLight(IS_DOOMSDAY ? 0xff4500 : 0xff2a85, 2.1, 12);
      rimRight.position.set(2.5, 2.4, -1.5);
      scene.add(rimRight);

      // Floor Shadow Catcher & Neon Grid
      const floorGeo = new THREE.CircleGeometry(3.2, 48);
      const floorMat = new THREE.MeshStandardMaterial({{
        color: IS_DOOMSDAY ? 0x0b110b : 0x0b0520,
        metalness: 0.72,
        roughness: 0.32
      }});
      const floorMesh = new THREE.Mesh(floorGeo, floorMat);
      floorMesh.rotation.x = -Math.PI / 2;
      floorMesh.receiveShadow = true;
      scene.add(floorMesh);

      const gridColor1 = IS_DOOMSDAY ? 0x39ff14 : 0x00f5d4;
      const gridColor2 = IS_DOOMSDAY ? 0x166534 : 0xff2a85;
      const gridHelper = new THREE.GridHelper(6.0, 18, gridColor1, gridColor2);
      gridHelper.position.y = 0.01;
      gridHelper.material.opacity = 0.72;
      gridHelper.material.transparent = true;
      scene.add(gridHelper);

      const ringGeo = new THREE.RingGeometry(0.95, 1.04, 48);
      const ringMat = new THREE.MeshBasicMaterial({{
        color: IS_DOOMSDAY ? 0x39ff14 : (MOOD === "bearish" ? 0xff2a85 : 0x00f5d4),
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.85
      }});
      const holoRing = new THREE.Mesh(ringGeo, ringMat);
      holoRing.rotation.x = -Math.PI / 2;
      holoRing.position.y = 0.015;
      scene.add(holoRing);

      // Articulated Character Rig (THREE.Group Hierarchy)
      const rootGroup = new THREE.Group();
      scene.add(rootGroup);

      const pelvis = new THREE.Group();
      pelvis.position.set(0, 1.48, 0);
      rootGroup.add(pelvis);

      const torso = new THREE.Group();
      torso.position.set(0, 0.14, 0);
      pelvis.add(torso);

      const chest = new THREE.Group();
      chest.position.set(0, 0.42, 0);
      torso.add(chest);

      const headGroup = new THREE.Group();
      headGroup.position.set(0, 0.50, 0);
      chest.add(headGroup);

      const shoulderL = new THREE.Group();
      shoulderL.position.set(-0.46, 0.34, 0);
      chest.add(shoulderL);
      const upperArmL = new THREE.Group();
      shoulderL.add(upperArmL);
      const forearmL = new THREE.Group();
      forearmL.position.set(0, -0.44, 0);
      upperArmL.add(forearmL);
      const handL = new THREE.Group();
      handL.position.set(0, -0.38, 0);
      forearmL.add(handL);

      const shoulderR = new THREE.Group();
      shoulderR.position.set(0.46, 0.34, 0);
      chest.add(shoulderR);
      const upperArmR = new THREE.Group();
      shoulderR.add(upperArmR);
      const forearmR = new THREE.Group();
      forearmR.position.set(0, -0.44, 0);
      upperArmR.add(forearmR);
      const handR = new THREE.Group();
      handR.position.set(0, -0.38, 0);
      forearmR.add(handR);

      const thighL = new THREE.Group();
      thighL.position.set(-0.18, -0.06, 0);
      pelvis.add(thighL);
      const shinL = new THREE.Group();
      shinL.position.set(0, -0.64, 0);
      thighL.add(shinL);
      const footL = new THREE.Group();
      footL.position.set(0, -0.66, 0.04);
      shinL.add(footL);

      const thighR = new THREE.Group();
      thighR.position.set(0.18, -0.06, 0);
      pelvis.add(thighR);
      const shinR = new THREE.Group();
      shinR.position.set(0, -0.64, 0);
      thighR.add(shinR);
      const footR = new THREE.Group();
      footR.position.set(0, -0.66, 0.04);
      shinR.add(footR);

      function addShadow(mesh) {{
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        return mesh;
      }}

      let capeSegs = [];
      let pulseTargets = [];
      let palmEnergyLight = null;
      let mistPoints = null;

      if (IS_DOOMSDAY) {{
        // ===== AVENGERS: DOOMSDAY 3D DOCTOR DOOM RIG =====
        const steelMat = new THREE.MeshPhysicalMaterial({{
          color: 0x8d99ae,
          metalness: 0.92,
          roughness: 0.24,
          clearcoat: 0.55
        }});
        const darkArmorMat = new THREE.MeshStandardMaterial({{
          color: 0x2b3036,
          metalness: 0.85,
          roughness: 0.35
        }});
        const emeraldFabricMat = new THREE.MeshStandardMaterial({{
          color: 0x0b4222,
          metalness: 0.15,
          roughness: 0.78,
          side: THREE.DoubleSide
        }});
        const eyeGlowMat = new THREE.MeshStandardMaterial({{
          color: 0x39ff14,
          emissive: 0x39ff14,
          emissiveIntensity: 2.2
        }});
        const arcaneOrbMat = new THREE.MeshPhysicalMaterial({{
          color: 0x39ff14,
          emissive: 0x39ff14,
          emissiveIntensity: 1.9,
          transparent: true,
          opacity: 0.9
        }});
        pulseTargets.push(eyeGlowMat, arcaneOrbMat);

        // Pelvis + Armored Belt + Tassets
        pelvis.add(addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.56, 0.24, 0.34), darkArmorMat)));
        const belt = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.60, 0.10, 0.37), steelMat));
        belt.position.y = 0.06;
        pelvis.add(belt);
        const claspBelt = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.06, 16), steelMat));
        claspBelt.rotation.x = Math.PI / 2;
        claspBelt.position.set(0, 0.06, 0.19);
        pelvis.add(claspBelt);

        // Torso & Chest Armor + Clasps
        const abdomen = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.25, 0.44, 16), emeraldFabricMat));
        abdomen.position.y = 0.20;
        torso.add(abdomen);
        const chestPlate = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.29, 0.50, 16), darkArmorMat));
        chestPlate.scale.set(1.12, 1, 0.78);
        chestPlate.position.y = 0.18;
        chest.add(chestPlate);
        const tunicTabard = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.75, 0.05), emeraldFabricMat));
        tunicTabard.position.set(0, -0.32, 0.17);
        pelvis.add(tunicTabard);

        // Shoulder Pauldrons & Twin Circular Chest Clasps
        [-0.30, 0.30].forEach(function(px) {{
          const clasp = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.065, 0.05, 18), steelMat));
          clasp.rotation.x = Math.PI / 2;
          clasp.position.set(px, 0.32, 0.25);
          chest.add(clasp);
        }});
        const chainArc = new THREE.Mesh(new THREE.TorusGeometry(0.29, 0.022, 10, 24, Math.PI), steelMat);
        chainArc.rotation.z = Math.PI;
        chainArc.position.set(0, 0.34, 0.26);
        chest.add(chainArc);

        // Articulated Multi-Segment Flowing Cape
        const capePivot1 = new THREE.Group();
        capePivot1.position.set(0, 0.44, -0.22);
        chest.add(capePivot1);
        const c1 = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.84, 0.56, 0.04), emeraldFabricMat));
        c1.position.y = -0.26;
        capePivot1.add(c1);

        const capePivot2 = new THREE.Group();
        capePivot2.position.set(0, -0.54, 0);
        capePivot1.add(capePivot2);
        const c2 = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.96, 0.62, 0.04), emeraldFabricMat));
        c2.position.y = -0.30;
        capePivot2.add(c2);

        const capePivot3 = new THREE.Group();
        capePivot3.position.set(0, -0.60, 0);
        capePivot2.add(capePivot3);
        const c3 = addShadow(new THREE.Mesh(new THREE.BoxGeometry(1.10, 0.66, 0.04), emeraldFabricMat));
        c3.position.y = -0.32;
        capePivot3.add(c3);
        capeSegs = [capePivot1, capePivot2, capePivot3];

        // Neck + Sculpted Iron Faceplate + Emerald Hood + Glowing Eyes
        const neck = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.10, 0.12, 0.16, 14), darkArmorMat));
        neck.position.y = -0.02;
        headGroup.add(neck);

        const maskSkull = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.145, 0.34, 18), steelMat));
        maskSkull.scale.set(0.92, 1, 1.05);
        maskSkull.position.y = 0.22;
        headGroup.add(maskSkull);
        const browPlate = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.07, 0.20), steelMat));
        browPlate.position.set(0, 0.29, 0.09);
        headGroup.add(browPlate);
        const jawGuard = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.20, 0.11, 0.15), darkArmorMat));
        jawGuard.position.set(0, 0.12, 0.12);
        headGroup.add(jawGuard);

        [-0.062, 0.062].forEach(function(ex) {{
          const eye = new THREE.Mesh(new THREE.BoxGeometry(0.058, 0.024, 0.03), eyeGlowMat);
          eye.position.set(ex, 0.24, 0.175);
          headGroup.add(eye);
        }});

        const hoodDome = addShadow(new THREE.Mesh(new THREE.SphereGeometry(0.25, 22, 18, 0, Math.PI * 2, 0, Math.PI * 0.72), emeraldFabricMat));
        hoodDome.position.set(0, 0.26, -0.02);
        hoodDome.rotation.x = -0.22;
        headGroup.add(hoodDome);
        const hoodDrape = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.23, 0.28, 0.34, 20, 1, true, Math.PI * 0.35, Math.PI * 1.3), emeraldFabricMat));
        hoodDrape.position.set(0, 0.17, -0.03);
        headGroup.add(hoodDrape);

        // Heavy Shoulder Pauldrons, Upper Arms, Metallic Gauntlets & Arcane Palm Orb
        [
          {{ s: shoulderL, u: upperArmL, f: forearmL, h: handL, dir: -1 }},
          {{ s: shoulderR, u: upperArmR, f: forearmR, h: handR, dir: 1 }}
        ].forEach(function(arm) {{
          const pauldron = addShadow(new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.6), steelMat));
          pauldron.rotation.z = arm.dir * -0.45;
          pauldron.position.y = 0.03;
          arm.s.add(pauldron);

          const upMesh = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.10, 0.09, 0.42, 14), darkArmorMat));
          upMesh.position.y = -0.22;
          arm.u.add(upMesh);

          const gauntlet = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.105, 0.085, 0.38, 14), steelMat));
          gauntlet.position.y = -0.19;
          arm.f.add(gauntlet);

          const fist = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.14, 0.13), steelMat));
          fist.position.y = -0.06;
          arm.h.add(fist);
        }});

        const arcaneOrb = new THREE.Mesh(new THREE.SphereGeometry(0.085, 18, 18), arcaneOrbMat);
        arcaneOrb.position.set(0, -0.15, 0.06);
        handR.add(arcaneOrb);
        palmEnergyLight = new THREE.PointLight(0x39ff14, 1.4, 3.2);
        palmEnergyLight.position.set(0, -0.15, 0.10);
        handR.add(palmEnergyLight);

        // Legs, Steel Greaves & Armored Boots
        [
          {{ t: thighL, s: shinL, f: footL }},
          {{ t: thighR, s: shinR, f: footR }}
        ].forEach(function(leg) {{
          const thighMesh = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.115, 0.60, 14), darkArmorMat));
          thighMesh.position.y = -0.32;
          leg.t.add(thighMesh);

          const kneeCap = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.14, 0.16), steelMat));
          kneeCap.position.set(0, -0.62, 0.04);
          leg.t.add(kneeCap);

          const greave = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.095, 0.62, 14), steelMat));
          greave.position.y = -0.33;
          leg.s.add(greave);

          const boot = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.19, 0.16, 0.34), darkArmorMat));
          boot.position.set(0, -0.08, 0.06);
          leg.f.add(boot);
          const sole = new THREE.Mesh(new THREE.BoxGeometry(0.20, 0.035, 0.36), eyeGlowMat);
          sole.position.set(0, -0.15, 0.06);
          leg.f.add(sole);
        }});

        // Floating 3D Emerald Mist Particles
        const pCount = 90;
        const pPos = new Float32Array(pCount * 3);
        for (let i = 0; i < pCount; i++) {{
          pPos[i * 3] = (Math.random() - 0.5) * 4.2;
          pPos[i * 3 + 1] = Math.random() * 3.4 + 0.1;
          pPos[i * 3 + 2] = (Math.random() - 0.5) * 3.2;
        }}
        const pGeo = new THREE.BufferGeometry();
        pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
        const pMat = new THREE.PointsMaterial({{
          color: 0x39ff14,
          size: 0.055,
          transparent: true,
          opacity: 0.72
        }});
        mistPoints = new THREE.Points(pGeo, pMat);
        scene.add(mistPoints);
      }} else {{
        // ===== GTA VI (VICE CITY) 3D CYBER-BROKER RIG =====
        const jacketMat = new THREE.MeshPhysicalMaterial({{
          color: 0x22104f,
          metalness: 0.28,
          roughness: 0.42,
          clearcoat: 0.35
        }});
        const teeMat = new THREE.MeshStandardMaterial({{
          color: 0x090517,
          roughness: 0.82
        }});
        const skinMat = new THREE.MeshStandardMaterial({{
          color: 0xd99b72,
          roughness: 0.55
        }});
        const hairMat = new THREE.MeshStandardMaterial({{
          color: 0x110b29,
          roughness: 0.48
        }});
        const slacksMat = new THREE.MeshStandardMaterial({{
          color: 0x14172b,
          roughness: 0.62
        }});
        const goldMat = new THREE.MeshPhysicalMaterial({{
          color: 0xfee440,
          metalness: 0.94,
          roughness: 0.16,
          emissive: 0x664400,
          emissiveIntensity: 0.25
        }});
        const cyanGlowMat = new THREE.MeshStandardMaterial({{
          color: 0x00f5d4,
          emissive: 0x00f5d4,
          emissiveIntensity: 1.7
        }});
        const pinkGlowMat = new THREE.MeshStandardMaterial({{
          color: 0xff2a85,
          emissive: 0xff2a85,
          emissiveIntensity: 1.7
        }});
        const shadeLensMat = new THREE.MeshPhysicalMaterial({{
          color: 0x00f5d4,
          emissive: MOOD === "bearish" ? 0xff2a85 : 0x00f5d4,
          emissiveIntensity: 1.35,
          metalness: 0.85,
          roughness: 0.1,
          clearcoat: 1.0
        }});
        pulseTargets.push(shadeLensMat, cyanGlowMat, pinkGlowMat);

        // Pelvis & Belt
        pelvis.add(addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.52, 0.20, 0.30), slacksMat)));
        const vBelt = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.54, 0.06, 0.32), teeMat));
        vBelt.position.y = 0.07;
        pelvis.add(vBelt);
        const vBuckle = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.07, 0.04), goldMat);
        vBuckle.position.set(0, 0.07, 0.17);
        pelvis.add(vBuckle);

        // Inner Black Tee + Open 3D Neon Blazer Panels + Gold Chain
        const teeCore = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.27, 0.24, 0.90, 16), teeMat));
        teeCore.position.y = 0.14;
        torso.add(teeCore);

        [-0.17, 0.17].forEach(function(jx, idx) {{
          const panel = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.88, 0.33), jacketMat));
          panel.position.set(jx, 0.02, 0.0);
          chest.add(panel);
          const lapel = new THREE.Mesh(
            new THREE.BoxGeometry(0.035, 0.56, 0.04),
            idx === 0 ? cyanGlowMat : pinkGlowMat
          );
          lapel.position.set(jx + (idx === 0 ? 0.09 : -0.09), 0.12, 0.175);
          lapel.rotation.z = idx === 0 ? -0.14 : 0.14;
          chest.add(lapel);
        }});
        const jacketBack = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.56, 0.88, 0.14), jacketMat));
        jacketBack.position.set(0, 0.02, -0.11);
        chest.add(jacketBack);

        const goldChain = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.016, 10, 24, Math.PI * 1.15), goldMat);
        goldChain.rotation.z = Math.PI * 0.92;
        goldChain.position.set(0, 0.39, 0.17);
        chest.add(goldChain);

        // Head, Sculpted Vice Hair, Holographic Aviator Shades
        const neck = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.095, 0.16, 14), skinMat));
        headGroup.add(neck);
        const headMesh = addShadow(new THREE.Mesh(new THREE.SphereGeometry(0.175, 22, 18), skinMat));
        headMesh.scale.set(0.92, 1.12, 0.98);
        headMesh.position.y = 0.21;
        headGroup.add(headMesh);

        const hairTop = addShadow(new THREE.Mesh(new THREE.SphereGeometry(0.185, 18, 16, 0, Math.PI * 2, 0, Math.PI * 0.58), hairMat));
        hairTop.scale.set(0.95, 1.05, 1.05);
        hairTop.position.set(0, 0.25, -0.02);
        hairTop.rotation.x = -0.18;
        headGroup.add(hairTop);
        const hairSweep = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.08, 0.14), hairMat));
        hairSweep.position.set(0.02, 0.37, 0.07);
        hairSweep.rotation.z = -0.12;
        headGroup.add(hairSweep);

        [-0.068, 0.068].forEach(function(gx) {{
          const lens = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.065, 0.03), shadeLensMat);
          lens.position.set(gx, 0.23, 0.165);
          headGroup.add(lens);
        }});
        const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.018, 0.025), goldMat);
        bridge.position.set(0, 0.24, 0.17);
        headGroup.add(bridge);

        // Arms & Neon High-Tops
        [
          {{ s: shoulderL, u: upperArmL, f: forearmL, h: handL, mat: cyanGlowMat }},
          {{ s: shoulderR, u: upperArmR, f: forearmR, h: handR, mat: pinkGlowMat }}
        ].forEach(function(arm) {{
          const cap = addShadow(new THREE.Mesh(new THREE.SphereGeometry(0.11, 14, 12), jacketMat));
          arm.s.add(cap);
          const upMesh = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.08, 0.42, 14), jacketMat));
          upMesh.position.y = -0.22;
          arm.u.add(upMesh);
          const foreMesh = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.082, 0.07, 0.36, 14), jacketMat));
          foreMesh.position.y = -0.18;
          arm.f.add(foreMesh);
          const cuff = new THREE.Mesh(new THREE.CylinderGeometry(0.076, 0.076, 0.045, 14), arm.mat);
          cuff.position.y = -0.35;
          arm.f.add(cuff);
          const handMesh = addShadow(new THREE.Mesh(new THREE.SphereGeometry(0.068, 12, 12), skinMat));
          handMesh.position.y = -0.05;
          arm.h.add(handMesh);
        }});

        [
          {{ t: thighL, s: shinL, f: footL, glow: cyanGlowMat }},
          {{ t: thighR, s: shinR, f: footR, glow: pinkGlowMat }}
        ].forEach(function(leg) {{
          const thighMesh = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.125, 0.105, 0.62, 14), slacksMat));
          thighMesh.position.y = -0.32;
          leg.t.add(thighMesh);
          const shinMesh = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.105, 0.088, 0.62, 14), slacksMat));
          shinMesh.position.y = -0.33;
          leg.s.add(shinMesh);
          const sneaker = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.15, 0.32), jacketMat));
          sneaker.position.set(0, -0.075, 0.06);
          leg.f.add(sneaker);
          const sole = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.036, 0.34), leg.glow);
          sole.position.set(0, -0.145, 0.06);
          leg.f.add(sole);
        }});
      }}

      // Initial Stance
      shoulderL.rotation.z = -0.12;
      shoulderR.rotation.z = 0.14;
      thighL.rotation.z = -0.04;
      thighR.rotation.z = 0.04;

      // Subtle Mouse Parallax
      let pointerX = 0;
      let pointerY = 0;
      window.addEventListener("pointermove", function(e) {{
        const rect = rootEl.getBoundingClientRect();
        pointerX = ((e.clientX - rect.left) / Math.max(1, rect.width) - 0.5) * 2;
        pointerY = ((e.clientY - rect.top) / Math.max(1, rect.height) - 0.5) * 2;
      }});

      const speakStart = performance.now();
      let speakingActive = IS_SPEAKING;
      const clock = new THREE.Clock();

      function animate() {{
        requestAnimationFrame(animate);
        const t = clock.getElapsedTime();

        if (speakingActive && performance.now() - speakStart > 4000) {{
          speakingActive = false;
          if (statusPill) statusPill.textContent = IDLE_LABEL;
        }}

        // Smooth 60fps Idle Breathing & Weight Shift
        const breathe = Math.sin(t * 2.1);
        const shift = Math.sin(t * 1.15);
        pelvis.position.y = 1.48 + breathe * 0.015;
        pelvis.position.x = shift * 0.025;
        chest.rotation.x = breathe * 0.022;
        rootGroup.rotation.y = THREE.MathUtils.lerp(
          rootGroup.rotation.y,
          pointerX * 0.22 + Math.sin(t * 0.7) * 0.05,
          0.06
        );

        // Expressive 4-Second Speaking Blend via THREE.MathUtils.lerp
        const targetArmRX = speakingActive ? (-0.95 + Math.sin(t * 6.0) * 0.18) : (-0.08 + Math.sin(t * 1.4) * 0.04);
        const targetArmRZ = speakingActive ? (0.35 + Math.cos(t * 4.5) * 0.08) : (0.14);
        const targetForeRX = speakingActive ? (-0.75 + Math.sin(t * 6.0 + 0.8) * 0.22) : (-0.18);
        const targetHeadX = speakingActive ? (0.04 + Math.sin(t * 5.2) * 0.08) : (breathe * 0.025);
        const targetHeadY = speakingActive ? (0.18 + Math.sin(t * 2.8) * 0.08) : (pointerX * 0.12);

        shoulderR.rotation.x = THREE.MathUtils.lerp(shoulderR.rotation.x, targetArmRX, 0.10);
        shoulderR.rotation.z = THREE.MathUtils.lerp(shoulderR.rotation.z, targetArmRZ, 0.10);
        forearmR.rotation.x = THREE.MathUtils.lerp(forearmR.rotation.x, targetForeRX, 0.12);
        shoulderL.rotation.x = THREE.MathUtils.lerp(shoulderL.rotation.x, -0.05 - breathe * 0.03, 0.08);
        forearmL.rotation.x = THREE.MathUtils.lerp(forearmL.rotation.x, -0.14, 0.08);

        headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, targetHeadX, 0.10);
        headGroup.rotation.y = THREE.MathUtils.lerp(headGroup.rotation.y, targetHeadY, 0.10);

        // Animated Multi-Segment Cape Sway (Doomsday Doctor Doom)
        if (capeSegs.length === 3) {{
          const waveBoost = speakingActive ? 1.7 : 1.0;
          capeSegs[0].rotation.x = 0.08 + Math.sin(t * 1.8) * 0.04 * waveBoost;
          capeSegs[1].rotation.x = 0.06 + Math.sin(t * 1.8 - 0.7) * 0.07 * waveBoost;
          capeSegs[2].rotation.x = 0.05 + Math.sin(t * 1.8 - 1.4) * 0.10 * waveBoost;
        }}

        // Pulsing Visor / Arcane Energy Glow & Particle Drift
        const glowTarget = speakingActive ? (2.2 + Math.sin(t * 8.0) * 0.65) : (1.35 + Math.sin(t * 2.4) * 0.25);
        for (let i = 0; i < pulseTargets.length; i++) {{
          pulseTargets[i].emissiveIntensity = THREE.MathUtils.lerp(pulseTargets[i].emissiveIntensity, glowTarget, 0.12);
        }}
        if (palmEnergyLight) {{
          palmEnergyLight.intensity = THREE.MathUtils.lerp(
            palmEnergyLight.intensity,
            speakingActive ? 2.8 : 1.25,
            0.12
          );
        }}
        if (mistPoints) {{
          mistPoints.rotation.y = t * 0.16;
          mistPoints.position.y = Math.sin(t * 1.1) * 0.08;
        }}

        // Mouse Parallax Camera Tilt
        camera.position.x = THREE.MathUtils.lerp(camera.position.x, pointerX * 0.35, 0.05);
        camera.position.y = THREE.MathUtils.lerp(camera.position.y, 2.05 - pointerY * 0.18, 0.05);
        camera.lookAt(0, 1.72, 0);

        renderer.render(scene, camera);
      }}

      animate();
    }})();
  </script>
</body>
</html>
"""
    if hasattr(st, "iframe"):
        st.iframe(stage_html, width="stretch", height=560)
    else:
        components.html(stage_html, height=560, scrolling=False)
