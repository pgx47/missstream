import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import expand_content as weekly
from build_feature_pages import maintain_packs
from refresh_products import load_documents

NOW='2026-10-28T08:00:00+00:00'
HITS=[{'asin':f'B{i:09d}','name':f'Real product {i}','price':20+i,'image':'https://example.test/image.png'} for i in range(1,6)]

class WeeklyTests(unittest.TestCase):
    def test_inspiration_uses_real_names_and_keeps_old_entries(self):
        old=[{'titre':'Old','image':'/old.webp','produits':[]}]
        with patch.object(weekly,'ask',return_value={'titre':'New','description':'Cozy','queries':['a','b','c']}), \
             patch.object(weekly,'search',return_value=HITS), \
             patch.object(weekly,'product_image',return_value='/product.webp'), \
             patch.object(weekly,'cover',return_value='/cover.webp'):
            result=weekly.inspiration(old,NOW)
        self.assertEqual(result[0],old[0])
        self.assertEqual([p['nom'] for p in result[1]['produits']],[h['name'] for h in HITS[:3]])
        self.assertEqual(len({p['asin'] for p in result[1]['produits']}),3)

    def test_weekly_rerun_does_not_call_providers(self):
        old=[{'titre':'New','publishedAt':NOW}]
        with patch.object(weekly,'ask',side_effect=AssertionError('No duplicate generation')):
            self.assertEqual(weekly.inspiration(old,'2026-10-29T08:00:00+00:00'),old)

    def test_cover_failure_leaves_old_collection_intact(self):
        old=[{'titre':'Old','image':'/old.webp'}]
        before=copy.deepcopy(old)
        with patch.object(weekly,'ask',return_value={'titre':'New','description':'Cozy','queries':['a','b','c']}), \
             patch.object(weekly,'search',return_value=HITS), \
             patch.object(weekly,'product_image',return_value='/p.webp'), \
             patch.object(weekly,'cover',side_effect=ValueError('image failed')):
            with self.assertRaises(ValueError): weekly.inspiration(old,NOW)
        self.assertEqual(old,before)

    def test_decor_keeps_115_items_and_uses_scraped_name_price(self):
        old=[{'asin':f'C{i:09d}','nom':str(i)} for i in range(115)]
        proposals={'items':[{'query':'q','cat':'lumieres','desc':'Soft'} for _ in range(8)]}
        with patch.object(weekly,'ask',return_value=proposals),patch.object(weekly,'search',return_value=HITS),patch.object(weekly,'product_image',return_value='/p.webp'):
            updated=weekly.decor(old,NOW)
        self.assertEqual(len(updated),119)
        self.assertEqual(updated[:115],old)
        self.assertEqual(updated[115]['nom'],HITS[0]['name'])
        self.assertEqual(updated[115]['prix'],'21.00 €')

    def test_dupe_rejects_invented_or_reversed_savings(self):
        proposal={'titre':'Claim','originalQuery':'o','dupeQuery':'d'}
        with patch.object(weekly,'ask',return_value=proposal),patch.object(weekly,'search',side_effect=[[HITS[0]],[HITS[1]]]):
            with self.assertRaises(ValueError): weekly.alternatives([],NOW)

    def test_pack_identity_and_content_are_not_regenerated(self):
        packs=[{'id':'studio','budget':'900 €','items':[{'asin':HITS[0]['asin'],'nom':'Original'}]}]
        maintained=maintain_packs(copy.deepcopy(packs),{HITS[0]['asin']:{'status':'unavailable'}})
        self.assertEqual(maintained[0]['id'],'studio')
        self.assertEqual(maintained[0]['items'][0]['nom'],'Original')
        self.assertEqual(maintained[0]['items'][0]['productStatus'],'unavailable')

    def test_health_covers_every_catalog_and_guides(self):
        documents=load_documents(Path(__file__).resolve().parents[2])
        filenames={p.name for p,_,_ in documents}
        self.assertTrue({'packs.json','deals.json','dupes.json','lookbook.json','deco_items.json','streamers.json'}.issubset(filenames))
        self.assertTrue(any(name.endswith('.mdx') for name in filenames))

if __name__=='__main__': unittest.main()
