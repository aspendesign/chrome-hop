const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'extension/help.js'),'utf8');
function harness(hash='#helper',platform={os:'win',arch:'x86-64'}){
  const ids=['heading','detail','windows-setup','platform-note','page-help','chrome-help'];
  const nodes=Object.fromEntries(ids.map(id=>[id,{textContent:'',hidden:false}]));
  const handlers={};const location={hash};
  vm.runInNewContext(source,{document:{getElementById:id=>nodes[id]},location,addEventListener:(event,fn)=>handlers[event]=fn,browser:{runtime:{getPlatformInfo:async()=>platform}}});
  return {nodes,async ready(){await new Promise(setImmediate)},hash(value){location.hash=value;handlers.hashchange()}};
}
test('helper route offers setup and switches correctly in a reused help tab',async()=>{
  const h=harness();await h.ready();assert.equal(h.nodes['windows-setup'].hidden,false);
  h.hash('#unsupported');assert.match(h.nodes.heading.textContent,/can’t hop/);assert.equal(h.nodes['windows-setup'].hidden,true);assert.equal(h.nodes['page-help'].hidden,false);
  h.hash('#helper');assert.match(h.nodes.heading.textContent,/One quick install/);assert.equal(h.nodes['windows-setup'].hidden,false);assert.equal(h.nodes['page-help'].hidden,true);
  h.hash('#chrome');assert.equal(h.nodes['windows-setup'].hidden,true);assert.equal(h.nodes['chrome-help'].hidden,false);
});
for(const platform of [{os:'mac',arch:'aarch64'},{os:'linux',arch:'x86-64'},{os:'win',arch:'aarch64'}])test('unsupported platform never offers an incompatible installer: '+platform.os+'/'+platform.arch,async()=>{
  const h=harness('#helper',platform);await h.ready();assert.equal(h.nodes['windows-setup'].hidden,true);assert.equal(h.nodes['platform-note'].hidden,false);assert.match(h.nodes.heading.textContent,/isn’t available yet/);
});
test('unknown or inherited hash cannot inject UI or crash the setup page',async()=>{
  const h=harness('#constructor');await h.ready();assert.match(h.nodes.heading.textContent,/One quick install/);
  h.hash('#<script>');assert.equal(h.nodes['windows-setup'].hidden,false);
});
test('download starts from a fixed release asset; GitHub remains a separate option',()=>{
  const html=fs.readFileSync(path.join(root,'extension/help.html'),'utf8');
  assert.match(html,/<a id="download"[^>]*href="https:\/\/github\.com\/aspendesign\/chrome-hop\/releases\/latest\/download\/ChromeHop-Setup-windows-x64\.exe"/);
  assert.match(html,/class="button secondary"[^>]*href="https:\/\/github\.com\/aspendesign\/chrome-hop\/releases\/latest"/);
  assert.doesNotMatch(html,/<script[^>]*src="https?:/);
  assert.doesNotMatch(source,/sendNativeMessage|fetch\s*\(|XMLHttpRequest|innerHTML/);
});
