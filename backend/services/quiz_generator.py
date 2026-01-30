"""Quiz generation service."""

import json
import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


class QuizGenerator:
    """Service for generating quizzes from knowledge base content."""

    def __init__(self):
        self.mock_mode = settings.is_mock_mode
        self._llm_client = None

    async def initialize(self) -> None:
        """Initialize the LLM client."""
        if self.mock_mode:
            logger.info("Quiz generator initialized in mock mode")
            return

        if settings.ANTHROPIC_API_KEY:
            try:
                import anthropic

                self._llm_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Quiz generator initialized with Anthropic client")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM client: {e}")
                self.mock_mode = True

    async def generate_questions(
        self,
        content: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: Optional[list[str]] = None,
    ) -> list[dict]:
        """Generate quiz questions from content."""
        question_types = question_types or ["multiple_choice"]

        if self.mock_mode or not self._llm_client:
            return self._generate_mock_questions(num_questions, difficulty, question_types)

        prompt = self._build_generation_prompt(
            content, num_questions, difficulty, question_types
        )

        try:
            response = self._llm_client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            return self._parse_questions(response.content[0].text)
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return self._generate_mock_questions(num_questions, difficulty, question_types)

    def _build_generation_prompt(
        self,
        content: str,
        num_questions: int,
        difficulty: str,
        question_types: list[str],
    ) -> str:
        """Build the prompt for question generation."""
        types_str = ", ".join(question_types)

        return f"""Based on the following content, generate {num_questions} quiz questions.

Content:
{content[:4000]}

Requirements:
- Difficulty level: {difficulty}
- Question types: {types_str}
- Each question should test understanding, not just recall
- Include clear correct answers and explanations

Return the questions as a JSON array with this structure:
[
  {{
    "question": "The question text",
    "question_type": "multiple_choice|true_false|short_answer",
    "options": ["A", "B", "C", "D"],  // only for multiple_choice
    "correct_answer": "The correct answer",
    "explanation": "Why this is correct",
    "difficulty": "{difficulty}"
  }}
]

Return ONLY the JSON array, no other text."""

    def _parse_questions(self, response: str) -> list[dict]:
        """Parse LLM response into question dictionaries."""
        try:
            # Try to extract JSON from the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            questions = json.loads(response.strip())
            return questions if isinstance(questions, list) else []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse questions JSON: {e}")
            return []

    def _generate_mock_questions(
        self, num_questions: int, difficulty: str, question_types: list[str]
    ) -> list[dict]:
        """Generate mock questions for testing."""
        mock_questions = []

        for i in range(num_questions):
            q_type = question_types[i % len(question_types)]

            if q_type == "multiple_choice":
                mock_questions.append(
                    {
                        "question": f"Mock multiple choice question {i+1}?",
                        "question_type": "multiple_choice",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": "This is a mock explanation.",
                        "difficulty": difficulty,
                    }
                )
            elif q_type == "true_false":
                mock_questions.append(
                    {
                        "question": f"Mock true/false question {i+1}?",
                        "question_type": "true_false",
                        "options": ["True", "False"],
                        "correct_answer": "True",
                        "explanation": "This is a mock explanation.",
                        "difficulty": difficulty,
                    }
                )
            else:
                mock_questions.append(
                    {
                        "question": f"Mock short answer question {i+1}?",
                        "question_type": "short_answer",
                        "options": None,
                        "correct_answer": "Mock answer",
                        "explanation": "This is a mock explanation.",
                        "difficulty": difficulty,
                    }
                )

        return mock_questions
