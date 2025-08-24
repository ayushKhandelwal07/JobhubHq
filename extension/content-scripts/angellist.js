// AngelList/Wellfound Content Script for Portia AI Job Tracker
console.log('Portia AI AngelList/Wellfound content script loaded');

// Configuration
const ANGELLIST_CONFIG = {
    selectors: {
        jobTitle: [
            'h1',
            '.job-title',
            '[data-test="JobHeader-title"]',
            '.styles_title__3xNdj'
        ],
        company: [
            '.company-name',
            '.startup-name',
            '[data-test="StartupNameAndAvatar"] a',
            '.styles_startupName__1bNso'
        ],
        location: [
            '.location',
            '.job-location',
            '[data-test="JobHeader-location"]',
            '.styles_location__2i3kN'
        ],
        description: [
            '.job-description',
            '.description',
            '.job-details',
            '[data-test="JobDescription"]',
            '.styles_description__2XQFl'
        ],
        salary: [
            '.compensation',
            '.salary-range',
            '[data-test="JobHeader-salary"]',
            '.styles_compensation__3xKjI'
        ],
        equity: [
            '.equity',
            '.equity-range',
            '[data-test="JobHeader-equity"]'
        ],
        applyButton: [
            '[data-test="apply-button"]',
            '.apply-button',
            '.styles_applyButton__2JzjO'
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
    console.log('Initializing AngelList/Wellfound job tracker...');
    
    // Check if we're on a job details page
    if (isJobDetailsPage()) {
        setupJobTracking();
        
        // Monitor for navigation changes (AngelList is a SPA)
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
    return (window.location.href.includes('/company/') && window.location.href.includes('/jobs/')) ||
           window.location.href.includes('/job/') ||
           document.querySelector('[data-test="JobHeader-title"], h1') !== null;
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
    }, 1500); // AngelList might take longer to load
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
        console.error('Error setting up AngelList job tracking:', error);
    }
}

function waitForContent() {
    return new Promise((resolve) => {
        const checkContent = () => {
            const titleElement = findElement(ANGELLIST_CONFIG.selectors.jobTitle);
            const companyElement = findElement(ANGELLIST_CONFIG.selectors.company);
            
            if (titleElement && titleElement.textContent.trim() && 
                companyElement && companyElement.textContent.trim()) {
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
        platform: 'angellist',
        jobUrl: window.location.href,
        extractedAt: new Date().toISOString()
    };
    
    // Extract job title
    const titleElement = findElement(ANGELLIST_CONFIG.selectors.jobTitle);
    if (titleElement) {
        jobData.jobTitle = titleElement.textContent.trim();
    }
    
    // Extract company
    const companyElement = findElement(ANGELLIST_CONFIG.selectors.company);
    if (companyElement) {
        jobData.company = companyElement.textContent.trim();
    }
    
    // Extract location
    const locationElement = findElement(ANGELLIST_CONFIG.selectors.location);
    if (locationElement) {
        jobData.location = locationElement.textContent.trim();
    }
    
    // Extract description
    const descElement = findElement(ANGELLIST_CONFIG.selectors.description);
    if (descElement) {
        jobData.description = descElement.textContent.trim().substring(0, 2000);
    }
    
    // Extract salary if available
    const salaryElement = findElement(ANGELLIST_CONFIG.selectors.salary);
    if (salaryElement) {
        jobData.salaryRange = salaryElement.textContent.trim();
    }
    
    // Extract equity if available
    const equityElement = findElement(ANGELLIST_CONFIG.selectors.equity);
    if (equityElement) {
        jobData.equityRange = equityElement.textContent.trim();
    }
    
    // Combine salary and equity for display
    if (jobData.salaryRange && jobData.equityRange) {
        jobData.compensation = `${jobData.salaryRange} + ${jobData.equityRange}`;
    } else if (jobData.salaryRange) {
        jobData.compensation = jobData.salaryRange;
    } else if (jobData.equityRange) {
        jobData.compensation = jobData.equityRange;
    }
    
    // Extract startup stage if available
    const stageElements = document.querySelectorAll('[data-test*="stage"], .stage, .company-stage');
    stageElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        if (text.includes('seed') || text.includes('series') || text.includes('pre-seed')) {
            jobData.startupStage = element.textContent.trim();
        }
    });
    
    // Extract company size if available
    const sizeElements = document.querySelectorAll('[data-test*="size"], .company-size, .team-size');
    sizeElements.forEach(element => {
        const text = element.textContent;
        if (text.match(/\d+[-\s]*\d*\s*(people|employees|team)/i)) {
            jobData.companySize = element.textContent.trim();
        }
    });
    
    // Extract job type and experience level from various places
    const allText = document.body.textContent.toLowerCase();
    
    // Job type detection
    if (allText.includes('full-time') || allText.includes('full time')) {
        jobData.jobType = 'Full-time';
    } else if (allText.includes('part-time') || allText.includes('part time')) {
        jobData.jobType = 'Part-time';
    } else if (allText.includes('contract')) {
        jobData.jobType = 'Contract';
    } else if (allText.includes('internship')) {
        jobData.jobType = 'Internship';
    }
    
    // Experience level detection
    if (allText.includes('senior') || allText.includes('sr.')) {
        jobData.experienceLevel = 'Senior';
    } else if (allText.includes('junior') || allText.includes('jr.')) {
        jobData.experienceLevel = 'Junior';
    } else if (allText.includes('lead') || allText.includes('principal')) {
        jobData.experienceLevel = 'Lead/Principal';
    } else if (allText.includes('entry level') || allText.includes('entry-level')) {
        jobData.experienceLevel = 'Entry Level';
    }
    
    // Extract job ID from URL
    const urlMatch = jobData.jobUrl.match(/\/jobs\/(\d+)/);
    if (urlMatch) {
        jobData.angellistJobId = urlMatch[1];
    }
    
    // Extract tags/skills if available
    const tagElements = document.querySelectorAll('.tag, .skill-tag, [data-test*="tag"]');
    const skills = [];
    tagElements.forEach(tag => {
        const text = tag.textContent.trim();
        if (text && text.length < 30) { // Avoid long descriptions
            skills.push(text);
        }
    });
    
    if (skills.length > 0) {
        jobData.skills = skills.slice(0, 10); // Limit to first 10 skills
    }
    
    console.log('Extracted AngelList job data:', jobData);
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
                (job.angellistJobId && job.angellistJobId === currentJobData.angellistJobId)
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
    const applyButton = findElement(ANGELLIST_CONFIG.selectors.applyButton);
    const jobHeader = document.querySelector('[data-test="JobHeader"], .job-header');
    const companySection = document.querySelector('[data-test="StartupNameAndAvatar"]');
    
    let insertLocation = applyButton?.parentElement || jobHeader || companySection;
    
    if (!insertLocation) {
        // Fallback: try to find any suitable container
        insertLocation = document.querySelector('.job-details, .job-content') || 
                        document.body;
    }
    
    if (insertLocation) {
        trackingButton = createTrackingButton();
        
        // Create a container for better positioning
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            margin: 15px 0;
            display: flex;
            justify-content: flex-start;
            align-items: center;
        `;
        buttonContainer.appendChild(trackingButton);
        
        // Insert button container
        if (applyButton?.parentElement) {
            applyButton.parentElement.insertBefore(buttonContainer, applyButton.nextSibling);
        } else if (jobHeader) {
            jobHeader.appendChild(buttonContainer);
        } else {
            insertLocation.insertBefore(buttonContainer, insertLocation.firstChild);
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
        padding: 12px 20px;
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
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
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
        button.style.background = '#3b82f6';
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
window.portiaAngelList = {
    extractJobData,
    trackJob,
    currentJobData
};
