from vgrep.templater import Templater
from langchain_core.runnables import Runnable
from typing import Generator

class Contextualizer:
    def __init__(self, llm: Runnable):
        self.templater = Templater("contextualize.txt.j2")
        self.llm = llm

    def contextualize(self,
                      text: str,
                      existing_context: str = ""):
        request = self.templater.render_template(context=existing_context,
                                                 chunk=text)
        res = self.llm.invoke(request)
        return res.content
