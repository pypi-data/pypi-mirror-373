
import sys
import os
import unittest
from utwrite.unittest_cases import *


class Test_auto_generate_test_AUTO(BaseTestCase):

    def test_make_test_res_data(self):

        from utwrite import auto_generate_test as agt
        d = agt.make_test_res_data(agt.TST_FUNC)
        self.assertEqual(d ['my_func'],[('\nmy_func(2)', ('Result', '3 ')), ('\nmy_func(0)',('Result', '1 ')), ('\nmy_func(4)', ('Result', '5 @self.assertAlmostEqual '))] )

    def test__check_in_res_keys(self):

        from utwrite import auto_generate_test as agt
        self.assertEqual(agt._check_in_res_keys('# Result:'),True )

        self.assertEqual(agt._check_in_res_keys('#RESULT:'),True )

        self.assertEqual(agt._check_in_res_keys('#result:'),True )

        self.assertEqual(agt._check_in_res_keys('#   result   :'),True )

        self.assertEqual(agt._check_in_res_keys('result'),False )

        self.assertEqual(agt._check_in_res_keys('Result'),False )

        self.assertEqual(agt._check_in_res_keys('#Result'),False )

        self.assertEqual(agt._check_in_res_keys('# Result'),False )

    def test__break_docstrings_in_tests_and_results(self):

        from utwrite import auto_generate_test as agt
        func_doc_data = {'my_func': '\n\n    my_func(2)\n    # Result: 3 #\n\n    my_func(0)\n    # Result: 1 #\n\n'}
        self.assertEqual(agt._break_docstrings_in_tests_and_results(func_doc_data),{'my_func': [('\nmy_func(2)', ('Result', '3 ')), ('\nmy_func(0)', ('Result', '1 '))]} )

    def test_make_test_body_from_test_result_data(self):

        import utwrite.auto_generate_test as agt
        func_doc_data = {'my_func': '\n\n    my_func(2)\n    # Result: 3 #\n\n    my_func(0)\n    # Result: 1 #\n\n'}
        mod_test_data = agt._break_docstrings_in_tests_and_results(func_doc_data)
        body = agt.make_test_body_from_test_result_data(mod_test_data)
        self.assertEqual(body,'\n    def test_my_func(self):\n\n        self.assertEqual(my_func(2),3 )\n\n        self.assertEqual(my_func(0),1 )\n' )

    def test_build_test_file(self):

        from utwrite import utilities
        from utwrite import headers
        import utwrite.auto_generate_test as agt
        import os, tempfile, shutil
        temp_dir = os.path.join(tempfile.gettempdir(), 'utwrite_agt_unittest_DELETE')
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        git_dir = os.path.join(temp_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(temp_dir, 'd1', 'd2', 'ut_file.py')
        utilities.ensure_path_to_file(f)
        with open(f, 'w') as m:
            m.write(agt.TST_FUNC)
        test_contents = agt.build_test_file(f, verbose=False)
        tst_file = os.path.join(temp_dir, 'tests', 'd1','d2','test_ut_file_auto.py')
        with open(tst_file ,'r') as t:
            file_contents = t.read()
        self.assertEqual(str(file_contents) == str(test_contents),True )

        test_body = agt.make_test_body_from_test_result_data(agt.make_test_res_data(f))
        expected_contents = headers.HEADER['default'] + test_body
        expected_contents = expected_contents % ('', 'ut_file', 'BaseTestCase')
        self.assertEqual(file_contents == expected_contents,True )

        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        self.assertEqual(os.path.isdir(temp_dir),False )

    def test_build(self):

        from utwrite import utilities
        import utwrite.auto_generate_test as agt
        import os, tempfile, shutil
        temp_dir = os.path.join(tempfile.gettempdir(), 'utwrite_agt_unittest_DELETE')
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        git_dir = os.path.join(temp_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(temp_dir, 'd1', 'd2', 'ut_file.py')
        utilities.ensure_path_to_file(f)
        with open(f, 'w') as m:
            m.write(agt.TST_FUNC)
        agt.build(f, verbose=False)
        tst_file = os.path.join(temp_dir, 'tests', 'd1','d2','test_ut_file_auto.py')
        with open(tst_file ,'r') as t:
            file_contents = t.read()
        test_data = agt.make_test_res_data(f)
        test_body = agt.make_test_body_from_test_result_data(test_data)
        self.assertEqual(test_body in file_contents,True )

        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        self.assertEqual(os.path.isdir(temp_dir),False )

    def test_get_module_unittest_deco(self):

        import utwrite.auto_generate_test as agt
        mod_docs = '\"\"\"'
        mod_docs += '\nSome module\n\n'
        mod_docs += ':Unittest decorator:\n'
        mod_docs += "@unittest.skipunless(1==2, 'Some reason')\n"
        mod_docs += '\"\"\"'
        self.assertEqual(agt.get_module_unittest_deco(mod_docs),"\n@unittest.skipunless(1==2, 'Some reason')" )

    def test_main(self):

        from utwrite import utilities
        import utwrite.auto_generate_test as agt
        import os, tempfile, shutil
        temp_dir = os.path.join(tempfile.gettempdir(), 'utwrite_agt_unittest_DELETE')
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        git_dir = os.path.join(temp_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(temp_dir, 'd1', 'd2', 'ut_file.py')
        utilities.ensure_path_to_file(f)
        with open(f, 'w') as m:
            m.write(agt.TST_FUNC)
        agt.main(f, verbose=False)
        tst_file = os.path.join(temp_dir, 'tests', 'd1','d2','test_ut_file_auto.py')
        with open(tst_file ,'r') as t:
            file_contents = t.read()
        test_data = agt.make_test_res_data(f)
        test_body = agt.make_test_body_from_test_result_data(test_data)
        self.assertEqual(test_body in file_contents,True )

        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        self.assertEqual(os.path.isdir(temp_dir),False )
