/**
 * Handles city selection when a timeline bar is clicked
 * @param {number} cityId - The ID of the city to select
 */
function select_city(cityId) {
    console.log(`City selected by ID: ${cityId}`);
    
    // Find the button with the matching city ID
    const cityButton = document.getElementById(`city${cityId}`);
    if (cityButton) {
        console.log(`Found button for city ID ${cityId}`);
        // Simulate a click on the button
        cityButton.click();
        return;
    }
    
    // If no button found, log available buttons
    const cityButtons = document.querySelectorAll('#city-buttons-container button');
    const cityIds = Array.from(cityButtons).map(button => button.id).filter(id => id.startsWith('city'));
    console.log(`Available city buttons: ${cityIds.join(', ')}`);
    console.log(`No button found for city ID: ${cityId}`);
}
