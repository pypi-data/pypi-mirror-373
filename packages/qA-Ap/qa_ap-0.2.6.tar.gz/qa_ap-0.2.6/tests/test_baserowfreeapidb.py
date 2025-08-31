import unittest
import base64
import os

from qA_Ap.db.baserowfreeapidb import BaseRowFreeApiDB, FileAlreadyExistsError, WriteInDatabaseError

API_TOKEN = os.environ.get("BASEROW_API_TOKEN", "tyesLJsYXhYHyR2LBI2jZcUG711W1iUu")

class TestBaseRowFreeApiDBIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = BaseRowFreeApiDB(API_TOKEN)
        cls.test_post_name = "UnitTestPost"
        cls.test_commenter = "UnitTestUser"
        cls.test_icon = cls._load_dummy_image()
        cls.test_screenshots = [("screenshot",cls._load_dummy_image())]
        cls.test_content = "This is a test post content."
        cls.test_comment_content = "This is a test comment."
        cls.test_attribute = "unittest-attribute"
        cls.test_attribute_value = "unittest-value"
        cls.test_vector_store_bytes = b"unit test vector store"

    @staticmethod
    def _load_dummy_image():
        with open("dummy.png", "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def test_write_and_get_post(self):
        # Clean up if post exists
        try:
            self.db.write_post(self.test_post_name, self.test_content, icon=self.test_icon, medias=self.test_screenshots)
        except FileAlreadyExistsError:
            pass  # Already exists, that's fine for test

        # Now get the post
        content, icon = self.db.get_post(self.test_post_name)
        self.assertEqual(content, self.test_content)
        self.assertEqual(icon, self.test_icon)

    def test_post_exists(self):
        self.assertTrue(self.db.post_exists(self.test_post_name))
        self.assertFalse(self.db.post_exists("DefinitelyNotARealPostName"))

    def test_write_and_get_comment(self):
        # Clean up if comment exists
        try:
            self.db.write_comment(self.test_post_name, self.test_commenter, self.test_comment_content, medias=self.test_screenshots)
        except FileAlreadyExistsError:
            pass

        comments = self.db.get_comments_for_post(self.test_post_name)
        found = any(
            c[0] == self.test_comment_content and c[1] == self.test_commenter
            for c in comments
        )
        self.assertTrue(found)

    def test_comment_exists(self):
        self.assertTrue(self.db.comment_exists(self.test_post_name, self.test_commenter))
        self.assertFalse(self.db.comment_exists(self.test_post_name, "DefinitelyNotARealUser"))

    def test_get_post_medias(self):
        medias = self.db.get_post_medias(self.test_post_name)
        self.assertTrue(any(isinstance(m, str) and len(m) > 0 for m in medias))

    def test_get_comment_medias(self):
        medias = self.db.get_comment_medias(self.test_post_name, self.test_commenter)
        self.assertTrue(any(isinstance(m, str) and len(m) > 0 for m in medias))

    def test_write_and_get_attribute(self):
        self.db.write_attribute(self.test_attribute, self.test_attribute_value)
        value = self.db.get_attribute(self.test_attribute)
        self.assertIn(self.test_attribute_value, value)

    def test_add_attribute(self):
        self.assertTrue(self.db.add_attribute(self.test_attribute, self.test_attribute_value))

    def test_write_and_get_vector_store(self):
        self.assertTrue(self.db.write_vector_store(self.test_vector_store_bytes))
        result = self.db.get_vector_store()
        self.assertEqual(result, self.test_vector_store_bytes)

    def test_get_all_posts_data(self):
        posts = self.db.get_all_posts_data()
        self.assertIsInstance(posts, list)
        self.assertTrue(any(p["title"] == self.test_post_name for p in posts))

if __name__ == "__main__":
    unittest.main()