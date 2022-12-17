from bs4 import BeautifulSoup
from common import split_into_ranges, DEBUG, save_image
from AkwamCommon import *
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import json
from time import perf_counter

MAIN_PAGE_URL = "https://akwam.to/movies?section=0&category=0&rating=0&year=0&language=1&formats=0&quality=0"


def get_movie(movies_links: list[str]) -> dict:
    movies_dict = {}

    for link in movies_links:
        movie_page = get_website_safe(link)
        soup = BeautifulSoup(movie_page.content, "html.parser")

        movie_id = link.split("/")[4]

        movie_title = soup.find(
            "h1", class_="entry-title font-size-28 font-weight-bold text-white mb-0").text

        image_url = soup.find(
            "div", "col-lg-3 col-md-4 text-center mb-5 mb-md-0").find("a")["href"]

        short_link_id = soup.find(
            "a", class_="link-btn link-show d-flex align-items-center px-3")["href"].split("/")[-1]

        movies_dict[movie_id] = {
            "Title": movie_title,
            "Category": "arabic-movies",
            "Image Source": save_image(image_url, movie_id + "-akwam", False, get_website_safe),
            "Source": f"https://akwam.to/watch/{short_link_id}/{movie_id}"
        }

    return movies_dict


def scrape_all_movies(page_range: tuple[int]) -> dict:
    movies_dict = {}

    for page in range(page_range[0], page_range[1]):
        main_page = get_website_safe(MAIN_PAGE_URL + f"&page={page}")

        with ThreadPoolExecutor() as executor:
            results = executor.map(get_movie, split_anchor_links(main_page))

        for result in results:
            movies_dict.update(result)

        print(f"Done scraping page {page}")

    return movies_dict


def main():
    page_ranges = split_into_ranges(8, get_last_page_number(MAIN_PAGE_URL))
    print(page_ranges)

    master_dict = {}

    with ProcessPoolExecutor() as executor:
        results = executor.map(scrape_all_movies, page_ranges)

    for result in results:
        master_dict.update(result)

    with open("./output/arabic-movies.json", "w", encoding="utf-8") as fp:
        json.dump(master_dict, fp, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print(
        f"Finished scraping all Arabic movies from akwam in about {round((end_time - start_time) / 60)} minute(s)"
    )
else:
    pass
