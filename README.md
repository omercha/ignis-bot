<h1 align="center">Ignis</h1>
<h3 align="center">An AI-powered study assistant for Discord</h3>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue?logo=python">
  <img src="https://img.shields.io/badge/discord-bot-5865F2?logo=discord&logoColor=white">
  <img src="https://img.shields.io/badge/powered%20by-OpenAI-412991?logo=openai">
  <img src="https://img.shields.io/badge/license-MIT-green">
</p>

## About

Ignis is a Discord bot powered by the OpenAI API that helps you **study smarter**.  
It can help you understand tough concepts, provide a quick definition, or even test you with a quiz!

## Installation

To start using Ignis, simply [**invite the bot to your Discord server**](https://discord.com/oauth2/authorize?client_id=1408938767489695826).  

Once Ignis joins your server, type `/help` to see available commands!  

## Commands

Ignis comes with a variety of commands designed to make learning easier and more interactive:

- `/help` → Display all available commands.  
- `/ask [question]` → Ask Ignis any question and get a detailed response. Stores context for the last 5 responses and removes the earliest response if the limit is reached.  
- `/reset` → Reset your current conversation with Ignis.  
- `/define [term]` → Get a simple, clear definition for a term or phrase.  
- `/explainlikeim5 [concept]` → Break down complex topics into easy-to-understand explanations.  
- `/summarise [text]` → Turn long text into a short, concise summary.  
- `/translate [text] [language]` → Translate text into another language.  
- `/quiz [topic] [num_questions]` → Generate a short quiz (up to 10 questions) on a chosen topic.  

## Known Issues & Bugs

- `/quiz` may get stuck in a loading state if an invalid topic is chosen.  
- Very large inputs for `/summarise` or `/translate` can hit Discord's character limit.  



## Contributions

If you encounter any bugs, have suggestions to help improve Ignis or just want to say hello, feel free to reach out to me on **Discord: `omer_c`**!
