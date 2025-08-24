// Portia AI Job Tracker - Background Script
console.log('Portia AI Job Tracker background script loaded');

// Extension settings
const API_BASE_URL = 'http://localhost:8000/api';
let userSettings = {};

// Load user settings on startup
chrome.runtime.onStartup.addListener(async () => {
  await loadUserSettings();
});

chrome.runtime.onInstalled.addListener(async () => {
  await loadUserSettings();
  
  // Set up context menu
  chrome.contextMenus.create({
    id: "trackJobApplication",
    title: "Track this job with Portia AI",
    contexts: ["page"],
    documentUrlPatterns: [
      "https://www.linkedin.com/jobs/*",
      "https://indeed.com/viewjob*",
      "https://angel.co/company/*/jobs/*",
      "https://wellfound.com/company/*/jobs/*"
    ]
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "trackJobApplication") {
    await trackJobFromPage(tab);
  }
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message);
  
  switch (message.type) {
    case 'TRACK_JOB':
      handleTrackJob(message.jobData, sender.tab);
      break;
    
    case 'GET_USER_SETTINGS':
      sendResponse(userSettings);
      break;
    
    case 'UPDATE_USER_SETTINGS':
      updateUserSettings(message.settings);
      sendResponse({ success: true });
      break;
    
    case 'SYNC_TO_BACKEND':
      syncJobToBackend(message.jobData);
      break;
    
    case 'GET_TRACKED_JOBS':
      getTrackedJobs().then(jobs => sendResponse(jobs));
      return true; // Keep message channel open for async response
    
    default:
      console.log('Unknown message type:', message.type);
  }
});

// Load user settings from storage
async function loadUserSettings() {
  try {
    const result = await chrome.storage.sync.get(['userSettings']);
    userSettings = result.userSettings || {
      apiToken: '',
      autoTrack: true,
      syncToBackend: true,
      trackingEnabled: true
    };
    console.log('Loaded user settings:', userSettings);
  } catch (error) {
    console.error('Error loading user settings:', error);
  }
}

// Update user settings
async function updateUserSettings(newSettings) {
  userSettings = { ...userSettings, ...newSettings };
  try {
    await chrome.storage.sync.set({ userSettings });
    console.log('Updated user settings:', userSettings);
  } catch (error) {
    console.error('Error saving user settings:', error);
  }
}

// Handle job tracking
async function handleTrackJob(jobData, tab) {
  console.log('Tracking job:', jobData);
  
  try {
    // Validate job data
    if (!jobData.jobTitle || !jobData.company) {
      throw new Error('Missing required job data (title or company)');
    }
    
    // Store job locally first
    await storeJobLocally(jobData);
    
    let syncStatus = 'saved_locally';
    let syncMessage = 'Job saved locally';
    
    // Sync to backend if enabled and user is authenticated
    if (userSettings.syncToBackend && userSettings.apiToken) {
      try {
        const backendResult = await syncJobToBackend(jobData);
        if (backendResult.success) {
          syncStatus = 'synced_to_backend';
          syncMessage = 'Job saved to database successfully!';
        }
      } catch (syncError) {
        console.warn('Backend sync failed, but job saved locally:', syncError);
        syncMessage = 'Job saved locally (sync failed)';
      }
    }
    
    // Show success notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: '✅ Job Saved Successfully!',
      message: `${jobData.jobTitle} at ${jobData.company}\n${syncMessage}`,
      priority: 2
    });
    
    // Update badge
    await updateBadgeCount();
    
    return { success: true, status: syncStatus };
    
  } catch (error) {
    console.error('Error tracking job:', error);
    
    // Show error notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: '❌ Error Saving Job',
      message: `Failed to save job: ${error.message}`,
      priority: 2
    });
    
    throw error;
  }
}

// Store job data locally
async function storeJobLocally(jobData) {
  const jobId = generateJobId(jobData);
  const jobRecord = {
    id: jobId,
    ...jobData,
    trackedAt: new Date().toISOString(),
    status: 'tracked',
    source: 'extension'
  };
  
  try {
    // Get existing jobs
    const result = await chrome.storage.local.get(['trackedJobs']);
    const trackedJobs = result.trackedJobs || {};
    
    // Add new job
    trackedJobs[jobId] = jobRecord;
    
    // Save back to storage
    await chrome.storage.local.set({ trackedJobs });
    console.log('Stored job locally:', jobRecord);
    
  } catch (error) {
    console.error('Error storing job locally:', error);
    throw error;
  }
}

// Sync job to backend
async function syncJobToBackend(jobData) {
  if (!userSettings.apiToken) {
    console.log('No API token, skipping backend sync');
    return { success: false, error: 'No API token configured' };
  }
  
  try {
    console.log('Syncing job to backend:', jobData);
    
    const response = await fetch(`${API_BASE_URL}/applications`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userSettings.apiToken}`,
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        job_title: jobData.jobTitle || 'Unknown Title',
        company: jobData.company || 'Unknown Company',
        job_url: jobData.jobUrl || '',
        salary_range: jobData.salaryRange || '',
        location: jobData.location || '',
        job_description: jobData.description || '',
        source: `${jobData.platform || 'extension'}_auto`,
        notes: `Auto-tracked via Portia AI Chrome Extension from ${jobData.platform || 'unknown'} at ${new Date().toLocaleString()}`
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('✅ Successfully synced job to backend:', result);
      
      // Update local record with backend ID
      const jobId = generateJobId(jobData);
      const result_local = await chrome.storage.local.get(['trackedJobs']);
      const trackedJobs = result_local.trackedJobs || {};
      
      if (trackedJobs[jobId]) {
        trackedJobs[jobId].backendId = result.id;
        trackedJobs[jobId].syncedAt = new Date().toISOString();
        trackedJobs[jobId].syncStatus = 'synced';
        await chrome.storage.local.set({ trackedJobs });
      }
      
      return { success: true, backendId: result.id };
      
    } else {
      const errorText = await response.text();
      console.error('❌ Backend sync failed:', response.status, response.statusText, errorText);
      
      // Handle specific error cases
      if (response.status === 401) {
        throw new Error('Authentication failed - please check your API token');
      } else if (response.status === 400) {
        throw new Error('Invalid job data - please try again');
      } else {
        throw new Error(`Server error (${response.status}): ${response.statusText}`);
      }
    }
    
  } catch (error) {
    console.error('❌ Error syncing to backend:', error);
    
    // Mark local job as sync failed
    try {
      const jobId = generateJobId(jobData);
      const result_local = await chrome.storage.local.get(['trackedJobs']);
      const trackedJobs = result_local.trackedJobs || {};
      
      if (trackedJobs[jobId]) {
        trackedJobs[jobId].syncStatus = 'failed';
        trackedJobs[jobId].syncError = error.message;
        await chrome.storage.local.set({ trackedJobs });
      }
    } catch (localError) {
      console.error('Error updating local sync status:', localError);
    }
    
    return { success: false, error: error.message };
  }
}

// Get all tracked jobs
async function getTrackedJobs() {
  try {
    const result = await chrome.storage.local.get(['trackedJobs']);
    const trackedJobs = result.trackedJobs || {};
    return Object.values(trackedJobs);
  } catch (error) {
    console.error('Error getting tracked jobs:', error);
    return [];
  }
}

// Track job from current page
async function trackJobFromPage(tab) {
  try {
    // Inject content script to extract job data
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: extractJobDataFromPage
    });
    
    if (results && results[0] && results[0].result) {
      const jobData = results[0].result;
      await handleTrackJob(jobData, tab);
    }
    
  } catch (error) {
    console.error('Error tracking job from page:', error);
  }
}

// Function to be injected into page to extract job data
function extractJobDataFromPage() {
  const url = window.location.href;
  let jobData = {
    jobUrl: url,
    platform: 'unknown'
  };
  
  // LinkedIn job extraction
  if (url.includes('linkedin.com/jobs')) {
    jobData.platform = 'linkedin';
    jobData.jobTitle = document.querySelector('.top-card-layout__title')?.textContent?.trim() || '';
    jobData.company = document.querySelector('.topcard__flavor-row .topcard__flavor--black-link')?.textContent?.trim() || '';
    jobData.location = document.querySelector('.topcard__flavor-row .topcard__flavor')?.textContent?.trim() || '';
    jobData.description = document.querySelector('.description__text')?.textContent?.trim()?.substring(0, 1000) || '';
    
    // Try to extract salary
    const salaryElement = document.querySelector('.salary, .compensation__salary');
    jobData.salaryRange = salaryElement?.textContent?.trim() || '';
  }
  
  // Indeed job extraction
  else if (url.includes('indeed.com/viewjob')) {
    jobData.platform = 'indeed';
    jobData.jobTitle = document.querySelector('[data-testid="jobsearch-JobInfoHeader-title"] span')?.textContent?.trim() || '';
    jobData.company = document.querySelector('[data-testid="inlineHeader-companyName"] span')?.textContent?.trim() || '';
    jobData.location = document.querySelector('[data-testid="job-location"]')?.textContent?.trim() || '';
    jobData.description = document.querySelector('#jobDescriptionText')?.textContent?.trim()?.substring(0, 1000) || '';
    
    // Try to extract salary
    const salaryElement = document.querySelector('.icl-u-xs-mr--xs .attribute_snippet');
    jobData.salaryRange = salaryElement?.textContent?.trim() || '';
  }
  
  // AngelList/Wellfound job extraction
  else if (url.includes('angel.co') || url.includes('wellfound.com')) {
    jobData.platform = 'angellist';
    jobData.jobTitle = document.querySelector('h1')?.textContent?.trim() || '';
    jobData.company = document.querySelector('.company-name, .startup-name')?.textContent?.trim() || '';
    jobData.location = document.querySelector('.location')?.textContent?.trim() || '';
    jobData.description = document.querySelector('.job-description, .description')?.textContent?.trim()?.substring(0, 1000) || '';
    
    // Try to extract salary/equity
    const compensationElement = document.querySelector('.compensation, .salary-range');
    jobData.salaryRange = compensationElement?.textContent?.trim() || '';
  }
  
  return jobData;
}

// Generate unique job ID
function generateJobId(jobData) {
  const urlParts = jobData.jobUrl.split('/');
  const jobIdFromUrl = urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2];
  return `${jobData.platform}_${jobIdFromUrl}_${Date.now()}`;
}

// Update extension badge with job count
async function updateBadgeCount() {
  try {
    const jobs = await getTrackedJobs();
    const count = jobs.length;
    
    chrome.action.setBadgeText({
      text: count > 99 ? '99+' : count.toString()
    });
    
    chrome.action.setBadgeBackgroundColor({
      color: '#4285F4'
    });
    
  } catch (error) {
    console.error('Error updating badge count:', error);
  }
}

// Initialize badge count on startup
updateBadgeCount();

// Periodic sync with backend (every 5 minutes)
setInterval(async () => {
  if (userSettings.syncToBackend && userSettings.apiToken) {
    console.log('Performing periodic sync check...');
    // Could implement incremental sync here
  }
}, 5 * 60 * 1000);

// Handle extension icon click
chrome.action.onClicked.addListener(async (tab) => {
  // Open popup or track current job
  if (tab.url.includes('linkedin.com/jobs') || 
      tab.url.includes('indeed.com/viewjob') || 
      tab.url.includes('angel.co') || 
      tab.url.includes('wellfound.com')) {
    await trackJobFromPage(tab);
  }
});

// Auto-track when user navigates to job pages
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  // Only process when page is completely loaded
  if (changeInfo.status !== 'complete' || !tab.url) return;
  
  // Check if it's a job page
  const isJobPage = tab.url.includes('linkedin.com/jobs/view/') ||
                   tab.url.includes('indeed.com/viewjob') ||
                   tab.url.includes('angel.co/company/') ||
                   tab.url.includes('wellfound.com/company/');
  
  if (isJobPage && userSettings.autoTrack) {
    console.log('🤖 Auto-track triggered for:', tab.url);
    
    // Small delay to ensure page is fully loaded
    setTimeout(async () => {
      try {
        await trackJobFromPage(tab);
      } catch (error) {
        console.error('Auto-track failed:', error);
      }
    }, 3000);
  }
});
