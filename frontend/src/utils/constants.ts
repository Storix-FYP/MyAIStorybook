// Application constants
export const LOADING_MESSAGES: string[] = [
  "Awakening the Storyteller...",
  "Gathering stardust and moonbeams...",
  "Dreaming up characters and quests...",
  "Painting scenes with vibrant colors...",
  "The final chapter is being written...",
];

export const API_ENDPOINTS = {
  GENERATE: 'http://localhost:8000/api/generate',
  DEVICE: 'http://localhost:8000/device',
  GENERATED: 'http://localhost:8000/generated'
} as const;

export const APP_CONFIG = {
  NAME: 'MyAIStorybook',
  DESCRIPTION: 'Create magical illustrated children\'s stories with AI',
  VERSION: '1.0.0'
} as const;
