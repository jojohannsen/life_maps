/**
 * Handles city selection when a timeline bar is clicked
 * @param {string} cityName - The name of the city to select
 */
function select_city(cityName) {
    console.log(`City selected: ${cityName}`);
    
    // First try to find the button by city name
    const cityButtons = document.querySelectorAll('#city-buttons-container button');
    for (const button of cityButtons) {
        // Check the text content of the div with city-name class
        const cityNameDiv = button.querySelector('.city-name');
        if (cityNameDiv && cityNameDiv.textContent.trim() === cityName) {
            console.log(`Found button for ${cityName}`);
            // Simulate a click on the button
            button.click();
            return;
        }
    }
    
    // If we couldn't find by name, try to find by ID (requires backend to have set city IDs)
    // This is a fallback in case the city name in the timeline doesn't exactly match the button
    const cityIds = Array.from(cityButtons).map(button => button.id).filter(id => id.startsWith('city'));
    console.log(`Available city buttons: ${cityIds.join(', ')}`);
    
    // If no button found, we could trigger an HTMX request to load this city
    console.log(`No button found for city: ${cityName}`);
}
