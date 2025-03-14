# PubMed Research Paper Fetcher

This project fetches research papers from PubMed based on a user query, filters affiliations related to pharmaceutical/biotech companies, and saves the results as CSV files.

## Features
- Fetch research papers from PubMed using a search query.
- Filter results to identify affiliations linked to pharmaceutical/biotech companies.
- Export results as CSV files.
- Command-line interface for ease of use.
- Uses Poetry for dependency management.

## Installation
### Prerequisites
- Python 3.13 (Ensure it is installed and added to PATH)
- Poetry (Python dependency manager)
- Git (for version control)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/kiranmathpati/pubmed-project.git
   cd pubmed-project
   ```
2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```
3. Activate the virtual environment:
   ```sh
   poetry shell
   ```

## Usage
Run the following command to fetch PubMed research papers:
```sh
poetry run pubmed-search "your search query" --max-results 20
```
### Example:
```sh
poetry run pubmed-search "clinical trials by pharmaceutical companies in India" --max-results 20 --file results.csv --debug
```
### Output:
- If `--file` is specified, results are saved as the given filename (e.g., `results.csv`).
- Otherwise, the output is displayed in the terminal.

## Error Handling
If you encounter issues:
- Ensure you are inside the Poetry virtual environment (`poetry shell`).
- Verify internet connectivity.
- Check for API rate limits from PubMed.

## Version Control
Ensure Git is initialized and changes are committed:
```sh
git status
git add .
git commit -m "Initial commit"
```

## Future Improvements
- Improve filtering logic.
- Enhance error handling.
- Add unit tests for better reliability.
- Publish the package to TestPyPI for broader accessibility.

## License
MIT License
