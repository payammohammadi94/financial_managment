document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const timeline = document.getElementById('timeline');
    const addMilestoneBtn = document.getElementById('addMilestoneBtn');
    const exportBtn = document.getElementById('exportBtn');
    const milestoneModal = document.getElementById('milestoneModal');
    const memberModal = document.getElementById('memberModal');
    const closeButtons = document.querySelectorAll('.close');
    const cancelMilestone = document.getElementById('cancelMilestone');
    const confirmMilestone = document.getElementById('confirmMilestone');
    const cancelMember = document.getElementById('cancelMember');
    const confirmMember = document.getElementById('confirmMember');
    const milestoneDate = document.getElementById('milestoneDate');
    const milestoneTitle = document.getElementById('milestoneTitle');
    const memberName = document.getElementById('memberName');
    const memberRole = document.getElementById('memberRole');
    const memberImage = document.getElementById('memberImage');
    const avatarPreview = document.getElementById('avatarPreview');
    const teamCount = document.getElementById('teamCount');
    
    // State
    let milestones = [];
    let currentMilestone = null;
    let totalTeamMembers = 0;
    
    // Initialize
    init();
    
    function init() {
        // Load sample data
        loadSampleData();
        updateTeamCount();
        
        // Event listeners
        addMilestoneBtn.addEventListener('click', openMilestoneModal);
        exportBtn.addEventListener('click', exportTimeline);
        
        // Modal controls
        closeButtons.forEach(btn => btn.addEventListener('click', closeAllModals));
        cancelMilestone.addEventListener('click', closeAllModals);
        confirmMilestone.addEventListener('click', addNewMilestone);
        cancelMember.addEventListener('click', closeAllModals);
        confirmMember.addEventListener('click', addNewMember);
        
        // Image upload preview
        memberImage.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    avatarPreview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
                };
                reader.readAsDataURL(file);
            }
        });
        
        // Set default date to today
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        milestoneDate.value = formattedDate;
    }
    
    function loadSampleData() {
        // Add some sample milestones for demonstration
        const sampleDates = [
            { date: '2023-06-15', title: 'SIMORGH' },
            { date: '2023-07-01', title: 'AIS' },
            { date: '2023-08-15', title: 'ANT' }
        ];
        
        sampleDates.forEach(item => {
            createMilestone(new Date(item.date), item.title);
        });
    }
    
    function openMilestoneModal() {
        milestoneModal.style.display = 'flex';
    }
    
    function openMemberModal(milestoneElement) {
        currentMilestone = milestoneElement;
        memberModal.style.display = 'flex';
        // Reset form
        memberName.value = '';
        memberRole.value = '';
        memberImage.value = '';
        avatarPreview.innerHTML = '<i class="fas fa-user-plus"></i>';
    }
    
    function closeAllModals() {
        milestoneModal.style.display = 'none';
        memberModal.style.display = 'none';
    }
    
    function addNewMilestone() {
        const dateValue = milestoneDate.value;
        const titleValue = milestoneTitle.value.trim();
        
        if (!dateValue) {
            alert('Please select a date');
            return;
        }
        
        const date = new Date(dateValue);
        
        // Check if milestone already exists for this date
        const exists = milestones.some(m => m.date.getTime() === date.getTime());
        if (exists) {
            alert('A milestone already exists for this date');
            return;
        }
        
        createMilestone(date, titleValue);
        closeAllModals();
        
        // Reset form
        milestoneTitle.value = '';
    }
    
    function createMilestone(date, title = '') {
        const milestone = {
            date,
            title,
            teamMembers: [],
            element: null
        };
        
        // Create DOM element
        const milestoneElement = document.createElement('div');
        milestoneElement.className = 'milestone';
        
        const day = date.getDate();
        
        milestoneElement.innerHTML = `
            ${title ? `<div class="milestone-title">${title}</div>` : ''}
            <div class="milestone-date">
                <span class="milestone-day">${day}</span>
            </div>
            <button class="add-member-btn">
                <i class="fas fa-user-plus"></i>
            </button>
            <div class="team-members"></div>
        `;
        
        // Add to array and sort
        milestone.element = milestoneElement;
        milestones.push(milestone);
        milestones.sort((a, b) => a.date - b.date);
        
        // Rebuild timeline
        rebuildTimeline();
        
        // Add event listeners
        const addMemberBtn = milestoneElement.querySelector('.add-member-btn');
        addMemberBtn.addEventListener('click', () => openMemberModal(milestoneElement));
    }
    
    function addNewMember() {
        const name = memberName.value.trim();
        const role = memberRole.value.trim();
        const imageFile = memberImage.files[0];
        
        if (!name) {
            alert('Please enter member name');
            return;
        }
        
        if (!imageFile) {
            alert('Please upload a photo');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const member = {
                name,
                role,
                image: e.target.result
            };
            
            // Find the milestone in our array
            const milestone = milestones.find(m => m.element === currentMilestone);
            if (milestone) {
                milestone.teamMembers.push(member);
                renderTeamMember(currentMilestone, member);
                totalTeamMembers++;
                updateTeamCount();
            }
            
            closeAllModals();
        };
        reader.readAsDataURL(imageFile);
    }
    
    function renderTeamMember(milestoneElement, member) {
        const teamMembersContainer = milestoneElement.querySelector('.team-members');
        
        const memberElement = document.createElement('div');
        memberElement.className = 'team-member';
        memberElement.innerHTML = `
            <div class="member-avatar">
                <img src="${member.image}" alt="${member.name}">
                <div class="member-info-tooltip">
                    <div class="member-name">${member.name}</div>
                    ${member.role ? `<div class="member-role">${member.role}</div>` : ''}
                </div>
            </div>
        `;
        
        // Add click to remove functionality
        const avatar = memberElement.querySelector('.member-avatar');
        avatar.addEventListener('click', function(e) {
            e.stopPropagation();
            if (confirm(`Remove ${member.name} from this milestone?`)) {
                memberElement.remove();
                
                // Remove from our data
                const milestone = milestones.find(m => m.element === milestoneElement);
                if (milestone) {
                    const index = milestone.teamMembers.indexOf(member);
                    if (index > -1) {
                        milestone.teamMembers.splice(index, 1);
                        totalTeamMembers--;
                        updateTeamCount();
                    }
                }
            }
        });
        
        teamMembersContainer.appendChild(memberElement);
    }
    
    function rebuildTimeline() {
        timeline.innerHTML = '';
        
        milestones.forEach(milestone => {
            timeline.appendChild(milestone.element);
            
            // Re-render team members
            const teamMembersContainer = milestone.element.querySelector('.team-members');
            teamMembersContainer.innerHTML = '';
            
            milestone.teamMembers.forEach(member => {
                renderTeamMember(milestone.element, member);
            });
        });
    }
    
    function updateTeamCount() {
        teamCount.textContent = totalTeamMembers;
    }
    
    function exportTimeline() {
        // Create a canvas to render the timeline
        const canvas = document.createElement('canvas');
        const timelineElement = document.querySelector('.timeline-scroll');
        const width = timelineElement.scrollWidth;
        const height = timelineElement.scrollHeight + 150; // Extra space for header
        
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        
        // Background
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, width, height);
        
        // Project info header
        ctx.fillStyle = '#4361ee';
        ctx.fillRect(0, 0, width, 80);
        
        // Project title
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 20px Arial';
        ctx.fillText('Project Timeline Export', 20, 30);
        
        ctx.font = '14px Arial';
        ctx.fillText(document.querySelector('.project-code').textContent + ' - ' + 
                    document.querySelector('.project-title').textContent, 20, 55);
        
        // Render timeline elements
        const data = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
            <foreignObject width="100%" height="100%">
                <div xmlns="http://www.w3.org/1999/xhtml">
                    ${document.querySelector('.timeline').outerHTML}
                </div>
            </foreignObject>
        </svg>`;
        
        const img = new Image();
        const svg = new Blob([data], {type: 'image/svg+xml'});
        const url = URL.createObjectURL(svg);
        
        img.onload = function() {
            ctx.drawImage(img, 0, 80, width, height-80);
            URL.revokeObjectURL(url);
            
            // Convert to PNG and download
            const pngUrl = canvas.toDataURL('image/png');
            const downloadLink = document.createElement('a');
            downloadLink.href = pngUrl;
            downloadLink.download = `timeline-export-${new Date().toISOString().slice(0,10)}.png`;
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
            
            // Show nice confirmation
            showExportSuccess();
        };
        
        img.src = url;
    }
    
    function showExportSuccess() {
        const notification = document.createElement('div');
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.right = '20px';
        notification.style.backgroundColor = '#4bb543';
        notification.style.color = 'white';
        notification.style.padding = '15px 25px';
        notification.style.borderRadius = '5px';
        notification.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        notification.style.zIndex = '1000';
        notification.style.display = 'flex';
        notification.style.alignItems = 'center';
        notification.style.gap = '10px';
        notification.style.animation = 'fadeIn 0.3s, fadeOut 0.3s 2.7s forwards';
        notification.innerHTML = `
            <i class="fas fa-check-circle" style="font-size: 20px;"></i>
            <span>Timeline exported successfully!</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === milestoneModal || event.target === memberModal) {
            closeAllModals();
        }
    });
});