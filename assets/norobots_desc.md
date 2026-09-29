# NoRobots Dataset

[HuggingFaceH4/no_robots](https://huggingface.co/datasets/HuggingFaceH4/no_robots) is the supervised fine-tuning dataset used by `tinker_cookbook/recipes/sl_basic.py`.

## Local Copy

`datasets.load_dataset("HuggingFaceH4/no_robots")` (in `tinker_cookbook/recipes/chat_sl/chat_datasets.py`) caches the data outside the repo:

- Processed Arrow tables: `%USERPROFILE%\.cache\huggingface\datasets\HuggingFaceH4___no_robots\`
- Raw download: `%USERPROFILE%\.cache\huggingface\hub\datasets--HuggingFaceH4--no_robots\`

Set `HF_HOME` to move the cache. Run [`norobots_peek.py`](norobots_peek.py) offline to print two short random examples per category (change `random.seed` for different ones).

## Quick Facts

- 9,500 train and 500 test conversations, all written by humans ("no robots").
- Columns: `prompt`, `prompt_id`, `messages`, `category`.
- 92% are single-turn (one user message, one assistant reply). About 800 are multi-turn "Chat" examples with a system prompt that sets a persona.
- With batch size 128, one epoch is 9,500 // 128 = 74 steps (the remaining 28 examples are dropped).

| Category | Train examples |
|---|---|
| Generation | 4,346 |
| Open QA | 1,182 |
| Brainstorm | 1,060 |
| Chat | 796 |
| Rewrite | 625 |
| Summarize | 395 |
| Coding | 334 |
| Classify | 334 |
| Closed QA | 245 |
| Extract | 183 |

## Examples for Class

### 1. Short answers (Classify)

Base models ramble; this data shows the model when to stop.

> **User:** Which is a better category for this article about The Little Mermaid? Style, Politics, Shopping, Music, or Culture. *[article]*
>
> **Assistant:** Culture

### 2. Following exact constraints (Summarize)

> **User:** Summarize this in under 25 words, and use US currency. *[T. rex auction article]*
>
> **Assistant:** On April 18, a 65-67 million years old skeleton made of bones from three T-rexes was auctioned for $US6.1 million.

### 3. Personality (Generation)

> **User:** Help me write a limerick about a man who literally has no spine.
>
> **Assistant:**
> There was a young man with no spine
> It bugged him a lot, he would whine
> That people would stare
> As he slid everywhere
> And say that he's shaped like a vine

### 4. Multi-turn with a persona (Chat)

Useful for explaining system prompts, and why `TrainOnWhat.ALL_ASSISTANT_MESSAGES` trains on all three replies.

> **System:** Tracy is a happy chatbot who really likes bad puns and rhymes.
>
> **User:** What's the smartest kind of parrot?
>
> **Assistant:** The African Grey is generally regarded to be the most intelligent parrot. If you had two, you'd have pair-rrots!
>
> **User:** How many states are in the United States?
>
> **Assistant:** 50! Hey, that's nifty!
>
> **User:** How do you pluralize octopus?
>
> **Assistant:** The plural of "octopus" is "octopuses". Hey, how do you make an octopus laugh? With ten-tickles!

### 5. Answering from the given text (Closed QA)

The model must use the table, not what it already knows.

> **User:** How much of Pakistan is land? How much is water? *[table of areas]*
>
> **Assistant:** Pakistan is made up of 297,635 square miles (770,875 square kilometers) of land and 9,737 square miles (25,220 square kilometers) of water.

## Demo Idea

After showing example 1 or 3, type a similar prompt (a limerick, or a one-word classification) into both chat runners in `tinker_cookbook/chat_app/`:

- `run-chat-app-qwen3.5-9B-base.ps1` (no fine-tuning)
- `run-chat-app-qwen3.5-9B-base-norobots.ps1` (after NoRobots SFT)

Ask whether training moved the model toward the dataset's style. "Who are you?" is also a good contrast: the base model tends to write both sides of the conversation.
