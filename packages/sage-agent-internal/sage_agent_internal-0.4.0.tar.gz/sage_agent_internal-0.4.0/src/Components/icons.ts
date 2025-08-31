import { LabIcon } from '@jupyterlab/ui-components';
import agentModeIcon from '../../style/icons/chat_input/agent-mode.svg';
import agentModeShinyIcon from '../../style/icons/chat_input/agent-mode-shiny.svg';
import handsOnModeIcon from '../../style/icons/chat_input/hands-on-mode.svg';
import askIcon from '../../style/icons/chat_input/ask-mode.svg';
import openModeSelectorIcon from '../../style/icons/chat_input/open.svg';
import sendIcon from '../../style/icons/chat_input/send.svg';
import stopIcon from '../../style/icons/chat_input/stop.svg';
import reapplyIcon from '../../style/icons/chat_input/reapply.svg';
import arrowUpIcon from '../../style/icons/chat_input/arrow-up.svg';
import arrowDownIcon from '../../style/icons/chat_input/arrow-down.svg';
import approveIcon from '../../style/icons/chat_input/approve.svg';
import rejectIcon from '../../style/icons/chat_input/reject.svg';
import runIcon from '../../style/icons/chat_input/run.svg';
import checkIcon from '../../style/icons/chat_input/check.svg';
import dashedCircleIcon from '../../style/icons/chat_input/dashed-circle.svg';

export const AGENT_MODE_ICON = new LabIcon({
  name: 'sage-agent-internal:agent-mode-icon', // unique name for your icon
  svgstr: agentModeIcon // the imported SVG content as string
});

export const AGENT_MODE_SHINY_ICON = new LabIcon({
  name: 'sage-agent-internal:agent-mode-shiny-icon', // unique name for your icon
  svgstr: agentModeShinyIcon // the imported SVG content as string
});

export const HANDS_ON_MODE_ICON = new LabIcon({
  name: 'sage-agent-internal:hands-on-icon',
  svgstr: handsOnModeIcon
});

export const ASK_ICON = new LabIcon({
  name: 'sage-agent-internal:ask-icon',
  svgstr: askIcon
});

export const OPEN_MODE_SELECTOR_ICON = new LabIcon({
  name: 'sage-agent-internal:open-mode-selector-icon',
  svgstr: openModeSelectorIcon
});

export const SEND_ICON = new LabIcon({
  name: 'sage-agent-internal:send-icon',
  svgstr: sendIcon
});

export const STOP_ICON = new LabIcon({
  name: 'sage-agent-internal:stop-icon',
  svgstr: stopIcon
});

export const REAPPLY_ICON = new LabIcon({
  name: 'sage-agent-internal:reapply-icon',
  svgstr: reapplyIcon
});

export const ARROW_UP_ICON = new LabIcon({
  name: 'sage-agent-internal:arrow-up-icon',
  svgstr: arrowUpIcon
});

export const ARROW_DOWN_ICON = new LabIcon({
  name: 'sage-agent-internal:arrow-down-icon',
  svgstr: arrowDownIcon
});

export const APPROVE_ICON = new LabIcon({
  name: 'sage-agent-internal:approve-icon',
  svgstr: approveIcon
});

export const REJECT_ICON = new LabIcon({
  name: 'sage-agent-internal:reject-icon',
  svgstr: rejectIcon
});

export const RUN_ICON = new LabIcon({
  name: 'sage-agent-internal:run-icon',
  svgstr: runIcon
});

export const CHECK_ICON = new LabIcon({
  name: 'sage-agent-internal:check-icon',
  svgstr: checkIcon
});

export const DASHED_CIRCLE_ICON = new LabIcon({
  name: 'sage-agent-internal:dashed-circle-icon',
  svgstr: dashedCircleIcon
});
