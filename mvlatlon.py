import sqlite3
from typing import Dict, Tuple
import logging

def setup_logging():
    """Configure logging for the script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_reference_data(db_path: str) -> Dict[str, Tuple[float, float]]:
    """
    Extract city coordinates from the reference database.
    
    Args:
        db_path: Path to the reference database file
        
    Returns:
        Dictionary mapping city names to (lat, lon) tuples
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, lat, lon FROM city_location WHERE lat IS NOT NULL AND lon IS NOT NULL")
            return {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    except sqlite3.Error as e:
        logging.error(f"Error reading reference database: {e}")
        raise

def update_cities_database(db_path: str, reference_data: Dict[str, Tuple[float, float]]) -> None:
    """
    Update the cities database with coordinates from the reference data.
    
    Args:
        db_path: Path to the cities database file
        reference_data: Dictionary mapping city names to (lat, lon) tuples
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get cities that need updating
            cursor.execute("SELECT name FROM city_location WHERE lat IS NULL OR lon IS NULL")
            cities_to_update = cursor.fetchall()
            
            updates = 0
            skipped = 0
            
            # Update each city if reference data exists
            for (city_name,) in cities_to_update:
                if city_name in reference_data:
                    lat, lon = reference_data[city_name]
                    cursor.execute(
                        "UPDATE city_location SET lat = ?, lon = ? WHERE name = ?",
                        (lat, lon, city_name)
                    )
                    updates += 1
                else:
                    skipped += 1
                    logging.warning(f"No reference data found for city: {city_name}")
            
            conn.commit()
            logging.info(f"Updated {updates} cities")
            logging.info(f"Skipped {skipped} cities (no reference data)")
            
            # Verify updates
            cursor.execute("SELECT COUNT(*) FROM city_location WHERE lat IS NULL OR lon IS NULL")
            remaining = cursor.fetchone()[0]
            logging.info(f"Cities still missing coordinates: {remaining}")
            
    except sqlite3.Error as e:
        logging.error(f"Error updating cities database: {e}")
        raise

def main():
    """Main function to coordinate the database synchronization"""
    setup_logging()
    
    try:
        # Load reference data
        reference_data = get_reference_data("cities.db")
        logging.info(f"Loaded {len(reference_data)} reference cities")
        
        # Update cities database
        update_cities_database("data/cities.db", reference_data)
        logging.info("Database synchronization completed successfully")
        
    except Exception as e:
        logging.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()
