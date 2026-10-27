import test from 'node:test';
import assert from 'node:assert/strict';
import { weeklySelection, latestInspirations, quizSelections, seasonalGuide, monthlyPanel } from './content-selection.mjs';

test('weekly selection is stable during a UTC week and changes next week', () => {
  const items = [1, 2, 3, 4, 5, 6];
  assert.deepEqual(weeklySelection(items, new Date('2026-10-26T00:00:00Z'), 3), weeklySelection(items, new Date('2026-11-01T23:59:00Z'), 3));
  assert.notDeepEqual(weeklySelection(items, new Date('2026-10-26'), 3), weeklySelection(items, new Date('2026-11-02'), 3));
  assert.equal(new Set(weeklySelection([1, 2], new Date(), 4)).size, 2);
});
test('inspirations prioritize dated additions without mutating source', () => {
  const rows = [{titre:'Old',image:'/old.webp'}, {titre:'New',image:'/new.webp',publishedAt:'2026-10-28'}];
  assert.equal(latestInspirations(rows)[0].titre, 'New');
  assert.equal(rows[0].titre, 'Old');
});
test('quiz excludes unavailable ASIN across duplicate references and selects relevant products', () => {
  const rows = [{nom:'Gaming headset',asin:'B000000001'}, {nom:'Micro USB',asin:'B000000002'}, {nom:'Camera webcam',asin:'B000000003'}, {nom:'Ring LED light',asin:'B000000004'}, {nom:'Headset dead',asin:'B000000005',productStatus:'unavailable'}, {nom:'Headset stale reference',asin:'B000000005'}];
  const selections = quizSelections(rows);
  assert.equal(selections.gaming[0].asin, 'B000000001');
  assert.equal(selections.chatting[0].asin, 'B000000003');
  assert.equal(selections.podcast[0].asin, 'B000000002');
  for (const items of Object.values(selections)) {
    assert.equal(items.length, 3);
    assert.equal(new Set(items.map(p=>p.asin)).size, 3);
    assert.ok(!items.some(p=>p.asin === 'B000000005'));
  }
});
test('seasonal banner uses existing guides and hides Halloween after October', () => {
  const guides=[{id:'halloween-setup', data:{title:'Setup Halloween',publishDate:new Date('2026-10-01')}}, {id:'cadeaux-stream',data:{title:'Cadeaux stream',publishDate:new Date('2026-09-01')}}];
  assert.equal(seasonalGuide(guides,new Date('2026-10-27')).id,'halloween-setup');
  assert.equal(seasonalGuide(guides,new Date('2026-12-01')).id,'cadeaux-stream');
  assert.equal(seasonalGuide([],new Date()),null);
});

test('monthly panels are stable during a month and vary across all twelve months', () => {
  assert.deepEqual(monthlyPanel(new Date('2026-10-01')), monthlyPanel(new Date('2026-10-31')));
  assert.equal(new Set(Array.from({length:12},(_,i)=>monthlyPanel(new Date(Date.UTC(2026,i,1))).label)).size,12);
});
