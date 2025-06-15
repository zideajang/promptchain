import asyncio
from typing import List
from pydantic import BaseModel,Field
from promptchain.llm import DeepseekChatMessageModel
from promptchain.utils import create_example_from_model
from promptchain.parser import PydanticParser

from promptchain.message import Message,Messages,SystemMessage

from promptchain.chain_processor import ChainProcessor
from promptchain.prompt import (
     HumanMessagePromptTemplate,
     SystemMessagePromptTemplate
)
from rich.console import Console
from rich.markdown import Markdown
# 给出 topic -> title -> outline -> content -> blog
llm = DeepseekChatMessageModel("test")

console = Console()
class TitleOutput(BaseModel):
    title: str = Field(
        description="The generated clickworthy title.",
        examples=["Unlocking Functional Python: A Deep Dive"]
    )
    topic: str = Field(
        description="The topic provided for the title.",
        examples=["functional programming"]
    )

class OutlineOutput(BaseModel):
    title: str = Field(
        description="The article title.",
        examples=["Unlocking Functional Python: A Deep Dive"]
    )
    topic: str = Field(
        description="The article topic.",
        examples=["functional programming"]
    )
    sections: List[str] = Field(
        description="A list of 3 section outlines.",
        examples=[
            ["Introduction to Functional Programming",
             "Core Functional Concepts in Python",
             "Advanced Functional Patterns"]
        ]
    )

class ContentOutput(BaseModel):
    title: str = Field(
        description="The article title.",
        examples=["Unlocking Functional Python: A Deep Dive"]
    )
    topic: str = Field(
        description="The article topic.",
        examples=["functional programming"]
    )
    sections: List[str] = Field(
        description="A list of 3 section outlines.",
        examples=[
            ["Introduction to Functional Programming",
             "Core Functional Concepts in Python",
             "Advanced Functional Patterns"]
        ]
    )
    content: List[str] = Field(
        description="One paragraph of content for each section.",
        examples=[
            ["Functional programming treats computation as the evaluation of mathematical functions, avoiding changing state and mutable data. In Python, this paradigm is supported through constructs like first-class functions and higher-order functions. It promotes writing more predictable and testable code by focusing on pure functions and immutability. Embracing this style can lead to cleaner, more modular programs, especially when dealing with complex data transformations and concurrent operations.",
             "Python embraces functional programming concepts through various features, making it a versatile language for this paradigm. Key aspects include the use of lambda functions for anonymous, small functions, and the `map`, `filter`, and `reduce` functions for transforming and processing iterables without explicit loops. Immutability, while not strictly enforced, is encouraged through data structures like tuples and frozensets, reducing side effects and making code easier to reason about.",
             "Beyond the basics, Python offers powerful advanced functional programming patterns. Decorators, for instance, are a sophisticated way to add functionality to functions without altering their structure, embodying the concept of higher-order functions. Closures allow functions to remember their lexical environment, enabling powerful design patterns like factory functions. Furthermore, generator functions and comprehensions provide memory-efficient ways to handle sequences, aligning with lazy evaluation principles often found in functional languages, enhancing both performance and code elegance."]
        ]
    )

class BlogOutput(BaseModel):
    markdown_blog: str = Field(
        description="The entire blog post formatted in markdown.",
        examples=[
            "# Unlocking Functional Python: A Deep Dive\n\n"
            "## Introduction to Functional Programming\n"
            "Functional programming treats computation as the evaluation of mathematical functions, avoiding changing state and mutable data. In Python, this paradigm is supported through constructs like first-class functions and higher-order functions. It promotes writing more predictable and testable code by focusing on pure functions and immutability. Embracing this style can lead to cleaner, more modular programs, especially when dealing with complex data transformations and concurrent operations.\n\n"
            "## Core Functional Concepts in Python\n"
            "Python embraces functional programming concepts through various features, making it a versatile language for this paradigm. Key aspects include the use of lambda functions for anonymous, small functions, and the `map`, `filter`, and `reduce` functions for transforming and processing iterables without explicit loops. Immutability, while not strictly enforced, is encouraged through data structures like tuples and frozensets, reducing side effects and making code easier to reason about.\n\n"
            "## Advanced Functional Patterns\n"
            "Beyond the basics, Python offers powerful advanced functional programming patterns. Decorators, for instance, are a sophisticated way to add functionality to functions without altering their structure, embodying the concept of higher-order functions. Closures allow functions to remember their lexical environment, enabling powerful design patterns like factory functions. Furthermore, generator functions and comprehensions provide memory-efficient ways to handle sequences, aligning with lazy evaluation principles often found in functional languages, enhancing both performance and code elegance."
        ]
    )

async def main():
    title_parser = PydanticParser(pydantic_model=TitleOutput, output_key="title")
    outline_parser = PydanticParser(pydantic_model=OutlineOutput, output_key="outline")
    content_parser = PydanticParser(pydantic_model=ContentOutput, output_key="content")
    blog_parser = PydanticParser(pydantic_model=BlogOutput, output_key="blog")


    system_prompt = SystemMessagePromptTemplate.from_template(
            """
EXAMPLE JSON OUTPUT:
            """ + f"""
{create_example_from_model(TitleOutput)}
    """
        )
    
    title_prompt = HumanMessagePromptTemplate.from_template("""
Generate a clickworthy title about this topic: {base_info}.
""")

    # Step 2: Generate Outline (uses 'title' and 'topic' from context, which PydanticParserTool updates)
    outline_prompt = HumanMessagePromptTemplate.from_template(
        """
Given the title '{title}' and topic '{topic}', generate a compelling 3-section outline.
EXAMPLE JSON OUTPUT:
            """ + f"""
{create_example_from_model(OutlineOutput)}
        """
    )
        
    # Step 3: Generate Content for sections (uses 'title', 'topic', 'sections' from context)
    content_prompt = HumanMessagePromptTemplate.from_template(
        """
Given the title '{title}', topic '{topic}', and sections: {sections}, generate 1 paragraph of content for each section.
EXAMPLE JSON OUTPUT:
            """ + f"""
{create_example_from_model(ContentOutput)}
        """
    )

    # Step 4: Generate Markdown Blog Post (uses 'markdown_blog' from context)
    blog_prompt = HumanMessagePromptTemplate.from_template(
        """
        Given the structured content: {title}, {topic}, {sections}, and {content}, generate a complete blog post formatted in Markdown.
    EXAMPLE JSON OUTPUT::
            """ + f"""
    {create_example_from_model(BlogOutput)}
    """
    )

    chain = ChainProcessor(
            messages=Messages(system_prompt.format())
        )
    chain | title_prompt | llm | title_parser 
    # | outline_prompt | llm | outline_parser | content_prompt | llm | content_parser | blog_prompt | llm | blog_parser
    initial_context = {"base_info":"functional programming"}
    final_context  = await chain.invoke(initial_context)
    
    console.print(final_context)

    # if "blog" in final_context:
    #     blog_output: BlogOutput = final_context["blog"]
    #     console.print("\n--- Generated Blog Post (Markdown) ---")
    #     console.print(Markdown(blog_output.markdown_blog))
    # else:
    #     console.print(":x: Failed to generate the final blog post.")
    #     if "blog_error" in final_context:
    #         console.print(f"Error: {final_context['blog_error']}")
    #     if "blog_raw_content" in final_context:
    #         console.print(f"Raw LLM output: {final_context['blog_raw_content']}")

if __name__ == "__main__":
    asyncio.run(main())