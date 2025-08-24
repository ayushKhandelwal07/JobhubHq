// Indeed Content Script for Portia AI Job Tracker
console.log('Portia AI Indeed content script loaded');

// Configuration
const INDEED_CONFIG = {
    selectors: {
        jobTitle: [
            '[data-testid="jobsearch-JobInfoHeader-title"] span',
            '.jobsearch-JobInfoHeader-title span',
            'h1[data-testid="jobsearch-JobInfoHeader-title"]'
        ],
        company: [
            '[data-testid="inlineHeader-companyName"] span',
            '[data-testid="inlineHeader-companyName"] a',
            '.icl-u-lg-mr--sm span'
        ],
        location: [
            '[data-testid="job-location"]',
            '.icl-u-xs-mt--xs div',
            '[data-testid="jobsearch-JobInfoHeader-subtitle"] div'
        ],
        description: [
            '#jobDescriptionText',
            '.jobsearch-jobDescriptionText',
            '[data-testid="jobsearch-JobComponent-description"]'
        ],
        salary: [
            '.attribute_snippet',
            '.icl-u-xs-mr--xs .attribute_snippet',
            '[data-testid="job-compensation"]'
        ],
        applyButton: [
            '#indeedApplyButton',
            '[data-testid="indeedApplyButton"]',
            '.ia-IndeedApplyButton'
        ]
    }
};

// State management
let currentJobData = null;
let trackingButton = null;
let isTracked = false;

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

function initialize() {
    console.log('Initializing Indeed job tracker...');
    
    // Check if we're on a job details page
    if (isJobDetailsPage()) {
        setupJobTracking();
        
        // Monitor for navigation changes
        let lastUrl = location.href;
        new MutationObserver(() => {
            const currentUrl = location.href;
            if (currentUrl !== lastUrl) {
                lastUrl = currentUrl;
                handleUrlChange();
            }
        }).observe(document, { subtree: true, childList: true });
    }
}

function isJobDetailsPage() {
    return window.location.href.includes('/viewjob?jk=') || 
           document.querySelector('[data-testid="jobsearch-JobInfoHeader-title"]') !== null;
}

function handleUrlChange() {
    // Clean up previous tracking button
    if (trackingButton) {
        trackingButton.remove();
        trackingButton = null;
    }
    
    // Reset state
    currentJobData = null;
    isTracked = false;
    
    // Setup tracking for new job if we're still on a job page
    setTimeout(() => {
        if (isJobDetailsPage()) {
            setupJobTracking();
        }
    }, 1000);
}

async function setupJobTracking() {
    try {
        // Wait for content to load
        await waitForContent();
        
        // Extract job data
        currentJobData = extractJobData();
        
        if (currentJobData && currentJobData.jobTitle) {
            // Check if job is already tracked
            await checkIfJobTracked();
            
            // Add tracking button
            addTrackingButton();
            
            // Auto-track if enabled
            const settings = await getUserSettings();
            if (settings && settings.autoTrack && !isTracked) {
                setTimeout(() => trackJob(), 2000);
            }
        }
        
    } catch (error) {
        console.error('Error setting up Indeed job tracking:', error);
    }
}

function waitForContent() {
    return new Promise((resolve) => {
        const checkContent = () => {
            const titleElement = findElement(INDEED_CONFIG.selectors.jobTitle);
            if (titleElement && titleElement.textContent.trim()) {
                resolve();
            } else {
                setTimeout(checkContent, 500);
            }
        };
        checkContent();
    });
}

function extractJobData() {
    const jobData = {
        platform: 'indeed',
        jobUrl: window.location.href,
        extractedAt: new Date().toISOString()
    };
    
    // Extract job title
    const titleElement = findElement(INDEED_CONFIG.selectors.jobTitle);
    if (titleElement) {
        jobData.jobTitle = titleElement.textContent.trim();
    }
    
    // Extract company
    const companyElement = findElement(INDEED_CONFIG.selectors.company);
    if (companyElement) {
        jobData.company = companyElement.textContent.trim();
    }
    
    // Extract location
    const locationElement = findElement(INDEED_CONFIG.selectors.location);
    if (locationElement) {
        jobData.location = locationElement.textContent.trim();
    }
    
    // Extract description
    const descElement = findElement(INDEED_CONFIG.selectors.description);
    if (descElement) {
        jobData.description = descElement.textContent.trim().substring(0, 2000);
    }
    
    // Extract salary if available
    const salaryElement = findElement(INDEED_CONFIG.selectors.salary);
    if (salaryElement) {
        jobData.salaryRange = salaryElement.textContent.trim();
    }
    
    // Extract job type and other attributes
    const attributeElements = document.querySelectorAll('.attribute_snippet');
    const attributes = [];
    attributeElements.forEach(attr => {
        const text = attr.textContent.trim();
        if (text && !text.includes('$')) { // Salary is handled separately
            attributes.push(text);
        }
    });
    
    if (attributes.length > 0) {
        jobData.jobAttributes = attributes;
        
        // Try to extract specific information
        const attributeText = attributes.join(' ').toLowerCase();
        if (attributeText.includes('full-time')) jobData.jobType = 'Full-time';
        else if (attributeText.includes('part-time')) jobData.jobType = 'Part-time';
        else if (attributeText.includes('contract')) jobData.jobType = 'Contract';
        else if (attributeText.includes('temporary')) jobData.jobType = 'Temporary';
    }
    
    // Extract job ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('jk');
    if (jobId) {
        jobData.indeedJobId = jobId;
    }
    
    // Extract company rating if available
    const ratingElement = document.querySelector('.icl-Ratings-starsCountWrapper');
    if (ratingElement) {
        jobData.companyRating = ratingElement.textContent.trim();
    }
    
    // Extract posting date if available
    const dateElement = document.querySelector('.jobsearch-JobMetadataFooter');
    if (dateElement) {
        const dateText = dateElement.textContent;
        const dateMatch = dateText.match(/(\d+\+?\s+days?\s+ago|Posted\s+\d+\+?\s+days?\s+ago)/i);
        if (dateMatch) {
            jobData.postedDate = dateMatch[0];
        }
    }
    
    console.log('Extracted Indeed job data:', jobData);
    return jobData;
}

function findElement(selectors) {
    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) return element;
    }
    return null;
}

async function checkIfJobTracked() {
    try {
        const trackedJobs = await new Promise((resolve) => {
            chrome.runtime.sendMessage({ type: 'GET_TRACKED_JOBS' }, resolve);
        });
        
        if (trackedJobs && currentJobData) {
            isTracked = trackedJobs.some(job => 
                job.jobUrl === currentJobData.jobUrl ||
                (job.indeedJobId && job.indeedJobId === currentJobData.indeedJobId)
            );
        }
    } catch (error) {
        console.error('Error checking if job is tracked:', error);
    }
}

function addTrackingButton() {
    // Remove existing button
    if (trackingButton) {
        trackingButton.remove();
    }
    
    // Find a good location to insert the button
    const applyButton = findElement(INDEED_CONFIG.selectors.applyButton);
    const jobHeader = document.querySelector('[data-testid="jobsearch-JobInfoHeader"]');
    const jobActions = document.querySelector('.jobsearch-JobMetadataHeader-container');
    
    let insertLocation = applyButton?.parentElement || jobActions || jobHeader;
    
    if (!insertLocation) {
        // Fallback: try to find any suitable container
        insertLocation = document.querySelector('.jobsearch-SerpJobCard') || 
                        document.querySelector('.jobsearch-JobComponent');
    }
    
    if (insertLocation) {
        trackingButton = createTrackingButton();
        
        // Create a container for better styling
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            margin: 10px 0;
            display: flex;
            align-items: center;
        `;
        buttonContainer.appendChild(trackingButton);
        
        // Insert button container
        if (applyButton?.parentElement) {
            applyButton.parentElement.appendChild(buttonContainer);
        } else {
            insertLocation.appendChild(buttonContainer);
        }
    }
}

function createTrackingButton() {
    const button = document.createElement('button');
    button.style.cssText = `
        background: ${isTracked ? '#10b981' : '#3b82f6'};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 18px;
        margin: 4px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s ease;
        z-index: 1000;
        position: relative;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    `;
    
    updateButtonState(button);
    
    button.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        if (!isTracked) {
            await trackJob();
        } else {
            showJobTrackedMessage();
        }
    });
    
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-1px)';
        button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    });
    
    return button;
}

function updateButtonState(button) {
    if (isTracked) {
        button.innerHTML = '✅ Tracked with Portia AI';
        button.style.background = '#10b981';
        button.disabled = false;
    } else {
        button.innerHTML = '🤖 Track with Portia AI';
        button.style.background = '#3b82f4';
        button.disabled = false;
    }
}

async function trackJob() {
    if (!currentJobData) {
        showMessage('Unable to extract job data', 'error');
        return;
    }
    
    try {
        // Update button to loading state
        if (trackingButton) {
            trackingButton.innerHTML = '⏳ Tracking...';
            trackingButton.disabled = true;
        }
        
        // Send to background script
        chrome.runtime.sendMessage({
            type: 'TRACK_JOB',
            jobData: currentJobData
        });
        
        // Update state
        isTracked = true;
        
        // Update button
        if (trackingButton) {
            updateButtonState(trackingButton);
        }
        
        // Show success message
        showMessage(`Successfully tracked: ${currentJobData.jobTitle} at ${currentJobData.company}`, 'success');
        
    } catch (error) {
        console.error('Error tracking job:', error);
        showMessage('Error tracking job: ' + error.message, 'error');
        
        // Reset button on error
        if (trackingButton) {
            trackingButton.innerHTML = '🤖 Track with Portia AI';
            trackingButton.disabled = false;
        }
    }
}

function showJobTrackedMessage() {
    showMessage('This job is already being tracked by Portia AI', 'info');
}

function showMessage(text, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.portia-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create message element
    const message = document.createElement('div');
    message.className = 'portia-message';
    message.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease-out;
        ${getMessageStyles(type)}
    `;
    
    message.textContent = text;
    
    // Add animation keyframes if not already added
    if (!document.querySelector('#portia-animations')) {
        const style = document.createElement('style');
        style.id = 'portia-animations';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(message);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (message.parentNode) {
            message.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (message.parentNode) {
                    message.remove();
                }
            }, 300);
        }
    }, 4000);
}

function getMessageStyles(type) {
    switch (type) {
        case 'success':
            return 'background: #10b981; color: white;';
        case 'error':
            return 'background: #ef4444; color: white;';
        case 'info':
        default:
            return 'background: #3b82f6; color: white;';
    }
}

async function getUserSettings() {
    try {
        return await new Promise((resolve) => {
            chrome.runtime.sendMessage({ type: 'GET_USER_SETTINGS' }, resolve);
        });
    } catch (error) {
        console.error('Error getting user settings:', error);
        return null;
    }
}

// Export functions for testing
window.portiaIndeed = {
    extractJobData,
    trackJob,
    currentJobData
};
