import click
import asyncio
import os
from .core import YouTubeFeedCustomizer

@click.command()
@click.argument('description')
@click.option('--duration', default=5, help='Duration to play each video (seconds)')
@click.option('--headless', default=True, type=bool, help='Run browser in headless mode (True/False)')
@click.option('--browser', default='chrome', type=click.Choice(['chrome', 'firefox']), help='Browser to use (chrome or firefox)')
@click.option('--openai-key', envvar='OPENAI_API_KEY', help='OpenAI API key (can also be set via OPENAI_API_KEY env var)')
@click.option('--youtube-key', envvar='YOUTUBE_API_KEY', help='YouTube API key (can also be set via YOUTUBE_API_KEY env var)')
def main(description, duration, headless, browser, openai_key, youtube_key):
    """Customize your YouTube feed based on your content interests.

    DESCRIPTION: Describe the kind of content you want to see

    \b
    Example:
    feedforge "I want to see videos about people building successful side projects and sharing their journey"

    \b
    More examples:
    feedforge "machine learning tutorials for beginners" --duration 3
    feedforge "startup founders sharing their stories" --browser firefox --headless false
    """
    click.echo(f"Analyzing your content preferences...")

    try:
        customizer = YouTubeFeedCustomizer(
            analysis_base_url="https://feedforge-backend.rishabhbhandari6.workers.dev"
        )
        asyncio.run(customizer.customize_feed(description, duration=duration, browser=browser))
    except ValueError as e:
        click.echo(f"\nError: {e}", err=True)
        click.echo("\nFor more information on getting API keys, visit:")
        click.echo("- OpenAI: https://platform.openai.com/api-keys")
        click.echo("- YouTube: https://console.cloud.google.com/apis/credentials")
        return

    click.echo("\nFeed customization complete! Your YouTube recommendations should start updating soon.")
    click.echo("Tip: For best results, interact with similar videos that appear in your feed.")

if __name__ == '__main__':
    main()
