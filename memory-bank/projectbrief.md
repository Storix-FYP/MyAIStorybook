# Project Brief: MyAIStorybook

## Project Overview
**MyAIStorybook** is an AI-powered children's storybook generator that creates complete illustrated stories from simple user prompts. It's a full-stack application with a FastAPI backend and React frontend, designed as a Final Year Project (FYP).

## Core Purpose
- **Primary Goal**: Generate engaging, age-appropriate children's stories with illustrations
- **Target Users**: Children, parents, educators, and anyone who wants to create custom storybooks
- **Value Proposition**: Transform simple ideas into complete, illustrated storybooks in minutes

## Key Features
1. **Intelligent Prompt Processing**: Validates and enhances user input using AI
2. **Multi-Agent Story Generation**: Uses specialized AI agents for different aspects of story creation
3. **Automatic Illustration**: Generates high-quality images for each story scene using Stable Diffusion
4. **Interactive Storybook Display**: Beautiful, page-turning interface for reading generated stories
5. **Quality Assurance**: Built-in review and editing pipeline to ensure story quality

## Technical Architecture
- **Backend**: FastAPI with Python, using Ollama for LLM inference and Stable Diffusion for image generation
- **Frontend**: React with modern UI/UX design
- **AI Pipeline**: Multi-agent system with specialized roles (Director, Writer, Reviewer, Editor, Image Generator)
- **Storage**: Local file system for generated content (stories, images, metadata)

## Success Criteria
- Generate coherent, engaging children's stories from simple prompts
- Produce high-quality illustrations that match story content
- Provide smooth, intuitive user experience
- Handle various input types gracefully (short phrases to detailed descriptions)
- Maintain consistent story quality and age-appropriateness

## Project Scope
- **In Scope**: Story generation, image creation, web interface, basic story management
- **Out of Scope**: User accounts, cloud storage, advanced editing features, multiple languages
- **Future Considerations**: User authentication, story sharing, advanced customization options
