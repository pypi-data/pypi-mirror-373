import pytest
from wbwriter.templatetags.writer import cite_article, table_of_contents


@pytest.mark.django_db
class TestWriter:
    def test_table_of_contents(self, article_factory):
        article_dict = {"article": article_factory(title="Test Article Title", name="Test Article Name")}
        toc = table_of_contents(article_dict, "ToC ")
        test_toc = {
            "title": "Test Article Title",
            "custom_enumeration": True,
            "anchor": "test-article-name",
            "enumerator": None,
            "level": 0,
            "articles": [],
        }
        assert toc == test_toc

    def test_table_of_contents_no_context(self):
        no_article_dict = {"blog": "Some Blog"}
        toc = table_of_contents(no_article_dict, "ToC ")
        test_toc = {"not_working": "<i>Table of content is only rendered in the exported PDF Version.</i>"}
        assert toc == test_toc

    def test_cite_article(self, article_factory):
        article = article_factory(title="Test Article Title", name="Test Article Name")
        article_dict: dict = {"article": article}
        ca = cite_article(article_dict, article.id)
        test_ca = {"anchor": "test-article-name", "text": "(see  Test Article Title)"}
        assert ca == test_ca

    def test_cite_article_no_context(self, article_factory):
        article = article_factory()
        no_article_dict = {"blog": "Some Blog"}
        ca = cite_article(no_article_dict, article.id)
        test_ca = {"not_working": "(article citations only work in a rendered pdf.)"}
        assert ca == test_ca
