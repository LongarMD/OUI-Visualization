# Alpha-Beta Pruning Algorithm

Alpha-beta pruning is an optimization technique for the minimax algorithm, commonly used in game-playing AI. It helps reduce the number of nodes that need to be evaluated.

## How It Works

### Basic Concepts

1. **Players**: There are two players:

   - MAX (usually the AI) tries to maximize the score
   - MIN (usually the opponent) tries to minimize the score

2. **Alpha (α)**: The best (maximum) score that MAX has found so far
3. **Beta (β)**: The best (minimum) score that MIN has found so far

### The Tree Structure

- The game is represented as a tree where:
  - Triangles pointing up (▲) are MAX nodes
  - Triangles pointing down (▼) are MIN nodes
  - Players alternate between levels
  - Leaf nodes contain actual scores

### The Algorithm

1. Start at the root (MAX node) with:

   - α = -∞ (negative infinity)
   - β = +∞ (positive infinity)

2. As we traverse down:

   - Pass α and β values to children
   - At leaf nodes:
     - MAX nodes set their α to their value
     - MIN nodes set their β to their value

3. As we traverse back up:

   - For MAX nodes:
     - α = max(current α, child's value)
   - For MIN nodes:
     - β = min(current β, child's value)

4. Pruning occurs when α ≥ β:
   - This means we've found a path that one player won't choose
   - We can skip evaluating the remaining siblings
   - This is shown by a red line cutting off branches

## Using the Simulator

1. **Input Format**:

   - Tree Structure: Use format like "2|2,2" where:
     - Numbers before | show children at first level
     - Numbers after | show children at next level
   - Leaf Values: Enter comma-separated numbers

2. **Controls**:

   - Use ">" to step forward
   - Use "<" to step backward
   - Watch α and β values update
   - Red lines show pruned branches

3. **Visual Elements**:
   - ▲ (Green) = MAX nodes
   - ▼ (Red) = MIN nodes
   - Highlighted node = Currently processing
   - Dotted lines separate levels
   - Numbers show node values and α/β values

## Example

For input:

- Tree: "2|2,2"
- Leaves: "3,8,2,4"

The simulator will show how alpha-beta pruning:

1. Evaluates the leftmost path first
2. Uses those values to potentially skip evaluations
3. Arrives at the optimal decision while examining fewer nodes than minimax would

This optimization makes the algorithm much more efficient for larger game trees while still finding the same optimal move as minimax would.
