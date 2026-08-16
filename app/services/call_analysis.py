from openai import OpenAI
from pydantic import ValidationError

from app.config import config
from app.schemas.buyer.conversation_report import ConversationReport

client = OpenAI(api_key=config.OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are a senior real estate CRM analyst.

Analyze the ENTIRE buyer conversation.

Your job is to extract ALL important business information.

Return ONLY the provided structured schema.

Rules:

- Never invent information.
- Missing values must be null.
- Extract:
    • Buyer contact details
    • Budget
    • Preferred city
    • Locality
    • Property type
    • Bedrooms
    • Amenities
    • Buying timeline
    • Financing method
    • Every property discussed
    • Every property the buyer liked
    • Every concern
    • Every objection
    • Every buying signal
    • Every negative signal
    • Viewing information
    • Human follow-up recommendations
    • Overall conversation summary
    • Buyer intent
    • Lead score
    • Lead priority
    • Qualification

Lead score must be between 0 and 100.

Do not hallucinate.

If information was never mentioned,
leave it null or empty.

Be conservative.
"""


class ConversationAnalyzer:

    @staticmethod
    def analyze(messages: list[dict]) -> ConversationReport:

        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                *messages,
            ],
            response_format=ConversationReport,
        )

        report = response.choices[0].message.parsed

        if report is None:
            raise ValueError("Failed to parse conversation report.")

        return report