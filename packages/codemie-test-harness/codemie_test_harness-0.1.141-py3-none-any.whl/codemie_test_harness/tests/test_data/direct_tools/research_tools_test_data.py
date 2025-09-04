import pytest

from codemie_test_harness.tests.enums.tools import ResearchToolName

research_tools_test_data = [
    (
        ResearchToolName.GOOGLE_SEARCH,
        {"query": "AI trends 2024"},
        """
        {'title': 'Data and AI Trends 2024', 'link': 'https://data-ai-trends.withgoogle.com/',
        'snippet': 'Data is the fuel for AI, and what powers its effectiveness. To truly take advantage of generative AI,
        you need to ground AI in your enterprise data.'}, {'title': 'McKinsey technology trends outlook 2025 | McKinsey', 'link':
        'https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/the-top-trends-in-tech', 'snippet': 'Jul 22, 2025 ...
        An overarching artificial intelligence category replaces these four trends: applied AI ... By 2024, the interest score for
        Artificial intelligence\xa0...'}, {'title': '3 big AI trends to watch in 2024', 'link': 'https://news.microsoft.com/three-big-ai-trends-to-watch-in-2024/',
         'snippet': 'Feb 12, 2024 ... 3 big AI trends to watch in 2024 · Small language models · Multimodal AI · AI in science. Experts are anticipating major
         gains in AI tools\xa0...'}, {'title': '2024 Global Trends in AI - WEKA', 'link': 'https://www.weka.io/resources/analyst-report/2024-global-trends-in-ai/',
          'snippet': 'Discover key AI trends in 2024. Explore generative AI, scaling challenges, GPU demand, and sustainable practices. Download the S&P Global
          report.'}, {'title': 'AI Index | Stanford HAI', 'link': 'https://hai.stanford.edu/ai-index', 'snippet': 'The AI Index offers one of
          the most comprehensive, data-driven views of artificial intelligence. Recognized as a trusted resource by global media, governments,\xa0...'},
          {'title': '7 rapid AI trends happening in 2025 | Khoros', 'link': 'https://khoros.com/blog/ai-trends', 'snippet': 'AI trends in e-commerce ·
          Automated dynamic pricing (adjusting pricing in real-time based on various factors) · AI-powered search and discovery to better capture\xa0...'},
           {'title': "IDC's 2024 AI opportunity study: Top five AI trends to watch - The ...", 'link': 'https://blogs.microsoft.com/blog/2024/11/12/idcs-2024-ai-opportunity-study-top-five-ai-trends-to-watch/', 'snippet': "Nov 12, 2024 ... IDC's 2024 top 5 trends for AI · #1 Enhanced productivity has become table stakes. · #2 Companies are gravitating to more advanced AI solutions."}, {'title': 'Five Key Trends in AI and Data Science for 2024', 'link': 'https://sloanreview.mit.edu/article/five-key-trends-in-ai-and-data-science-for-2024/', 'snippet': 'Jan 9, 2024 ... 1. Generative AI sparkles but needs to deliver value. · 2. Data science is shifting from artisanal to industrial. · 3. Two versions of data\xa0...'}, {'title': 'Top 5 AI Trends to Watch in 2025 | Coursera', 'link': 'https://www.coursera.org/articles/ai-trends', 'snippet': 'Mar 25, 2025 ... In March 2024, the European Union debated a landmark comprehensive AI bill designed to regulate AI and address concerns for consumers. It became\xa0...'}, {'title': '2025 AI Trends for Marketers', 'link': 'https://offers.hubspot.com/ai-marketing', 'snippet': '... AI from a side project into their competitive edge. Get the Free Report in the 2024 report. 05.2025 - AI for Marketers - LP Feat Image. 2025. AI Trends for\xa0...'}]
        """,
    ),
    pytest.param(
        ResearchToolName.TAVILY_SEARCH,
        {
            "query": "AI trends 2024",
        },
        """
        answer
        """,
        marks=pytest.mark.skip(
            reason="Temporarily skipping Tavily test until it is fixed"
        ),
    ),
    (
        ResearchToolName.GOOGLE_PLACES,
        {"query": "McDonalds in Kyiv Pechersk"},
        """
        1. McDonald`s
        Address: Mykoly Mikhnovskoho Blvd, 33а, Kyiv, Ukraine, 02000
        Google place ID: ChIJ6VRsfMvP1EARzU53lRLoyNY
        Phone: Unknown
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        2. McDonald's
        Address: Ivan Mazepa St, 1, Kyiv, Ukraine, 02000
        Google place ID: ChIJhS93nAPP1EARK_wse3FkC2A
        Phone: 050 323 5560
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        3. McDonald's
        Address: Khreschatyk St, 19-a, Kyiv, Ukraine, 01001
        Google place ID: ChIJR10zt1bO1EARzFVgiVtzgQQ
        Phone: 050 386 3077
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        4. McDonald's
        Address: Velyka Vasylkivska St, 22, Kyiv, Ukraine, 02000
        Google place ID: ChIJnxzJyf7O1EARoJ9OclXxvxA
        Phone: 050 463 2116
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        5. McDonald's
        Address: Demiivska Square, 1, Kyiv, Ukraine, 02000
        Google place ID: ChIJW--WXDfP1EAR0PCTBPlGIS0
        Phone: 050 463 4065
        Website: http://www.mcdonalds.ua/ukr/najblizhchij-makdonaljdz/41/


        6. McDonald's
        Address: Antonovycha St, 176, 1 Poverkh, Kyiv, Ukraine, 03150
        Google place ID: ChIJ89EnF3TE1EARI2pQahE8o6E
        Phone: 095 273 8065
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        7. McDonald’s
        Address: Antonovycha St, 176, 2 поверх, Kyiv, Ukraine, 03680
        Google place ID: ChIJwZqV4zvP1EARK6eT4K7kaPI
        Phone: 095 273 8066
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        8. McDonald's
        Address: Sofiivs'ka St, 1/2, Kyiv, Ukraine, 01001
        Google place ID: ChIJOailWFDO1EARToEABwvJTbU
        Phone: 050 334 0422
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        9. McDonald's
        Address: Bohdana Khmel'nyts'koho St, 40/25, Kyiv, Ukraine, 01030
        Google place ID: ChIJjWkM4DbZ1EAR--4oZh9XwGA
        Phone: 050 463 9123
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        10. McDonalds
        Address: Ivana Mykolaichuka St, 16, Kyiv, Ukraine, 02000
        Google place ID: ChIJG80R5d3F1EAR2f7HuHAB5w0
        Phone: 095 328 2733
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        11. McDonald's
        Address: Borychiv Descent, 10А, Kyiv, Ukraine, 04070
        Google place ID: ChIJh3HPZkbO1EARWC7LTOqpaHY
        Phone: 095 272 1033
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        12. McDonald’s
        Address: Sicheslavska St, 6, Kyiv, Ukraine, 02000
        Google place ID: ChIJjV0cwJLO1EARIHlut47gm4c
        Phone: 050 386 9092
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        13. McDonald's
        Address: Vokzal'na Square, 2, Kyiv, Ukraine, 01032
        Google place ID: ChIJF3afFWrP1EARzfE8DP4TiPc
        Phone: 050 463 9133
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        14. Будівництво McDonalds
        Address: Pozniaky, Kyiv, Ukraine, 02000
        Google place ID: ChIJCe9UdgDF1EARzVld3kEFEJ8
        Phone: Unknown
        Website: Unknown


        15. KFC
        Address: Lesi Ukrainky Blvd, 26, Kyiv, Ukraine, 02000
        Google place ID: ChIJA2xBCHHP1EARdPNX4qMqHtw
        Phone: 067 560 2544
        Website: https://kfc.ua/


        16. McDonald's
        Address: Heorhiia Kirpy St, 5-а, Kyiv, Ukraine, 02000
        Google place ID: ChIJTVVl8-zO1EARuBqq9ke6Le0
        Phone: 050 356 1189
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        17. McDonald's
        Address: Vulytsya Yevhena Sverstyuka, 1, Kyiv, Ukraine, 02000
        Google place ID: ChIJSUsh1fHP1EARjVwA1Dh3m-w
        Phone: 050 463 8509
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        18. McDonald’s (будується)
        Address: Oleny Pchilky St, 1, Kyiv, Ukraine, 02000
        Google place ID: ChIJuebjagDF1EARzhVGCNHkzV4
        Phone: Unknown
        Website: http://mcdonalds.com/


        19. McDonald’s
        Address: Borshchahivska St, 2-б, Kyiv, Ukraine, 03056
        Google place ID: ChIJB7xWP4_O1EARYOxU8nmxLQI
        Phone: 050 463 8515
        Website: https://www.mcdonalds.com/ua/uk-ua.html


        20. McDonald's
        Address: Mykhaila Hryshka St, 7, Kyiv, Ukraine, 02000
        Google place ID: ChIJqxjOKrPF1EAR2_ySSJxA-vc
        Phone: 050 463 3402
        Website: https://www.mcdonalds.com/ua/uk-ua.html
        """,
    ),
    (
        ResearchToolName.GOOGLE_PLACES_FIND_NEAR,
        {"current_location_query": "Kyiv", "target": "McDonalds", "radius": 20},
        """
        [{'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 50.4512347, 'lng': 30.52158039999999},
                'viewport': {'northeast': {'lat': 50.45260392989272,
                'lng': 30.52294777989271},
                'southwest': {'lat': 50.44990427010727,
                'lng': 30.52024812010727}}},
        'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png',
        'icon_background_color': '#FF9E67',
        'icon_mask_base_uri': 'https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet',
        'name': "McDonald's", 'opening_hours': {'open_now': True}, 'photos': [{'height': 3472, 'html_attributions': [
                '<a href="https://maps.google.com/maps/contrib/105080954131297233218">Viktoriia Saienko</a>'],
                        'photo_reference': '',
                        'width': 4640}],
        'place_id': 'ChIJOailWFDO1EARToEABwvJTbU', 'price_level': 2, 'rating': 4.3,
        'reference': 'ChIJOailWFDO1EARToEABwvJTbU', 'scope': 'GOOGLE',
        'types': ['restaurant', 'food', 'point_of_interest', 'establishment'], 'user_ratings_total': 11087,
        'vicinity': "Sofiivs'ka St, 1/2, Kyiv"}], 
        """,
    ),
    (
        ResearchToolName.WEB_SCRAPPER,
        {
            "url": "https://webscraper.io/about-us",
        },
        """
        # About us | Web Scraper

        *Source: https://webscraper.io/about-us*
        
        About us | Web Scraper
        
        Toggle navigation
        
        [![Web Scraper](/img/logo_white.svg)](/)
        
        * [Web Scraper](/)
        * [Cloud Scraper](/cloud-scraper)
        * [Pricing](/pricing)
        * Learn
        
          * [Documentation](/documentation)
          * [Video Tutorials](/tutorials)
          * [Test Sites](/test-sites)
          * [Forum](https://forum.webscraper.io/)
        * [Install](https://chromewebstore.google.com/detail/web-scraper-free-web-scra/jnhgnonknehpejjnehehllkliplmbmhn?hl=en)
        * [Cloud Login](https://cloud.webscraper.io/)
        
        # About us
        
        ## Our story
        
        Web Scraper started as a Chrome browser extension in 2013. Its
        popularity quickly grew as it was the most advanced and completely
        free. Today Web Scraper is both a free browser extension and also a
        Cloud based Web Scraping solution for complete automation.
        
        ## Our mission
        
        Our mission is to make web data accessible to everyone by making
        the most advanced and easiest to use web scraping tool.
        
        ![](/img/about-us.jpg)
        
        ## Company data
        
        * Company: “Web Graph“ SIA
        * Registration number: 40203093908
        * VAT number: LV40203093908
        * Address: Ubelu 5-71, Adazi, Latvia, LV-2164
        * Bank: “Swedbank” AS
        * Bank account: LV31HABA0551044098666
        
        * Products
        * [Web Scraper browser extension](https://chromewebstore.google.com/detail/web-scraper-free-web-scra/jnhgnonknehpejjnehehllkliplmbmhn?hl=en)
        * [Web Scraper Cloud](/cloud-scraper)
        
        * Company
        * [About us](/about-us)
        * [Contact](/contact)
        * [Website Privacy Policy](/privacy-policy)
        * [Browser Extension Privacy Policy](/extension-privacy-policy)
        * [Media kit](https://webscraper.io/downloads/Web_Scraper_Media_Kit.zip)
        * [Jobs](/jobs)
        
        * Resources
        * [Blog](/blog)
        * [Documentation](/documentation)
        * [Video Tutorials](/tutorials)
        * [Screenshots](/screenshots)
        * [Test Sites](/test-sites)
        * [Forum](https://forum.webscraper.io/)
        * [Status](https://status.webscraper.io/)
        
        * CONTACT US
        * [info@webscraper.io](mailto:info@webscraper.io)
        * Ubelu 5-71,  
        
           Adazi, Latvia, LV-2164
        
        Copyright © 2025
        **Web Scraper** | All rights reserved
        """,
    ),
    (
        ResearchToolName.WIKIPEDIA,
        {"query": "Ethics of artificial intelligence"},
        """
        Page: Ethics of artificial intelligence
        Summary: The ethics of artificial intelligence covers a broad range of topics within AI that are considered to have particular
        ethical stakes. This includes algorithmic biases, fairness, automated decision-making, accountability, privacy, and regulation.
        It also covers various emerging or potential future challenges such as machine ethics (how to make machines that behave ethically),
        lethal autonomous weapon systems, arms race dynamics, AI safety and alignment, technological unemployment, AI-enabled misinformation,
         how to treat certain AI systems if they have a moral status (AI welfare and rights), artificial superintelligence and existential risks.
        Some application areas may also have particularly important ethical implications, like healthcare, education, criminal justice, or the military.
        
        Page: Friendly artificial intelligence
        Summary: Friendly artificial intelligence (friendly AI or FAI) is hypothetical artificial general intelligence (AGI)
        that would have a positive (benign) effect on humanity or at least align with human interests such as fostering the improvement of the
        human species. It is a part of the ethics of artificial intelligence and is closely related to machine ethics. While machine ethics is
        concerned with how an artificially intelligent agent should behave, friendly artificial intelligence research is focused on how to practically
        bring about this behavior and ensuring it is adequately constrained.
        
        Page: Regulation of artificial intelligence
        Summary: Regulation of artificial intelligence is the development of public sector policies and laws for promoting and
        regulating artificial intelligence (AI). It is part of the broader regulation of algorithms. The regulatory and policy landscape
        for AI is an emerging issue in jurisdictions worldwide, including for international organizations without direct enforcement power
        like the IEEE or the OECD. Since 2016, numerous AI ethics guidelines have been published in order to maintain social control over
        the technology. Regulation is deemed necessary to both foster AI innovation and manage associated risks. Furthermore, organizations
        deploying AI have a central role to play in creating and implementing trustworthy AI, adhering to established principles, and taking
        accountability for mitigating risks. Regulating AI through mechanisms such as review boards can also be seen as social means to approach
        the AI control problem.
        """,
    ),
]
