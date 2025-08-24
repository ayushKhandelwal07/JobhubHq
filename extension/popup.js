// Portia AI Job Tracker - Popup Script
console.log('Portia AI Job Tracker popup loaded');

// DOM elements
const dashboardView = document.getElementById('dashboard-view');
const settingsView = document.getElementById('settings-view');
const jobsView = document.getElementById('jobs-view');
const messageContainer = document.getElementById('message-container');

// Dashboard elements
const connectionStatus = document.getElementById('connection-status');
const connectionText = document.getElementById('connection-text');
const jobsCount = document.getElementById('jobs-count');
const trackCurrentJobBtn = document.getElementById('track-current-job');
const viewAllJobsBtn = document.getElementById('view-all-jobs');
const openSettingsBtn = document.getElementById('open-settings');

// Settings elements
const apiTokenInput = document.getElementById('api-token');
const autoTrackToggle = document.getElementById('auto-track-toggle');
const syncBackendToggle = document.getElementById('sync-backend-toggle');
const notificationsToggle = document.getElementById('notifications-toggle');
const saveSettingsBtn = document.getElementById('save-settings');
const backToDashboardBtn = document.getElementById('back-to-dashboard');

// Jobs view elements
const recentJobsList = document.getElementById('recent-jobs-list');
const syncAllJobsBtn = document.getElementById('sync-all-jobs');
const exportJobsBtn = document.getElementById('export-jobs');
const backFromJobsBtn = document.getElementById('back-from-jobs');

// Current user settings
let userSettings = {};

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
    await loadUserSettings();
    await updateDashboard();
    setupEventListeners();
});

// Load user settings
async function loadUserSettings() {
    try {
        const response = await chrome.runtime.sendMessage({ type: 'GET_USER_SETTINGS' });
        userSettings = response || {
            apiToken: '',
            autoTrack: true,
            syncToBackend: true,
            trackingEnabled: true,
            showNotifications: true
        };
        console.log('Loaded settings:', userSettings);
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Update dashboard with current data
async function updateDashboard() {
    try {
        // Update connection status
        if (userSettings.apiToken && userSettings.syncToBackend) {
            connectionStatus.className = 'status-icon status-connected';
            connectionText.textContent = 'Connected to Portia AI';
        } else {
            connectionStatus.className = 'status-icon status-disconnected';
            connectionText.textContent = 'Not connected';
        }
        
        // Get tracked jobs count
        const jobs = await chrome.runtime.sendMessage({ type: 'GET_TRACKED_JOBS' });
        jobsCount.textContent = jobs ? jobs.length : 0;
        
        // Check if current tab is a job page
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const isJobPage = isJobSite(tab.url);
        
        trackCurrentJobBtn.disabled = !isJobPage;
        trackCurrentJobBtn.textContent = isJobPage ? '📋 Track Current Job' : '❌ Not a job page';
        
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Dashboard buttons
    trackCurrentJobBtn.addEventListener('click', trackCurrentJob);
    viewAllJobsBtn.addEventListener('click', showJobsView);
    openSettingsBtn.addEventListener('click', showSettingsView);
    
    // Settings buttons and toggles
    saveSettingsBtn.addEventListener('click', saveSettings);
    backToDashboardBtn.addEventListener('click', showDashboardView);
    
    // Toggle switches
    autoTrackToggle.addEventListener('click', () => toggleSetting('autoTrack', autoTrackToggle));
    syncBackendToggle.addEventListener('click', () => toggleSetting('syncToBackend', syncBackendToggle));
    notificationsToggle.addEventListener('click', () => toggleSetting('showNotifications', notificationsToggle));
    
    // Jobs view buttons
    syncAllJobsBtn.addEventListener('click', syncAllJobs);
    exportJobsBtn.addEventListener('click', exportJobs);
    backFromJobsBtn.addEventListener('click', showDashboardView);
    
    // Update settings UI
    updateSettingsUI();
}

// Track current job
async function trackCurrentJob() {
    try {
        showMessage('Tracking current job...', 'info');
        
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        // Execute content script to extract job data
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: extractJobData
        });
        
        if (results && results[0] && results[0].result) {
            const jobData = results[0].result;
            
            // Send to background script for processing
            chrome.runtime.sendMessage({
                type: 'TRACK_JOB',
                jobData: jobData
            });
            
            showMessage(`Successfully tracked: ${jobData.jobTitle} at ${jobData.company}`, 'success');
            await updateDashboard();
        } else {
            showMessage('Could not extract job data from this page', 'error');
        }
        
    } catch (error) {
        console.error('Error tracking job:', error);
        showMessage('Error tracking job: ' + error.message, 'error');
    }
}

// Show jobs view
async function showJobsView() {
    try {
        dashboardView.classList.add('hidden');
        jobsView.classList.remove('hidden');
        
        // Load recent jobs
        await loadRecentJobs();
        
    } catch (error) {
        console.error('Error showing jobs view:', error);
        showMessage('Error loading jobs', 'error');
    }
}

// Load recent jobs
async function loadRecentJobs() {
    try {
        const jobs = await chrome.runtime.sendMessage({ type: 'GET_TRACKED_JOBS' });
        
        if (!jobs || jobs.length === 0) {
            recentJobsList.innerHTML = '<div class="loading">No jobs tracked yet</div>';
            return;
        }
        
        // Sort jobs by tracked date (most recent first)
        const sortedJobs = jobs.sort((a, b) => new Date(b.trackedAt) - new Date(a.trackedAt));
        
        // Display jobs
        recentJobsList.innerHTML = sortedJobs.slice(0, 10).map(job => `
            <div class="job-item">
                <div class="job-title">${job.jobTitle || 'Unknown Title'}</div>
                <div class="job-company">${job.company || 'Unknown Company'} • ${job.platform || 'Unknown'}</div>
                <div class="job-company">${formatDate(job.trackedAt)} ${job.backendId ? '✅' : '⏳'}</div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading recent jobs:', error);
        recentJobsList.innerHTML = '<div class="error">Error loading jobs</div>';
    }
}

// Show settings view
function showSettingsView() {
    dashboardView.classList.add('hidden');
    settingsView.classList.remove('hidden');
    updateSettingsUI();
}

// Show dashboard view
function showDashboardView() {
    settingsView.classList.add('hidden');
    jobsView.classList.add('hidden');
    dashboardView.classList.remove('hidden');
    updateDashboard();
}

// Update settings UI
function updateSettingsUI() {
    apiTokenInput.value = userSettings.apiToken || '';
    
    updateToggle(autoTrackToggle, userSettings.autoTrack);
    updateToggle(syncBackendToggle, userSettings.syncToBackend);
    updateToggle(notificationsToggle, userSettings.showNotifications);
}

// Update toggle switch
function updateToggle(toggle, isActive) {
    if (isActive) {
        toggle.classList.add('active');
    } else {
        toggle.classList.remove('active');
    }
}

// Toggle setting
function toggleSetting(settingName, toggleElement) {
    userSettings[settingName] = !userSettings[settingName];
    updateToggle(toggleElement, userSettings[settingName]);
}

// Save settings
async function saveSettings() {
    try {
        userSettings.apiToken = apiTokenInput.value.trim();
        
        await chrome.runtime.sendMessage({
            type: 'UPDATE_USER_SETTINGS',
            settings: userSettings
        });
        
        showMessage('Settings saved successfully!', 'success');
        
        // Update dashboard after saving
        setTimeout(() => {
            showDashboardView();
        }, 1500);
        
    } catch (error) {
        console.error('Error saving settings:', error);
        showMessage('Error saving settings: ' + error.message, 'error');
    }
}

// Sync all jobs to backend
async function syncAllJobs() {
    try {
        if (!userSettings.apiToken) {
            showMessage('Please configure your API token first', 'error');
            return;
        }
        
        showMessage('Syncing jobs to backend...', 'info');
        
        const jobs = await chrome.runtime.sendMessage({ type: 'GET_TRACKED_JOBS' });
        const unsyncedJobs = jobs.filter(job => !job.backendId);
        
        if (unsyncedJobs.length === 0) {
            showMessage('All jobs are already synced!', 'success');
            return;
        }
        
        // Sync each unsynced job
        let syncedCount = 0;
        for (const job of unsyncedJobs) {
            try {
                chrome.runtime.sendMessage({
                    type: 'SYNC_TO_BACKEND',
                    jobData: job
                });
                syncedCount++;
            } catch (error) {
                console.error('Error syncing job:', error);
            }
        }
        
        showMessage(`Initiated sync for ${syncedCount} jobs`, 'success');
        
        // Refresh the jobs list after a delay
        setTimeout(() => {
            loadRecentJobs();
        }, 2000);
        
    } catch (error) {
        console.error('Error syncing jobs:', error);
        showMessage('Error syncing jobs: ' + error.message, 'error');
    }
}

// Export jobs
async function exportJobs() {
    try {
        const jobs = await chrome.runtime.sendMessage({ type: 'GET_TRACKED_JOBS' });
        
        if (!jobs || jobs.length === 0) {
            showMessage('No jobs to export', 'error');
            return;
        }
        
        // Create CSV content
        const csvHeader = 'Job Title,Company,Platform,Location,Salary Range,Tracked Date,Job URL,Status\n';
        const csvRows = jobs.map(job => {
            return [
                job.jobTitle || '',
                job.company || '',
                job.platform || '',
                job.location || '',
                job.salaryRange || '',
                job.trackedAt || '',
                job.jobUrl || '',
                job.status || ''
            ].map(field => `"${field.replace(/"/g, '""')}"`).join(',');
        }).join('\n');
        
        const csvContent = csvHeader + csvRows;
        
        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        
        // Download file
        const a = document.createElement('a');
        a.href = url;
        a.download = `portia-ai-jobs-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        showMessage(`Exported ${jobs.length} jobs to CSV`, 'success');
        
    } catch (error) {
        console.error('Error exporting jobs:', error);
        showMessage('Error exporting jobs: ' + error.message, 'error');
    }
}

// Utility functions
function isJobSite(url) {
    if (!url) return false;
    
    return url.includes('linkedin.com/jobs') ||
           url.includes('indeed.com/viewjob') ||
           url.includes('angel.co/company') ||
           url.includes('wellfound.com/company');
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    
    return date.toLocaleDateString();
}

function showMessage(text, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = type;
    messageDiv.textContent = text;
    
    messageContainer.innerHTML = '';
    messageContainer.appendChild(messageDiv);
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (messageContainer.contains(messageDiv)) {
            messageContainer.removeChild(messageDiv);
        }
    }, 3000);
}

// Function to be injected for job data extraction
function extractJobData() {
    const url = window.location.href;
    let jobData = {
        jobUrl: url,
        platform: 'unknown'
    };
    
    try {
        // LinkedIn job extraction
        if (url.includes('linkedin.com/jobs')) {
            jobData.platform = 'linkedin';
            
            // Try multiple selectors for job title
            const titleSelectors = [
                '.top-card-layout__title',
                '.jobs-unified-top-card__job-title h1',
                '.job-details-jobs-unified-top-card__job-title h1'
            ];
            
            for (const selector of titleSelectors) {
                const element = document.querySelector(selector);
                if (element) {
                    jobData.jobTitle = element.textContent.trim();
                    break;
                }
            }
            
            // Try multiple selectors for company
            const companySelectors = [
                '.topcard__flavor-row .topcard__flavor--black-link',
                '.jobs-unified-top-card__company-name a',
                '.job-details-jobs-unified-top-card__company-name a'
            ];
            
            for (const selector of companySelectors) {
                const element = document.querySelector(selector);
                if (element) {
                    jobData.company = element.textContent.trim();
                    break;
                }
            }
            
            // Location
            const locationElement = document.querySelector('.topcard__flavor-row .topcard__flavor, .jobs-unified-top-card__bullet');
            if (locationElement) {
                jobData.location = locationElement.textContent.trim();
            }
            
            // Description
            const descElement = document.querySelector('.description__text, .jobs-box__html-content');
            if (descElement) {
                jobData.description = descElement.textContent.trim().substring(0, 1000);
            }
        }
        
        // Indeed job extraction
        else if (url.includes('indeed.com/viewjob')) {
            jobData.platform = 'indeed';
            
            const titleElement = document.querySelector('[data-testid="jobsearch-JobInfoHeader-title"] span, .jobsearch-JobInfoHeader-title span');
            if (titleElement) {
                jobData.jobTitle = titleElement.textContent.trim();
            }
            
            const companyElement = document.querySelector('[data-testid="inlineHeader-companyName"] span, .icl-u-lg-mr--sm span');
            if (companyElement) {
                jobData.company = companyElement.textContent.trim();
            }
            
            const locationElement = document.querySelector('[data-testid="job-location"], .icl-u-xs-mt--xs div');
            if (locationElement) {
                jobData.location = locationElement.textContent.trim();
            }
            
            const descElement = document.querySelector('#jobDescriptionText, .jobsearch-jobDescriptionText');
            if (descElement) {
                jobData.description = descElement.textContent.trim().substring(0, 1000);
            }
        }
        
        // AngelList/Wellfound job extraction
        else if (url.includes('angel.co') || url.includes('wellfound.com')) {
            jobData.platform = 'angellist';
            
            const titleElement = document.querySelector('h1, .job-title');
            if (titleElement) {
                jobData.jobTitle = titleElement.textContent.trim();
            }
            
            const companyElement = document.querySelector('.company-name, .startup-name, .company h2');
            if (companyElement) {
                jobData.company = companyElement.textContent.trim();
            }
            
            const locationElement = document.querySelector('.location, .job-location');
            if (locationElement) {
                jobData.location = locationElement.textContent.trim();
            }
            
            const descElement = document.querySelector('.job-description, .description, .job-details');
            if (descElement) {
                jobData.description = descElement.textContent.trim().substring(0, 1000);
            }
        }
        
    } catch (error) {
        console.error('Error extracting job data:', error);
    }
    
    return jobData;
}
