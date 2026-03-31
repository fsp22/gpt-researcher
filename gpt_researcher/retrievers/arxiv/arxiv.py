import time
import arxiv


class ArxivSearch:
    """
    Arxiv API Retriever
    """
    def __init__(self, query, sort='Relevance', query_domains=None):
        self.arxiv = arxiv
        self.query = query
        assert sort in ['Relevance', 'SubmittedDate'], "Invalid sort criterion"
        self.sort = arxiv.SortCriterion.SubmittedDate if sort == 'SubmittedDate' else arxiv.SortCriterion.Relevance
        

    def search(self, max_results=5):
        """
        Performs the search with retry mechanism for HTTP 429 errors
        :param max_results:
        :return:
        """
        max_retries = 3
        retry_count = 0
        backoff_factor = 30

        while retry_count < max_retries:
            try:
                arxiv_gen = list(self.arxiv.Client().results(
                    self.arxiv.Search(
                        query=self.query,
                        max_results=max_results,
                        sort_by=self.sort,
                    )))

                search_result = []

                for result in arxiv_gen:
                    search_result.append({
                        "title": result.title,
                        "href": result.pdf_url,
                        "body": result.summary,
                    })
                
                return search_result
            
            except Exception as e:
                # Check if it's a 429 error (rate limit)
                if "429" in str(e) or "Too Many Requests" in str(e):
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(f"Max retries ({max_retries}) reached. Unable to complete arxiv search for query: {self.query}") from e
                    
                    # Calculate exponential backoff: 2^retry_count seconds
                    wait_time = backoff_factor * (2 ** retry_count)
                    time.sleep(wait_time)
                else:
                    # Re-raise if it's not a 429 error
                    raise
