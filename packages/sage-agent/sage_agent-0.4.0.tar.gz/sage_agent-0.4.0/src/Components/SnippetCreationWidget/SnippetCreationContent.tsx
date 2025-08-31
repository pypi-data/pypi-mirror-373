import * as React from 'react';
import { SnippetCreationContentProps } from './types';
import { SnippetFormModal } from './SnippetFormModal';
import { SnippetList } from './SnippetList';
import { SEARCH_ICON } from '../../Chat/ChatContextMenu/icons';

/**
 * Main content component that orchestrates the different views
 */
export function SnippetCreationContent({
  state,
  onCreateNew,
  onSave,
  onEdit,
  onView,
  onDelete,
  onClose,
  onEnable,
  onTitleChange,
  onDescriptionChange,
  onContentChange
}: SnippetCreationContentProps): JSX.Element | null {
  const [searchQuery, setSearchQuery] = React.useState('');

  if (!state.isVisible) {
    return null;
  }

  const isFormMode = state.isCreating || state.editingSnippet;

  // Filter snippets based on search query
  const filteredSnippets = state.snippets.filter(snippet => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    return (
      snippet.title.toLowerCase().includes(query) ||
      snippet.description.toLowerCase().includes(query) ||
      snippet.content.toLowerCase().includes(query)
    );
  });

  return (
    <div className={'w-100 h-100'}>
      <div className="sage-ai-snippet-creation-panel">
        <div className="d-flex flex-column w-100 sage-ai-snippet-header-div">
          <div className="sage-ai-snippet-panel-header">
            <h3>Rules</h3>
          </div>

          <div className="d-flex flex-row">
            <div
              className="sage-ai-mention-search-container w-100"
              style={{ marginRight: 8 }}
            >
              <div style={{ marginBottom: '4px' }}>
                <SEARCH_ICON.react className="sage-ai-mention-search-icon" />
              </div>

              <input
                type="text"
                className="sage-ai-mention-search-input"
                placeholder="Search rules..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
            </div>
            <button
              className="sage-ai-snippet-create-btn"
              onClick={onCreateNew}
              title="Create New Snippet"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 5V19M5 12H19"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </button>
          </div>
        </div>

        <SnippetList
          snippets={filteredSnippets}
          onView={onEdit} // Now triggers edit mode
          onDelete={onDelete}
          onCreateNew={onCreateNew}
        />
      </div>

      {/* Modal for creating/editing snippets */}
      {isFormMode && (
        <SnippetFormModal
          title={state.title}
          description={state.description}
          content={state.content}
          isEditing={!!state.editingSnippet}
          onSave={onSave}
          onClose={onClose}
          onTitleChange={onTitleChange}
          onDescriptionChange={onDescriptionChange}
          onContentChange={onContentChange}
        />
      )}
    </div>
  );
}
