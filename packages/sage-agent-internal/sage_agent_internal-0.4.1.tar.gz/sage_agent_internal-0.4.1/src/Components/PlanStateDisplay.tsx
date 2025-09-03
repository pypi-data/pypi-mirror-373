import * as React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';
import { ISignal, Signal } from '@lumino/signaling';
import { AppStateService } from '../AppState';

/**
 * Interface for the Plan state
 */
interface IPlanState {
  isVisible: boolean;
  currentStep?: string;
  nextStep?: string;
  source?: string;
  isLoading: boolean;
}

interface PlanStateDisplayWidgetProps {
  isVisible: boolean;
  currentStep?: string;
  nextStep?: string;
  source?: string;
  isLoading: boolean;
}

/**
 * React component for displaying Plan state content
 */
interface PlanStateContentProps {
  isVisible: boolean;
  currentStep?: string;
  nextStep?: string;
  source?: string;
  isLoading: boolean;
}

/**
 * Extract task items and title from plan markdown
 * @param source The markdown source content
 * @returns Object with title and tasks array with completion status, task type, and subtopics
 *
 * Example input:
 * # [Data Analysis] Plan
 * - [ ] Load and explore the dataset
 *   - Subtopic: Data overview
 * - [x] Clean missing values
 *   - [ ] Handle outliers
 *   - [ ] Impute missing data
 * - [ ] Create visualizations
 *
 * Example output: {
 *   title: "[Data Analysis] Plan",
 *   tasks: [
 *     {
 *       text: "Load and explore the dataset",
 *       completed: false,
 *       type: "task",
 *       subtopics: ["Data overview"]
 *     },
 *     {
 *       text: "Clean missing values",
 *       completed: true,
 *       type: "task",
 *       subtopics: []
 *     },
 *     {
 *       text: "Handle outliers",
 *       completed: false,
 *       type: "subtask",
 *       subtopics: []
 *     },
 *     {
 *       text: "Impute missing data",
 *       completed: false,
 *       type: "subtask",
 *       subtopics: []
 *     },
 *     {
 *       text: "Create visualizations",
 *       completed: false,
 *       type: "task",
 *       subtopics: []
 *     }
 *   ]
 * }
 */
function extractPlanContent(source: string): {
  title?: string;
  tasks: Array<{
    text: string;
    completed: boolean;
    type: 'task' | 'subtask';
    subtopics: string[];
  }>;
} {
  if (!source || !source.trim()) {
    return { tasks: [] };
  }

  const lines = source.split('\n');
  const tasks: Array<{
    text: string;
    completed: boolean;
    type: 'task' | 'subtask';
    subtopics: string[];
  }> = [];
  let title: string | undefined;
  let currentTask: {
    text: string;
    completed: boolean;
    type: 'task' | 'subtask';
    subtopics: string[];
  } | null = null;

  for (const line of lines) {
    const trimmedLine = line.trim();

    // Match title: # [Task Name] Plan
    const titleMatch = trimmedLine.match(/^#\s*(.+)$/);
    if (titleMatch && !title) {
      title = titleMatch[1].trim();
      continue;
    }

    // Match main task items: - [ ] or - [x] followed by task description
    // Examples: "- [ ] Task description" or "- [x] Completed task"
    const taskMatch = trimmedLine.match(/^-\s*\[([ x])\]\s*(.+)$/);
    if (taskMatch) {
      // If we have a previous task, add it to the tasks array
      if (currentTask) {
        tasks.push(currentTask);
      }

      const completed = taskMatch[1] === 'x';
      const text = taskMatch[2].trim();
      const type = line.startsWith('    ') ? 'subtask' : 'task';

      currentTask = {
        text,
        completed,
        type,
        subtopics: []
      };
      continue;
    }

    // Match subtopics: lines with indentation that don't start with - [ ]
    // These are informational subtopics, not actionable subtasks
    const subtopicMatch = line.startsWith('    -');
    if (subtopicMatch && currentTask) {
      const subtopicText = line.replace('    -', '');
      currentTask.subtopics.push(subtopicText);
      continue;
    }
  }

  // Don't forget to add the last task
  if (currentTask) {
    tasks.push(currentTask);
  }

  return { title, tasks };
}

function PlanStateContent({
  isVisible,
  currentStep,
  nextStep,
  source,
  isLoading
}: PlanStateContentProps): JSX.Element | null {
  const [isSourceExpanded, setIsSourceExpanded] = React.useState(false);
  const [planContent, setPlanContent] = React.useState<{
    title?: string;
    tasks: Array<{
      text: string;
      completed: boolean;
      type: 'task' | 'subtask';
      subtopics: string[];
    }>;
  }>({ tasks: [] });

  // Refs for task items to enable scrolling
  const taskRefs = React.useRef<(HTMLDivElement | null)[]>([]);

  // Helper function to determine if a task is currently being executed
  const isTaskExecuting = (taskText: string): boolean => {
    return !!(
      isLoading &&
      currentStep &&
      currentStep.toLowerCase().includes(taskText.toLowerCase())
    );
  };

  // Helper function to find the first executing task index
  const findFirstExecutingTaskIndex = (): number => {
    return planContent.tasks.findIndex(task => isTaskExecuting(task.text));
  };

  // Helper function to find the next task to execute (first incomplete task)
  const findNextTaskToExecuteIndex = (): number => {
    return planContent.tasks.findIndex(task => !task.completed);
  };

  // Extract plan content from source content
  React.useEffect(() => {
    if (source && source.trim()) {
      const content = extractPlanContent(source);
      setPlanContent(content);
      // Initialize refs array when tasks change
      taskRefs.current = new Array(content.tasks.length).fill(null);
    } else {
      setPlanContent({ tasks: [] });
      taskRefs.current = [];
    }
  }, [source]);

  // Scroll to the first executing task or next task to execute
  React.useEffect(() => {
    if (isSourceExpanded && planContent.tasks.length > 0) {
      const executingIndex = findFirstExecutingTaskIndex();
      const nextIndex = findNextTaskToExecuteIndex();

      // Prioritize executing task, then next task to execute
      const targetIndex = executingIndex >= 0 ? executingIndex : nextIndex;

      if (targetIndex >= 0 && taskRefs.current[targetIndex]) {
        setTimeout(() => {
          taskRefs.current[targetIndex]?.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
        }, 100); // Small delay to ensure DOM is ready
      }
    }
  }, [isSourceExpanded, planContent.tasks, isLoading, currentStep]);

  if (!isVisible) {
    return null;
  }

  const hasSource = source && source.trim();
  const hasContent = planContent.tasks.length > 0 || planContent.title;

  return (
    <div className="sage-ai-plan-state-display">
      <div className="sage-ai-plan-state-header">
        {isLoading && <div className="sage-ai-plan-state-loader" />}
        <div className="sage-ai-plan-state-content">
          <div className="sage-ai-plan-current-step">
            <span className="sage-ai-plan-current-text">
              {stripMarkdown(currentStep || 'No current step')}
            </span>
          </div>

          {(nextStep || hasSource) && (
            <div className="sage-ai-plan-bottom-row">
              {nextStep && (
                <div className="sage-ai-plan-next-text">
                  Next: {stripMarkdown(nextStep)}
                </div>
              )}
            </div>
          )}
        </div>
        {hasContent && (
          <button
            className="sage-ai-plan-source-toggle"
            onClick={() => setIsSourceExpanded(!isSourceExpanded)}
            aria-expanded={isSourceExpanded}
            type="button"
            title="Toggle plan details"
          >
            <svg
              width="17"
              height="18"
              viewBox="0 0 17 18"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M3.54134 6.65503L13.458 6.65503L8.49967 11.3448L3.54134 6.65503Z"
                fill="#949494"
              />
            </svg>
          </button>
        )}
      </div>

      {hasContent && (
        <div
          className={`sage-ai-plan-source-content ${isSourceExpanded ? 'expanded' : 'collapsed'}`}
        >
          <div className="sage-ai-plan-tasks-list">
            {planContent.title && (
              <div className="sage-ai-plan-title">{planContent.title}</div>
            )}
            {planContent.tasks.map((task, index) => {
              if (!task.subtopics.length) {
                return (
                  <RenderTaskItem
                    key={index}
                    isTaskExecuting={isTaskExecuting}
                    taskRefs={taskRefs}
                    index={index}
                    task={task}
                  />
                );
              }

              return (
                <div key={index}>
                  <RenderTaskItem
                    isTaskExecuting={isTaskExecuting}
                    taskRefs={taskRefs}
                    index={index}
                    task={task}
                  />
                  {task.subtopics.length > 0 && (
                    <ul className="sage-ai-plan-subtopics">
                      {task.subtopics.map((subtopic, subtopicIndex) => (
                        <li
                          key={`subtopic-${index}-${subtopicIndex}`}
                          className="sage-ai-plan-subtopic"
                        >
                          <span className="sage-ai-subtopic-text">
                            {subtopic}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function RenderTaskItem({
  task,
  isTaskExecuting,
  taskRefs,
  index
}: {
  task: {
    text: string;
    completed: boolean;
    type: 'task' | 'subtask';
    subtopics: string[];
  };
  isTaskExecuting: (taskText: string) => boolean;
  taskRefs: React.MutableRefObject<(HTMLDivElement | null)[]>;
  index: number;
}): JSX.Element {
  const executing = isTaskExecuting(task.text);
  const isSubtask = task.type === 'subtask';

  return (
    <div
      className={`sage-ai-plan-task-item ${isSubtask ? 'sage-ai-plan-subtask-item' : ''}`}
      ref={el => {
        if (taskRefs.current && el) {
          taskRefs.current[index] = el;
        }
      }}
    >
      <div
        className={`sage-ai-task-icon ${executing ? 'sage-ai-task-executing' : ''}`}
      >
        {task.completed ? (
          <svg
            width="14"
            height="15"
            viewBox="0 0 14 15"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M11.6663 4L5.24967 10.4167L2.33301 7.5"
              stroke="#22C55E"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        ) : (
          <svg
            width="14"
            height="15"
            viewBox="0 0 14 15"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              cx="7"
              cy="7.5"
              r="6.25"
              stroke="url(#paint0_linear_549_10580)"
              strokeWidth="1.5"
              strokeLinejoin="round"
              strokeDasharray="3 3"
            />
            <defs>
              <linearGradient
                id="paint0_linear_549_10580"
                x1="0"
                y1="0.5"
                x2="14"
                y2="14.5"
                gradientUnits="userSpaceOnUse"
              >
                <stop stopColor="#FEC163" />
                <stop offset="1" stopColor="#DE4313" />
              </linearGradient>
            </defs>
          </svg>
        )}
      </div>
      <span className={executing ? 'sage-ai-task-executing' : ''}>
        {stripMarkdown(task.text)}
      </span>
    </div>
  );
}

// Helper to remove markdown formatting (bold, italic, inline code, etc.)
function stripMarkdown(text: string): string {
  // Remove bold (**text** or __text__)
  text = text.replace(/(\*\*|__)(.*?)\1/g, '$2');
  // Remove italic (*text* or _text_)
  text = text.replace(/(\*|_)(.*?)\1/g, '$2');
  // Remove inline code (`text`)
  text = text.replace(/`([^`]+)`/g, '$1');
  // Remove strikethrough (~~text~~)
  text = text.replace(/~~(.*?)~~/g, '$1');
  // Remove markdown links [text](url)
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
  // Remove images ![alt](url)
  text = text.replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1');
  // Remove any remaining markdown symbols
  text = text.replace(/[#>*_`~\-]/g, '');
  // Collapse multiple spaces
  text = text.replace(/\s{2,}/g, ' ');
  return text.trim();
}

/**
 * Component for displaying Plan processing state above the chatbox
 */
export class PlanStateDisplay extends ReactWidget {
  private _state: IPlanState;
  private _stateChanged = new Signal<this, IPlanState>(this);

  constructor() {
    super();
    this._state = {
      isVisible: false,
      currentStep: undefined,
      nextStep: undefined,
      source: undefined,
      isLoading: false
    };
    this.addClass('sage-ai-plan-state-widget');
  }

  /**
   * Get the signal that fires when state changes
   */
  public get stateChanged(): ISignal<this, IPlanState> {
    return this._stateChanged;
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    return (
      <PlanStateContent
        isVisible={this._state.isVisible}
        currentStep={this._state.currentStep}
        nextStep={this._state.nextStep}
        source={this._state.source}
        isLoading={this._state.isLoading}
      />
    );
  }

  /**
   * Update the plan state with current and next step information
   * @param currentStep The current step text
   * @param nextStep The next step text
   * @param source The source content in markdown format
   */
  public async updatePlan(
    currentStep?: string,
    nextStep?: string,
    source?: string,
    isLoading?: boolean
  ): Promise<void> {
    const shouldShow = !!(currentStep || nextStep);

    this._state = {
      isVisible: shouldShow,
      currentStep,
      nextStep,
      source,
      isLoading: isLoading ?? !!currentStep
    };

    // Handle hidden class like LLMStateDisplay does
    if (!shouldShow) {
      this.addClass('hidden');
    } else {
      this.removeClass('hidden');
    }

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Show the plan state display
   */
  public show(): void {
    this._state = {
      ...this._state,
      isVisible: true
    };
    this.removeClass('hidden');
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Hide the plan state display
   */
  public hide(): void {
    this._state = {
      ...this._state,
      isVisible: false
    };
    this.addClass('hidden');
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Set the loading state
   * @param loading Whether the plan is currently loading
   */
  public setLoading(loading: boolean): void {
    this._state = {
      ...this._state,
      isLoading: loading
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Update only the current step text
   * @param currentStep The current step text
   */
  public updateCurrentStep(currentStep: string): void {
    this._state = {
      ...this._state,
      currentStep,
      isVisible: true
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Update only the next step text
   * @param nextStep The next step text
   */
  public updateNextStep(nextStep: string): void {
    this._state = {
      ...this._state,
      nextStep
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Update only the source content
   * @param source The source content in markdown format
   */
  public updateSource(source: string): void {
    this._state = {
      ...this._state,
      source
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Check if the state display is currently visible
   */
  public getIsVisible(): boolean {
    return this._state.isVisible;
  }

  /**
   * Get the current state
   */
  public getState(): IPlanState {
    return { ...this._state };
  }

  /**
   * Get the widget for adding to layout (for backwards compatibility)
   */
  public getWidget(): Widget {
    return this;
  }
}
