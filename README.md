AI QuizMaster
======

A LLM-powered Game inspired by "Who wants to be a millionaire" with questions generated randomly by AI and large language models.

<p align="center" width="100%">
<img src="llmgame/static/quiz-bg.png" alt="quiz" style="width: 50%; min-width: 150px; display: block; margin: auto;">
</p>

## The idea

A trivia game where the LLM creates questions across a vast range of topics. The twist is that many questions will be unusual, humorous, or might require creative thinking rather than just factual knowledge.

### LLM Usage:

* Generates quirky and unexpected questions (e.g., "If birds had a currency, what would it be called?").
* Provides hints that are subtly helpful yet playful.
* Tailors the difficulty or adds humorous commentary based on the player's performance.

## Core Gameplay Loop

### Topic Selection:

* Offer a few broad categories (e.g., History, Pop Culture, Science, Random).
* Include a "Surprise Me!" option for a completely random LLM-generated category.

### Question Generation: 

The LLM crafts a quirky question within the chosen category.

### Player Answer: 

Multiple choice options could be offered, or open-ended text input for increased challenge.

### The Reveal:

* LLM provides the correct answer along with a witty explanation.
* Might include a humorous "wrong answer" commentary if the player gets it wrong.

## Key Features

* Adaptive Difficulty: The LLM starts simple, but gauges player performance and ramps up difficulty with more obscure questions or stricter answer formats.
* Personality: Give the AI Quizmaster a distinct character – sarcastic, overly enthusiastic, historical figure, etc. This reflects in its question style and commentary.
* Theme Variations
    * "Riddle Me This": Questions focused on riddles and wordplay.
    * "Fact or Fiction": Presents statements the player must determine as true or false.
    * "Image Interrogation": Shows an image with the question relating to a detail within it.