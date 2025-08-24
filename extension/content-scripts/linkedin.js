// Portia AI Job Tracker - LinkedIn Content Script
console.log('🔗 Portia AI LinkedIn content script loaded');

let isTrackingEnabled = true;
let hasTrackedCurrentJob = false;

// Initialize when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

function init() {
  console.log('🚀 Initializing LinkedIn job tracker');
  
  // Check if we're on a job page
  if (isJobPage()) {
    setupJobPageTracking();
  }
  
  // Listen for URL changes (LinkedIn is a SPA)
  setupNavigationListener();
}

function isJobPage() {
  const url = window.location.href;
  return url.includes('/jobs/view/') || url.includes('/jobs/collections/');
}

function setupJobPageTracking() {
  console.log('📋 Setting up job page tracking');
  
  // Reset tracking flag for new job
  hasTrackedCurrentJob = false;
  
  // Add auto-track button
  addTrackButton();
  
  // Auto-track if enabled (with delay for page to load)
    setTimeout(() => {
    checkAutoTrack();
  }, 2000);
}

function addTrackButton() {
  // Remove existing button
  const existingButton = document.querySelector('#portia-track-button');
  if (existingButton) {
    existingButton.remove();
  }
  
  // Find a good place to add the button
  const targetSelectors = [
    '.jobs-unified-top-card__content--two-pane',
    '.jobs-details__main-content',
    '.job-details-jobs-unified-top-card__content',
    '.jobs-search__job-details--container'
  ];
  
  let targetElement = null;
  for (const selector of targetSelectors) {
    targetElement = document.querySelector(selector);
    if (targetElement) break;
  }
  
  if (!targetElement) {
    console.log('❌ Could not find suitable location for track button');
    return;
  }
  
  // Create track button with elegant black & white theme
  const trackButton = document.createElement('button');
  trackButton.id = 'portia-track-button';
  trackButton.innerHTML = '🤖 Save to Portia AI';
  trackButton.style.cssText = `
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    color: white;
    border: 1px solid rgba(255,255,255,0.2);
    padding: 10px 18px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    margin: 12px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1000;
    position: relative;
    backdrop-filter: blur(10px);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    letter-spacing: 0.2px;
  `;
  
  trackButton.addEventListener('mouseenter', () => {
    trackButton.style.transform = 'translateY(-2px)';
    trackButton.style.boxShadow = '0 8px 24px rgba(0,0,0,0.4)';
    trackButton.style.background = 'linear-gradient(135deg, #2a2a2a 0%, #3d3d3d 100%)';
    trackButton.style.borderColor = 'rgba(255,255,255,0.3)';
  });
  
  trackButton.addEventListener('mouseleave', () => {
    trackButton.style.transform = 'translateY(0)';
    trackButton.style.boxShadow = '0 4px 16px rgba(0,0,0,0.3)';
    trackButton.style.background = 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)';
    trackButton.style.borderColor = 'rgba(255,255,255,0.2)';
  });
  
  trackButton.addEventListener('click', handleTrackButtonClick);
  
  // Insert button
  targetElement.insertBefore(trackButton, targetElement.firstChild);
  console.log('✅ Track button added');
}

async function handleTrackButtonClick() {
  const button = document.querySelector('#portia-track-button');
  if (!button) return;
  
  // Update button state
  button.innerHTML = '⏳ Saving...';
  button.disabled = true;
  
  try {
    const jobData = extractJobData();
    
    if (!jobData.jobTitle || !jobData.company) {
      throw new Error('Could not extract job title or company');
    }
    
    // Send to background script
    chrome.runtime.sendMessage({
      type: 'TRACK_JOB',
      jobData: jobData
    });
    
    // Update button to success state
    button.innerHTML = '✅ Saved!';
    button.style.background = 'linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)';
    button.style.color = '#1a1a1a';
    button.style.borderColor = 'rgba(255,255,255,0.4)';
    
    hasTrackedCurrentJob = true;
    
    // Reset button after 3 seconds
    setTimeout(() => {
      button.innerHTML = '🤖 Save to Portia AI';
      button.style.background = 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)';
      button.style.color = 'white';
      button.style.borderColor = 'rgba(255,255,255,0.2)';
      button.disabled = false;
    }, 3000);
    
  } catch (error) {
    console.error('❌ Error tracking job:', error);
    
    // Update button to error state
    button.innerHTML = '❌ Error';
    button.style.background = 'linear-gradient(135deg, #666666 0%, #888888 100%)';
    button.style.color = '#ffffff';
    button.style.borderColor = 'rgba(255,255,255,0.3)';
    
    // Reset button after 3 seconds
    setTimeout(() => {
      button.innerHTML = '🤖 Save to Portia AI';
      button.style.background = 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)';
      button.style.color = 'white';
      button.style.borderColor = 'rgba(255,255,255,0.2)';
      button.disabled = false;
    }, 3000);
  }
}

function extractJobData() {
  console.log('📊 Extracting job data from LinkedIn');
  
  const url = window.location.href;
  const jobData = {
    jobUrl: url,
    platform: 'linkedin',
    extractedAt: new Date().toISOString()
  };
  
  // Extract job title
  const titleSelectors = [
    '.jobs-unified-top-card__job-title h1',
    '.job-details-jobs-unified-top-card__job-title h1',
    '.jobs-details__main-content h1',
    '.job-title'
  ];
  
  for (const selector of titleSelectors) {
        const element = document.querySelector(selector);
    if (element && element.textContent.trim()) {
      jobData.jobTitle = element.textContent.trim();
      break;
    }
  }
  
  // Extract company name
  const companySelectors = [
    '.jobs-unified-top-card__company-name a',
    '.job-details-jobs-unified-top-card__company-name a',
    '.jobs-unified-top-card__subtitle-primary-grouping a',
    '.jobs-details-top-card__company-url'
  ];
  
  for (const selector of companySelectors) {
    const element = document.querySelector(selector);
    if (element && element.textContent.trim()) {
      jobData.company = element.textContent.trim();
      break;
    }
  }
  
  // Extract location
  const locationSelectors = [
    '.jobs-unified-top-card__bullet',
    '.jobs-unified-top-card__subtitle-secondary-grouping',
    '.job-details-jobs-unified-top-card__primary-description-container'
  ];
  
  for (const selector of locationSelectors) {
    const element = document.querySelector(selector);
    if (element && element.textContent.trim()) {
      const locationText = element.textContent.trim();
      // Clean up location text (remove extra info)
      jobData.location = locationText.split('·')[0].trim();
      break;
    }
  }
  
  // Extract job description
  const descSelectors = [
    '.jobs-box__html-content',
    '.jobs-description-content__text',
    '.jobs-description__content'
  ];
  
  for (const selector of descSelectors) {
    const element = document.querySelector(selector);
    if (element && element.textContent.trim()) {
      jobData.description = element.textContent.trim().substring(0, 1500);
      break;
    }
  }
  
  // Try to extract salary/compensation
  const salarySelectors = [
    '.jobs-unified-top-card__job-insight',
    '.job-details-preferences-and-skills__pill'
  ];
  
  for (const selector of salarySelectors) {
    const elements = document.querySelectorAll(selector);
    for (const element of elements) {
      const text = element.textContent.trim();
      if (text.includes('$') || text.includes('salary') || text.includes('compensation')) {
        jobData.salaryRange = text;
        break;
      }
    }
    if (jobData.salaryRange) break;
  }
  
  // Extract job ID from URL
  const jobIdMatch = url.match(/\/jobs\/view\/(\d+)/);
  if (jobIdMatch) {
    jobData.jobId = jobIdMatch[1];
  }
  
  console.log('📋 Extracted job data:', jobData);
  return jobData;
}

async function checkAutoTrack() {
  if (hasTrackedCurrentJob) {
    console.log('🔄 Job already tracked, skipping auto-track');
        return;
    }
    
    try {
    // Get user settings
    const response = await chrome.runtime.sendMessage({ type: 'GET_USER_SETTINGS' });
    const settings = response || {};
    
    if (settings.autoTrack) {
      console.log('🤖 Auto-tracking enabled, tracking job...');
      
      const jobData = extractJobData();
      
      if (jobData.jobTitle && jobData.company) {
        chrome.runtime.sendMessage({
            type: 'TRACK_JOB',
          jobData: jobData
        });
        
        hasTrackedCurrentJob = true;
        
        // Update button if it exists
        const button = document.querySelector('#portia-track-button');
        if (button) {
          button.innerHTML = '✅ Auto-saved!';
          button.style.background = 'linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)';
          button.style.color = '#1a1a1a';
          button.style.borderColor = 'rgba(255,255,255,0.4)';
        }
      }
    }
  } catch (error) {
    console.error('❌ Auto-track error:', error);
  }
}

function setupNavigationListener() {
  // Listen for URL changes in LinkedIn SPA
  let lastUrl = location.href;
  
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      console.log('🔄 Navigation detected:', url);
      
      // Small delay to let page content load
    setTimeout(() => {
        if (isJobPage()) {
          setupJobPageTracking();
        }
      }, 1000);
    }
  }).observe(document, { subtree: true, childList: true });
}

// Handle messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📨 LinkedIn content script received message:', message);
  
  if (message.type === 'EXTRACT_JOB_DATA') {
    const jobData = extractJobData();
    sendResponse(jobData);
  }
});

console.log('✅ LinkedIn content script initialized');