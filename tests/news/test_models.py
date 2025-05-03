from django.test import TestCase

from tests.accounts.factories import UserFactory
from travel.news.models import News


class NewsModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.news = News.objects.create(
            title="Test News",
            description="Test Description",
            content="Test Content",
            created_by=self.user,
        )

    def test_create_news(self):
        """Test creating a news item."""
        self.assertEqual(self.news.title, "Test News")
        self.assertEqual(self.news.description, "Test Description")
        self.assertEqual(self.news.content, "Test Content")
        self.assertEqual(self.news.created_by, self.user)
        self.assertIsNotNone(self.news.created_at)

    def test_news_str(self):
        """Test the string representation of a news item."""
        self.assertEqual(str(self.news), "Test News")

    def test_news_verbose_names(self):
        """Test the verbose names of the News model."""
        self.assertEqual(News._meta.verbose_name, "Новость")
        self.assertEqual(News._meta.verbose_name_plural, "Новости")
