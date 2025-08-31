import click
import asyncio
import os
from .core import YouTubeFeedCustomizer

@click.command()
@click.argument('description')
@click.option('--duration', default=5, help='Duration to play each video (seconds)')
@click.option('--headless', default=True, type=bool, help='Run browser in headless mode (True/False)')
@click.option('--browser', default='chrome', type=click.Choice(['chrome', 'firefox']), help='Browser to use (chrome or firefox)')
def main(description, duration, headless, browser):
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

    customizer = YouTubeFeedCustomizer(browser=browser, headless=headless)
    asyncio.run(customizer.customize_feed(description, duration=duration))

    click.echo("\nFeed customization complete! Your YouTube recommendations should start updating soon.")
    click.echo("Tip: For best results, interact with similar videos that appear in your feed.")

if __name__ == '__main__':
    main()
