import sys
sys.path.append('..')
import tttt
from xml.dom import minidom


env = {
    'fruit' : 'cantaloupe',
    'fruit_list' : ['banana', 'cantaloupe', 'apple', 'banana'],
    'groceries' : [['apple', 'banana', 'cherry'], ['Apple', 'Android']],
}

def case1():
    """
>>> test('tttt_test_define.xml')
I'm so dadgum smart.
    """

def case2():
    """
>>> test('tttt_test_attribute_collection.xml')
I'm so dadgum smart.
    """

def case3():
    """
>>> test('tttt_test_select.xml')
I'm full.
    """

def case4():
    """
>>> test('tttt_test_repeat.xml')
banana
cantaloupe
apple
banana
<BLANKLINE>
    """

def case5():
    """
>>> test('tttt_test_execute.xml')
dog food is my favourite
    """

def case6():
    """
>>> test('tttt_test_enumerate.xml')
0 apple
1 banana
2 cherry
0 Apple
1 Android
<BLANKLINE>
    """

def case7():
    """
>>> test('tttt_test_enumerate_order.xml')
2 apple
0 banana
3 banana
1 cantaloupe
<BLANKLINE>
    """

def case12():
    """
>>> test('tttt_test_enumerate_tag_rename.xml')
2 apple
0 banana
3 banana
1 cantaloupe
<BLANKLINE>
    """

def case8():
    """
>>> test('tttt_test_enumerate_unique.xml')
banana
cantaloupe
apple
<BLANKLINE>
    """

def case9():
    """
>>> test('tttt_test_loadenv.xml')
0 kiwi
1 blackberry
<BLANKLINE>
    """

def case10():
    """
>>> test('tttt_test_transform.xml')
I'm full.
    """

def case11():
    """
>>> test('tttt_test_import.xml')
0 kiwi
1 blackberry
<BLANKLINE>
    """

def test(testxml):
    print tttt.gen_str('cases/' + testxml, env)

import doctest
doctest.testmod()
