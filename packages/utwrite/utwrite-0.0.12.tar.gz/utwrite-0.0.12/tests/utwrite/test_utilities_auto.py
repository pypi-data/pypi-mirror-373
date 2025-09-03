
import sys
import os
import unittest
from utwrite.unittest_cases import *


class Test_utilities_AUTO(BaseTestCase):

    def test_leading_whitespace(self):

        from utwrite import utilities
        s = '    foo bar'
        self.assertEqual(utilities.leading_whitespace(s),4 )

        self.assertEqual(utilities.leading_whitespace('no whitespace'),0 )

        self.assertEqual(utilities.leading_whitespace(' one  two   three'),1 )

    def test_get_files_from_dir(self):

        from utwrite import utilities
        p = utilities.__file__
        files = utilities.get_files_from_dir(p)
        files = [os.path.basename(f) for f in files]
        expected_files = ['auto_generate_test.py', 'headers.py', 'unittest_cases.py', 'utilities.py']
        self.assertEqual(all (e in files for e in expected_files),True )

        self.assertEqual('__init__.py' in files,True )

        files = utilities.get_files_from_dir(p, ext=['.py'], ignore=['__init__.py'])
        files = [os.path.basename(f) for f in files]
        self.assertEqual('__init__.py' in files,False )

        self.assertEqual('utilities.py' in files,True )

    def test_write_to_file(self):

        from utwrite import utilities
        import os, tempfile, shutil
        temp_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        f = os.path.join(temp_dir, 'f.txt')
        if os.path.isfile(f):
           shutil.rmtree(temp_dir)
        self.assertEqual(os.path.isfile(f),False )

        utilities.write_to_file('utwrite.utilities.write_to_file() unittest', f, verbose=False)
        self.assertEqual(os.path.isfile(f),True )

        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)

    def test_populate_init_files(self):

        from utwrite import utilities
        import os, tempfile, shutil
        root_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)
        self.assertEqual(os.path.isdir(root_dir),False )

        from utwrite import utilities
        import os, tempfile, shutil
        root_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)
        self.assertEqual(os.path.isdir(root_dir),False )

        f = os.path.join(root_dir, 'd1', 'd2', 'ut_file.py')
        utilities.ensure_path_to_file(f)
        utilities.populate_init_files(f, root=root_dir, verbose=False)
        self.assertEqual(os.path.isfile(os.path.join(root_dir, '__init__.py')),False )

        self.assertEqual(os.path.isfile(os.path.join(root_dir, 'd1', '__init__.py')),True )

        self.assertEqual(os.path.isfile(os.path.join(root_dir, 'd1', 'd2', '__init__.py')),True )

        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)

    def test_get_test_dir(self):

        from utwrite import utilities
        import os, tempfile, shutil
        root_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)
        git_dir = os.path.join(root_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(root_dir, 'd1', 'd2', 'ut_file.py')
        utilities.ensure_path_to_file(f)
        test_dir = utilities.get_test_dir(f)
        self.assertEqual(os.path.realpath(test_dir) == os.path.realpath(os.path.join(root_dir, 'tests', 'd1', 'd2')),True )

        from utwrite import utilities
        import os, tempfile, shutil
        root_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)
        git_dir = os.path.join(root_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(root_dir, 'd1', 'd2', 'ut_file.py')
        utilities.ensure_path_to_file(f)
        test_dir = utilities.get_test_dir(f)
        self.assertEqual(os.path.realpath(test_dir) == os.path.realpath(os.path.join(root_dir, 'tests', 'd1', 'd2')),True )

        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)

    def test_number_increase(self):

        from utwrite import utilities
        self.assertEqual(utilities.number_increase('some string'),'some string1' )

        self.assertEqual(utilities.number_increase('1_some_string_2'),'1_some_string_3')

        self.assertEqual(utilities.number_increase('my_string_005', increase_by=10),'my_string_015')

    def test_flatten_list(self):

        from utwrite import utilities
        l = [0,1,[2],3,[4,[5,6,7,[8]]]]
        self.assertEqual(utilities.flatten_list(l),[0, 1, 2, 3, 4, 5, 6, 7, 8] )

    def test_add_to_env(self):

        import sys,os
        from utwrite import utilities
        usr_dir = os.path.realpath(os.path.expanduser('~'))
        if usr_dir in sys.path:
             sys.path.remove(usr_dir)
        self.assertEqual(utilities.add_to_env('PATH', usr_dir),[True] )

        self.assertEqual(usr_dir in os.environ['PATH'],True )

        self.assertEqual(usr_dir in sys.path,True )

        sys.path.remove(usr_dir)
        self.assertEqual(usr_dir in sys.path,False )

        self.assertEqual(utilities.add_to_env('PATH', usr_dir),[True] )

        self.assertEqual(utilities.add_to_env('PATH', usr_dir),[False] )

    def test_clean_file_path(self):

        import os
        from utwrite import utilities
        cur_home = os.path.expanduser('~')
        utw_path = os.path.dirname(utilities.__file__)
        os.environ['HOME'] = utw_path
        os.environ['USERPROFILE'] = utw_path
        home_contents = os.listdir(os.path.expanduser('~'))
        if home_contents:
            v = '~/%s'%home_contents[0]
            self.assertEqual(    len(v) < len(utilities.clean_file_path(v)),    True )

        os.environ['HOME'] = cur_home
        os.environ['USERPROFILE'] = cur_home
