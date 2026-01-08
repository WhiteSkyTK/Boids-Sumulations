# Python Boids Flocking Simulation 🦅✨

A comparative implementation of the classic "Boids" flocking algorithm. This repository contains two versions: a readable **Object-Oriented** version and a high-performance **NumPy** version.

**🔗 [View the Video Demo](LINK_TO_VIDEO)**

## 🧪 The Algorithm
Both simulations follow Craig Reynolds' three core rules:

1.  **Separation:** Steer to avoid crowding local flockmates.
2.  **Alignment:** Steer towards the average heading of local flockmates.
3.  **Cohesion:** Steer to move towards the average position of local flockmates.

![Flocking Rules](https://upload.wikimedia.org/wikipedia/commons/e/e1/FlockingBoids.gif)

---

## 📂 The Versions

### 1. `boids_oop.py` (Object Oriented + Spatial Grid)
* **Approach:** Uses Python classes (`class Boid`) and a `SpatialGrid` class to manage neighbor lookups.
* **Best For:** Understanding the code, readability, and logic flow.
* **Performance:** Good for 300-500 boids.
* **Key Tech:** Spatial Hashing (Grid) to avoid checking every boid against every other boid.

### 2. `boids_numpy.py` (Vectorized / Data-Oriented)
* **Approach:** Uses `numpy` arrays to store positions and velocities. It calculates distances and rules using matrix operations instead of `for` loops.
* **Best For:** Raw performance and massive flock sizes.
* **Performance:** Can handle 800-1500+ boids easily.
* **Key Tech:** Vectorization, Broadcasting, Boolean Masking.

---

## 🛠️ Installation & Usage

### Prerequisites
You need standard Python libraries plus **NumPy**.

```bash
pip install pygame numpy

🎮 ControlsBoth versions share similar controls, though the OOP version has more interactive physics tweaking.KeyActionSToggle SeparationAToggle AlignmentCToggle CohesionSpacePause SimulationVToggle Simple View (Dots vs Triangles)MCycle Mouse Modes (None -> Follow -> Scare)UP/DOWNAdd/Remove Boids (OOP Version Only)Q / WIncrease / Decrease Max Speed (OOP Version Only)E / RIncrease / Decrease Max Force (OOP Version Only)DToggle Debug Radius View (OOP Version Only)🧠 Technical Deep DiveSpatial Grid (OOP Version)Instead of an $O(N^2)$ operation where every boid checks every other boid, we divide the screen into grid cells. A boid only checks neighbors in its own cell and the 8 surrounding cells.Vectorization (NumPy Version)Instead of looping through objects, we perform math on the entire data set at once.Python# NumPy Example: Calculating distance to all neighbors at once
diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
dist_sq = np.sum(diff**2, axis=2)
📜 LicenseOpen Source. Feel free to use this for your own projects!
