# High-Level Diagrams for MyAIStorybook

This folder contains simplified, high-level diagrams designed for better readability in documentation. These diagrams focus on the essential components and flows without overwhelming detail.

## Diagram Files

### 1. Use Case Diagram
- **File**: `use_case_diagram_simplified.puml`
- **Description**: Clean use case diagram without complex relationships
- **Features**:
  - Removed include/exclude relationships
  - Removed detailed sticky notes
  - Added external APIs and admin actors
  - Removed theme toggle use case
  - Focused on core functionality

### 2. Architecture Diagram
- **File**: `architecture_diagram_high_level.puml`
- **Description**: High-level layered architecture
- **Layers**:
  - **Presentation Layer**: Next.js Frontend, UI, Theme Management
  - **Business Logic Layer**: Multi-Agent Pipeline and specialized agents
  - **API Layer**: FastAPI Backend, REST endpoints, WebSocket, Authentication
  - **Data Processing Layer**: LLM, Image Generation, Audio Processing
  - **Database Layer**: PostgreSQL with user, story, and session data
  - **Storage Layer**: File system for generated content
  - **External Services**: Ollama and model storage

### 3. Domain Model Diagram
- **File**: `domain_model_simplified.mmd` (Mermaid format)
- **Alternative**: `domain_model_simplified.puml` (PlantUML format)
- **Description**: Simplified domain model showing core entities and relationships
- **Entity Groups**:
  - **Core Story Entities**: Story, Scene, Character
  - **User and Interaction**: User, UserPreferences, ChatSession
  - **Media and Export**: ImageFile, AudioFile, PDFExport
  - **System Management**: AgentExecution, EvaluationMetrics

### 4. Data Flow Diagram
- **File**: `data_flow_diagram_detailed.mmd` (Mermaid format) - **RECOMMENDED**
- **Alternative**: `data_flow_diagram_detailed.puml` (PlantUML format)
- **Simple Version**: `data_flow_diagram_simplified.mmd` (Context level only)
- **Description**: Level 1 DFD showing actual system processes and data stores
- **Key Elements**:
  - **External Entity**: User
  - **Processes**: Validate Input, Generate Story, Create Images, Review Quality, Format Output
  - **Data Stores**: Prompts, Drafts, Images, Reviews, Stories
  - **Data Flows**: Complete pipeline from user input to final story output

### 5. Class Diagram
- **File**: `class_diagram_simplified.mmd` (Mermaid format)
- **Alternative**: `class_diagram_simplified.puml` (PlantUML format)
- **Description**: Simplified class structure showing core classes and relationships
- **Class Groups**:
  - **Domain Classes**: Story, Scene, Character
  - **Agent Classes**: PromptAgent, WriterAgent, ImageAgent, DirectorAgent
  - **UI Classes**: FrontendApp, StoryInput, StoryDisplay
  - **API Classes**: FastAPIApp

### 6. State Transition Diagram
- **File**: `state_diagram_simplified.mmd` (Mermaid format)
- **Description**: Simplified state machine showing core story generation lifecycle
- **Key States**:
  - **Input States**: Idle, ValidatingInput, VoiceInput
  - **Processing States**: GeneratingStory, ReviewingContent, EditingContent
  - **Media States**: GeneratingImages, GeneratingAudio (conditional)
  - **Final States**: SavingStory, Completed, ErrorState
- **Transitions**: Clear flow from input to completion with error handling

### 7. Activity Diagram
- **File**: `activity_diagram_simplified.mmd` (Mermaid format)
- **Description**: Simplified activity diagram showing core story generation workflow
- **Key Activities**:
  - **Input Processing**: Validate & Enhance Input
  - **Story Generation**: Generate Story with Characters
  - **Quality Control**: Review Content Quality
  - **Content Processing**: Edit & Format Content
  - **Media Generation**: Generate Images and Audio (conditional)
  - **Output**: Save Story and Return Response
- **Decision Points**: Input validation, content approval, media generation toggles
- **Error Handling**: Graceful degradation for failed media generation

### 8. Sequence Diagrams (Multiple Focused Diagrams)

#### Basic Story Generation
- **File**: `sequence_diagram_basic_generation.puml`
- **Description**: Core text-to-story generation process
- **Flow**: User input → Prompt validation → Story generation → Review → Edit → Display

#### Image Generation
- **File**: `sequence_diagram_image_generation.puml`
- **Description**: Image generation with character consistency
- **Flow**: Scene processing → Stable Diffusion → IP-Adapter → Style transfer → File storage

#### Voice Interaction
- **File**: `sequence_diagram_voice_interaction.puml`
- **Description**: Voice input and audio generation
- **Flow**: Voice input → STT processing → Story generation → TTS synthesis → Audio playback

#### Chat Interaction
- **File**: `sequence_diagram_chat_interaction.puml`
- **Description**: Interactive conversational story development
- **Flow**: Chat initiation → Conversation → Context management → Story generation

#### Export Process
- **File**: `sequence_diagram_export_process.puml`
- **Description**: PDF and audio book export functionality
- **Flow**: Export request → Content formatting → File generation → Download

## Benefits of High-Level Diagrams

1. **Improved Readability**: Clean, focused diagrams without overwhelming detail
2. **Documentation Friendly**: Easy to include in LaTeX documents
3. **Stakeholder Communication**: Clear for non-technical audiences
4. **Modular Approach**: Separate diagrams for different system aspects
5. **Maintainability**: Easier to update individual components

## Usage in Documentation

These diagrams are designed to be included in the FYP documentation:

- **Use Case Diagram**: Chapter 2 (Requirements)
- **Architecture Diagram**: Chapter 3 (System Design)
- **Domain Model Diagram**: Chapter 3 (System Design) or Appendix
- **Sequence Diagrams**: Chapter 3 (System Design) or Appendix

## Original Diagrams

The original detailed diagrams are preserved in the parent `diagrams/` folder:
- `use_case_diagram.puml` - Original complex use case diagram
- `architecture_diagram.mmd` - Original detailed architecture
- `domain_model.mmd` - Original comprehensive domain model
- `sequence_diagram.mmd` - Original comprehensive sequence diagram

## Generation Instructions

To generate these diagrams:

1. **PlantUML Diagrams**: Use PlantUML renderer
   ```bash
   plantuml *.puml
   ```

2. **Mermaid Diagrams**: Use Mermaid renderer
   ```bash
   mmdc -i *.mmd -o *.png
   ```

3. **Online Rendering**: 
   - **Mermaid**: Use [Mermaid Live Editor](https://mermaid.live/)
   - **PlantUML**: Use [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)

## File Naming Convention

- `*_simplified.puml` - Simplified versions of complex diagrams
- `*_simplified.mmd` - Mermaid format versions for better compatibility
- `*_high_level.puml` - High-level architectural views
- `*_basic_*.puml` - Focused sequence diagrams for specific flows
