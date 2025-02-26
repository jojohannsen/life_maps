/**
 * Handles city selection when a timeline bar is clicked
 * @param {number} cityId - The ID of the city to select
 */
function select_city(cityId) {
    setTimeout(() => {
        // Find the button with the matching city ID
        const cityButton = document.getElementById(`city${cityId}`);
        if (cityButton) {
            console.log(`Found button for city ID ${cityId}`);
            // Simulate a click on the button
            cityButton.click();
            return;
        }
    }, 500);
}
