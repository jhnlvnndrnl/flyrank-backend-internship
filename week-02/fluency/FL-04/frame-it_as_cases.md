# Week 2 — Frame It as Cases

**Name:** John Elvin Endrenal

**Project:** VeriPHy

---

# Voice Card

> **Direct, thoughtful, evidence over hype.**

---

# Case Study — VeriPHy: Designing an Evidence-First AI News Verification System

## Problem

Misinformation spreads faster than corrections. By the time professional fact-checking organizations respond to a false claim, it has often already reached thousands of people. Existing fact-checking websites are valuable, but they require users to stop what they're doing, search for a claim manually, and read through long articles. In practice, most people don't take that extra step.

The idea for VeriPHy came from observing this pattern repeatedly on social media. I often saw articles, screenshots, and posts shared without anyone checking where they came from, while corrections spread much more slowly. That made me see misinformation not only as a social issue but also as an engineering problem: **how can verification become as easy as sharing?**

---

## What I Did (and What I Decided)

VeriPHy is currently in the **research and system design phase**. Rather than jumping directly into implementation, I decided to validate the architecture, understand the tradeoffs, and define the system before writing production code.

### Product Direction

One of the earliest decisions was choosing **Messenger** as the MVP platform instead of a traditional website or browser extension.

My initial target audience is people in the Philippines, where Facebook and Messenger are among the primary platforms used for consuming and sharing news. Instead of asking users to install another application or visit another website, I wanted fact-checking to happen where conversations already exist.

The long-term vision includes expanding to additional platforms, but the MVP focuses on validating the idea with the audience it is designed for.

### System Design

The planned workflow is:

1. A user submits a news link or text claim through Messenger.
2. The system extracts the article or claim.
3. An LLM identifies the key factual claims and important entities.
4. Relevant evidence is retrieved from trusted sources.
5. The AI generates an explanation grounded in the retrieved evidence.
6. The user receives a structured report with supporting citations.

Conceptually, the system follows a **Retrieval-Augmented Generation (RAG)** approach. Rather than relying on an LLM's internal knowledge, the model is expected to reason only over retrieved evidence.

### Engineering Decisions

During research, I compared several approaches.

For claim extraction, I considered traditional NLP techniques such as Named Entity Recognition and rule-based parsing. While they are fast and predictable, they do not reliably identify the actual factual claim, especially when news articles contain implied or multiple statements. Because of this, I decided an LLM would provide better contextual understanding while keeping deterministic methods for preprocessing and metadata extraction.

For evidence retrieval, I compared three approaches:

- General search APIs
- Curated trusted source lists
- Fact-checking APIs

Each had strengths and weaknesses. Search APIs provide broad and current information but may include unreliable sources. Curated lists improve reliability but risk missing emerging stories. Fact-checking APIs only work for claims that have already been investigated.

At the moment, I am leaning toward a hybrid approach that combines search with a curated trust layer so that retrieved evidence comes from multiple vetted sources instead of relying on a single website.

### Biggest Design Shift

The biggest change in my thinking happened during research.

Initially, I assumed VeriPHy should classify information as simply **true or false**. After studying how professional fact-checking organizations work, I realized that many claims are more nuanced than a binary label. Some are partially true, missing context, or still developing.

That fundamentally changed the project's direction.

Instead of positioning the AI as the authority, VeriPHy is designed to **help users verify information themselves** by collecting evidence, presenting supporting and conflicting viewpoints, and clearly communicating uncertainty whenever the available evidence is inconclusive.

### Challenges

The biggest unresolved challenge is trustworthiness.

Large language models are capable of hallucinating or confidently presenting unsupported conclusions. For a fact-checking system, that risk is unacceptable.

My current design treats the LLM only as an explanation engine. Evidence should always be retrieved first, and every explanation should reference the sources used to generate it. If evidence is insufficient or conflicting, the system should communicate that uncertainty instead of forcing a confident answer.

This remains an active research problem and one of the primary reasons I have not started implementation yet.

### Technical Stack

The current architecture is intentionally modular.

- **Backend:** FastAPI
- **Language:** Python
- **Architecture:** Retrieval-Augmented Generation (planned)
- **LLM:** Under evaluation
- **Retrieval:** Custom pipeline under development

I intentionally chose to design the retrieval pipeline myself before introducing frameworks like LangChain because I want to understand each stage of the process before adding additional abstractions.

Another design consideration that emerged during the interview was language support. Since the target audience is in the Philippines, the system will eventually need to understand English, Filipino, and Taglish instead of assuming English-only input.

---

## Outcome

VeriPHy is not yet a deployed application.

The project currently exists as a researched architecture supported by documented design decisions and identified technical challenges.

The MVP goal is straightforward:

- Accept a news link or claim through Messenger.
- Retrieve supporting evidence from trusted sources.
- Generate an evidence-based explanation with citations.
- Return the result in a conversational interface.

Success for the MVP is not measured by user growth. Instead, I want to validate whether a small group of users finds the explanations understandable, transparent, and trustworthy enough to incorporate into their own fact-checking process.

---

## What I Learned

I originally believed that integrating an AI model would be the hardest part of this project.

Research changed that assumption.

The real challenge is designing a trustworthy system around the model: deciding what counts as reliable evidence, handling conflicting information, communicating uncertainty honestly, and preventing the AI from presenting unsupported conclusions with confidence.

I also learned that designing AI systems requires questioning initial assumptions. What started as an idea for a true-or-false classifier evolved into an evidence-first verification assistant because the research showed that real-world fact-checking is rarely binary.

Although VeriPHy is still in the design phase, I believe understanding and defending these engineering decisions is a stronger foundation than rushing into implementation without validating the architecture.

---

# Bio

I'm **John Elvin Endrenal**, a Computer Engineering student interested in backend systems, artificial intelligence, and software engineering.

I enjoy building practical systems that solve real-world problems through thoughtful engineering decisions. My current interests include AI-assisted applications, backend architecture, and machine learning, with a focus on building systems that are reliable, explainable, and useful.

---

# Contact / Call to Action

If you're interested in AI systems, backend engineering, software development, or research, I'd love to connect.

- **Portfolio:** https://jeendrenal.online
- **LinkedIn:** https://www.linkedin.com/in/jeendrenal/
- **GitHub:** https://github.com/jhnlvnndrnl

---

# Before & After

## Before (Generic AI)

> Developed an innovative AI-powered fact-checking platform utilizing advanced machine learning algorithms to improve information credibility and enhance user experience.

## After (Edited)

> I designed VeriPHy around a simple question: **how can verifying information become as easy as sharing it?** Instead of asking an AI to decide what is true, the system gathers evidence from trusted sources, explains where that evidence agrees or conflicts, and helps users make more informed decisions.

---

# Reflection

This case study was developed through an iterative interview with Claude. Instead of asking AI to write a portfolio entry from scratch, I used it to interview me one question at a time about the project's motivation, constraints, design decisions, tradeoffs, and future direction.

After the interview, I reviewed every section, removed generic language, corrected details that did not accurately reflect my thinking, and edited the writing so it sounded like my own voice.

This process reinforced an important lesson: AI is most useful when it helps uncover and organize your thinking, not when it replaces it.