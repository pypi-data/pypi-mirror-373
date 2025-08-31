import { ISnippet } from '../../AppState';

/**
 * Interface for the SnippetCreation state
 */
export interface ISnippetCreationState {
  isVisible: boolean;
  snippets: ISnippet[];
  isCreating: boolean;
  editingSnippet: ISnippet | null;
  viewingSnippet: ISnippet | null;
  title: string;
  description: string;
  content: string;
}

/**
 * Props for the main SnippetCreationContent component
 */
export interface SnippetCreationContentProps {
  state: ISnippetCreationState;
  onCreateNew: () => void;
  onSave: () => void;
  onEdit: (snippet: ISnippet) => void;
  onView: (snippet: ISnippet) => void;
  onDelete: (snippetId: string) => void;
  onClose: () => void;
  onEnable: (snippet: ISnippet) => void;
  onTitleChange: (value: string) => void;
  onDescriptionChange: (value: string) => void;
  onContentChange: (value: string) => void;
}

/**
 * Props for the SnippetForm component
 */
export interface SnippetFormProps {
  title: string;
  description: string;
  content: string;
  isEditing: boolean;
  onSave: () => void;
  onClose: () => void;
  onTitleChange: (value: string) => void;
  onDescriptionChange: (value: string) => void;
  onContentChange: (value: string) => void;
}

/**
 * Props for the SnippetViewer component
 */
export interface SnippetViewerProps {
  snippet: ISnippet;
  onEdit: (snippet: ISnippet) => void;
  onEnable: (snippet: ISnippet) => void;
  onClose: () => void;
}

/**
 * Props for the SnippetList component
 */
export interface SnippetListProps {
  snippets: ISnippet[];
  onView: (snippet: ISnippet) => void; // Now used for editing
  onDelete: (snippetId: string) => void;
  onCreateNew: () => void;
}
