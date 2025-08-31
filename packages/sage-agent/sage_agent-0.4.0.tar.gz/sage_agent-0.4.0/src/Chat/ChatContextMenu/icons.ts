import { LabIcon } from '@jupyterlab/ui-components';
import variableIcon from '../../../style/icons/context_menu/variable.svg';
import snippetsIcon from '../../../style/icons/context_menu/snippets.svg';
import dataIcon from '../../../style/icons/context_menu/data.svg';
import cellIcon from '../../../style/icons/context_menu/cell.svg';
import searchIcon from '../../../style/icons/context_menu/search.svg';
import insertIcon from '../../../style/icons/context_menu/insert.svg';
// Context menu icons
export const VARIABLE_ICON = new LabIcon({
  name: 'sage-agent:context-variable-icon',
  svgstr: variableIcon
});

export const SNIPPETS_ICON = new LabIcon({
  name: 'sage-agent:context-snippets-icon',
  svgstr: snippetsIcon
});

export const DATA_ICON = new LabIcon({
  name: 'sage-agent:context-data-icon',
  svgstr: dataIcon
});

export const CELL_ICON = new LabIcon({
  name: 'sage-agent:context-cell-icon',
  svgstr: cellIcon
});

export const SEARCH_ICON = new LabIcon({
  name: 'sage-agent:search-icon',
  svgstr: searchIcon
});

export const BACK_CARET_ICON = new LabIcon({
  name: 'sage-agent:back-caret-icon',
  svgstr: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="15" viewBox="0 0 14 15" fill="none">
    <path d="M8.75 11L5.25 7.5L8.75 4" stroke="#E7E7E7" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`
});

export const INSERT_ICON = new LabIcon({
  name: 'sage-agent:insert-icon',
  svgstr: insertIcon
});
