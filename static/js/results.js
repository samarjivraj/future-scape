document.addEventListener('DOMContentLoaded', function() {
    initStoryAnimation();
    initCrystalBallInteraction();
    initScrollToStory();
});

// animate story text with sequential fade-in
function initStoryAnimation() {
    const storyContent = document.querySelector('.story-content');
    if (!storyContent) return;

    // split the story into paragraphs and process each one
    const paragraphs = storyContent.innerHTML.split('\n\n');
    storyContent.innerHTML = ''; 

    paragraphs.forEach((paragraph, index) => {
        if (paragraph.trim()) {
            const p = document.createElement('p');
            p.innerHTML = paragraph.trim();
            p.style.opacity = '0';
            p.style.transform = 'translateY(20px)';
            p.style.transition = `all 0.6s ease ${index * 0.3}s`;
            storyContent.appendChild(p);
        }
    });

    // trigger animation after a short delay
    setTimeout(() => {
        const paragraphs = storyContent.querySelectorAll('p');
        paragraphs.forEach(p => {
            p.style.opacity = '1';
            p.style.transform = 'translateY(0)';
        });
    }, 500);
}

// add crystal ball interactions
function initCrystalBallInteraction() {
    const crystalBall = document.querySelector('.results-crystal-image');
    if (!crystalBall) return;

    // add hover effect
    crystalBall.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.05)';
        this.style.filter = 'brightness(1.2) drop-shadow(0 0 20px rgba(255, 215, 0, 0.6))';
    });

    crystalBall.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
        this.style.filter = 'brightness(1) drop-shadow(0 0 15px rgba(255, 215, 0, 0.4))';
    });
}

// smooth scroll to story section when crystal ball is clicked
function initScrollToStory() {
    const crystalBall = document.querySelector('.results-crystal-image');
    if (!crystalBall) return;

    crystalBall.addEventListener('click', function() {
        const storySection = document.querySelector('.story-section');
        if (storySection) {
            storySection.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
}
