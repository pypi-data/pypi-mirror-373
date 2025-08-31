/**
 * Constants and loading methods for chat context menu
 */
import { Contents } from '@jupyterlab/services';
import { ToolService } from '../../Services/ToolService';
import { DatabaseMetadataCache } from '../../Services/DatabaseMetadataCache';
import { KernelPreviewUtils } from '../../utils/kernelPreview';
import { AppStateService, ISnippet } from '../../AppState';

export interface MentionContext {
  type: 'snippets' | 'data' | 'variable' | 'cell';
  id: string;
  name: string;
  content?: string;
  description?: string;
}

// Constants
export const VARIABLE_TYPE_BLACKLIST = [
  'module',
  'type',
  'function',
  'ZMQExitAutocall',
  'method'
];

export const VARIABLE_NAME_BLACKLIST = ['In', 'Out'];

export const MENTION_CATEGORIES = [
  {
    id: 'snippets',
    name: 'Rules',
    icon: '📄',
    description: 'Reusable code and prompt templates'
  },
  {
    id: 'data',
    name: 'Data',
    icon: '📊',
    description: 'Dataset references and info'
  },
  {
    id: 'variables',
    name: 'Variables',
    icon: '🔤',
    description: 'Code variables and values'
  },
  {
    id: 'cells',
    name: 'Cells',
    icon: '📝',
    description: 'Notebook cell references'
  }
];

/**
 * Class responsible for loading different types of context items
 */
export class ChatContextLoaders {
  private contentManager: Contents.IManager;
  private toolService: ToolService;

  constructor(contentManager: Contents.IManager, toolService: ToolService) {
    this.contentManager = contentManager;
    this.toolService = toolService;
  }

  /**
   * Initialize context items for each category
   */
  public async initializeContextItems(): Promise<
    Map<string, MentionContext[]>
  > {
    const contextItems = new Map<string, MentionContext[]>();

    // Load snippets from AppState (empty initially)
    contextItems.set('snippets', []);
    contextItems.set('data', []);
    contextItems.set('variables', []);
    contextItems.set('cells', []);

    console.log(
      'All context items after initialization:',
      Array.from(contextItems.entries())
    ); // Debug log

    return contextItems;
  }

  /**
   * Load snippets from AppState
   */
  public async loadSnippets(): Promise<MentionContext[]> {
    const snippets = AppStateService.getSnippets();
    return snippets.map(snippet => ({
      type: 'snippets' as const,
      id: snippet.id,
      name: snippet.title,
      description:
        snippet.description.length > 100
          ? snippet.description.substring(0, 100) + '...'
          : snippet.description,
      content: snippet.content
    }));
  }

  /**
   * Load datasets from the data directory and include database metadata
   */
  public async loadDatasets(): Promise<MentionContext[]> {
    const datasetContexts: MentionContext[] = [];

    // First, try to add database metadata from cache (never retry pulling it)
    try {
      const dbCache = DatabaseMetadataCache.getInstance();
      const cachedMetadata = await dbCache.getCachedMetadata();
      const db_prompt =
        'Database Connection Available:\n' +
        '- DB_URL environment variable is configured in your Python kernel\n' +
        '- You can connect to the database using standard Python libraries like psycopg2 or sqlalchemy\n' +
        '\n' +
        'Database Schema:\n';
      if (cachedMetadata) {
        datasetContexts.push({
          type: 'data' as const,
          id: 'database-schema',
          name: 'Database Schema',
          description: 'Current database schema information',
          content: `${db_prompt} \n \n ${cachedMetadata}`
        });
        console.log(
          '[ChatContextLoaders] Added database schema to data contexts'
        );
      }
    } catch (error) {
      console.warn(
        '[ChatContextLoaders] Could not load database metadata:',
        error
      );
    }

    // Then load file-based datasets
    try {
      const datasets = await this.contentManager.get('./data');
      console.log('Loaded datasets:', datasets); // Debug log

      if (datasets.content && Array.isArray(datasets.content)) {
        const fileDatasets: MentionContext[] = await Promise.all(
          datasets.content
            .filter(file => file.type === 'file')
            .map(async file => {
              // remove everything from the last dot to the end (e.g. ".json", ".csv", ".txt", etc.)
              const name = file.name.replace(/\.[^/.]+$/, '');

              const content = await this.contentManager.get(
                './data/' + file.name
              );

              const contentString = `${content.content}`;
              const filePath = `./data/${file.name}`;

              // Determine file type and process content accordingly
              let processedContent = '';
              const isCSV = file.name.toLowerCase().endsWith('.csv');

              if (isCSV) {
                // For CSV files: get first 2 rows, limited to 5000 characters
                const lines = contentString.split('\n');
                const headerAndFirstRow = lines.slice(0, 5).join('\n');
                processedContent = headerAndFirstRow.slice(0, 5000);
              } else {
                // For non-CSV files: get last 2000 characters
                processedContent = contentString.slice(-2000);
              }

              // Include the file path in the content
              const contentWithPath = `File Path: ${filePath}\n\n${processedContent}`;

              return {
                type: 'data' as const,
                id: file.path,
                name,
                description: `Dataset file (${isCSV ? 'CSV' : 'Data'} file)`,
                content: contentWithPath
              };
            })
        );

        datasetContexts.push(...fileDatasets);
      }
    } catch (error) {
      console.error('Error loading datasets:', error);
    }

    return datasetContexts;
  }

  /**
   * Load notebook cells
   */
  public async loadCells(): Promise<MentionContext[]> {
    console.log('Loading cells... ======================');
    const notebook = this.toolService.getCurrentNotebook();
    if (!notebook) {
      console.warn('No notebook available');
      return [];
    }

    const cellContexts: MentionContext[] = [];
    const cells = notebook.widget.model.cells as any;

    for (const cell of cells) {
      console.log('Cell:', cell); // Debug log
      console.log('Cell metadata:', cell.metadata); // Debug log

      const tracker = cell.metadata.cell_tracker;
      if (tracker) {
        cellContexts.push({
          type: 'cell',
          id: tracker.trackingId,
          name: tracker.trackingId,
          description: '',
          content: cell.sharedModel.getSource()
        });
      }
    }

    console.log('CELL LOADING, cells:', cells); // Debug log
    return cellContexts;
  }

  /**
   * Load variables from the current kernel
   */
  public async loadVariables(): Promise<MentionContext[]> {
    console.log('Loading variables... ======================');
    const kernel = this.toolService.getCurrentNotebook()?.kernel;
    if (!kernel) {
      console.warn('No kernel available');
      return [];
    }

    try {
      // Use the shared kernel preview utilities to get detailed variable information
      const kernelVariables = await KernelPreviewUtils.getKernelVariables();

      if (!kernelVariables) {
        console.log('No kernel variables available');
        return [];
      }

      const variableContexts: MentionContext[] = [];

      for (const [varName, varInfo] of Object.entries(kernelVariables)) {
        // Skip variables in blacklists
        if (VARIABLE_NAME_BLACKLIST.includes(varName)) continue;
        if (VARIABLE_TYPE_BLACKLIST.includes(varInfo.type)) continue;

        // Create a description based on the variable info
        let description = varInfo.type || 'unknown';
        if (varInfo.shape) {
          description += ` (shape: ${JSON.stringify(varInfo.shape)})`;
        } else if (varInfo.size !== undefined && varInfo.size !== null) {
          description += ` (size: ${varInfo.size})`;
        }

        // Create content for the variable
        let content = '';
        if (varInfo.value !== undefined) {
          content = JSON.stringify(varInfo.value);
        } else if (varInfo.preview !== undefined) {
          content = JSON.stringify(varInfo.preview);
        } else if (varInfo.repr) {
          content = varInfo.repr;
        }

        variableContexts.push({
          type: 'variable',
          id: varName,
          name: varName,
          description: description,
          content: content
        });
      }

      console.log(
        `[ChatContextLoaders] Loaded ${variableContexts.length} variables`
      );
      return variableContexts;
    } catch (error) {
      console.error('Error loading variables:', error);
      return [];
    }
  }
}
