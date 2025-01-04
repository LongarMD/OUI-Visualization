# D-Separation Algorithm

## What is D-Separation?

D-separation (directional separation) is a criterion used in Bayesian networks to determine whether two variables are conditionally independent given a set of other variables. This concept is crucial in understanding how information flows through a directed acyclic graph (DAG).

D-separation is based on blocking paths between nodes. A path can be blocked in three ways:

### 1. Serial Connection

A → B → C

- If B is observed (in the separating set), the path is blocked
- Information cannot flow through an observed middle node
- Example: If we know B's value, then learning A's value doesn't tell us anything new about C

### 2. Divergent Connection

B
↙ ↘
A C

- If B is observed, the path is blocked
- When we know the cause (B), its effects (A and C) become independent
- Example: If we know it rained (B), then wet grass (A) doesn't tell us anything new about a wet sidewalk (C)

### 3. Convergent Connection (v-structure)

A C
↘ ↙
B

- By default, the path is blocked (A and C are independent)
- The path becomes unblocked if B or any of B's descendants are observed
- Example: Flu (A) and Allergies (C) are independent until we observe their common effect, Sneezing (B)

## Algorithm Details

The algorithm works by:

1. Finding all undirected paths between the two selected nodes
2. For each path:
   - Identifying the type of connection at each intermediate node (serial, divergent, or convergent)
   - Determining which sets of nodes would block that path
3. Taking the intersection of blocking sets across all paths
