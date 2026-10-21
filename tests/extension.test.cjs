const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname,'..');
const source = fs.readFileSync(path.join(root,'extension/background.js'),'utf8');

function harness(native = async()=>({ok:true,code:'opened'})) {
  let handler,installed;
  const calls={native:[],created:[],updated:[],badges:[],titles:[]};
  let now = 10000;
  const action={onClicked:{addListener(fn){handler=fn}},async setBadgeText(v){calls.badges.push(v)},async setBadgeBackgroundColor(){},async setTitle(v){calls.titles.push(v)}};
  let helpURL;
  const browser={action,runtime:{onInstalled:{addListener(fn){installed=fn}},getURL:p=>'moz-extension://fixture/'+p,async sendNativeMessage(host,message){calls.native.push({host,message});return native(message)}},tabs:{async create(v){calls.created.push(v);helpURL=v.url;return {id:99}},async get(){return {id:99,url:helpURL}},async update(id,v){calls.updated.push({id,...v});helpURL=v.url}}};
  vm.runInNewContext(source,{browser,URL,TextEncoder,Date:{now:()=>now}});
  return {calls,installed:reason=>installed({reason}),navigateHelp:url=>helpURL=url,click:(url,id=3)=>handler({id,url}),advance:()=>now+=1001};
}

test('manifest has precisely the two approved permissions and no website access',()=>{
  const m=JSON.parse(fs.readFileSync(path.join(root,'extension/manifest.json')));
  assert.deepEqual(m.permissions,['activeTab','nativeMessaging']);
  for(const key of ['optional_permissions','host_permissions','optional_host_permissions','content_scripts','web_accessible_resources','externally_connectable','commands','update_url'])assert.equal(m[key],undefined,key);
  assert.equal(m.browser_specific_settings.gecko.id,'chrome-hop@aspendesign.github.io');
  assert.equal(m.manifest_version,3);
  assert.equal(m.browser_specific_settings.gecko.strict_min_version,'142.0');
  assert.equal(m.browser_specific_settings.gecko_android,undefined);
});
test('one click forwards exactly the clicked URL and fixed operation/host',async()=>{
  const h=harness();const url='http://localhost:3000/path?q=a&b=1#here';await h.click(url);
  assert.equal(h.calls.native.length,1);assert.equal(h.calls.native[0].host,'io.github.aspendesign.chrome_hop');
  assert.equal(JSON.stringify(h.calls.native[0].message),JSON.stringify({op:'open',url}));
  assert.equal(h.calls.created.length,0);assert.equal(h.calls.badges.at(-1).text,'✓');
});
for(const url of ['https://example.com/','https://example.com/?q=%22&x=|','https://例え.テスト/'])test('accepts web URL '+url,async()=>{const h=harness();await h.click(url);assert.equal(h.calls.native.length,1)});
for(const url of [undefined,'about:config','file:///C:/a','data:text/html,hi','javascript:alert(1)','--incognito','https://','https://example.com\n','https://example.com/%0a','https://user:pass@example.com','https://example.com\\@evil.test','https://example.com/"cmd','https://example.com/'+ 'x'.repeat(16384)])test('rejects unsafe input '+String(url).slice(0,50),async()=>{
  const h=harness();await h.click(url);assert.equal(h.calls.native.length,0);assert.match(h.calls.created[0].url,/#unsupported$/);
});
test('concurrent/rapid clicks produce one launch; later deliberate click works',{timeout:3000},async()=>{
  let resolve;const h=harness(()=>new Promise(r=>resolve=r));const a=h.click('https://example.com/');
  await new Promise(setImmediate);await h.click('https://example.com/');resolve({ok:true,code:'opened'});await a;
  await h.click('https://example.com/');assert.equal(h.calls.native.length,1);h.advance();
  const b=h.click('https://example.com/');await new Promise(setImmediate);resolve({ok:true,code:'opened'});await b;assert.equal(h.calls.native.length,2);
});
for(const [response,code] of [[{ok:false,code:'chrome_not_found'},'chrome'],[{ok:false,code:'invalid_message'},'unsupported'],[{ok:true,code:'nonsense'},'launch'],[null,'launch']])test('sanitized helper error '+code,async()=>{
  const h=harness(async()=>response);await h.click('https://example.com/?private=TEST');assert.match(h.calls.created[0].url,new RegExp('#'+code+'$'));assert.ok(!JSON.stringify(h.calls.created).includes('private'));
});
test('missing helper gives repair instructions and reuses its own help tab',async()=>{
  const h=harness(async()=>{throw Error('TEST-SENSITIVE-URL')});await h.click('https://example.com/');await h.click('https://example.com/');
  assert.equal(h.calls.created.length,1);assert.equal(h.calls.updated.length,1);assert.match(h.calls.created[0].url,/#helper$/);assert.ok(!JSON.stringify(h.calls).includes('SENSITIVE'));
});
test('no native call at startup, website listeners, injection, telemetry or shell',()=>{
  const h=harness();assert.equal(h.calls.native.length,0);
  for(const forbidden of [/\.onMessage/,/\.onConnect/,/fetch\s*\(/,/XMLHttpRequest/,/executeScript/,/\.tabs\.query/,/eval\s*\(/,/console\./])assert.doesNotMatch(source,forbidden);
});

test('first install opens local setup; updates and browser upgrades stay quiet',async()=>{
  const h=harness(); await h.installed('update'); await h.installed('browser_update');
  assert.equal(h.calls.created.length,0); await h.installed('install');
  assert.deepEqual(h.calls.created.map(v=>v.url),['moz-extension://fixture/help.html#setup']);
  assert.equal(h.calls.native.length,0);
});

test('a former help tab navigated to a website is preserved',async()=>{
  const h=harness(async()=>{throw Error('missing')});await h.installed('install');
  h.navigateHelp('https://example.com/');await h.click('https://example.com/');
  assert.equal(h.calls.updated.length,0);assert.equal(h.calls.created.length,2);
  assert.match(h.calls.created[1].url,/#helper$/);
});
