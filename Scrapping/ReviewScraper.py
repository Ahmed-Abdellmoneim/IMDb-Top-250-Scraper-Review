import os
import time
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_empty_csv_file(file_path, headers):
    folder_path = os.path.dirname(file_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    df = pd.DataFrame(columns=headers)
    df.to_csv(file_path, index=False)
    print(f"Empty CSV file '{file_path}' created successfully.")


def append_to_csv(csv_file_path, data):
    df = pd.DataFrame(data)
    df.to_csv(csv_file_path, mode="a", header=False, index=False)


URL = "https://m.imdb.com"
csvReviews = os.path.join(".", "CSV Folder", "Review.csv")
create_empty_csv_file(csvReviews, headers=["Movie", "Title", "Review", "Rank"])
header = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(header)
driver = webdriver.Chrome(options=options)

try:
    driver.get(URL + "/chart/top/")
    Blocks = driver.find_elements(
        By.XPATH,
        '//li[contains(@class, "ipc-metadata-list-summary-item sc-10233bc-0 iherUv cli-parent")]',
    )
    print(f"Total Blocks found: {len(Blocks)}")

    for idx, Block in enumerate(tqdm(Blocks, desc="Processing Blocks")):

        """
        Get The Data of The Movies
        """

        movieURL = driver.find_elements(
            By.XPATH,
            '//a[@class="ipc-title-link-wrapper"]',
        )[idx].get_attribute("href")

        movieTitle = driver.find_elements(
            By.XPATH,
            '//div[@class="sc-b189961a-0 hBZnfJ cli-children"]//h3[@class="ipc-title__text"]',
        )[idx].text
        movieTitle = movieTitle.split(". ", 1)[1]

        # Navigate the Movie Page
        driver.get(movieURL)

        reviewLink = driver.find_element(
            By.XPATH,
            '//div[@data-testid="reviews-header"]//a[@class="ipc-title-link-wrapper"]',
        ).get_attribute("href")

        # Navigate to The Review Page
        driver.get(reviewLink)

        """
        Get the Reviews of the Movies
        """

        # Click "Load More" until it disappears
        while True:
            try:
                loadMoreButton = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//button[@class="ipl-load-more__button"]')
                    )
                )
                driver.execute_script("arguments[0].scrollIntoView();", loadMoreButton)
                loadMoreButton.click()
                time.sleep(10)
            except Exception as e:
                print(f"No more 'Load More' button or timeout occurred. Error: {e}")
                break

        # Scrape All the Reviews for single Movie
        reviewBlocks = driver.find_elements(
            By.XPATH, '//li[@class="ipl-content-list__item"]'
        )
        print(f"The Movie {movieTitle} has {len(reviewBlocks)} Reviews")

        # Variables for each Movie
        reviewTitles = []
        reviewRatings = []
        reviewContents = []

        for id, reviewBlock in enumerate(
            tqdm(reviewBlocks, desc="Processing Review Blocks")
        ):
            try:
                reviewRating = reviewBlock.find_element(
                    By.XPATH,
                    './/span[@class="rating-other-user-rating"]//span[1]',
                ).text

                reviewTitle = reviewBlock.find_element(
                    By.XPATH,
                    './/a[@class="title"]',
                ).get_attribute("innerText")

                reviewContent = reviewBlock.find_element(
                    By.XPATH,
                    './/div[@class="text"]',
                ).text

                # Check if All the Data is There
                if reviewRating == "" or reviewTitle == "" or reviewContent == "":
                    print(f"Skipping review block {id + 1} due to missing data")
                    continue

                reviewRatings.append(reviewRating)
                reviewTitles.append(reviewTitle)
                reviewContents.append(reviewContent)

            except Exception as e:
                print(f"Skipping review block {id + 1} due to missing data")
                continue

        print(f"The Length of the Rank is {len(reviewRatings)}")
        print(f"The Length of the Titles is {len(reviewTitles)}")
        print(f"The Length of the Content is {len(reviewContents)}")

        append_to_csv(
            csvReviews,
            {
                "Movie": [movieTitle] * len(reviewTitles),
                "Title": reviewTitles,
                "Review": reviewContents,
                "Rank": reviewRatings,
            },
        )

        # Return to the Main Page
        driver.get(URL + "/chart/top/")
        time.sleep(10)

finally:
    driver.quit()
