document.addEventListener("DOMContentLoaded",()=>{
  "use strict";
  const SK="hf_settings";
  const load=()=>{try{return JSON.parse(localStorage.getItem(SK))||{}}catch(_){return{}}};
  const save=o=>localStorage.setItem(SK,JSON.stringify(o));
  const form=document.getElementById("settings-form");
  if(form){
    const s=load();
    ["gemini_key","pexels_key","pixabay_key","yt_client_id","yt_client_secret","yt_refresh_token","github_pat","github_repo"].forEach(id=>{
      const inp=document.getElementById(id);if(inp&&s[id])inp.value=s[id];});
    form.addEventListener("submit",e=>{e.preventDefault();const d={};
      new FormData(form).forEach((v,k)=>d[k]=v);save(d);toast("Settings saved ✓");});}
  const rBtn=document.getElementById("btn-random-topic");
  if(rBtn){const ts=["The Fall of Rome","D-Day","The Black Death","Apollo 11","Cleopatra","Vikings","Genghis Khan","Bermuda Triangle","Nikola Tesla","Chernobyl"];
    rBtn.addEventListener("click",()=>{const inp=document.getElementById("topic-input");
      if(inp)inp.value=ts[Math.floor(Math.random()*ts.length)];});}
  const cBtn=document.getElementById("btn-create-video");
  if(cBtn)cBtn.addEventListener("click",async()=>{
    const topic=document.getElementById("topic-input")?.value||"auto";
    const style=document.getElementById("style-select")?.value||"documentary";
    const duration=document.getElementById("duration-select")?.value||"15";
    const voice=document.getElementById("voice-select")?.value||"male";
    const s=load();if(!s.github_pat||!s.github_repo){toast("⚠ Set GitHub PAT & repo in Settings");return;}
    cBtn.disabled=true;cBtn.textContent="Dispatching…";
    try{const r=await fetch(`https://api.github.com/repos/${s.github_repo}/actions/workflows/daily-video-pipeline.yml/dispatches`,{
      method:"POST",headers:{"Authorization":`token ${s.github_pat}`,"Accept":"application/vnd.github+json"},
      body:JSON.stringify({ref:"main",inputs:{topic,duration,voice,style,publish:"draft"}})});
      toast(r.status===204?"🚀 Pipeline dispatched!":"❌ Failed ("+r.status+")");}
    catch(e){toast("❌ "+e.message);}
    finally{cBtn.disabled=false;cBtn.textContent="🎬 CREATE VIDEO";}});
  const pEl=document.getElementById("pipeline-content");
  if(pEl){const steps=["Topic","Script","Voice","Footage","Edit","Subs","Thumb","Meta","Upload"];
    pEl.innerHTML=`<div style="display:flex;flex-wrap:wrap;gap:.5rem;justify-content:center">${steps.map(s=>`<div style="padding:.5rem 1rem;background:rgba(255,255,255,.04);border-radius:8px;text-align:center;min-width:80px"><div style="font-size:1.2rem">○</div><div style="font-size:.75rem">${s}</div></div>`).join("")}</div>`;}
  const tEl=document.getElementById("topics-content");
  if(tEl)fetch("../config/topics_database.json").then(r=>r.json()).then(db=>{
    const cats=db.categories||{};
    tEl.innerHTML=Object.entries(cats).map(([k,c])=>`<div style="margin-bottom:1.5rem"><h4>${c.icon||""} ${c.label||k}</h4><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:.6rem">${(c.topics||[]).map(t=>`<div style="padding:.6rem 1rem;background:rgba(255,255,255,.04);border-radius:8px;cursor:pointer" onclick="document.getElementById('topic-input').value='${t.title.replace(/'/g,"")}'"><strong>${t.title}</strong><br><span style="font-size:.75rem;color:#888">${t.era||""}</span></div>`).join("")}</div></div>`).join("");
  }).catch(()=>{tEl.innerHTML="<p class='muted'>Could not load topics.</p>";});
  function toast(msg){let t=document.getElementById("toast");
    if(!t){t=document.createElement("div");t.id="toast";document.body.appendChild(t);}
    t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),4000);}
});
