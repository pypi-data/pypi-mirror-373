import * as React from 'react';
import { ReactWidget } from '@jupyterlab/ui-components';
import { ISignal, Signal } from '@lumino/signaling';
import { ListModel } from '@jupyterlab/extensionmanager';
import { CachingService, SETTING_KEYS } from '../../utils/caching';

/**
 * Interface for the UpdateBanner state
 */
interface IUpdateBannerState {
  isVisible: boolean;
  currentVersion?: string;
  latestVersion?: string;
  isUpdating: boolean;
  isDeclined: boolean;
  isMajorUpdate: boolean;
}

/**
 * React component for displaying update banner content
 */
interface UpdateBannerContentProps {
  isVisible: boolean;
  currentVersion?: string;
  latestVersion?: string;
  isUpdating: boolean;
  isMajorUpdate?: boolean;
  onUpdate: () => void;
  onAskLater: () => void;
  onDecline: () => void;
}

function UpdateBannerContent({
  isVisible,
  currentVersion,
  latestVersion,
  isUpdating,
  isMajorUpdate = false,
  onUpdate,
  onAskLater,
  onDecline
}: UpdateBannerContentProps): JSX.Element | null {
  if (!isVisible) {
    return null;
  }

  const showActions = !isUpdating && !isMajorUpdate;

  return (
    <div className="sage-ai-update-banner">
      <div className="sage-ai-update-banner-content">
        <div className="sage-ai-update-banner-icon">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
              fill="currentColor"
            />
          </svg>
        </div>
        <div className="sage-ai-update-banner-text">
          <div className="sage-ai-update-banner-title">
            {isMajorUpdate
              ? 'Sage is auto-updating to a major version'
              : 'Sage needs to update'}
          </div>
          {currentVersion && latestVersion && (
            <div className="sage-ai-update-banner-version">
              v{currentVersion} → v{latestVersion}
              {isMajorUpdate && ' (Major Version)'}
            </div>
          )}
          {isMajorUpdate && (
            <div className="sage-ai-update-banner-description">
              Major version updates are applied automatically for important
              improvements and security fixes.
            </div>
          )}
        </div>
        {showActions && (
          <div className="sage-ai-update-banner-actions">
            <button
              className="sage-ai-update-banner-button sage-ai-update-banner-button-update"
              onClick={onUpdate}
              disabled={isUpdating}
            >
              {isUpdating ? 'Updating...' : 'Update'}
            </button>
            <button
              className="sage-ai-update-banner-button sage-ai-update-banner-button-later"
              onClick={onAskLater}
              disabled={isUpdating}
            >
              Ask Me Later
            </button>
            <button
              className="sage-ai-update-banner-button sage-ai-update-banner-button-decline"
              onClick={onDecline}
              disabled={isUpdating}
            >
              Decline
            </button>
          </div>
        )}
        {(isUpdating || isMajorUpdate) && (
          <div className="sage-ai-update-banner-progress">
            <div className="sage-ai-update-banner-spinner"></div>
            <span>{isUpdating ? 'Updating...' : 'Preparing update...'}</span>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Component for displaying update banner above the chatbox
 */
export class UpdateBannerWidget extends ReactWidget {
  private _state: IUpdateBannerState;
  private _stateChanged = new Signal<this, IUpdateBannerState>(this);
  private _extensions: ListModel;
  private _packageName: string = 'sage-agent-internal';
  private _checkInterval: number | null = null;

  constructor(extensions: ListModel) {
    super();
    this._extensions = extensions;
    this._state = {
      isVisible: false,
      isUpdating: false,
      isDeclined: false, // Initialize with default, will be updated async
      isMajorUpdate: false
    };
    this.addClass('sage-ai-update-banner-widget');

    // Initially hide the widget
    this.node.style.display = 'none';

    this.initializeWidget();
  }

  /**
   * Initialize the widget asynchronously
   */
  private async initializeWidget(): Promise<void> {
    try {
      // No need to check declined status during initialization
      // Version-specific decline checking happens in checkForUpdates
      this.checkForUpdates();
    } catch (error) {
      console.error('Failed to initialize UpdateBannerWidget:', error);
      this.checkForUpdates();
    }
  }

  /**
   * Get the signal that fires when state changes
   */
  public get stateChanged(): ISignal<this, IUpdateBannerState> {
    return this._stateChanged;
  }

  /**
   * Check if a specific version has been declined
   */
  private async getDeclinedStatus(): Promise<boolean> {
    try {
      const declinedVersion = await CachingService.getStringSetting(
        SETTING_KEYS.UPDATE_DECLINED_VERSION,
        ''
      );
      // We'll check against the actual available version in checkForUpdates
      // For now, just return false during initialization
      return false;
    } catch {
      return false;
    }
  }

  /**
   * Check if a specific version has been declined
   */
  private async isVersionDeclined(version: string): Promise<boolean> {
    try {
      const declinedVersion = await CachingService.getStringSetting(
        SETTING_KEYS.UPDATE_DECLINED_VERSION,
        ''
      );
      return declinedVersion === version;
    } catch {
      return false;
    }
  }

  /**
   * Set declined status for a specific version
   */
  private async setDeclinedStatus(declined: boolean, version?: string): Promise<void> {
    try {
      if (declined && version) {
        await CachingService.setStringSetting(
          SETTING_KEYS.UPDATE_DECLINED_VERSION,
          version
        );
      } else {
        await CachingService.removeSetting(SETTING_KEYS.UPDATE_DECLINED_VERSION);
      }
    } catch {
      // Ignore settings registry errors
    }
  }

  /**
   * Parse a semantic version string and return major, minor, patch numbers
   */
  private parseVersion(
    version: string
  ): { major: number; minor: number; patch: number } | null {
    const match = version.match(/^(\d+)\.(\d+)\.(\d+)/);
    if (!match) {
      return null;
    }
    return {
      major: parseInt(match[1], 10),
      minor: parseInt(match[2], 10),
      patch: parseInt(match[3], 10)
    };
  }

  /**
   * Check if the version difference is a major version change
   */
  private isMajorVersionChange(
    currentVersion: string,
    latestVersion: string
  ): boolean {
    const current = this.parseVersion(currentVersion);
    const latest = this.parseVersion(latestVersion);

    if (!current || !latest) {
      return false;
    }

    return latest.major > current.major;
  }

  /**
   * Check for updates and show banner if needed
   */
  public async checkForUpdates(): Promise<void> {
    try {
      await this._extensions.refreshInstalled(true);
      const installed = this._extensions.installed.find(
        value => value.name === this._packageName
      );

      if (
        installed &&
        installed.installed_version !== installed.latest_version
      ) {
        const currentVersion = installed.installed_version;
        const latestVersion = installed.latest_version;

        // Check if this specific version has been declined
        const isVersionDeclined = await this.isVersionDeclined(latestVersion);
        if (isVersionDeclined) {
          console.log(`Version ${latestVersion} has been declined, not showing banner`);
          return;
        }

        // Check if this is a major version change
        if (this.isMajorVersionChange(currentVersion, latestVersion)) {
          console.log(
            `Major version change detected: ${currentVersion} → ${latestVersion}. Auto-updating...`
          );

          // Set state to show updating immediately
          this._state = {
            ...this._state,
            isVisible: true,
            isUpdating: true,
            isMajorUpdate: true,
            currentVersion,
            latestVersion,
            isDeclined: false
          };
          this._stateChanged.emit(this._state);
          this.updateDisplayState();
          this.update();

          // Automatically trigger the update
          await this.handleUpdate();
          return;
        }

        // For non-major version changes, show the banner normally
        this._state = {
          ...this._state,
          isVisible: true,
          isMajorUpdate: false,
          currentVersion,
          latestVersion,
          isDeclined: false
        };
        this._stateChanged.emit(this._state);
        this.updateDisplayState();
        this.update();
      }
    } catch (error) {
      console.error('Failed to check for updates:', error);
    }
  }

  /**
   * Update the widget's display state based on visibility
   */
  private updateDisplayState(): void {
    this.node.style.display = this._state.isVisible ? 'block' : 'none';
  }

  /**
   * Handle update button click
   */
  private handleUpdate = async (): Promise<void> => {
    this._state = { ...this._state, isUpdating: true };
    this._stateChanged.emit(this._state);
    this.update();

    try {
      const installed = this._extensions.installed.find(
        value => value.name === this._packageName
      );

      if (installed) {
        console.log(
          `Updating ${this._packageName} to version ${installed.latest_version}`
        );

        // Perform the actual update
        await this._extensions.install(installed, {
          useVersion: installed.latest_version
        });

        // Hide the banner after successful update
        this._state = {
          ...this._state,
          isVisible: false,
          isUpdating: false
        };
        this._stateChanged.emit(this._state);
        this.updateDisplayState();
        this.update();

        console.log(
          `Successfully updated ${this._packageName} to version ${installed.latest_version}`
        );
      }
    } catch (error) {
      console.error('Failed to update:', error);
      this._state = { ...this._state, isUpdating: false };
      this._stateChanged.emit(this._state);
      this.updateDisplayState();
      this.update();
    }
  };

  /**
   * Handle ask me later button click
   */
  private handleAskLater = (): void => {
    this._state = { ...this._state, isVisible: false };
    this._stateChanged.emit(this._state);
    this.updateDisplayState();
    this.update();
  };

  /**
   * Handle decline button click
   */
  private handleDecline = async (): Promise<void> => {
    // Store the specific version that was declined
    if (this._state.latestVersion) {
      await this.setDeclinedStatus(true, this._state.latestVersion);
    }
    this._state = {
      ...this._state,
      isVisible: false,
      isDeclined: true
    };
    this._stateChanged.emit(this._state);
    this.updateDisplayState();
    this.update();
  };

  /**
   * Show the banner (e.g., after app launch)
   */
  public showBanner(): void {
    // Always check for updates - version-specific decline checking is done in checkForUpdates
    this.checkForUpdates();
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    return (
      <UpdateBannerContent
        isVisible={this._state.isVisible}
        currentVersion={this._state.currentVersion}
        latestVersion={this._state.latestVersion}
        isUpdating={this._state.isUpdating}
        isMajorUpdate={this._state.isMajorUpdate}
        onUpdate={this.handleUpdate}
        onAskLater={this.handleAskLater}
        onDecline={this.handleDecline}
      />
    );
  }

  /**
   * Dispose of the widget
   */
  dispose(): void {
    if (this._checkInterval) {
      clearInterval(this._checkInterval);
      this._checkInterval = null;
    }
    super.dispose();
  }
}
