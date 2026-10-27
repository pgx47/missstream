import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from content_pipeline import merge_entries, product_result, valid_selection, select_batch, observed_price

class ContentTests(unittest.TestCase):
    def test_incremental_preserves_old_entries_beyond_previous_cap(self):
        old = [{'asin': f'B{i:09d}', 'nom': str(i)} for i in range(115)]
        self.assertEqual(len(merge_entries(old, [{'asin':'B999999999','nom':'new'}], 'asin', 4)), 116)
        self.assertEqual(old, merge_entries(old, [old[0]], 'asin', 4))

    def test_no_overwrite_of_existing_look(self):
        old = [{'titre':'Cozy', 'image':'original.webp', 'produits':[1,2,3]}]
        self.assertEqual(merge_entries(old, [{'titre':'cozy', 'image':'wrong'}], 'titre', 1), old)

    def test_upstream_error_or_absence_is_unknown(self):
        for payload in ({}, {'error':'quota'}, {'results':[]}, {'results':[{'asin':'B000000002'}]}):
            self.assertEqual(product_result('B000000001', payload)['status'], 'unknown')

    def test_exact_identity_and_explicit_stock_status(self):
        self.assertEqual(product_result('B000000001', {'results':[{'asin':'B000000001','name':'Real'}]})['status'], 'available')
        self.assertEqual(product_result('B000000001', {'results':[{'asin':'B000000001','in_stock':False}]})['status'], 'unavailable')

    def test_generated_selection_rejects_unknown_and_duplicate_products(self):
        catalog = {'B000000001': {'nom':'Real','asin':'B000000001'}}
        self.assertIsNone(valid_selection([{'asin':'B000000099'}], catalog, minimum=1))
        self.assertIsNone(valid_selection([{'asin':'B000000001'},{'asin':'B000000001'}], catalog, minimum=2))
        self.assertEqual(valid_selection([{'nom':'Invented','asin':'B000000001'}],catalog,minimum=1)[0]['nom'],'Real')

    def test_batch_wraps_without_starving_products(self):
        first, cursor = select_batch(['a','b','c','d','e'],0,3)
        second, cursor = select_batch(['a','b','c','d','e'],cursor,3)
        self.assertEqual(set(first+second),set('abcde'))
        self.assertEqual(select_batch([],7,3),([],0))

    def test_price_requires_real_numeric_observation(self):
        self.assertEqual(observed_price({'price':{'value':49.99,'currency':'EUR'}}),49.99)
        self.assertIsNone(observed_price({'price':'≈ 50 €'}))
        self.assertIsNone(observed_price({'price':{'value':99,'currency':'USD'}}))
        self.assertIsNone(observed_price({'price':-1}))

if __name__ == '__main__': unittest.main()
