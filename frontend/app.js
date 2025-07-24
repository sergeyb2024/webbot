document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');

    // IMPORTANT: Replace this with your actual deployed Heroku API URL
    const API_BASE_URL = 'http://127.0.0.1:5000';

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const keyword = searchInput.value.trim();
        if (!keyword) return;

        displayLoadingSpinner();

        try {
            // The front-end makes a simple request to the API.
            // The API handles the complex task of querying the pre-populated database.
            const response = await fetch(`${API_BASE_URL}/api/search?keyword=${encodeURIComponent(keyword)}`);

            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }

            const articles = await response.json();
            displayResults(articles);

        } catch (error) {
            console.error('Error fetching news:', error);
            displayError('Failed to fetch news. The bot might be resting. Please try again later.');
        }
    });

    function displayLoadingSpinner() {
        resultsContainer.innerHTML = '<div class="loading-spinner"></div>';
    }

    function displayError(message) {
        resultsContainer.innerHTML = `<p style="text-align: center; color: #ff8a80;">${message}</p>`;
    }

    function displayResults(articles) {
        resultsContainer.innerHTML = ''; // Clear previous results or spinner

        if (articles.length === 0) {
            resultsContainer.innerHTML = '<p style="text-align: center;">The bot searched far and wide but found no recent news for that keyword.</p>';
            return;
        }

        articles.forEach(article => {
            const card = document.createElement('div');
            card.className = 'article-card';

            // Create and append the image
            const image = document.createElement('img');
            image.src = article.image_url || 'https://via.placeholder.com/400x200.png?text=No+Image';
            image.alt = article.headline;
            image.className = 'article-image';
            // Handle image loading errors
            image.onerror = () => {
                image.src = 'https://via.placeholder.com/400x200.png?text=Image+Error';
            };
            card.appendChild(image);

            // Create and append the content container
            const content = document.createElement('div');
            content.className = 'article-content';

            // Create and append the headline
            const headline = document.createElement('h2');
            const link = document.createElement('a');
            link.href = article.source_url;
            link.textContent = article.headline;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            headline.appendChild(link);
            content.appendChild(headline);

            // Create and append the summary
            const summary = document.createElement('p');
            summary.textContent = article.summary;
            content.appendChild(summary);

            card.appendChild(content);
            resultsContainer.appendChild(card);
        });
    }
});