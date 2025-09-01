import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { BoxLayout } from '@lumino/widgets';

import { FloatingInputWidget } from './widget';

/**
 * Initialization data for the pantheon-notebook extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'pantheon-notebook:plugin',
  description: 'A JupyterLab extension for Pantheon CLI integration',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, notebookTracker: INotebookTracker) => {
    console.log('JupyterLab extension pantheon-notebook is activated!');
    
    // Map to store widgets for each notebook
    const widgetMap = new Map<NotebookPanel, FloatingInputWidget>();
    
    // Listen for new notebooks being added
    notebookTracker.widgetAdded.connect((sender, notebook) => {
      console.log('New notebook opened, adding Pantheon widget');
      
      // Create a new floating widget for this notebook
      const floatingWidget = new FloatingInputWidget(app, notebookTracker);
      
      // Store the widget reference
      widgetMap.set(notebook, floatingWidget);
      
      // Add the widget to the notebook's layout
      const layout = notebook.layout as BoxLayout;
      if (layout) {
        floatingWidget.setParentLayout(layout);
        layout.addWidget(floatingWidget);
      }
      
      // Clean up when notebook is disposed
      notebook.disposed.connect(() => {
        console.log('Notebook closed, removing Pantheon widget');
        const widget = widgetMap.get(notebook);
        if (widget) {
          widget.dispose();
          widgetMap.delete(notebook);
        }
      });
    });
    
    console.log('Pantheon notebook extension setup complete');
  }
};

export default plugin;