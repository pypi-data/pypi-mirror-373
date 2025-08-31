import { LabIcon } from '@jupyterlab/ui-components';
import menuIcon from '../../../style/icons/state_display/menu-icon.svg';
import menuCloseIcon from '../../../style/icons/state_display/menu-close.svg';
import runCellIcon from '../../../style/icons/state_display/run_cell.svg';

export const MENU_ICON = new LabIcon({
  name: 'sage-agent-internal:state-menu-icon', // unique name for your icon
  svgstr: menuIcon // the imported SVG content as string
});

export const MENU_CLOSE_ICON = new LabIcon({
  name: 'sage-agent-internal:state-menu-close-icon', // unique name for your icon
  svgstr: menuCloseIcon // the imported SVG content as string
});

export const RUN_CELL_ICON = new LabIcon({
  name: 'sage-agent-internal:run-cell-icon',
  svgstr: runCellIcon
});
