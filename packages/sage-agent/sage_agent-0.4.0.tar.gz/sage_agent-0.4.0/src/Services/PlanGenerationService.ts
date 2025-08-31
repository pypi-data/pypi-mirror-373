import { AppStateService } from '../AppState';

export interface PlanGenerationRequest {
  notebookSummary: string;
  currentPlan: string;
  immediateAction: string;
}

export class PlanGenerationService {
  private static planPrompt: string = '';

  /**
   * Initialize the service by loading the plan generation prompt
   */
  static async initialize(): Promise<void> {
    try {
      this.planPrompt = require('../Config/prompts/plan_generation_prompt.md');
      console.log('[PlanGenerationService] Initialized with prompt');
    } catch (error) {
      console.error('[PlanGenerationService] Failed to initialize:', error);
      throw error;
    }
  }

  /**
   * Generate a plan using a separate LLM call
   */
  static async generatePlan(request: PlanGenerationRequest): Promise<string> {
    try {
      const chatService = AppStateService.getChatService();

      // Create the user message with context
      const userMessage = `## Notebook Summary
${request.notebookSummary}

## Current Plan
${request.currentPlan || 'No existing plan'}

## Immediate Action
${request.immediateAction}

Generate an updated plan based on this context.`;

      // Use the same model as the main chat service
      const modelName = chatService.getModelName();

      // Make ephemeral call to generate plan
      const response = await chatService.sendEphemeralMessage(
        userMessage,
        this.planPrompt,
        modelName, // Use same model as main chat
        undefined,
        { maxTokens: 2048 } // Increase token limit for full plans
      );

      return response.trim();
    } catch (error) {
      console.error('[PlanGenerationService] Failed to generate plan:', error);
      throw error;
    }
  }
}
