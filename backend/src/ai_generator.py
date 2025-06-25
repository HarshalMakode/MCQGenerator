import os
import json
from openai import OpenAI
from typing import Dict, Any
from dotenv import load_dotenv
import re


load_dotenv() 

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def generate_challenge_with_ai(difficulty: str) -> Dict[str, Any]:
    system_prompt = """You are an expert coding challenge creator.
        Your task is to generate a coding question with multiple choice answers.
        The question should be appropriate for the specified difficulty level.

        - For easy questions: Focus on basic syntax, simple operations, or common programming concepts.
        - For medium questions: Cover intermediate concepts like data structures, algorithms, or language features.
        - For hard questions: Include advanced topics, design patterns, optimization techniques, or complex algorithms.

        If the question is based on the output or behavior of a Python program, include the full Python code inside the "title" field, formatted using triple backticks (```python ... ```).

        Return the challenge in the following **valid JSON format**:
        {
            "title": "The question text. If code is needed, include it using a Markdown code block.",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answer_id": 0,
            "explanation": "Detailed explanation of why the correct answer is right"
        }

        Make sure the options are plausible but only one is clearly correct.
        Ensure the response is directly parsable JSON — do not include any extra text or markdown outside the JSON object.
    """

    try:
        client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=GITHUB_TOKEN
        )

        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a {difficulty} difficulty coding challenge."}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        raw_content = response.choices[0].message.content.strip()
        
        if raw_content.startswith("```"):
            raw_content = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content.strip(), flags=re.DOTALL)


        challenge_data = json.loads(raw_content)

        required_fields = ["title", "options", "correct_answer_id", "explanation"]
        for field in required_fields:
            if field not in challenge_data:
                raise ValueError(f"Missing required field: {field}")

        return challenge_data

    except Exception as e:
        print(e)
        raise
        # return {
        #     "title": "Basic Python List Operation",
        #     "options": [
        #         "my_list.append(5)",
        #         "my_list.add(5)",
        #         "my_list.push(5)",
        #         "my_list.insert(5)",
        #     ],
        #     "correct_answer_id": 0,
        #     "explanation": "In Python, append() is the correct method to add an element to the end of a list."
        # }