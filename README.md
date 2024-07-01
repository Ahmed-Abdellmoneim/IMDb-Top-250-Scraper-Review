# IMDb Top 250 Movies Scraper

This project involves comprehensive web scraping of IMDb's Top 250 movies using Selenium and Python. The objective is to gather detailed data on each movie, including extensive user reviews. We successfully scraped reviews for over 250 movies, storing the data in a CSV file for further analysis.

In addition to data collection, we developed a machine-learning pipeline and neural network models. These models classify sentiment in reviews and predict ratings, even when not explicitly provided. This deepens our understanding of audience opinions and enhances insights into movie ratings based on textual reviews.

Furthermore, we conducted a comparative analysis between traditional machine learning models and neural networks to determine which approach achieves superior results in sentiment classification and rating prediction.

## Scraping

Using Selenium for web scraping IMDb offers several advantages:

1. **Realistic Interaction**: Selenium mimics user interaction, handling dynamic content and AJAX requests effectively, which can be challenging with simple HTTP requests.

2. **JavaScript Rendering**: Selenium fully renders pages with heavy JavaScript usage or dynamic content loading, ensuring comprehensive data capture.

3. **Handling Dynamic Content**: Explicit waits (`WebDriverWait`) in Selenium ensure elements are fully loaded before scraping, maintaining data integrity.

4. **Complex Navigation**: Selenium facilitates navigation through multiple pages and interaction with various elements like dropdowns and forms.

5. **Visual Feedback**: Operating in a browser instance provides visual verification of the scraping process, aiding in debugging and ensuring accuracy.

6. **Politeness Factor**: Selenium allows controlled interaction to avoid server overload, adhering to ethical scraping practices.

## After-processing of the Data

Post-scraping, the data underwent thorough processing and analysis:
