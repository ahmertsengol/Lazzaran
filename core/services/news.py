"""
News service for fetching and formatting news articles.
"""

import requests
from dataclasses import dataclass
from typing import List, Optional
import logging
from datetime import datetime
from bs4 import BeautifulSoup

@dataclass
class NewsArticle:
    title: str
    description: str
    url: str
    source: str
    published_at: datetime
    category: str

class NewsService:
    def __init__(self, api_key: str, language: str = 'tr'):
        self.api_key = api_key
        self.language = language
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://newsapi.org/v2"
        
    def get_top_headlines(self, category: str = None, max_results: int = 5) -> List[NewsArticle]:
        """
        Fetch top headlines, optionally filtered by category.
        """
        try:
            endpoint = f"{self.base_url}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'language': self.language,
                'pageSize': max_results
            }
            
            if category:
                params['category'] = category
                
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            articles = []
            for article in response.json()['articles'][:max_results]:
                try:
                    articles.append(NewsArticle(
                        title=article['title'],
                        description=article.get('description', ''),
                        url=article['url'],
                        source=article['source']['name'],
                        published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                        category=category or 'general'
                    ))
                except KeyError as e:
                    self.logger.warning(f"Skipping article due to missing field: {e}")
                    continue
                    
            return articles
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching news: {e}")
            return []
            
    def search_news(self, query: str, max_results: int = 5) -> List[NewsArticle]:
        """
        Search for news articles by query.
        """
        try:
            endpoint = f"{self.base_url}/everything"
            params = {
                'apiKey': self.api_key,
                'language': self.language,
                'q': query,
                'pageSize': max_results,
                'sortBy': 'relevancy'
            }
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            articles = []
            for article in response.json()['articles'][:max_results]:
                try:
                    articles.append(NewsArticle(
                        title=article['title'],
                        description=article.get('description', ''),
                        url=article['url'],
                        source=article['source']['name'],
                        published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                        category='search'
                    ))
                except KeyError as e:
                    self.logger.warning(f"Skipping article due to missing field: {e}")
                    continue
                    
            return articles
            
        except requests.RequestException as e:
            self.logger.error(f"Error searching news: {e}")
            return []
    
    def format_articles_response(self, articles: List[NewsArticle], detailed: bool = False) -> str:
        """
        Format articles into a readable response.
        """
        if not articles:
            return "Üzgünüm, hiç haber bulunamadı."
            
        category_names = {
            'business': 'İş',
            'entertainment': 'Eğlence',
            'health': 'Sağlık',
            'science': 'Bilim',
            'sports': 'Spor',
            'technology': 'Teknoloji',
            'general': 'Genel',
            'search': 'Arama Sonuçları'
        }
        
        category = category_names.get(articles[0].category, 'Haberler')
        response = [f"\n{category} Haberleri:"]
        
        for i, article in enumerate(articles, 1):
            published = article.published_at.strftime('%H:%M')
            if detailed:
                response.append(f"\n{i}. {article.title}")
                if article.description:
                    response.append(f"   {article.description}")
                response.append(f"   Kaynak: {article.source} - Saat: {published}")
                response.append(f"   Link: {article.url}\n")
            else:
                response.append(f"\n{i}. {article.title}")
                response.append(f"   Kaynak: {article.source} - Saat: {published}")
        
        return "\n".join(response)
    
    def get_article_summary(self, url: str) -> Optional[str]:
        """
        Get a summary of a specific article by URL.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find the main article content
            article_text = ""
            
            # Look for common article content containers
            content_tags = soup.find_all(['article', 'main', 'div'], class_=['content', 'article-content', 'post-content'])
            
            if content_tags:
                # Get text from paragraphs in the first matching container
                paragraphs = content_tags[0].find_all('p')
                article_text = ' '.join(p.get_text().strip() for p in paragraphs)
            
            if not article_text:
                # Fallback: just get all paragraphs
                paragraphs = soup.find_all('p')
                article_text = ' '.join(p.get_text().strip() for p in paragraphs[:5])
            
            # Truncate if too long
            if len(article_text) > 500:
                article_text = article_text[:497] + "..."
                
            return article_text if article_text else None
            
        except Exception as e:
            self.logger.error(f"Error getting article summary: {e}")
            return None 