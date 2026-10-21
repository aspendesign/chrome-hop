const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname,'..');
const source = fs.readFileSync(path.join(root,'extension/background.js'),'utf8');

function harness(native = async()=>({ok:true,code:'opened'}),options={}) {
  let handler,installed,menu;
  const calls={native:[],created:[],updated:[],badges:[],titles:[],permissions:[],queries:[],menus:[]};
  let now = 10000;
  const action={onClicked:{addListener(fn){handler=fn}},async setBadgeText(v){calls.badges.push(v)},async setBadgeBackgroundColor(){},async setTitle(v){calls.titles.push(v)}};
  let helpURL;
  const browser={action,menus:{create(v){calls.menus.push(v)},onClicked:{addListener(fn){menu=fn}}},permissions:{async request(v){calls.permissions.push(v);return options.granted??true}},runtime:{onInstalled:{addListener(fn){installed=fn}},getURL:p=>'moz-extension://fixture/'+p,async sendNativeMessage(host,message){calls.native.push({host,message});return native(message)}},tabs:{async query(v){calls.queries.push(v);if(options.queryError)throw Error('private-error');return options.tabs||[]},async create(v){calls.created.push(v);helpURL=v.url;return {id:99}},async get(){return {id:99,url:helpURL}},async update(id,v){calls.updated.push({id,...v});helpURL=v.url}}};
  vm.runInNewContext(source,{browser,URL,TextEncoder,Date:{now:()=>now}});
  return {calls,installed:reason=>installed({reason}),bulk:(id='open-all-tabs')=>menu({menuItemId:id},{id:3,windowId:7}),navigateHelp:url=>helpURL=url,click:(url,id=3)=>handler({id,url}),advance:()=>now+=1001};
}

test('manifest has toolbar permissions plus optional bulk-only tab access, no website access',()=>{
  const m=JSON.parse(fs.readFileSync(path.join(root,'extension/manifest.json')));
  assert.deepEqual(m.permissions,['activeTab','nativeMessaging','menus']);
  assert.deepEqual(m.optional_permissions,['tabs']);
  for(const key of ['host_permissions','optional_host_permissions','content_scripts','web_accessible_resources','externally_connectable','commands','update_url'])assert.equal(m[key],undefined,key);
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
  assert.equal(h.calls.permissions.length,0);assert.equal(h.calls.queries.length,0);
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
  for(const forbidden of [/\.onMessage/,/\.onConnect/,/fetch\s*\(/,/XMLHttpRequest/,/executeScript/,/eval\s*\(/,/console\./])assert.doesNotMatch(source,forbidden);
  assert.equal(h.calls.permissions.length,0);assert.equal(h.calls.queries.length,0);
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

test('right-click option is confined to the toolbar action context',async()=>{
  const h=harness();await h.installed('update');
  assert.equal(JSON.stringify(h.calls.menus),JSON.stringify([{id:'open-all-tabs',title:'Open all tabs in this window',contexts:['action']}]));
  await h.bulk('unrelated-menu');assert.equal(h.calls.permissions.length,0);
});
test('bulk permission denial reads no other tabs, opens nothing; left-click still works',async()=>{
  const h=harness(undefined,{granted:false});await h.bulk();
  assert.equal(h.calls.queries.length,0);assert.equal(h.calls.native.length,0);assert.match(h.calls.created[0].url,/#permission$/);
  await h.click('https://example.com/');assert.equal(h.calls.native.length,1);assert.equal(h.calls.permissions.length,1);
});
test('bulk forwards current-window HTTP(S) tabs in tab order and skips unsupported pages',async()=>{
  const h=harness(undefined,{tabs:[{index:2,url:'https://example.com/second'},{index:0,url:'http://localhost:3000/first'},{index:1,url:'about:config'},{index:3,url:'file:///C:/private'},{index:4,url:'https://user:pass@example.com/'}]});
  await h.bulk();
  assert.equal(JSON.stringify(h.calls.queries),JSON.stringify([{windowId:7}]));
  assert.equal(JSON.stringify(h.calls.permissions),JSON.stringify([{permissions:['tabs']}]));
  assert.deepEqual(h.calls.native.map(c=>c.message.url),['http://localhost:3000/first','https://example.com/second']);
  assert.equal(h.calls.badges.at(-1).text,'2');assert.match(h.calls.titles.at(-1).title,/skipped 3 unsupported/);
});
test('bulk cannot overlap another bulk or ordinary click and never runs native hosts concurrently',{timeout:3000},async()=>{
  let resolve;const h=harness(()=>new Promise(r=>resolve=r),{tabs:[{index:0,url:'https://example.com/a'},{index:1,url:'https://example.com/b'}]});
  const pending=h.bulk();await new Promise(setImmediate);assert.equal(h.calls.native.length,1);
  await h.bulk();await h.click('https://example.com/c');assert.equal(h.calls.native.length,1);
  resolve({ok:true,code:'opened'});await new Promise(setImmediate);assert.equal(h.calls.native.length,2);
  resolve({ok:true,code:'opened'});await pending;assert.equal(h.calls.native.length,2);
});
test('bulk stops after a native failure and reports the completed count without private URLs',async()=>{
  let n=0;const h=harness(async()=>++n===1?{ok:true,code:'opened'}:{ok:false,code:'chrome_not_found'},{tabs:[0,1,2].map(index=>({index,url:'https://example.com/?private='+index}))});
  await h.bulk();assert.equal(h.calls.native.length,2);assert.match(h.calls.created[0].url,/#chrome$/);assert.match(h.calls.titles.at(-1).title,/Opened 1 of 3/);
  assert.ok(!JSON.stringify([...h.calls.created,...h.calls.titles]).includes('private='));
});
test('no supported tabs gives local guidance; revoked permission fails without native launch',async()=>{
  const empty=harness(undefined,{tabs:[{index:0,url:'about:addons'}]});await empty.bulk();assert.equal(empty.calls.native.length,0);assert.match(empty.calls.created[0].url,/#empty$/);
  const revoked=harness(undefined,{queryError:true});await revoked.bulk();assert.equal(revoked.calls.native.length,0);assert.match(revoked.calls.created[0].url,/#permission$/);
});
