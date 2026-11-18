"""Permission rules must also hold for direct API and cached PDF access."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import importlib.util
import json
import unittest

spec=importlib.util.spec_from_file_location('local_pdfs',Path(__file__).resolve().parents[1]/'local_pdfs.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class SchoolPermissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/'catalog').mkdir()
        (self.root/'catalog/permissions.json').write_text(json.dumps({'letovo':{'status':'granted','preserveOriginal':True}}))
        self.pdfs=module.LocalPDFs(self.root)
        self.addCleanup(self.pdfs.pool.shutdown)
        self.addCleanup(self.pdfs.background_pool.shutdown)
        self.addCleanup(self.tmp.cleanup)

    def test_grant_allows_original_but_blocks_translation(self):
        self.assertNotIn('letovo',self.pdfs.page_only())
        self.assertIn('letovo',self.pdfs.translation_blocked())
        with patch.object(self.pdfs,'resolve',side_effect=AssertionError('Must reject before rendering')):
            self.assertEqual(self.pdfs.submit({'source':'letovo','doc':'https://letovo.ru/test.pdf','lang':'en'}),
                             {'state':'unavailable','reason':'permission'})

    def test_existing_translation_is_blocked_but_original_remains_accessible(self):
        key='a'*64
        url='https://letovo.ru/test.pdf'
        (self.root/(key+'.metadata.json')).write_text(json.dumps({'url':url}))
        with patch.object(self.pdfs,'mirror',return_value={url:{'source':'letovo','sha':key}}),patch.object(module,'JOBS',self.root):
            self.assertFalse(self.pdfs.restricted('pdf',key))
            self.assertTrue(self.pdfs.restricted('translated',key))
            self.assertIsNone(self.pdfs.file('translated',key))

if __name__=='__main__':unittest.main()
