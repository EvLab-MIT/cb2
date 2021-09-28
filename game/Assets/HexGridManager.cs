using System.Collections;
using System.Collections.Generic;
using UnityEngine;


// This class manages the hexagonal grid. It is responsible for pulling map
// updates from an IMapSource and then loading the required assets from an
// IAssetSource. These are specified via an interface to generically decouple
// this class from Asset and Map implementations (Dependency Injection).
//
// This class uses the Hexagon Efficient Coordinate System (HECS) as
// detailed in the following link. This means coordinates consist of 3
// parameters: A, R, C.
// https://en.wikipedia.org/wiki/Hexagonal_Efficient_Coordinate_System
public class HexGridManager
{
    public class TileInformation
    {
        public int AssetId;
        public HexCell Cell;
        public int RotationDegrees;  // Multiple of 60 for grid alignment.
    }

    public class Tile
    {
        public int AssetId;
        public HexCell Cell;
        public int RotationDegrees;  // Multiple of 60 for grid alignment.
        public GameObject Model;
    }

    // Interface for loading assets.
    public interface IAssetSource
    {
        // Returns a prefab of the requested asset.
        GameObject Load(int assetId);

        // TODO(sharf): If we want to remove unity-specific interfaces entirely,
        // this interface can be rewritten to add something similar to Unity's
        // "Instantiate" function. 
    }

    // Interface for retrieving map updates.
    public interface IMapSource
    {
        // Retrieves the dimensions of the hexagon grid.
        (int, int) GetMapDimensions();

        // List of tiles. Each tile represents one cell in the grid.
        List<TileInformation> GetTileList();

        // Returns an integer. Increments each time any change is made to the map.
        // If the iteration remains unchanged, no map updates need to be done.
        // Technically there's a race condition between this and GetGrid.
        // TODO(sharf): update this interface to be atomic with GetGrid().
        // Worst case with this race, too much rendering is done, or an update
        // comes a bit late.
        int GetMapIteration();
    }

    private IMapSource _mapSource;
    private IAssetSource _assetSource;

    // Used to determine if player can walk through an edge.
    private HexCell[,,] _edgeMap;

    // A list of all the tiles currently placed in the map.
    private Tile[,,] _grid;

    // Used to check if the map needs to be re-loaded.
    private int _lastMapIteration = 0;

    public HexGridManager(IMapSource mapSource, IAssetSource assetSource)
    {
        _mapSource = mapSource;
        _assetSource = assetSource;
    }

    public void Start()
    {
        (int rows, int cols) = _mapSource.GetMapDimensions();
        _grid = new Tile[2, rows / 2, cols];
        _edgeMap = new HexCell[2, rows / 2, cols];

        // Pre-initialize the edge map to be all-empty.
        for (int r = 0; r < rows; r++)
        {
            for (int c = 0; c < cols; c++)
            {
                int hecsA = r % 2;
                int hecsR = r / 2;
                int hecsC = c;

                _edgeMap[hecsA, hecsR, hecsC] = new HexCell(
                    new HecsCoord(hecsA, hecsR, hecsC), new HexBoundary());
            }
        }
    }

    public void Update()
    {
        UpdateMap();
    }

    // Updates the edge boundary map for a single cell.
    private void UpdateCellEdges(HexCell c)
    {
        _edgeMap[c.coord.a, c.coord.r, c.coord.c].boundary.MergeWith(c.boundary);

        // Edge map symmetry must be retained. That is -- if cell B has an edge
        // boundary with A, then A must also have a matching boundary with B.
        // Update neighbor cell boundaries to match.
        HecsCoord[] neighbors = c.coord.Neighbors();
        foreach (HecsCoord n in neighbors)
        {
            _edgeMap[n.a, n.r, n.c].boundary.SetEdgeWith(n, c.coord);
        }
    }

    private void UpdateEdgeMap(TileInformation tile)
    {
        UpdateCellEdges(tile.Cell);

    }

    private void UpdateMap()
    {
        if (_mapSource == null)
        {
            Debug.Log("Null map source.");
            return;
        }
        int iteration = _mapSource.GetMapIteration();
        if (iteration == _lastMapIteration)
        {
            // The map hasn't changed.
            return;
        }

        List<TileInformation> tileList = _mapSource.GetTileList();

        if (tileList == null)
        {
            Debug.Log("Null item list received.");
            return;
        }
        foreach (var t in tileList)
        {
            GameObject prefab = _assetSource.Load(t.AssetId);
            Tile tile = _grid[t.Cell.coord.a, t.Cell.coord.r, t.Cell.coord.c];
            tile.Cell = t.Cell;
            tile.AssetId = t.AssetId;
            tile.Model = GameObject.Instantiate(prefab, tile.Cell.Center(), Quaternion.identity);
            UpdateEdgeMap(t);
        }
        _lastMapIteration = iteration;
    }
}
