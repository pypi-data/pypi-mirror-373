from numba import njit, prange


@njit()
def maximum_path_each(path, value, t_x, t_y, max_neg_val):
    index = t_x - 1
    # Forward pass: Calculate max path sums
    for y in range(t_y):
        for x in range(max(0, t_x + y - t_y), min(t_x, y + 1)):
            v_cur = max_neg_val if x == y else value[x, y - 1]
            v_prev = (
                0.0
                if (x == 0 and y == 0)
                else (max_neg_val if x == 0 else value[x - 1, y - 1])
            )
            value[x, y] = max(v_cur, v_prev) + value[x, y]

    # Backtrack to store the path
    for y in range(t_y - 1, -1, -1):
        path[index, y] = 1
        if index != 0 and (index == y or value[index, y - 1] < value[index - 1, y - 1]):
            index -= 1


@njit()  # Took almost 10x the time while testing using "parallel=True".
def maximum_path(paths, values, t_xs, t_ys, max_neg_val=-1e9):
    """
    Example:
    ```python
        paths = tc.randn((2, 3, 3)).numpy()
        values = tc.randn((2, 3, 3)).numpy()
        t_xs = tc.tensor([3, 3, 3]).numpy()
        t_ys = tc.tensor([3, 3]).numpy()

        # to display values (before) and paths:
        print("=====================")
        print("Paths:")
        print(paths)
        print("Original Values:")
        print(values)

        maximum_path(paths, values, t_xs, t_ys)

        print("Updated Values:")
        print(values)
        print("=====================")

    ```
    Outputs:
    ```md
        =====================
        Paths:
        [[[ 2.310408   -1.9375949  -0.57884663]
        [ 1.0308106   1.0793993   0.4461908 ]
        [ 0.26789713  0.48924422  0.3409592 ]]]
        Original Values:
        [[[-0.48256454  0.51348686 -1.8236492 ]
        [ 0.9949021  -0.6066166   0.18991096]
        [ 1.2555764  -0.24222293 -0.78757876]]]
        Updated Values:
        [[[-0.48256454  0.51348686 -1.8236492 ]
        [ 0.9949021  -1.0891812   0.18991096]
        [ 1.2555764  -0.24222293 -1.87676   ]]]
        =====================
    ```
    This may not be the standard, but may work for your project.
    """
    batch_size = values.shape[0]
    for i in prange(batch_size):
        maximum_path_each(paths[i], values[i], t_xs[i], t_ys[i], max_neg_val)
