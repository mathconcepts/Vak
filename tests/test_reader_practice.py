"""Reader behaviour in a real browser: practice ranges loop exactly the chosen words, and the swara lens
is built once per line (not once per word). Skips when node + Playwright or ffmpeg are not installed."""
import json, os, shutil, subprocess, tempfile
import pytest
from vakstudio import htmlbuild

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE_TEST = r"""
const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+process.argv[2]); await p.waitForTimeout(2500);
const r=await p.evaluate(async()=>{
  const out={};
  Practice.open(); S.lines[4].words[4].el.click(); S.lines[4].words[1].el.click();   // last word first: order is fixed up
  const ws=Music.wordsFor(4);
  out.start=+(Practice.start+0.12).toFixed(2); out.wantStart=ws[1][0];
  out.end=+(Practice.end-0.25).toFixed(2); out.wantEnd=ws[4][1];
  out.tiles=document.querySelectorAll('.rg').length;
  Practice.close(); out.closedTiles=document.querySelectorAll('.rg').length;
  // stop playback for good (a play queued by the practice step must not restart it), so only this test drives the lens
  Music.tryPlay=()=>{}; for(let k=0;k<20;k++){ Music.el.pause(); await new Promise(r=>setTimeout(r,100)); if(Music.el.paused&&k>4) break; }
  cancelAnimationFrame(Music.raf);
  // lens: feed every word time of lines 3..6 and count how often it is rebuilt
  let n=0; const o=Lens.build.bind(Lens); Lens.build=i=>{n++;return o(i)};
  for(const i of [3,4,5,6]){ const w=Music.wordsFor(i); for(const t of w.filter(Boolean)) Lens.update(i,t[0]+0.01,w); }
  out.builds=n;
  // pitch you can feel: at rest the word stays whole; while sung, svarita glides up and anudatta down
  const i=Lens.i, w=Music.wordsFor(i), qs=Lens.items.findIndex(x=>x.a.kind==='sv'), qa=Lens.items.findIndex(x=>x.a.kind==='anu');
  const es=Lens.items[qs].el, ea=Lens.items[qa].el;
  const ty=e=>{ const m=getComputedStyle(e).transform; return m&&m!=='none'? +m.split(',')[5].replace(')','') : 0; }, mid=q=>(Lens.tm[q][0]+Lens.tm[q][1])/2;
  const pause=ms=>new Promise(r=>setTimeout(r,ms));
  Lens.update(i,mid(qs),w); await pause(700); out.svGlide=-ty(es); out.svRest=ty(ea);
  Lens.update(i,mid(qa),w); await pause(700); out.anuGlide=ty(ea); out.svBack=ty(es);
  out.rails=document.querySelectorAll('.lens .pc line').length;
  const r=$("pracQuick").getBoundingClientRect(); out.practiseVisible=r.width>0&&$("morePanel").hidden;
  return out; });
r.errors=errs; console.log(JSON.stringify(r)); await b.close(); })();
"""

def _have():
    if not shutil.which("node") or not shutil.which("ffmpeg"):
        return False
    return subprocess.run(["node", "-e", "require('playwright')"], capture_output=True).returncode == 0

@pytest.mark.skipif(not _have(), reason="needs node + Playwright and ffmpeg")
def test_practice_range_and_line_lens():
    pack = json.load(open(os.path.join(ROOT, "packs/namakam/pack.json"), encoding="utf-8"))
    with tempfile.TemporaryDirectory() as d:
        mp3 = os.path.join(d, "s.mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", "60", "-b:a", "16k", mp3], check=True)
        html, _ = htmlbuild.render([pack], {"namakam": (open(mp3, "rb").read(), "audio/mpeg")})
        page = os.path.join(d, "r.html"); open(page, "w", encoding="utf-8").write(html)
        js = os.path.join(d, "t.js"); open(js, "w").write(NODE_TEST)
        r = json.loads(subprocess.run(["node", js, page], capture_output=True, text=True, timeout=90).stdout.strip().splitlines()[-1])
    assert r["errors"] == []
    assert abs(r["start"] - r["wantStart"]) < 0.02 and abs(r["end"] - r["wantEnd"]) < 0.02
    assert r["tiles"] == 4 and r["closedTiles"] == 0
    assert r["builds"] == 4          # once per line, however many words it has
    assert r["svGlide"] > 8 and r["anuGlide"] > 8   # while sung: svarita glides up, anudatta down
    assert r["svRest"] == 0 and abs(r["svBack"]) < 1  # at rest the word stays whole
    assert r["rails"] >= 2                            # high and low guide rails
    assert r["practiseVisible"]                       # Practise is in the main bar, not hidden in More
