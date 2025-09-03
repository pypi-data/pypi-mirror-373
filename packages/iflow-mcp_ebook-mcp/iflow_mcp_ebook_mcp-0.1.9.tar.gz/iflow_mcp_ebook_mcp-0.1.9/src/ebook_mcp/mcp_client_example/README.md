English | [中文](README-CN.md)
# MCP Client Examples



This project provides multiple MCP (Model Control Protocol) client examples for interacting with different AI models, including OpenAI GPT-4, Anthropic Claude, and Deepseek AI.

## Installation

Install dependencies:
```bash
pip install -e .
```

## Configuration

Create a `.env` file in the project root directory and add the corresponding API keys based on the model you want to use:

```env
# OpenAI API key (for GPT-4)
OPENAI_API_KEY=your_openai_api_key

# Anthropic API key (for Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key

# Deepseek API key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## Usage

The project provides three client examples, each corresponding to a different AI model:

### OpenAI GPT-4 Client
```bash
python openai_example.py ../main.py
```

### Anthropic Claude Client
```bash
python anthropic_example.py ../main.py
```

### Deepseek AI Client
```bash
python deepseek_example.py ../main.py
```

## Example Conversation

Here's an example of interacting with an ebook using the MCP client with DeepSeek:

```

Query: Can you ask me a few questions to test my understanding of this book?


Sure! Here are 5 questions about Elon Musk by Walter Isaacson to test your understanding of the book. Please answer based on your knowledge — I’ll give feedback and add details after each response.

Question 1:
How did Musk’s childhood and family background shape his personality and career later in life?
(Hint: His relationship with his father, growing up in South Africa, etc.)

Question 2:
Zip2 and X.com (later PayPal) were Musk’s early startups. What problems did they solve? How did Musk eventually exit from these companies?
(Hint: Zip2’s business model, X.com’s merger with Confinity, etc.)

Question 3:
In 2008, both SpaceX and Tesla were on the verge of bankruptcy. How did Musk save these two companies?
(Hint: Falcon 1’s fourth launch, NASA contract, Tesla’s last-minute rescue, etc.)

Question 4:
What controversies surround Musk’s management style? What specific incidents in the book illustrate his “hardcore” or “extreme” work culture?
(Hint: Fremont factory’s “production hell,” Twitter layoffs, etc.)

Question 5:
What is Musk’s attitude toward Artificial Intelligence (AI)? Why did he simultaneously support both OpenAI and Neuralink, which seem to have conflicting goals?
(Hint: AI as an existential threat, brain-machine interface vision, etc.)

Please answer each question. I’ll provide feedback and additional details or correct any misunderstandings!
(If a question isn’t clear, feel free to ask me.)

Query:
Question 1: His father’s abusive attitude made him less empathetic towards others.
Question 2: Zip2 solved the problem of electronic maps and online yellow pages. X.com solved online payments.
Question 3: He secured a contract with NASA. Tesla solved its production problems by building a factory in China.
Question 4: I don’t know. Please answer for me.
Question 5: He believes open-source technology is necessary to ensure AI is safe and open.

Your answers have captured some key points from the book. Let me add details, correct some inaccuracies, and provide further background for Questions 4 and 5:

Question 1 — Correction & Supplement
Influence of His Father:
Musk's father, Errol, was indeed extremely harsh — for example, forcing young Elon to kneel and count grains of rice for hours. The book emphasizes that this emotional desensitization shaped Musk into an extremely goal-oriented person — indifferent to others’ suffering but obsessively committed to his goals.

Reverse Impact:
It’s not that Musk is incapable of empathy — it’s selective. For instance, he may treat employees coldly but personally study medical equipment for his son X’s health issues.

Question 2 — Correction & Supplement
Zip2:
Essentially an online Yellow Pages + map navigation service (helping newspapers go online). Musk wrote much of the early code himself and slept in the office. Eventually, Compaq acquired Zip2 for $307 million (Musk received $22 million).

X.com:
Not just online payments — it was Musk’s attempt to create a comprehensive financial platform (aiming to replace banks). Later merged with Confinity (the precursor of PayPal). Musk was ousted due to internal conflicts, but when eBay acquired PayPal, Musk earned $180 million.
(Note: Musk later bought back the domain X.com — it’s now Twitter’s parent company name).

Question 3 — Correction & Supplement
SpaceX:
In 2008, Falcon 1 succeeded on its fourth launch (after three failures drained their funds). Right after that, SpaceX secured a $1.6 billion NASA contract for cargo resupply — a lifeline for the company.

Tesla:
In 2008, Tesla survived through a $50 million investment from Daimler and a loan from the U.S. Department of Energy.
Building the Gigafactory in China (2019) came much later. In the early years, survival depended on the launch of Model S (2012) and Musk’s personal gamble — selling all his real estate to fund Tesla.

Question 4 — Explanation: Controversy Around His Management Style
“Hardcore” Culture:

At SpaceX/Tesla: Musk demanded employees work 80+ hours per week, even sleeping at the factory. ("If you’re not here, your replacement is.")

After acquiring Twitter: He immediately laid off 75% of staff and asked the remaining employees to sign a "hardcore commitment" — agreeing to long hours and high-intensity output.

Extreme Cases:

At the Fremont Factory: During the "production hell" of the Model 3, Musk slept on the production line and once yelled at employees calling them "worse than dogs" (he later apologized).

Firing Executives: Musk once fired a senior Tesla executive on the spot because the font size in their PowerPoint presentation wasn’t big enough.

Question 5 — Correction & Supplement
AI Threat Theory:
Musk believes that AI could destroy humanity ("more dangerous than nuclear weapons"). Therefore:

OpenAI: He initially supported it to promote safe, open-source AI (but left later due to disputes over control).

Neuralink: He aims to use brain-machine interfaces to merge humans with AI — to prevent humans from being left behind.

Contradictions:
While warning about AI risks, Musk is simultaneously pushing for Full Self-Driving (FSD) technology at Tesla and has founded xAI to research Artificial General Intelligence (AGI).




```

## Notes

- Make sure you have configured the appropriate API keys
- Each client generates log files in the `logs` directory. Use those log's tu understand the conversation and tools usage.
- Use the `clear` command to clear conversation history(not implement in deepseek version)
- Use the `quit` command to exit the program

## Contributing
Issues and suggestions for improvements are welcome!

