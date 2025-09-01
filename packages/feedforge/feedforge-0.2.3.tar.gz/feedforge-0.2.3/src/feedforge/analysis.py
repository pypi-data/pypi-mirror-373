from __future__ import annotations

import asyncio
import os
from typing import List, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


class Analyzer:
    """Encapsulates analysis of user input into keywords and similar videos."""

    def __init__(self) -> None:
        self._load_env()
        openai_key = os.getenv('OPENAI_API_KEY')
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        if not openai_key or not youtube_key:
            raise ValueError("Both OPENAI_API_KEY and YOUTUBE_API_KEY must be set in .env file")

                # Initialize API clients with real keys
        self.llm = ChatOpenAI(model='gpt-4o', api_key=openai_key)
        self.youtube = build('youtube', 'v3', developerKey=youtube_key)

    def _load_env(self) -> None:
        current_dir = Path.cwd()
        while current_dir.parent != current_dir:
            if (current_dir / '.env').exists():
                load_dotenv(current_dir / '.env')
                return
            current_dir = current_dir.parent
        # If not found, load defaults (no error), FastAPI may still inject env
        load_dotenv()

    async def generate_keywords(self, user_input: str, num_keywords: int = 5) -> List[str]:
        prompt = (
            f"Based on this description of video interests: \"{user_input}\"\n"
            f"Generate {num_keywords} specific YouTube search keywords or phrases that would find relevant content.\n"
            f"Return only the keywords, separated by commas. Make them specific and targeted."
        )

        messages = [HumanMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)

        content: str
        if hasattr(response, 'content'):
            content = response.content
        elif hasattr(response, 'completion'):
            content = response.completion
        else:
            content = str(response)

        keywords = [kw.strip() for kw in content.strip().split(',') if kw.strip()]
        return keywords

    async def search_videos(self, keywords: List[str], max_results_per_keyword: int = 2) -> List[str]:
        def search_for_keyword(keyword: str) -> Dict[str, Any]:
            try:
                request = self.youtube.search().list(
                    part="id",
                    q=keyword,
                    type="video",
                    maxResults=max_results_per_keyword,
                    videoDefinition="high",
                    relevanceLanguage="en",
                )
                response = request.execute()
                videos = [
                    f"https://www.youtube.com/watch?v={item['id']['videoId']}&mute=1"
                    for item in response.get('items', [])
                ]
                return {"keyword": keyword, "videos": videos}
            except Exception:
                return {"keyword": keyword, "videos": []}

        tasks = [asyncio.to_thread(search_for_keyword, keyword) for keyword in keywords]
        results = await asyncio.gather(*tasks)
        keyword_videos = {result['keyword']: result['videos'] for result in results}

        all_videos: List[str] = []
        seen = set()
        keyword_indices = {keyword: 0 for keyword in keywords}
        active_keywords = set(keywords)

        while active_keywords:
            active_keywords = {k for k in active_keywords if keyword_indices[k] < len(keyword_videos.get(k, []))}
            if not active_keywords:
                break
            import random
            keyword = random.choice(list(active_keywords))
            idx = keyword_indices[keyword]
            if idx < len(keyword_videos[keyword]):
                video = keyword_videos[keyword][idx]
                if video not in seen:
                    seen.add(video)
                    all_videos.append(video)
                keyword_indices[keyword] += 1

        return all_videos

    async def analyze(self, description: str, max_results_per_keyword: int = 2, num_keywords: int = 5) -> Dict[str, Any]:
        keywords = await self.generate_keywords(description, num_keywords=num_keywords)
        videos = await self.search_videos(keywords, max_results_per_keyword=max_results_per_keyword)
        return {"keywords": keywords, "videos": videos}
