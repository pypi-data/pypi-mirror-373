import unittest
from kea2.u2Driver import U2StaticChecker, U2StaticDevice
from lxml import etree
from pathlib import Path



XML_PATH = Path(__file__).parent / "hidden_widget_test.xml"


class U2StaticCheckerForTest(U2StaticChecker):
    def __init__(self):
        self.d = U2StaticDevice(script_driver=None)


def get_static_checker():
    xml: etree._ElementTree = etree.parse(XML_PATH)
    d = U2StaticCheckerForTest()
    return d.getInstance(xml)


class TestHiddenWidget(unittest.TestCase):

    def test_hidden_widget(self):
        d = get_static_checker()
        assert not d(text="微信(690)").exists

import unittest

class TestSupportedAttributes(unittest.TestCase):

    def setUp(self):
        self.d = get_static_checker()

    def test_text(self):
        assert self.d(text="添加朋友").exists
        assert self.d(textContains="朋友").exists
        assert self.d(textStartsWith="添加").exists


    def test_class_name(self):
        assert self.d(className="android.widget.Button").exists

    def test_description(self):
        assert self.d(description="企业微信联系人，，通过手机号搜索企业微信用户").exists
        assert self.d(descriptionContains="微信联系人").exists
        assert self.d(descriptionStartsWith="企业微信").exists


    def test_clickable_true(self):
        assert self.d(clickable=True).exists
        assert self.d(clickable=False).exists
        assert self.d(enabled=True).exists
        assert self.d(focusable=True).exists
        assert self.d(focusable=False).exists
        assert self.d(scrollable=False).exists
        assert self.d(checkable=False).exists
        assert self.d(checked=False).exists
        assert self.d(focused=False).exists
        assert self.d(selected=False).exists
        assert self.d(packageName="com.tencent.mm").exists
        assert self.d(resourceId="com.tencent.mm:id/search_ll").exists


    def test_combined_text_and_className(self):
        assert self.d(text="添加朋友", className="android.widget.TextView").exists

    def test_combined_resourceId_and_className(self):
        assert self.d(resourceId="com.tencent.mm:id/search_ll", className="android.widget.LinearLayout").exists

    def test_combined_attributes_search_button(self):
        assert self.d(text="添加朋友", clickable=False).exists

    def test_child_element(self):
        assert self.d(resourceId="android:id/list").child(description="手机联系人，，添加通讯录中的朋友").exists


    def test_sibling_element(self):
        assert self.d(description="雷达，，添加身边的朋友").sibling(description="手机联系人，，添加通讯录中的朋友").exists



class TestUnsupportedMethods(unittest.TestCase):

    def setUp(self):
        self.d = get_static_checker()

    def test_positional_left_not_supported(self):
        try:
            result = self.d(text="微信(690)").left(text="搜索")
            assert False, "left() method should not be supported"
        except:
            assert True

    def test_positional_right_not_supported(self):
        try:
            result = self.d(text="微信(690)").right(text="搜索")
            assert False, "right() method should not be supported"
        except:
            assert True

    def test_positional_up_not_supported(self):
        try:
            result = self.d(text="通讯录").up(text="10:21")
            assert False, "up() method should not be supported"
        except:
            assert True

    def test_positional_down_not_supported(self):
        try:
            result = self.d(text="10:21").down(text="通讯录")
            assert False, "down() method should not be supported"
        except:
            assert True

    def test_child_by_text_not_supported(self):
        try:
            result = self.d(resourceId="android:id/list").child_by_text("通讯录")
            assert False, "child_by_text() method should not be supported"
        except:
            assert True

    def test_child_by_description_not_supported(self):
        try:
            result = self.d(className="android.widget.ListView").child_by_description("扫描")
            assert False, "child_by_description() method should not be supported"
        except:
            assert True

    def test_child_by_instance_not_supported(self):
        try:
            result = self.d(className="android.widget.LinearLayout").child_by_instance(1)
            assert False, "child_by_instance() method should not be supported"
        except:
            assert True

    def test_instance_parameter_not_supported(self):
        try:
            result = self.d(className="android.widget.TextView", instance=0)
            assert False, "instance parameter should not be supported"
        except:
            assert True

    def test_text_matches_not_supported(self):
        try:
            result = self.d(textMatches="微信.*")
            assert False, "textMatches should not be supported"
        except:
            assert True

    def test_class_name_matches_not_supported(self):
        try:
            result = self.d(classNameMatches=".*TextView")
            assert False, "classNameMatches should not be supported"
        except:
            assert True

    def test_description_matches_not_supported(self):
        try:
            result = self.d(descriptionMatches=".*搜索.*")
            assert False, "descriptionMatches should not be supported"
        except:
            assert True

    def test_package_name_matches_not_supported(self):
        try:
            result = self.d(packageNameMatches="com.tencent.*")
            assert False, "packageNameMatches should not be supported"
        except:
            assert True

    def test_resource_id_matches_not_supported(self):
        try:
            result = self.d(resourceIdMatches=".*:id/.*")
            assert False, "resourceIdMatches should not be supported"
        except:
            assert True

class TestEdgeCases(unittest.TestCase):

    def setUp(self):
        self.d = get_static_checker()

    def test_empty_text(self):
        assert self.d(text="").exists

    def test_empty_resource_id(self):
        assert self.d(resourceId="").exists

    def test_special_characters_in_text(self):
        assert not self.d(text="微信(690)").exists
        assert not self.d(text="[有人@我] 测试: [聊天记录]").exists

    def test_non_existent_element(self):
        assert not self.d(text="不存在的文本").exists
        assert not self.d(resourceId="com.example.nonexistent").exists

class TestWidget(unittest.TestCase):

    def test_widget(self):
        d = get_static_checker()
        


if __name__ == "__main__":
    unittest.main()
