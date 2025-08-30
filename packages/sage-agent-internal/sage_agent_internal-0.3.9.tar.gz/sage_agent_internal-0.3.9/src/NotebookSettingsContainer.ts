import { PanelLayout, Widget } from '@lumino/widgets';
import { SettingsWidget } from './Components/Settings/SettingsWidget';
import { ToolService } from './Services/ToolService';
import { NotebookDiffManager } from './Notebook/NotebookDiffManager';
import { NotebookContextManager } from './Notebook/NotebookContextManager';

/**
 * Container widget that holds only the settings
 */
export class NotebookSettingsContainer extends Widget {
  private settingsWidget: SettingsWidget;

  constructor(
    toolService: ToolService,
    diffManager: NotebookDiffManager | null | undefined,
    contextManager: NotebookContextManager | null | undefined
  ) {
    super();

    this.id = 'sage-ai-settings-container';
    this.title.label = 'Sage Settings';
    this.title.closable = true;
    this.addClass('sage-ai-settings-container');

    // Create the settings widget
    this.settingsWidget = new SettingsWidget(toolService);

    // Fix layout type issue - create a proper PanelLayout
    const layout = new PanelLayout();
    layout.addWidget(this.settingsWidget);

    // Set the layout properly
    this.layout = layout;
  }
}
