import os
import time
import hashlib
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def convertArrToString(arr):
    string = ""
    for i in arr:
        string += i
        string += ", "
    return string[:-2]


def create_empty_csv_file(file_path, headers):
    folder_path = os.path.dirname(file_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    df = pd.DataFrame(columns=headers)
    df.to_csv(file_path, index=False)
    print(f"Empty CSV file '{file_path}' created successfully.")


def append_to_csv(csvFilePath, data):
    df = pd.DataFrame(data)
    df.to_csv(csvFilePath, mode="a", header=False, index=False)


def generateHash(s):
    return hashlib.sha256(s.encode()).hexdigest()


def readCSVToDict(csvFilePath):
    if os.path.exists(csvFilePath):
        print(f"CSV file '{csvFilePath}' has been read successfully.")
        return pd.read_csv(csvFilePath).to_dict(orient="records")
    return []


def updateCSV(csvFilePath, updatedData, hashValue):
    df = pd.read_csv(csvFilePath)
    df.loc[df["HashURL"] == hashValue] = updatedData
    df.to_csv(csvFilePath, index=False)


URL = "https://m.imdb.com"
csvFilePath = os.path.join(".", "CSV Folder", "Data.csv")
csvHashMovies = os.path.join(".", "CSV Folder", "Hash Movies.csv")
# create_empty_csv_file(
#    csvFilePath,
#    headers=[
#        "Film Title",
#        "IMDb Rating",
#        "Release Year",
#        "Genre",
#        "Director",
#        "Movie Image",
#        "Stars",
#    ],
# )
# create_empty_csv_file(csvHashMovies, headers=["HashURL"])
# Read the hash CSV and the data CSV into dictionaries
hashData = readCSVToDict(csvHashMovies)
existingData = readCSVToDict(csvFilePath)
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
        Hash The Link of The Movies
        """

        movieURL = driver.find_elements(
            By.XPATH,
            '//a[@class="ipc-title-link-wrapper"]',
        )[idx].get_attribute("href")
        hashmovieURL = generateHash(movieURL)

        if hashData[idx]["HashURL"] == hashmovieURL:
            # Update the Movie Rating
            rating = driver.find_elements(
                By.XPATH,
                '//span[@class="ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating"]',
            )[idx].text
            rating = rating[:3]
            existingData[idx]["IMDb Rating"] = rating

            print(f"Skipping already processed movie: {movieURL}")
            continue
        else:
            """
            Get The Data of The Movies
            """

            movieTitle = driver.find_elements(
                By.XPATH,
                '//div[@class="sc-b189961a-0 hBZnfJ cli-children"]//h3[@class="ipc-title__text"]',
            )[idx].text
            movieTitle = movieTitle.split(". ", 1)[1]

            releaseYearBox = driver.find_elements(
                By.XPATH, '//div[@class="sc-b189961a-7 feoqjK cli-title-metadata"]'
            )[idx]
            releaseYear = releaseYearBox.find_elements(
                By.XPATH,
                './/span[@class="sc-b189961a-8 kLaxqf cli-title-metadata-item"]',
            )[0].text

            rating = driver.find_elements(
                By.XPATH,
                '//span[@class="ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating"]',
            )[idx].text
            rating = rating[:3]

            movieImage = driver.find_elements(
                By.XPATH,
                '//img[@class="ipc-image"]',
            )[
                idx
            ].get_attribute("src")

            # Navigate the Movie Page
            driver.get(movieURL)

            # Wait for genres to be present
            genresTag = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        '//div[@class="ipc-chip-list__scroller"]//a[@class="ipc-chip ipc-chip--on-baseAlt"]//span[@class="ipc-chip__text"]',
                    )
                )
            )
            genres = [genre.text for genre in genresTag]
            genres = convertArrToString(genres)

            # Wait for directors to be present
            directorTag = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//li[@data-testid="title-pc-principal-credit"]')
                )
            )

            directorsTags = directorTag.find_elements(
                By.XPATH,
                './/a[@class="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"]',
            )
            directors = [
                director.get_attribute("innerText") for director in directorsTags
            ]
            directors = convertArrToString(directors)

            # Navigate to cast link
            castLink = driver.find_element(
                By.XPATH,
                '//div[@data-testid="title-cast-header"]//a[@class="ipc-title-link-wrapper"]',
            ).get_attribute("href")
            driver.get(castLink)

            # Wait for cast members to be present
            castMembers = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[@class="media-body media-vertical-align"]//h4')
                )
            )
            castCrew = [cast.text for cast in castMembers]
            castCrew = convertArrToString(castCrew)

            # Update the Movie Data
            hashData[idx]["HashURL"] = hashmovieURL
            existingData[idx]["Genre"] = genres
            existingData[idx]["Stars"] = castCrew
            existingData[idx]["IMDb Rating"] = rating
            existingData[idx]["Director"] = directors
            existingData[idx]["Film Title"] = movieTitle
            existingData[idx]["Movie Image"] = movieImage
            existingData[idx]["Release Year"] = releaseYear

            # Return to the Main Page
            driver.get(URL + "/chart/top/")

            time.sleep(20)

finally:
    driver.quit()
