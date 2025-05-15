echo "Pac-Man Maze Preview Options"
echo "1. Show Kruskal Grid Carving"
echo "2. Show Pac-Man Tile Map"
echo "3. Generate Maze Silently"
echo "4. Use Custom Seed"
echo "0. Exit"
read -p "Choose an option [0-4]: " option

case $option in
    1)
        echo "Running Kruskal grid carving..."
        python kruskal_algorithm.py --mode kruskal
        ;;
    2)
        echo "Running Pac-Man tile map visualization..."
        python kruskal_algorithm.py --mode tile
        ;;
    3)
        echo "Generating maze silently..."
        python kruskal_algorithm.py
        ;;
    4)
        read -p "Enter seed value: " seed
        echo "Running both modes with seed $seed..."
        python kruskal_algorithm.py --mode kruskal --seed "$seed"
        python kruskal_algorithm.py --mode tile --seed "$seed"
        ;;
    0)
        echo "Exiting."
        ;;
    *)
        echo "Invalid option."
        ;;
esac
