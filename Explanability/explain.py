import os
from groq import Groq

client = Groq(
    api_key="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",
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": (
                "Given the following impactful features and their corresponding explanations, "
                "generate a clear, user-friendly explanation about the predicted fantasy performance of the player. "
                "Use a natural and engaging tone, avoiding technical terms like SHAP values. Focus on making the explanation understandable and relatable to a general audience, and ensure it highlights the key "
                "factors influencing the prediction.\n\n"
                "### Input Format:\n"
                "- Player Name: Virat Kohli\n"
                "- Role: Batsman\n"
                "- Most Impactful Features:\n"
                "  1. player_batting_overall: +0.97\n"
                "  2. opponent_fielding_overall: +1.09\n"
                "  3. opponent_bowling_avg_10: -1.07\n"
                "  4. opponent_bowling_overall: 2.05\n"
                "  5. player_batting_avg_20: -0.5\n"
                "- General Context to understand the features: "
                "in the features if player1_batting_points_avg_10 denotes opponent player 1's batting points average over 10 matches, "
                "sixes_ewma denotes the exponent weighted average of sixes hit by the player of all the previous matches.\n\n"
                "### Output Example:\n"
                "'Since [Player Name]'s recent performances have been exceptional, it is likely they will continue their form in this match. "
                "Additionally, the opponent's [specific weakness or factor] might give them an edge. The [additional context, e.g., conditions, team dynamics] "
                "further supports the prediction of a strong performance.'\n\n"
                "Generate a concise yet elaborate paragraph summarizing the input in a way that provides actionable insights to the user."
            )
        }
    ],
    model="llama3-70b-8192",
)

print(chat_completion.choices[0].message.content)