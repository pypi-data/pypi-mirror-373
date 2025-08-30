from tavily import AsyncTavilyClient
from xgatools.tool_base import XGASandBoxTool,XGAToolResult
from xgatools.config import config
from daytona_sdk import AsyncSandbox
from urllib.parse import urlparse

import httpx
import json
import datetime
import asyncio
import logging

class WebSearchTool(XGASandBoxTool):
    """Tool for performing web searches using Tavily API and web scraping using Firecrawl."""

    def __init__(self, sandbox: AsyncSandbox):
        super().__init__(sandbox)
        self.sandbox = sandbox

        # Get API configuration from config module
        tavily_config = config.get_tavily_config()
        firecrawl_config = config.get_firecrawl_config()

        self.tavily_api_key = tavily_config['api_key']
        self.firecrawl_api_key = firecrawl_config['api_key']
        self.firecrawl_url = firecrawl_config['url']

        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in configuration")
        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in configuration")

        # Tavily asynchronous search client
        self.tavily_client = AsyncTavilyClient(api_key=self.tavily_api_key)

    async def web_search(
            self,
            query: str,
            num_results: int = 20
    ) -> XGAToolResult:
        """
        Search the web using the Tavily API to find relevant and up-to-date information.
        """
        try:
            # Ensure we have a valid query
            if not query or not isinstance(query, str):
                return XGAToolResult(
                    success=False,
                    output="A valid search query is required."
                )

            # Normalize num_results
            if num_results is None:
                num_results = 20
            elif isinstance(num_results, int):
                num_results = max(1, min(num_results, 50))
            elif isinstance(num_results, str):
                try:
                    num_results = max(1, min(int(num_results), 50))
                except ValueError:
                    num_results = 20
            else:
                num_results = 20

            # Execute the search with Tavily
            logging.info(f"Executing web search for query: '{query}' with {num_results} results")
            search_response = await self.tavily_client.search(
                query=query,
                max_results=num_results,
                include_images=True,
                include_answer="advanced",
                search_depth="advanced",
            )

            # Check if we have actual results or an answer
            results = search_response.get('results', [])
            answer = search_response.get('answer', '')

            logging.info(f"Retrieved search results for query: '{query}' with answer and {len(results)} results")

            def decode_unicode(obj):
                if isinstance(obj, str):
                    # 直接返回字符串（已自动处理Unicode转义）
                    return obj
                elif isinstance(obj, dict):
                    return {k: decode_unicode(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [decode_unicode(item) for item in obj]
                else:
                    return obj

            # 解码所有Unicode转义序列
            decoded_response = decode_unicode(search_response)
            # Consider search successful if we have either results OR an answer
            if len(results) > 0 or (answer and answer.strip()):
                return XGAToolResult(
                    success=True,
                    output=json.dumps(decoded_response, ensure_ascii=False, indent=2)
                )
            else:
                # No results or answer found
                logging.warning(f"No search results or answer found for query: '{query}'")
                return XGAToolResult(
                    success=False,
                    output=json.dumps(decoded_response, ensure_ascii=False, indent=2)
                )

        except Exception as e:
            error_message = str(e)
            logging.error(f"Error performing web search for '{query}': {error_message}")
            return XGAToolResult(
                success=False,
                output=f"Error performing web search: {error_message[:200]}"
            )

    async def scrape_webpage(self, urls: str) -> XGAToolResult:
        """
        Retrieve the complete text content of multiple webpages in a single efficient operation.

        ALWAYS collect multiple relevant URLs from search results and scrape them all at once
        rather than making separate calls for each URL. This is much more efficient.

        Parameters:
        - urls: Multiple URLs to scrape, separated by commas
        """
        try:
            logging.info(f"Starting to scrape webpages: {urls}")

            # Parse the URLs parameter
            if not urls:
                logging.warning("Scrape attempt with empty URLs")
                return XGAToolResult(
                    success=False,
                    output="Valid URLs are required."
                )

            # Split the URLs string into a list
            url_list = [url.strip() for url in urls.split(',') if url.strip()]

            if not url_list:
                logging.warning("No valid URLs found in the input")
                return XGAToolResult(
                    success=False,
                    output="No valid URLs provided."
                )

            if len(url_list) == 1:
                logging.warning("Only a single URL provided - for efficiency you should scrape multiple URLs at once")

            logging.info(f"Processing {len(url_list)} URLs: {url_list}")

            # Process each URL and collect results
            results = []
            for url in url_list:
                try:
                    # Add protocol if missing
                    if not (url.startswith('http://') or url.startswith('https://')):
                        url = 'https://' + url
                        logging.info(f"Added https:// protocol to URL: {url}")

                    # Scrape this URL
                    result = await self._scrape_single_url(url)
                    results.append(result)

                except Exception as e:
                    logging.error(f"Error processing URL {url}: {str(e)}")
                    results.append({
                        "url": url,
                        "success": False,
                        "error": str(e)
                    })

            # Summarize results
            successful = sum(1 for r in results if r.get("success", False))
            failed = len(results) - successful

            # Create success/failure message
            if successful == len(results):
                message = f"Successfully scraped all {len(results)} URLs."
                for r in results:
                    if r.get("file_path"):
                        message += f"\n- {r.get('file_path')}"
            elif successful > 0:
                message = f"Scraped {successful} URLs successfully and {failed} failed."
                for r in results:
                    if r.get("success", False) and r.get("file_path"):
                        message += f"\n- {r.get('file_path')}"
                message += "\n\nFailed URLs:"
                for r in results:
                    if not r.get("success", False):
                        message += f"\n- {r.get('url')}: {r.get('error', 'Unknown error')}"
            else:
                error_details = "; ".join([f"{r.get('url')}: {r.get('error', 'Unknown error')}" for r in results])
                return XGAToolResult(
                    success=False,
                    output=f"Failed to scrape all {len(results)} URLs. Errors: {error_details}"
                )
            return XGAToolResult(
                success=True,
                output=message
            )

        except Exception as e:
            error_message = str(e)
            logging.error(f"Error in scrape_webpage: {error_message}")
            return XGAToolResult(
                success=False,
                output=f"Error processing scrape request: {error_message[:200]}"
            )

    async def _scrape_single_url(self, url: str) -> dict:
        """
        Helper function to scrape a single URL and return the result information.
        """
        logging.info(f"Scraping single URL: {url}")

        try:
            # ---------- Firecrawl scrape endpoint ----------
            logging.info(f"Sending request to Firecrawl for URL: {url}")
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.firecrawl_api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "url": url,
                    "formats": ["markdown"]
                }

                # Use longer timeout and retry logic for more reliability
                max_retries = 3
                timeout_seconds = 120
                retry_count = 0

                while retry_count < max_retries:
                    try:
                        logging.info(f"Sending request to Firecrawl (attempt {retry_count + 1}/{max_retries})")
                        response = await client.post(
                            f"{self.firecrawl_url}/v1/scrape",
                            json=payload,
                            headers=headers,
                            timeout=timeout_seconds,
                        )
                        response.raise_for_status()
                        data = response.json()
                        logging.info(f"Successfully received response from Firecrawl for {url}")
                        break
                    except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ReadError) as timeout_err:
                        retry_count += 1
                        logging.warning(f"Request timed out (attempt {retry_count}/{max_retries}): {str(timeout_err)}")
                        if retry_count >= max_retries:
                            raise Exception(
                                f"Request timed out after {max_retries} attempts with {timeout_seconds}s timeout")
                        # Exponential backoff
                        logging.info(f"Waiting {2 ** retry_count}s before retry")
                        await asyncio.sleep(2 ** retry_count)
                    except Exception as e:
                        # Don't retry on non-timeout errors
                        logging.error(f"Error during scraping: {str(e)}")
                        raise e

            # Format the response
            title = data.get("data", {}).get("metadata", {}).get("title", "")
            markdown_content = data.get("data", {}).get("markdown", "")
            logging.info(f"Extracted content from {url}: title='{title}', content length={len(markdown_content)}")

            formatted_result = {
                "title": title,
                "url": url,
                "text": markdown_content
            }

            # Add metadata if available
            if "metadata" in data.get("data", {}):
                formatted_result["metadata"] = data["data"]["metadata"]
                logging.info(f"Added metadata: {data['data']['metadata'].keys()}")

            # Create a simple filename from the URL domain and date
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Extract domain from URL for the filename
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace("www.", "")

            # Clean up domain for filename
            domain = "".join([c if c.isalnum() else "_" for c in domain])
            safe_filename = f"{timestamp}_{domain}.json"

            logging.info(f"Generated filename: {safe_filename}")

            # Save results to a file in the /workspace/scrape directory if sandbox is available
            file_path = None
            if self.sandbox and hasattr(self.sandbox, 'fs'):
                try:
                    scrape_dir = f"/workspace/scrape"
                    # Create directory
                    await self.sandbox.fs.create_folder(scrape_dir, "755")

                    file_path = f"{scrape_dir}/{safe_filename}"
                    json_content = json.dumps(formatted_result, ensure_ascii=False, indent=2)
                    logging.info(f"Saving content to file: {file_path}, size: {len(json_content)} bytes")

                    await self.sandbox.fs.upload_file(
                        json_content.encode(),
                        file_path,
                    )
                except Exception as e:
                    logging.warning(f"Could not save to sandbox filesystem: {str(e)}")
                    file_path = None

            return {
                "url": url,
                "success": True,
                "title": title,
                "file_path": file_path,
                "content_length": len(markdown_content),
                "content": formatted_result
            }

        except Exception as e:
            error_message = str(e)
            logging.error(f"Error scraping URL '{url}': {error_message}")

            # Create an error result
            return {
                "url": url,
                "success": False,
                "error": error_message
            }


if __name__ == "__main__":
    async def test_web_search():
        """Test function for the web search tool"""
        # This test function is not compatible with the sandbox version
        print("Test function needs to be updated for sandbox version")


    async def test_scrape_webpage():
        """Test function for the webpage scrape tool"""
        # This test function is not compatible with the sandbox version
        print("Test function needs to be updated for sandbox version")


    async def run_tests():
        """Run all test functions"""
        await test_web_search()
        await test_scrape_webpage()


    asyncio.run(run_tests())