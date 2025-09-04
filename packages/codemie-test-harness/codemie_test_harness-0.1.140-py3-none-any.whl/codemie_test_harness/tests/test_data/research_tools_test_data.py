import pytest

from codemie_test_harness.tests.enums.tools import ResearchToolName

search_tools_test_data = [
    (
        ResearchToolName.GOOGLE_SEARCH,
        """
            Run Google Search Tool and query: AI trends.
            Represent in JSON format with title and link
        """,
        50,
    ),
    pytest.param(
        ResearchToolName.TAVILY_SEARCH,
        """
            Run Google Search Tool and query: AI trends
            Represent in JSON format with title and link
        """,
        50,
        marks=pytest.mark.skip(
            reason="Temporarily skipping Tavily test until it is fixed"
        ),
    ),
]
interactions_tools_test_data = [
    (
        ResearchToolName.GOOGLE_PLACES,
        "Find McDonald in the Kyiv on the Khreschatyk in radius 2 km",
        """
            I found a McDonald's location on Khreschatyk Street in Kyiv:
            McDonald's
            Address: Khreschatyk St, 19-a, Kyiv, Ukraine
            Rating: 4.4 (based on 21,802 user ratings)
            Open Now: Yes
            Price Level: 2
        """,
    ),
    (
        ResearchToolName.GOOGLE_PLACES_FIND_NEAR,
        "Find McDonalds in the Kyiv near Khreschatyk in radius 2 km",
        """
            I found a McDonald's location on Khreschatyk Street in Kyiv:
            McDonald's
            Address: Khreschatyk St, 19-a, Kyiv, Ukraine
            Rating: 4.4 (based on 21,802 user ratings)
            Open Now: Yes
            Price Level: 2
        """,
    ),
    (
        ResearchToolName.WIKIPEDIA,
        "Short description of AI from Wikipedia",
        """
            Artificial intelligence (AI) is the capability of computer systems to perform tasks requiring human intelligence,
            such as learning, reasoning, problem-solving, and decision-making. It encompasses various technologies and methods,
            including machine learning and neural networks, enabling machines to perceive their environment, adapt, and take
            actions to achieve specific goals. AI applications include virtual assistants, self-driving cars, recommendation systems,
            and advanced game play, with ongoing advancements raising ethical and regulatory considerations.
        """,
    ),
    (
        ResearchToolName.WEB_SCRAPPER,
        "Web Scrap this page https://webscraper.io/about-us",
        """
            Here is the scraped content from the [Web Scraper - About Us](https://webscraper.io/about-us) page:
            # About us | Web Scraper
            ## Our story
            Web Scraper started as a Chrome browser extension in 2013. Its popularity quickly grew as it was the most advanced and completely free. Today Web Scraper is both a free browser extension and also a Cloud based Web Scraping solution for complete automation.
            ## Our mission
            Our mission is to make web data accessible to everyone by making the most advanced and easiest to use web scraping tool.
            ![About us image](https://webscraper.io/img/about-us.jpg)
            ## Company data
            - **Company**: “Web Graph“ SIA
            - **Registration number**: 40203093908
            - **VAT number**: LV40203093908
            - **Address**: Ubelu 5-71, Adazi, Latvia, LV-2164
            - **Bank**: “Swedbank” AS
            - **Bank account**: LV31HABA0551044098666
            ## Products
            - [Web Scraper browser extension](https://chromewebstore.google.com/detail/web-scraper-free-web-scra/jnhgnonknehpejjnehehllkliplmbmhn?hl=en)
            - [Web Scraper Cloud](https://webscraper.io/cloud-scraper)
            ## Company
            - [About us](https://webscraper.io/about-us)
            - [Contact](https://webscraper.io/contact)
            - [Website Privacy Policy](https://webscraper.io/privacy-policy)
            - [Browser Extension Privacy Policy](https://webscraper.io/extension-privacy-policy)
            - [Media kit](https://webscraper.io/downloads/Web_Scraper_Media_Kit.zip)
            - [Jobs](https://webscraper.io/jobs)
            ## Resources
            - [Blog](https://webscraper.io/blog)
            - [Documentation](https://webscraper.io/documentation)
            - [Video Tutorials](https://webscraper.io/tutorials)
            - [Screenshots](https://webscraper.io/screenshots)
            - [Test Sites](https://webscraper.io/test-sites)
            - [Forum](https://forum.webscraper.io/)
            - [Status](https://status.webscraper.io/)
            ## Contact Us
            - Email: [info@webscraper.io](mailto:info@webscraper.io)
            - Address: Ubelu 5-71, Adazi, Latvia, LV-2164
            **Copyright © 2025 Web Scraper | All rights reserved**
        """,
    ),
]
