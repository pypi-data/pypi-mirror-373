import { INotebookTracker } from '@jupyterlab/notebook';
import { AppStateService } from './AppState';

/**
 * Utility to help migrate or fix tracking IDs in notebooks
 */
export class TrackingIDUtility {
  private notebookTracker: INotebookTracker;

  constructor(notebookTracker: INotebookTracker) {
    this.notebookTracker = notebookTracker;
  }

  /**
   * Helper to get the next available cell number for cell IDs
   */
  private getNextCellNumber(notebook: any): number {
    const cells = notebook.widgets;
    let maxNum = 0;
    for (let i = 0; i < cells.length; i++) {
      const metadata: any = cells[i].model.sharedModel.getMetadata() || {};
      const trackingId = metadata.cell_tracker?.trackingId;
      if (trackingId && /^cell_(\d+)$/.test(trackingId)) {
        const num = parseInt(trackingId.split('_')[1], 10);
        if (num > maxNum) maxNum = num;
      }
    }
    return maxNum + 1;
  }

  /**
   * Ensure a specific cell has a valid tracking ID
   * @param cell The cell to check/update
   * @returns The tracking ID (either existing or newly created)
   */
  public ensureCellHasTrackingID(cell: any): string {
    if (!cell) return '';

    const notebook = this.notebookTracker.currentWidget?.content;
    const metadata: any = cell.model.sharedModel.getMetadata() || {};

    // Check if cell_tracker metadata exists and has a valid tracking ID
    if (!metadata.cell_tracker || !metadata.cell_tracker.trackingId) {
      // Create or update tracking metadata
      const now = new Date().toISOString();
      const trackingId = `cell_${this.getNextCellNumber(notebook)}`;

      metadata.cell_tracker = {
        trackingId,
        createdAt: now,
        lastModified: now,
        origin: 'user', // Assume user origin for existing cells
        summary: metadata.custom?.summary || ''
      };

      // Apply the updated metadata
      cell.model.sharedModel.setMetadata(metadata);
      return metadata.cell_tracker.trackingId;
    }

    return metadata.cell_tracker.trackingId;
  }

  /**
   * Ensure all cells in the current notebook have valid tracking IDs
   * @param notebookId Optional path to a specific notebook
   * @returns Number of cells that were fixed/updated
   */
  public fixTrackingIDs(notebookId?: string): number {
    // Get notebook by path or current if not specified
    let notebook;
    if (notebookId) {
      notebook = AppStateService.getCurrentNotebook();
      if (!notebook) {
        console.warn(`Notebook with ID ${notebookId} not found`);
        return 0;
      }
    }

    if (!notebook) return 0;

    const cells = notebook.content.widgets;
    let fixedCount = 0;

    for (let i = 0; i < cells.length; i++) {
      const cell = cells[i];
      const metadata: any = cell.model.sharedModel.getMetadata() || {};
      let needsNewId = false;
      // Check if cell_tracker metadata exists and has a valid tracking ID
      if (!metadata.cell_tracker || !metadata.cell_tracker.trackingId) {
        needsNewId = true;
      } else {
        // If the trackingId does not match the cell_# format, regenerate it
        if (
          metadata.cell_tracker.trackingId !== 'planning_cell' &&
          !/^cell_\d+$/.test(metadata.cell_tracker.trackingId)
        ) {
          needsNewId = true;
        }
      }
      if (needsNewId) {
        // Create or update tracking metadata
        const now = new Date().toISOString();
        const trackingId = `cell_${this.getNextCellNumber(notebook.content)}`;
        metadata.cell_tracker = {
          trackingId,
          createdAt: now,
          lastModified: now,
          origin: 'user', // Assume user origin for existing cells
          summary: metadata.custom?.summary || ''
        };
        // Apply the updated metadata
        cell.model.sharedModel.setMetadata(metadata);
        fixedCount++;
      }
    }

    return fixedCount;
  }

  /**
   * Get a report of cell tracking IDs and their associated model IDs
   * @param notebookPath Optional path to a specific notebook
   * @returns Array of objects with tracking ID and model ID information
   */
  public getTrackingIDReport(notebookPath?: string): Array<{
    trackingId: string;
    modelId: string;
    cellType: string;
    index: number;
  }> {
    // Get notebook by path or current if not specified
    let notebook;
    if (notebookPath) {
      // Find notebook by path
      let found = false;
      this.notebookTracker.forEach(widget => {
        if (widget.context.path === notebookPath) {
          notebook = widget.content;
          found = true;
        }
      });
      if (!found) {
        console.warn(`Notebook with path ${notebookPath} not found`);
        return [];
      }
    } else {
      // Use current notebook
      notebook = this.notebookTracker.currentWidget?.content;
    }

    if (!notebook) return [];

    const cells = notebook.widgets;
    const report = [];

    // Reverse the index count so that index 0 is at the top of the notebook
    const cellCount = cells.length;

    for (let i = 0; i < cellCount; i++) {
      const cell = cells[i];
      const metadata: any = cell.model.sharedModel.getMetadata() || {};

      report.push({
        trackingId: metadata.cell_tracker?.trackingId || 'missing',
        modelId: cell.model.id,
        cellType: cell.model.type,
        index: i // This is the index from top to bottom (0 is top, increasing downward)
      });
    }

    return report;
  }
}
