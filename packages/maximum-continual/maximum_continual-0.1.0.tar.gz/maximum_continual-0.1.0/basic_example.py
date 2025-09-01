from maximum_continual import MaximumContinual, PredictionResponseT, Tool, MessageT
from maximum_continual.system_prompt import fetch_default_system_prompt
from maximum_continual.types import PredictionResponseWithRewardT
from pydantic import BaseModel
import json
import requests
import json



class WebSearchTool(Tool):
    name = "web_search"
    description = "Performs a web search for a query and returns a string of the top search results formatted as markdown with titles, links, and descriptions."
    inputs = {"query": {"type": "string", "description": "The search query to perform."}}
    output_type = "string"

    def __init__(self, max_results: int = 10, engine: str = "duckduckgo"):
        super().__init__()
        self.max_results = max_results
        self.engine = engine

    def forward(self, query: str) -> str:
        results = self.search(query)
        if len(results) == 0:
            raise Exception("No results found! Try a less restrictive/shorter query.")
        return self.parse_results(results)

    def search(self, query: str) -> list:
        if self.engine == "duckduckgo":
            return self.search_duckduckgo(query)
        elif self.engine == "bing":
            return self.search_bing(query)
        else:
            raise ValueError(f"Unsupported engine: {self.engine}")

    def parse_results(self, results: list) -> str:
        return "## Search Results\n\n" + "\n\n".join(
            [f"[{result['title']}]({result['link']})\n{result['snippet']}" for result in results]
        )

    def search_duckduckgo(self, query: str) -> list:
        import requests

        url = "https://google.serper.dev/search"

        payload = json.dumps({
        "q": query
        })
        headers = {
        'X-API-KEY': '5c2ec9373f610408e11fc4b068d847767d4ba87b',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()['organic']
    
    def _create_duckduckgo_parser(self):
        from html.parser import HTMLParser

        class SimpleResultParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.results = []
                self.current = {}
                self.capture_title = False
                self.capture_description = False
                self.capture_link = False

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "a" and attrs.get("class") == "result-link":
                    self.capture_title = True
                elif tag == "td" and attrs.get("class") == "result-snippet":
                    self.capture_description = True
                elif tag == "span" and attrs.get("class") == "link-text":
                    self.capture_link = True

            def handle_endtag(self, tag):
                if tag == "a" and self.capture_title:
                    self.capture_title = False
                elif tag == "td" and self.capture_description:
                    self.capture_description = False
                elif tag == "span" and self.capture_link:
                    self.capture_link = False
                elif tag == "tr":
                    # Store current result if all parts are present
                    if {"title", "description", "link"} <= self.current.keys():
                        self.current["description"] = " ".join(self.current["description"])
                        self.results.append(self.current)
                        self.current = {}

            def handle_data(self, data):
                if self.capture_title:
                    self.current["title"] = data.strip()
                elif self.capture_description:
                    self.current.setdefault("description", [])
                    self.current["description"].append(data.strip())
                elif self.capture_link:
                    self.current["link"] = "https://" + data.strip()

        return SimpleResultParser()

class FinalAnswer(BaseModel):
    answer: str
    reasoning: str

client = MaximumContinual(auto_deploy=True)

with client.init_model(
    model_id="test_model_v3",
) as model:
    tools= [WebSearchTool()]
    final_answer_model=FinalAnswer
    additional_authorized_imports=["os"]
    print(WebSearchTool().forward("Racoon City video game franchise"))
    response = model.predict(
        messages=[
            MessageT(**{"role": "system", "content": fetch_default_system_prompt(tools, additional_authorized_imports, final_answer_model=final_answer_model)}),
            MessageT(**{"role": "user", "content": "What is Racoon City and from what popular gaming franchise is it from and then compare it to silent hill. Use the websearch tool to find the answer."})
        ],
        final_answer_model=final_answer_model,
        tools=tools,
        additional_authorized_imports=additional_authorized_imports,
        logger=lambda x: print(x.model_dump_json(indent=4))
    )
    with open("response.json", "w") as f:
        f.write(response.model_dump_json(indent=4))
    with open("response.json", "r") as f:
        response = PredictionResponseT(**json.load(f))

    model.update(
        [PredictionResponseWithRewardT(
            prediction=response,
            reward=1.0
        )]
    )
    # print(response.final_response)


