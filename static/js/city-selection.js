/**
 * Handles city selection when a timeline bar is clicked
 * @param {string} cityName - The name of the city to select
 */
function select_city(cityName) {
    console.log(`City selected: ${cityName}`);
    
    // Find any city button with this city name
    const cityButtons = document.querySelectorAll('#city-buttons-container button');
    for (const button of cityButtons) {
        if (button.textContent.includes(cityName)) {
            // Simulate a click on the button
            button.click();
            return;
        }
    }
    
    // If no button found, we could trigger an HTMX request to load this city
    console.log(`No button found for city: ${cityName}`);
}
