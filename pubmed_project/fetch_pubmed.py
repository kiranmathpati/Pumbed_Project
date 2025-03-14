import requests
import argparse
import xmltodict
import pandas as pd
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# PubMed API Base URLs
PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Function to fetch PubMed article IDs
def fetch_pubmed_articles(query: str, max_results: int = 10) -> List[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "xml",
    }

    logging.info(f"🔎 Searching PubMed for: {query}...")

    response = requests.get(PUBMED_API_URL, params=params)
    response.raise_for_status()

    # Parse XML response
    data: Dict[str, Any] = xmltodict.parse(response.text)
    article_ids = data["eSearchResult"].get("IdList", {}).get("Id", [])

    if not article_ids:
        logging.warning("⚠ No articles found for the given query.")
        return []

    logging.info(f"📄 Found {len(article_ids)} articles. Fetching details...")

    return article_ids

# Function to fetch article details from PubMed
def fetch_article_details(article_ids: List[str]) -> List[Dict[str, Any]]:
    if not article_ids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(article_ids),
        "retmode": "xml",
    }

    response = requests.get(PUBMED_FETCH_URL, params=params)
    response.raise_for_status()

    data: Dict[str, Any] = xmltodict.parse(response.text)
    articles = data["PubmedArticleSet"].get("PubmedArticle", [])

    return articles if isinstance(articles, list) else [articles]

# Function to extract relevant article information
def extract_article_info(articles: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []

    for article in articles:
        medline = article.get("MedlineCitation", {})
        article_data = medline.get("Article", {})

        pubmed_id = medline.get("PMID", {})
        if isinstance(pubmed_id, dict):
            pubmed_id = pubmed_id.get("#text", "N/A")

        title = article_data.get("ArticleTitle", "N/A")
        if isinstance(title, dict):
            title = title.get("#text", "N/A")

        pub_date = (
            article_data.get("Journal", {})
            .get("JournalIssue", {})
            .get("PubDate", {})
            .get("Year", "N/A")
        )

        authors_list = article_data.get("AuthorList", {}).get("Author", [])
        if not isinstance(authors_list, list):
            authors_list = [authors_list]

        non_academic_authors: List[str] = []
        company_affiliations: List[str] = []
        corresponding_email: str = ""

        for author in authors_list:
            affiliation_info = author.get("AffiliationInfo", None)
            affiliation = ""

            if isinstance(affiliation_info, list) and affiliation_info:
                affiliation = affiliation_info[0].get("Affiliation", "")
            elif isinstance(affiliation_info, dict):
                affiliation = affiliation_info.get("Affiliation", "")

            if "pharma" in affiliation.lower() or "biotech" in affiliation.lower():
                non_academic_authors.append(author.get("LastName", "Unknown"))
                company_affiliations.append(affiliation)

            if "@" in affiliation:
                corresponding_email = affiliation

        results.append(
            {
                "PubmedID": pubmed_id,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academic Author(s)": ", ".join(non_academic_authors) if non_academic_authors else "N/A",
                "Company Affiliation(s)": ", ".join(company_affiliations) if company_affiliations else "N/A",
                "Corresponding Author Email": corresponding_email if corresponding_email else "N/A",
            }
        )

    return results

# Main function to run the script
def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", type=str, help="Search query for PubMed")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum number of articles to fetch")
    parser.add_argument("-f", "--file", type=str, help="Save output to CSV file")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    article_ids = fetch_pubmed_articles(args.query, args.max_results)
    articles = fetch_article_details(article_ids)
    extracted_data = extract_article_info(articles)

    if extracted_data:
        df = pd.DataFrame(extracted_data)

        if args.file:
            df.to_csv(args.file, index=False)
            logging.info(f"✅ Results saved to {args.file}")
        else:
            print(df.to_string(index=False))
    else:
        logging.warning("⚠ No pharma/biotech-affiliated papers found.")

if __name__ == "__main__":
    main()
