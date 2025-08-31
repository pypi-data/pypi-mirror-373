import { JupyterFrontEnd } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import { AppStateService } from './AppState';
import {
  INotebookTracker,
  NotebookActions,
  NotebookPanel
} from '@jupyterlab/notebook';
import { ChatHistoryManager } from './Chat/ChatHistoryManager';
import { timeout } from './utils';
import { IDocumentManager } from '@jupyterlab/docmanager';

/**
 * Register all commands for the sage-ai extension
 */
export function registerEvalCommands(
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  documentManager: IDocumentManager
): void {
  // Register test add with diff command
  registerRunEvals(app, palette, documentManager);
}

/**
 * Register the test add with diff command
 */
function registerRunEvals(
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  documentManager: IDocumentManager
): void {
  const runEvalCommand: string = 'sage-ai:run_eval';

  app.commands.addCommand(runEvalCommand, {
    label: 'Run Eval',
    execute: async args => {
      const notebookTools = AppStateService.getNotebookTools();
      const diffManager = AppStateService.getNotebookDiffManager();
      const notebooks = AppStateService.getNotebookTracker();

      console.log('TOOL CALL LIMIT', args.tool_call_limit);

      // Set the tool call limit in AppState if provided
      if (args.tool_call_limit && typeof args.tool_call_limit === 'number') {
        AppStateService.setMaxToolCallLimit(args.tool_call_limit);
        console.log('Set max tool call limit to:', args.tool_call_limit);
      } else {
        AppStateService.setMaxToolCallLimit(null);
      }

      const { commands, shell } = app;
      const current = shell.currentWidget;
      const notebookPath = 'evals.ipynb';
      console.log(
        'CURRENT NOTEBOOK ID:',
        AppStateService.getNotebookTracker().currentWidget?.sessionContext.path
      );

      if (notebooks.currentWidget) {
        // await documentManager.overwrite(notebookPath, notebookPath);
        // if (notebooks.currentWidget.context.canSave)
        await notebooks.currentWidget.context.revert();
        // else await notebooks.currentWidget.context.revert();
        await documentManager.closeFile(notebookPath);
      }
      documentManager.open(notebookPath, 'default', undefined, {
        activate: true
      });

      await timeout(500); // Wait for the notebook to open

      // Get the unique_id from the opened notebook metadata
      const currentNotebook = notebooks.currentWidget;
      let notebookUniqueId: string | null = null;

      if (currentNotebook) {
        try {
          const contentManager = AppStateService.getContentManager();
          const nbFile = await contentManager?.get(
            currentNotebook.context.path
          );
          if (nbFile?.content?.metadata?.sage_ai?.unique_id) {
            notebookUniqueId = nbFile.content.metadata.sage_ai.unique_id;
          }
        } catch (error) {
          console.warn(
            'Could not get notebook metadata for eval notebook:',
            error
          );
        }
      }

      AppStateService.setCurrentNotebookId(notebookUniqueId || notebookPath);

      const notebook = notebooks.currentWidget?.content;
      if (notebook)
        await NotebookActions.runAll(
          notebook,
          notebooks.currentWidget?.sessionContext
        );

      const chatWidget = AppStateService.getChatContainerSafe()?.chatWidget;
      if (!chatWidget) {
        console.error('Chat widget not found');
        return;
      }

      const contentManager = AppStateService.getContentManager();
      const prompt = await contentManager.get('eval_prompt.txt');

      if (!prompt || !prompt.content) {
        console.error('Prompt content not found');
        return;
      }

      await chatWidget.threadManager.createNewThread();
      await timeout(200);

      chatWidget.conversationService.setAutoRun(true);
      chatWidget.inputManager.setInputValue(prompt.content);
      await chatWidget.inputManager.sendMessage();

      const chatHistory = chatWidget.chatHistoryManager.getCurrentThread();

      if (!chatHistory) {
        console.error('Chat history not found');
        return;
      }

      const cleanedMessages =
        ChatHistoryManager.getCleanMessageArrayWithTimestamps(chatHistory);

      notebooks.currentWidget?.sessionContext.restartKernel();

      // Create json file and save messages
      const filename = 'eval_output.json';
      await contentManager.save(filename, {
        type: 'file',
        format: 'text',
        content: JSON.stringify(cleanedMessages, null, 2)
      });

      console.log('Cleaned Messages:', cleanedMessages);

      const checkpoints = await currentNotebook?.context.listCheckpoints();

      if (checkpoints) {
        for (const checkpoint of checkpoints) {
          console.log('Checkpoint:', checkpoint);
          currentNotebook?.context.deleteCheckpoint(checkpoint.id);
        }
      }

      currentNotebook?.context.createCheckpoint();
      currentNotebook?.context.save();

      const result = {
        messages: cleanedMessages,
        notebook_content:
          notebook?.widgets.map(cell => ({
            source: cell.model.sharedModel.getSource(),
            cell_type: cell.model.sharedModel.cell_type,
            output:
              cell.model.sharedModel.cell_type === 'code'
                ? (cell as any).outputArea &&
                  (cell as any).outputArea.model.toJSON()
                : null
          })) || []
      };

      await timeout(1000);

      console.log(result);

      AppStateService.setMaxToolCallLimit(null);

      return result;
    }
  });

  palette.addItem({ command: runEvalCommand, category: 'AI Tools' });
}
